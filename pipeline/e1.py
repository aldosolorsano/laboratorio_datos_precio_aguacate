"""Construye plata, oro y cuarentena desde instantáneas locales de bronce."""

import argparse
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

from tools.perfilar_sniim import MERCADOS, PRECIO, kilos, leer_capturas


CLAVE = ["fecha", "presentacion", "origen", "mercado"]
PRECIOS = ["minimo_mxn_kg", "maximo_mxn_kg", "frecuente_mxn_kg"]
COLUMNAS = CLAVE + PRECIOS + ["archivo_sniim"]
LOCALIDADES = {
    "Jalisco": ("ciudad_guzman_jal",),
    "Michoacán": ("tancitaro_mich", "uruapan_mich"),
}
ESQUEMA = pa.DataFrameSchema(
    {
        **{c: pa.Column(str, pa.Check.str_length(min_value=1)) for c in CLAVE},
        **{c: pa.Column(float, pa.Check.gt(0)) for c in PRECIOS},
        "archivo_sniim": pa.Column(str),
    },
    checks=pa.Check(
        lambda d: d[PRECIOS[0]].le(d[PRECIOS[2]]) & d[PRECIOS[2]].le(d[PRECIOS[1]]),
        error="mínimo ≤ frecuente ≤ máximo",
    ),
    unique=CLAVE,
    strict=True,
)


def precios_por_kg(valores, peso):
    if not all(PRECIO.fullmatch(valor) for valor in valores):
        raise ValueError("formato o valor faltante en los precios")
    return [float(Decimal(valor.replace(",", "")) / peso) for valor in valores]


def limpiar(bronce):
    _, cotizaciones, filas = leer_capturas(bronce / "sniim", solo_completas=True)
    claves = Counter(fila[:4] for fila in cotizaciones)
    candidatos, originales, rechazos = [], [], []
    for fila, ruta in cotizaciones.items():
        fecha, presentacion, origen, mercado, minimo, maximo, frecuente, _ = fila
        archivo = ruta.relative_to(bronce).as_posix()
        original = [*fila, archivo]
        try:
            dia = pd.to_datetime(fecha, format="%d/%m/%Y").date().isoformat()
            precios = precios_por_kg((minimo, maximo, frecuente), kilos(presentacion))
            if claves[fila[:4]] > 1:
                raise ValueError("cotizaciones distintas con la misma clave")
        except ValueError as error:
            rechazos.append([*original, str(error)])
            continue
        candidatos.append([dia, presentacion, origen, mercado, *precios, archivo])
        originales.append(original)

    plata = pd.DataFrame(candidatos, columns=COLUMNAS)
    try:
        ESQUEMA.validate(plata, lazy=True)
    except pa.errors.SchemaErrors as error:
        motivos = {}
        for caso in error.failure_cases.itertuples():
            if pd.isna(caso.index):
                raise
            motivos.setdefault(caso.index, set()).add(str(caso.check))
        rechazos.extend([*originales[i], ", ".join(sorted(m))] for i, m in motivos.items())
        plata = plata.drop(index=list(motivos))
    plata = ESQUEMA.validate(plata).sort_values(CLAVE)
    cuarentena = pd.DataFrame(rechazos, columns=[
        *CLAVE, "minimo_original", "maximo_original", "frecuente_original",
        "observaciones", "archivo_sniim", "motivo",
    ])
    return plata, cuarentena, filas - len(cotizaciones)


def ultima_captura(bronce, patron):
    rutas = sorted(bronce.glob(patron))
    if not rutas:
        raise ValueError(f"Falta una captura para {patron}")
    ruta = rutas[-1]
    return json.loads(ruta.read_text(encoding="utf-8"))["respuesta"], ruta.relative_to(bronce).as_posix()


def integrar(plata, bronce):
    datos, archivo = ultima_captura(bronce, "banxico/usdmxn_*.json")
    fix = pd.DataFrame(datos["bmx"]["series"][0]["datos"])
    fix["fecha"] = pd.to_datetime(fix["fecha"], format="%d/%m/%Y").dt.strftime("%Y-%m-%d")
    fix["fix_mxn_usd"] = pd.to_numeric(fix["dato"].str.replace(",", ""), errors="coerce")
    fix["archivo_banxico"] = archivo
    tablas = []
    for origen, localidades in LOCALIDADES.items():
        for lugar in localidades:
            datos, archivo = ultima_captura(bronce, f"openmeteo/{lugar}_*.json")
            tabla = pd.DataFrame(datos["daily"]).rename(columns={
                "time": "fecha", "temperature_2m_mean": "temperatura_c",
                "precipitation_sum": "precipitacion_mm",
            })
            tablas.append(tabla.assign(origen=origen, archivo_clima=archivo))
    clima = pd.concat(tablas).groupby(["fecha", "origen"], as_index=False).agg(
        temperatura_c=("temperatura_c", "mean"),
        precipitacion_mm=("precipitacion_mm", "mean"),
        archivo_clima=("archivo_clima", lambda serie: "|".join(sorted(serie))),
    )
    oro = plata.merge(fix[["fecha", "fix_mxn_usd", "archivo_banxico"]], on="fecha",
                      how="left", validate="many_to_one")
    return oro.merge(clima, on=["fecha", "origen"], how="left", validate="many_to_one")


def semanal(oro):
    datos = oro.loc[oro["mercado"].isin(MERCADOS)].copy()
    dia = pd.to_datetime(datos["fecha"])
    datos["semana"] = dia - pd.to_timedelta(dia.dt.dayofweek, unit="D")
    # Cada día pesa lo mismo, aunque tenga más orígenes cotizados.
    diario = datos.groupby(["mercado", "semana", "fecha"], as_index=False).agg(
        precio=("frecuente_mxn_kg", "median"),
        fix=("fix_mxn_usd", "first"),
    )
    return diario.groupby(["mercado", "semana"], as_index=False).agg(
        precio_frecuente_mxn_kg=("precio", "median"),
        dias_cotizados=("fecha", "size"),
        fix_mxn_usd=("fix", "mean"),
    )


def perfil_precios(plata):
    """Describe los precios por mercado sin cambiar la serie del pronóstico."""
    grupos = plata.groupby("mercado")["frecuente_mxn_kg"]
    precios = plata["frecuente_mxn_kg"]
    minimo, maximo = grupos.transform("min"), grupos.transform("max")
    media, desviacion = grupos.transform("mean"), grupos.transform("std")
    q1 = grupos.transform("quantile", q=0.25)
    q3 = grupos.transform("quantile", q=0.75)
    amplitud = q3 - q1
    return plata[CLAVE].assign(
        frecuente_mxn_kg=precios,
        min_max=(precios - minimo).div((maximo - minimo).replace(0, float("nan"))),
        z_score=(precios - media).div(desviacion.replace(0, float("nan"))),
        banda_mxn_kg=pd.cut(
            precios, bins=[0, 25, 50, 75, 100, float("inf")],
            labels=["0–25", ">25–50", ">50–75", ">75–100", ">100"],
        ),
        atipico_iqr=precios.lt(q1 - 1.5 * amplitud) | precios.gt(q3 + 1.5 * amplitud),
    )


def ejecutar(bronce, salida):
    plata, cuarentena, repetidas = limpiar(bronce)
    oro = integrar(plata, bronce)
    semanas = semanal(oro)
    perfil = perfil_precios(plata)
    cotizaciones_objetivo = int(oro["mercado"].isin(MERCADOS).sum())
    for capa, nombre, tabla in (
        ("plata", "precios_sniim.csv", plata),
        ("oro", "cotizaciones.csv", oro),
        ("oro", "precios_semanales.csv", semanas),
        ("oro", "perfil_precios.csv", perfil),
        ("cuarentena", "precios_sniim.csv", cuarentena),
    ):
        ruta = salida / capa / nombre
        ruta.parent.mkdir(parents=True, exist_ok=True)
        tabla.to_csv(ruta, index=False)
    calidad = {
        "cotizaciones_validas": len(plata),
        "rechazos": len(cuarentena),
        "duplicados_exactos": repetidas,
        "mercados_semana": len(semanas),
        "cotizaciones_mercados_objetivo": cotizaciones_objetivo,
        "atipicos_iqr_marcados": int(perfil["atipico_iqr"].sum()),
        "valores_presentes_oro": oro.notna().sum().to_dict(),
    }
    (salida / "oro" / "calidad.json").write_text(
        json.dumps(calidad, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Plata: {len(plata)}. Cuarentena: {len(cuarentena)}. "
          f"Repetidas exactas: {repetidas}. Mercado-semana en oro: {len(semanas)}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bronce", type=Path, default=Path("data/bronce"))
    parser.add_argument("--salida", type=Path, default=Path("data"))
    args = parser.parse_args()
    ejecutar(args.bronce, args.salida)
