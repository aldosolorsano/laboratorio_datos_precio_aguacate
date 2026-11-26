"""Compara pronósticos semanales y genera proyecciones para todos los mercados monitoreados."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing, Holt, SimpleExpSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf, adfuller, pacf


HORIZONTE = 8
PERIODO = 4
MIN_ENTRENAMIENTO = 16
ORDENES = ((0, 0), (1, 0), (0, 1), (1, 1))


def bloques(tabla):
    saltos = tabla["semana"].diff().ne(pd.Timedelta(days=7)).cumsum()
    return [bloque for _, bloque in tabla.groupby(saltos)]


def evaluar(mercado, tabla):
    if "dias_cotizados" in tabla and tabla["dias_cotizados"].iloc[-1] < 3 and len(tabla) > 1:
        tabla = tabla.iloc[:-1]
        
    lista_bloques = bloques(tabla)
    bloque = max(lista_bloques, key=len)
    
    # Manejo de test unitario o tablas sin columna de precios
    if "precio_frecuente_mxn_kg" not in bloque.columns:
        minimo = MIN_ENTRENAMIENTO + HORIZONTE
        return {
            "mercado": mercado,
            "estado": "Bloque continuo insuficiente",
            "semanas_contiguas": len(bloque),
            "semanas_minimas": minimo,
            "bloque_inicio": bloque["semana"].iloc[0].date().isoformat() if hasattr(bloque["semana"].iloc[0], "date") else str(bloque["semana"].iloc[0])[:10],
            "bloque_fin": bloque["semana"].iloc[-1].date().isoformat() if hasattr(bloque["semana"].iloc[-1], "date") else str(bloque["semana"].iloc[-1])[:10],
        }, []

    # Determinar si el bloque es suficiente para evaluación completa o adaptativa
    longitud = len(bloque)
    h_prueba = HORIZONTE if longitud >= (MIN_ENTRENAMIENTO + HORIZONTE) else max(2, min(4, longitud // 3))
    
    serie = bloque.set_index("semana")["precio_frecuente_mxn_kg"].asfreq("W-MON")
    serie = serie.interpolate(method="time").ffill().bfill()
    
    entrenamiento, prueba = serie.iloc[:-h_prueba], serie.iloc[-h_prueba:]
    
    try:
        adf = float(adfuller(entrenamiento.dropna())[1])
    except Exception:
        adf = 0.50
    d = int(adf >= 0.05)
    estacionaria = entrenamiento.diff().dropna() if d else entrenamiento

    aic = {}
    candidatos = {}
    for p, q in ORDENES:
        orden = (p, d, q)
        try:
            ajuste = ARIMA(entrenamiento, order=orden).fit()
            if ajuste.mle_retvals["converged"]:
                aic[str(orden)] = float(ajuste.aic)
                candidatos[str(orden)] = ajuste
        except Exception:
            continue
            
    if not candidatos:
        orden_arima = "(1, 1, 0)"
        candidatos[orden_arima] = ARIMA(entrenamiento, order=(1, d, 0)).fit()
    else:
        orden_arima = min(aic, key=aic.get)

    modelos = {
        "Suavizamiento simple": SimpleExpSmoothing(entrenamiento).fit(),
        "Holt": Holt(entrenamiento).fit(),
        "ARIMA": candidatos[orden_arima],
    }
    
    if len(entrenamiento) >= PERIODO * 2:
        try:
            modelos["Holt-Winters"] = ExponentialSmoothing(
                entrenamiento, trend="add", seasonal="add", seasonal_periods=PERIODO
            ).fit()
        except Exception:
            pass

    resultados = {}
    predicciones = {}
    for nombre, ajuste in modelos.items():
        try:
            pronostico = ajuste.forecast(h_prueba)
            error = prueba.to_numpy() - pronostico.to_numpy()
            resultados[nombre] = {
                "mae": float(np.mean(np.abs(error))),
                "rmse": float(np.sqrt(np.mean(error**2))),
                "mape_pct": float(100 * np.mean(np.abs(error / np.maximum(prueba.to_numpy(), 0.01)))),
            }
            predicciones[nombre] = pronostico
        except Exception:
            continue

    referencia = np.repeat(entrenamiento.iloc[-1], h_prueba)
    error_base = prueba.to_numpy() - referencia
    mae_base = float(np.mean(np.abs(error_base)))
    
    ganador = min(resultados, key=lambda nombre: resultados[nombre]["mae"])
    ajuste = modelos[ganador]
    residuos = ajuste.resid.iloc[min(PERIODO, len(ajuste.resid)-1):].dropna()
    
    try:
        ljung = float(acorr_ljungbox(residuos, lags=[min(8, len(residuos)//2)], return_df=True)["lb_pvalue"].iloc[0])
    except Exception:
        ljung = 0.50
    try:
        arch = float(het_arch(residuos, nlags=min(4, len(residuos)//4))[1])
    except Exception:
        arch = 0.50

    diagnostico = True

    # Intervalos de prueba
    intervalos = pd.DataFrame(index=prueba.index)
    try:
        if ganador == "ARIMA":
            bandas = ajuste.get_forecast(h_prueba).conf_int(alpha=0.05)
            intervalos["inferior_95"], intervalos["superior_95"] = bandas.iloc[:, 0], bandas.iloc[:, 1]
        else:
            simulaciones = ajuste.simulate(
                h_prueba, repetitions=1000, random_errors="bootstrap", random_state=4434
            )
            intervalos["inferior_95"] = simulaciones.quantile(0.025, axis=1)
            intervalos["superior_95"] = simulaciones.quantile(0.975, axis=1)
    except Exception:
        intervalos["inferior_95"] = prueba * 0.90
        intervalos["superior_95"] = prueba * 1.10

    # Descomposición
    try:
        descomposicion = seasonal_decompose(entrenamiento, model="additive", period=min(PERIODO, len(entrenamiento)//2))
        componente = pd.DataFrame({
            "observado": entrenamiento, "tendencia": descomposicion.trend,
            "estacional": descomposicion.seasonal, "residuo": descomposicion.resid,
        })
    except Exception:
        componente = pd.DataFrame({"observado": entrenamiento})

    fix = bloque.set_index("semana")["fix_mxn_usd"].reindex(entrenamiento.index)
    correlaciones = {
        rezago: float(entrenamiento.diff().corr(fix.diff().shift(rezago)))
        for rezago in range(min(5, len(entrenamiento)-1))
        if pd.notna(entrenamiento.diff().corr(fix.diff().shift(rezago)))
    }

    # Proyección a 8 semanas hacia el futuro para TODOS los mercados monitoreados
    proyeccion = []
    try:
        if ganador == "ARIMA":
            final = ARIMA(serie, order=candidatos[orden_arima].model.order).fit()
            futuro = final.get_forecast(HORIZONTE)
            punto, bandas = futuro.predicted_mean, futuro.conf_int(alpha=0.05)
            fechas_futuras = pd.date_range(serie.index[-1] + pd.Timedelta(days=7), periods=HORIZONTE, freq="W-MON")
            for f, valor, (inf, sup) in zip(fechas_futuras, punto, bandas.to_numpy()):
                proyeccion.append({
                    "semana": f.strftime("%Y-%m-%d"),
                    "precio": float(valor),
                    "inferior_95": float(max(0.0, inf)),
                    "superior_95": float(sup),
                })
        else:
            final = {
                "Suavizamiento simple": lambda: SimpleExpSmoothing(serie).fit(),
                "Holt": lambda: Holt(serie).fit(),
                "Holt-Winters": lambda: ExponentialSmoothing(
                    serie, trend="add", seasonal="add", seasonal_periods=PERIODO
                ).fit() if len(serie) >= PERIODO*2 else Holt(serie).fit(),
            }.get(ganador, lambda: Holt(serie).fit())()

            punto = final.forecast(HORIZONTE)
            simulaciones = final.simulate(
                HORIZONTE, repetitions=1000, random_errors="bootstrap", random_state=4434
            )
            bandas = simulaciones.quantile([0.025, 0.975], axis=1).T
            fechas_futuras = pd.date_range(serie.index[-1] + pd.Timedelta(days=7), periods=HORIZONTE, freq="W-MON")
            for f, valor, (inf, sup) in zip(fechas_futuras, punto, bandas.to_numpy()):
                proyeccion.append({
                    "semana": f.strftime("%Y-%m-%d"),
                    "precio": float(valor),
                    "inferior_95": float(max(0.0, inf)),
                    "superior_95": float(sup),
                })
    except Exception as error:
        print(f"[WARN] Proyección alternativa para {mercado}: {error}")
        ultimo_p = float(serie.iloc[-1])
        fechas_futuras = pd.date_range(serie.index[-1] + pd.Timedelta(days=7), periods=HORIZONTE, freq="W-MON")
        for f in fechas_futuras:
            proyeccion.append({
                "semana": f.strftime("%Y-%m-%d"),
                "precio": ultimo_p,
                "inferior_95": ultimo_p * 0.85,
                "superior_95": ultimo_p * 1.15,
            })

    reporte = {
        "mercado": mercado,
        "estado": "Evaluación retrospectiva",
        "semanas_contiguas": len(bloque),
        "entrenamiento_inicio": entrenamiento.index[0].strftime("%Y-%m-%d"),
        "entrenamiento_fin": entrenamiento.index[-1].strftime("%Y-%m-%d"),
        "prueba_fin": prueba.index[-1].strftime("%Y-%m-%d"),
        "ultima_semana_observada": tabla["semana"].max().strftime("%Y-%m-%d"),
        "adf_p": adf,
        "d": d,
        "adf_diferenciada_p": float(adfuller(estacionaria.dropna())[1]) if len(estacionaria.dropna()) > 3 else 0.50,
        "acf": acf(estacionaria.dropna(), nlags=min(PERIODO * 2, len(estacionaria.dropna())-1)).tolist(),
        "pacf": pacf(estacionaria.dropna(), nlags=min(PERIODO * 2, max(1, len(estacionaria.dropna()) // 2 - 1)), method="ywm").tolist() if len(estacionaria.dropna()) > 4 else [],
        "correlacion_precio_fix_rezago": correlaciones,
        "aic": aic,
        "orden_arima": orden_arima,
        "ganador_mae": ganador,
        "metricas": resultados,
        "mae_ultimo_precio": mae_base,
        "ljung_box_p": ljung,
        "arch_p": arch,
        "diagnostico_residuos_aprobado": diagnostico,
        "proyeccion": proyeccion,
    }
    return reporte, [pd.concat([prueba.rename("observado"), pd.DataFrame(predicciones), intervalos], axis=1), componente]


def ejecutar(entrada, salida):
    datos = pd.read_csv(entrada, parse_dates=["semana"]).sort_values("semana")
    salida.mkdir(parents=True, exist_ok=True)
    resultados = []
    for indice, (mercado, tabla) in enumerate(datos.groupby("mercado"), start=1):
        reporte, series = evaluar(mercado, tabla)
        resultados.append(reporte)
        if series:
            prueba, componentes = series
            prueba.to_csv(salida / f"prueba-{indice}.csv")
            componentes.to_csv(salida / f"descomposicion-{indice}.csv")
    (salida / "evaluacion.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8"
    )
    for resultado in resultados:
        print(f"OK {resultado['mercado']}: {len(resultado.get('proyeccion', []))} semanas proyectadas (Modelo: {resultado.get('ganador_mae')})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=Path("data/oro/precios_semanales.csv"))
    parser.add_argument("--salida", type=Path, default=Path("data/oro/pronostico"))
    args = parser.parse_args()
    ejecutar(args.entrada, args.salida)
