"""Transforma métricas de redes sociales de Bronce a Plata y Oro.

Lee datos reales de redes sociales desde data/bronce/redes/ (y data/bronce/reddit/)
Agrega por fecha para correlacionar con los precios mayoristas diarios del aguacate.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd


def leer_bronce_redes(bronce_dir: Path) -> pd.DataFrame:
    archivos = sorted(bronce_dir.glob("redes_aguacate_*.json"))
    registros = []
    for archivo in archivos:
        try:
            contenido = json.loads(archivo.read_text(encoding="utf-8"))
            capturado_utc = contenido.get("_meta", {}).get("capturado_utc", "")
            fuente = contenido.get("_meta", {}).get("fuente", "mastodon-social-api-v1")
            ruta_rel = str(archivo).replace("\\", "/")
            partes = ruta_rel.split("/")
            try:
                idx = partes.index("data")
                ruta_relativa = "/".join(partes[idx:])
            except ValueError:
                ruta_relativa = ruta_rel

            for r in contenido.get("registros", []):
                r["_archivo_bronce"] = ruta_relativa
                r["_capturado_utc"] = capturado_utc
                r["_fuente"] = fuente
                registros.append(r)
        except Exception as error:
            print(f"[WARN] Error leyendo {archivo}: {error}")
            continue

    if not registros:
        return pd.DataFrame()

    df = pd.DataFrame(registros)
    # Deduplicar por id único de publicación
    df = df.drop_duplicates(subset=["id", "_fuente"], keep="first")
    return df


def transformar_plata_redes(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[
            "fecha", "menciones_redes", "interacciones_totales",
            "favoritos_total", "compartidos_total", "respuestas_total", "archivo_redes"
        ])

    agregado = df.groupby("fecha", as_index=False).agg(
        menciones_redes=("id", "count"),
        interacciones_totales=("interacciones_totales", "sum"),
        favoritos_total=("favoritos", "sum"),
        compartidos_total=("compartidos", "sum"),
        respuestas_total=("respuestas", "sum"),
        archivo_redes=("_archivo_bronce", lambda s: "|".join(sorted(s.unique()))),
    )
    return agregado.sort_values("fecha").reset_index(drop=True)


def transformar_oro_redes(plata: pd.DataFrame, df_bronce: pd.DataFrame) -> pd.DataFrame:
    if plata.empty:
        return plata.copy()
    oro = plata.copy()
    if not df_bronce.empty and "_capturado_utc" in df_bronce.columns:
        ingesta = df_bronce.groupby("fecha")["_capturado_utc"].first().reset_index().rename(
            columns={"_capturado_utc": "_ingesta_bronce_utc"}
        )
        oro = oro.merge(ingesta, on="fecha", how="left")
    else:
        oro["_ingesta_bronce_utc"] = ""
    oro["_linaje_fuente"] = "mastodon-social-api-v1"
    return oro


def ejecutar(bronce_dir: Path, salida_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_bronce = leer_bronce_redes(bronce_dir)
    plata = transformar_plata_redes(df_bronce)
    oro = transformar_oro_redes(plata, df_bronce)

    ruta_plata = salida_dir / "plata" / "redes_metricas_diarias.csv"
    ruta_oro = salida_dir / "oro" / "redes_metricas_diarias.csv"
    ruta_plata.parent.mkdir(parents=True, exist_ok=True)
    ruta_oro.parent.mkdir(parents=True, exist_ok=True)

    plata.to_csv(ruta_plata, index=False)
    oro.to_csv(ruta_oro, index=False)
    print(f"Redes transformadas: {len(oro)} fechas registradas.")
    return plata, oro
