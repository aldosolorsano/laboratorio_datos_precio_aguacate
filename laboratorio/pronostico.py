"""Compara pronósticos semanales en un bloque continuo y genera evidencia de E1."""

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
PERIODO = 4  # Ciclo exploratorio de cuatro semanas, sin asumir un ciclo anual.
MIN_ENTRENAMIENTO = 16
ORDENES = ((0, 0), (1, 0), (0, 1), (1, 1))


def bloques(tabla):
    saltos = tabla["semana"].diff().ne(pd.Timedelta(weeks=1)).cumsum()
    return [bloque for _, bloque in tabla.groupby(saltos)]


def evaluar(mercado, tabla):
    if "dias_cotizados" in tabla and tabla["dias_cotizados"].iloc[-1] < 3 and len(tabla) > 1:
        tabla = tabla.iloc[:-1]
    bloque = max(bloques(tabla), key=len)
    if len(bloque) < MIN_ENTRENAMIENTO + HORIZONTE:
        minimo = MIN_ENTRENAMIENTO + HORIZONTE
        return {"mercado": mercado, "estado": "Bloque continuo insuficiente",
                "semanas_contiguas": len(bloque), "semanas_minimas": minimo,
                "bloque_inicio": bloque["semana"].iloc[0].date().isoformat(),
                "bloque_fin": bloque["semana"].iloc[-1].date().isoformat()}, []
    serie = bloque.set_index("semana")["precio_frecuente_mxn_kg"].asfreq("W-MON")
    entrenamiento, prueba = serie.iloc[:-HORIZONTE], serie.iloc[-HORIZONTE:]
    adf = float(adfuller(entrenamiento)[1])
    d = int(adf >= 0.05)
    estacionaria = entrenamiento.diff().dropna() if d else entrenamiento
    aic = {}
    candidatos = {}
    for p, q in ORDENES:
        orden = p, d, q
        ajuste = ARIMA(entrenamiento, order=orden).fit()
        if ajuste.mle_retvals["converged"]:
            aic[str(orden)] = float(ajuste.aic)
            candidatos[str(orden)] = ajuste
    orden_arima = min(aic, key=aic.get)
    modelos = {
        "Suavizamiento simple": SimpleExpSmoothing(entrenamiento).fit(),
        "Holt": Holt(entrenamiento).fit(),
        "Holt-Winters": ExponentialSmoothing(
            entrenamiento, trend="add", seasonal="add", seasonal_periods=PERIODO
        ).fit(),
        "ARIMA": candidatos[orden_arima],
    }
    resultados = {}
    predicciones = {}
    for nombre, ajuste in modelos.items():
        pronostico = ajuste.forecast(HORIZONTE)
        error = prueba.to_numpy() - pronostico.to_numpy()
        resultados[nombre] = {
            "mae": float(np.mean(np.abs(error))),
            "rmse": float(np.sqrt(np.mean(error**2))),
            "mape_pct": float(100 * np.mean(np.abs(error / prueba.to_numpy()))),
        }
        predicciones[nombre] = pronostico
    referencia = np.repeat(entrenamiento.iloc[-1], HORIZONTE)
    error_base = prueba.to_numpy() - referencia
    ganador = min(resultados, key=lambda nombre: resultados[nombre]["mae"])
    ajuste = modelos[ganador]
    residuos = ajuste.resid.iloc[PERIODO:].dropna()
    ljung = float(acorr_ljungbox(residuos, lags=[8], return_df=True)["lb_pvalue"].iloc[0])
    arch = float(het_arch(residuos, nlags=4)[1])
    diagnostico = ljung >= 0.05 and arch >= 0.05
    mae_base = float(np.mean(np.abs(error_base)))
    intervalos = pd.DataFrame(index=prueba.index)
    if diagnostico:
        if ganador == "ARIMA":
            bandas = ajuste.get_forecast(HORIZONTE).conf_int(alpha=0.05)
            intervalos["inferior_95"], intervalos["superior_95"] = bandas.iloc[:, 0], bandas.iloc[:, 1]
        else:
            simulaciones = ajuste.simulate(
                HORIZONTE, repetitions=2000, random_errors="bootstrap", random_state=4434
            )
            intervalos["inferior_95"] = simulaciones.quantile(0.025, axis=1)
            intervalos["superior_95"] = simulaciones.quantile(0.975, axis=1)
    descomposicion = seasonal_decompose(entrenamiento, model="additive", period=PERIODO)
    componente = pd.DataFrame({
        "observado": entrenamiento, "tendencia": descomposicion.trend,
        "estacional": descomposicion.seasonal, "residuo": descomposicion.resid,
    })
    fix = bloque.set_index("semana")["fix_mxn_usd"].reindex(entrenamiento.index)
    correlaciones = {
        rezago: entrenamiento.diff().corr(fix.diff().shift(rezago)) for rezago in range(5)
    }
    proyeccion = []
    if (diagnostico and resultados[ganador]["mae"] < mae_base
            and prueba.index[-1] == tabla["semana"].max()):
        if ganador == "ARIMA":
            final = ARIMA(serie, order=candidatos[orden_arima].model.order).fit()
            if final.mle_retvals["converged"]:
                futuro = final.get_forecast(HORIZONTE)
                punto, bandas = futuro.predicted_mean, futuro.conf_int(alpha=0.05)
            else:
                punto, bandas = pd.Series(dtype=float), pd.DataFrame()
        else:
            final = {
                "Suavizamiento simple": lambda: SimpleExpSmoothing(serie).fit(),
                "Holt": lambda: Holt(serie).fit(),
                "Holt-Winters": lambda: ExponentialSmoothing(
                    serie, trend="add", seasonal="add", seasonal_periods=PERIODO
                ).fit(),
            }[ganador]()
            punto = final.forecast(HORIZONTE)
            simulaciones = final.simulate(
                HORIZONTE, repetitions=2000, random_errors="bootstrap", random_state=4434
            )
            bandas = simulaciones.quantile([0.025, 0.975], axis=1).T
        proyeccion = [
            {"semana": fecha.date().isoformat(), "precio": float(valor),
             "inferior_95": float(inferior), "superior_95": float(superior)}
            for (fecha, valor), (inferior, superior) in zip(punto.items(), bandas.to_numpy())
        ]
    reporte = {
        "mercado": mercado, "estado": "Evaluación retrospectiva",
        "semanas_contiguas": len(bloque),
        "entrenamiento_inicio": entrenamiento.index[0].date().isoformat(),
        "entrenamiento_fin": entrenamiento.index[-1].date().isoformat(),
        "prueba_fin": prueba.index[-1].date().isoformat(),
        "ultima_semana_observada": tabla["semana"].max().date().isoformat(),
        "adf_p": adf, "d": d, "adf_diferenciada_p": float(adfuller(estacionaria)[1]),
        "acf": acf(estacionaria, nlags=PERIODO * 2).tolist(),
        "pacf": pacf(estacionaria, nlags=min(PERIODO * 2, len(estacionaria) // 2 - 1),
                     method="ywm").tolist(),
        "correlacion_precio_fix_rezago": {
            k: float(v) if pd.notna(v) else None for k, v in correlaciones.items()
        },
        "aic": aic, "orden_arima": orden_arima, "ganador_mae": ganador,
        "metricas": resultados, "mae_ultimo_precio": mae_base,
        "ljung_box_p": ljung, "arch_p": arch,
        "diagnostico_residuos_aprobado": diagnostico,
        "proyeccion": proyeccion,
    }
    return reporte, [pd.concat([prueba.rename("observado"), pd.DataFrame(predicciones),
                                intervalos], axis=1), componente]


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
        print(resultado["mercado"], resultado["estado"], resultado.get("ganador_mae", ""))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=Path("data/oro/precios_semanales.csv"))
    parser.add_argument("--salida", type=Path, default=Path("data/oro/pronostico"))
    args = parser.parse_args()
    ejecutar(args.entrada, args.salida)
