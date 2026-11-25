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
import re
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
        try:
            payload = json.loads(archivo.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as error:
            raise ValueError(f"No se pudo leer la captura {archivo}") from error

        registros = payload.get("registros", [])
        capturado_utc = payload.get("_meta", {}).get("capturado_utc", "")
        if not capturado_utc:
            raise ValueError(f"Falta fecha de captura en {archivo}")
        captura = pd.Timestamp(capturado_utc)
        if captura.tzinfo is None:
            raise ValueError(f"La captura necesita zona horaria: {archivo}")

        for r in registros:
            rid = r.get("id")
            if not isinstance(rid, str) or not re.fullmatch(r"[0-9a-z]+", rid):
                raise ValueError(f"Identificador Reddit no válido en {archivo}: {rid}")
            campos_prohibidos = {"author", "title", "selftext", "body", "user", "username", "email"}
            if campos_prohibidos.intersection(r):
                raise ValueError(f"Campos no admitidos en {archivo}")
            fecha_post = pd.to_datetime(r["created_utc"], unit="s", utc=True)
            if fecha_post > captura:
                raise ValueError(f"Publicación posterior a la captura en {archivo}")
            if (payload.get("_meta", {}).get("ventana_busqueda") == "week"
                    and fecha_post < captura - pd.Timedelta(days=7)):
                raise ValueError(f"Publicación fuera de la ventana week en {archivo}")
            if (not isinstance(r["score"], int) or not isinstance(r["num_comments"], int)
                    or r["num_comments"] < 0 or not 0 <= r["upvote_ratio"] <= 1):
                raise ValueError(f"Métricas Reddit no válidas en {archivo}")
            # Enriquecer con metadatos de archivo
            r["_archivo_bronce"] = archivo.relative_to(bronce_dir.parent).as_posix()
            r["_capturado_utc"] = capturado_utc
            todos.append(r)
            # Guardar el archivo más antiguo como origen canónico
            if rid not in meta_por_id:
                meta_por_id[rid] = r["_archivo_bronce"]

    if not todos:
        return pd.DataFrame(), {}

    df = pd.DataFrame(todos)

    # Deduplicar: conservar primera aparición de cada id (archivo más antiguo)
    df = df.drop_duplicates(subset="id", keep="first")

    # La unión con SNIIM usa el día calendario de Ciudad de México.
    df["fecha"] = (pd.to_datetime(df["created_utc"], unit="s", utc=True)
                   .dt.tz_convert("America/Mexico_City").dt.strftime("%Y-%m-%d"))

    print(f"Bronce: {len(archivos)} archivos | {len(df)} posts únicos")
    return df, meta_por_id


# ---------------------------------------------------------------------------
# Transformación a Plata
# ---------------------------------------------------------------------------

def transformar_plata(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega métricas por fecha local de Ciudad de México.

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
