"""Transforma datos bronce de Reddit a Plata y los integra en Oro.

Flujo:
  data/bronce/reddit/*.json
      ↓ deduplica por id
      ↓ agrega métricas por día
  data/plata/reddit_metricas_diarias.csv
      ↓ añade linaje
  data/oro/reddit_metricas_diarias.csv
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


BRONCE_DIR = Path("data/bronce/reddit")
PLATA_CSV = Path("data/plata/reddit_metricas_diarias.csv")
ORO_CSV = Path("data/oro/reddit_metricas_diarias.csv")


# ---------------------------------------------------------------------------
# Lectura y deduplicación de bronce
# ---------------------------------------------------------------------------

def leer_bronce(bronce_dir: Path) -> tuple[pd.DataFrame, dict[str, str]]:
    """Lee todos los JSON de bronce/reddit y devuelve un DataFrame deduplicado.

    Returns:
        df: DataFrame con todos los registros únicos.
        meta_por_id: dict {post_id -> ruta_relativa_archivo_bronce}.
    """
    archivos = sorted(bronce_dir.glob("reddit_aguacate_*.json"))
    if not archivos:
        print(f"[WARN] No se encontraron archivos en {bronce_dir}")
        return pd.DataFrame(), {}

    todos: list[dict] = []
    meta_por_id: dict[str, str] = {}  # id -> archivo bronce más antiguo

    for archivo in archivos:
        ruta_rel = str(archivo).replace("\\", "/")
        # Ruta relativa desde la raíz del proyecto
        partes = ruta_rel.split("/")
        try:
            idx = partes.index("data")
            ruta_relativa = "/".join(partes[idx:])
        except ValueError:
            ruta_relativa = ruta_rel

        try:
            payload = json.loads(archivo.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as error:
            print(f"[WARN] No se pudo leer {archivo}: {error}")
            continue

        registros = payload.get("registros", [])
        capturado_utc = payload.get("_meta", {}).get("capturado_utc", "")

        for r in registros:
            rid = r.get("id")
            if not rid:
                continue
            # Enriquecer con metadatos de archivo
            r["_archivo_bronce"] = ruta_relativa
            r["_capturado_utc"] = capturado_utc
            todos.append(r)
            # Guardar el archivo más antiguo como origen canónico
            if rid not in meta_por_id:
                meta_por_id[rid] = ruta_relativa

    if not todos:
        return pd.DataFrame(), {}

    df = pd.DataFrame(todos)

    # Deduplicar: conservar primera aparición de cada id (archivo más antiguo)
    df = df.drop_duplicates(subset="id", keep="first")

    # Convertir timestamp Unix a fecha
    df["fecha"] = pd.to_datetime(df["created_utc"], unit="s", utc=True).dt.strftime("%Y-%m-%d")

    print(f"Bronce: {len(archivos)} archivos | {len(df)} posts únicos")
    return df, meta_por_id


# ---------------------------------------------------------------------------
# Transformación a Plata
# ---------------------------------------------------------------------------

def transformar_plata(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega métricas por fecha (día calendario UTC del post).

    Columnas de salida:
        fecha, posts_mencionando_aguacate, score_total, score_promedio,
        comentarios_total, ratio_positivo_promedio, archivo_reddit
    """
    if df.empty:
        return pd.DataFrame(columns=[
            "fecha", "posts_mencionando_aguacate", "score_total",
            "score_promedio", "comentarios_total", "ratio_positivo_promedio",
            "archivo_reddit",
        ])

    agregado = df.groupby("fecha", as_index=False).agg(
        posts_mencionando_aguacate=("id", "count"),
        score_total=("score", "sum"),
        score_promedio=("score", "mean"),
        comentarios_total=("num_comments", "sum"),
        ratio_positivo_promedio=("upvote_ratio", "mean"),
        # Trazabilidad: lista de archivos bronce fuente (dedupada y ordenada)
        archivo_reddit=("_archivo_bronce", lambda s: "|".join(sorted(s.unique()))),
    )

    agregado["score_promedio"] = agregado["score_promedio"].round(2)
    agregado["ratio_positivo_promedio"] = agregado["ratio_positivo_promedio"].round(4)
    return agregado.sort_values("fecha").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Transformación a Oro
# ---------------------------------------------------------------------------

def transformar_oro(plata: pd.DataFrame, df_bronce: pd.DataFrame) -> pd.DataFrame:
    """Añade columnas de linaje a la capa Plata para producir la capa Oro."""
    if plata.empty:
        return plata.copy()

    # _ingesta_bronce_utc: timestamp de captura del primer archivo bronce de cada día
    if not df_bronce.empty and "_capturado_utc" in df_bronce.columns:
        ingesta_por_fecha = (
            df_bronce.groupby("fecha")["_capturado_utc"]
            .first()
            .reset_index()
            .rename(columns={"_capturado_utc": "_ingesta_bronce_utc"})
        )
        oro = plata.merge(ingesta_por_fecha, on="fecha", how="left")
    else:
        oro = plata.copy()
        oro["_ingesta_bronce_utc"] = ""

    oro["_linaje_fuente"] = "reddit-api-v1"
    return oro


# ---------------------------------------------------------------------------
# Persistencia
# ---------------------------------------------------------------------------

def guardar(df: pd.DataFrame, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False)
    print(f"Guardado: {ruta} ({len(df)} filas)")


# ---------------------------------------------------------------------------
# Punto de entrada principal
# ---------------------------------------------------------------------------

def ejecutar(
    bronce_dir: Path = BRONCE_DIR,
    plata_csv: Path = PLATA_CSV,
    oro_csv: Path = ORO_CSV,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Transforma bronce Reddit → plata → oro. Devuelve (plata, oro)."""
    print("=== Transformador Reddit: Bronce → Plata → Oro ===")

    df_bronce, _ = leer_bronce(bronce_dir)
    plata = transformar_plata(df_bronce)
    oro = transformar_oro(plata, df_bronce)

    guardar(plata, plata_csv)
    guardar(oro, oro_csv)

    print(f"Días con métricas Reddit: {len(plata)}")
    return plata, oro


if __name__ == "__main__":
    ejecutar()
