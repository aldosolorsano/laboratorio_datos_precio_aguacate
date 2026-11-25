"""Pipeline E2: integra Reddit con la capa Oro de precios del aguacate.

Pasos:
  1. Ejecuta pipeline E1 (plata, oro, cuarentena desde SNIIM + Banxico + Open-Meteo).
  2. Transforma métricas Reddit desde bronce → plata → oro diario.
  3. Hace join entre cotizaciones_oro (E1) y reddit_metricas_diarias (E2) por fecha.
  4. Garantiza trazabilidad completa de cada registro: archivo_origen y fecha de ingesta bronce.
  5. Guarda data/oro/cotizaciones_e2.csv.
  6. Genera data/oro/linaje.json con el grafo de trazabilidad + hashes SHA-256.
  7. Genera data/oro/calidad_e2.json con métricas de cobertura y trazabilidad.

Uso:
  python -m pipeline.e2 [--bronce data/bronce] [--salida data]
"""

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# Importar pipeline E1
from pipeline.e1 import ejecutar as ejecutar_e1

from src.transformadores.integrar_reddit import ejecutar as ejecutar_reddit


# ---------------------------------------------------------------------------
# Utilidades de trazabilidad y linaje
# ---------------------------------------------------------------------------

def sha256_archivo(ruta: Path) -> str:
    """Calcula SHA-256 de un archivo. Devuelve 'N/A' si no existe."""
    if not ruta.exists():
        return "N/A"
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def listar_archivos_bronce(bronce: Path, patron: str) -> list[dict]:
    """Devuelve lista de {ruta_relativa, sha256} para un patrón glob."""
    return [
        {
            "ruta": str(p.relative_to(bronce)).replace("\\", "/"),
            "sha256": sha256_archivo(p),
        }
        for p in sorted(bronce.glob(patron))
    ]


def extraer_fecha_ingesta_bronce(ruta_archivo: str) -> str:
    """Extrae la fecha de captura/ingesta a partir de la ruta del archivo bronce.
    Ejemplo: 'sniim/2026-11-09/aguacate...' -> '2026-11-09'
    """
    if not isinstance(ruta_archivo, str) or not ruta_archivo:
        return ""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", ruta_archivo)
    return m.group(1) if m else ""


def construir_linaje(bronce: Path, salida: Path, cotizaciones_e2: pd.DataFrame) -> dict:
    """Construye el grafo completo de trazabilidad para linaje.json."""
    ahora_utc = datetime.now(timezone.utc).isoformat()

    archivos_sniim = listar_archivos_bronce(bronce, "sniim/**/*.html")
    archivos_banxico = listar_archivos_bronce(bronce, "banxico/*.json")
    archivos_clima = listar_archivos_bronce(bronce, "openmeteo/*.json")
    archivos_reddit = listar_archivos_bronce(bronce, "reddit/*.json")

    def valores_unicos(col: str) -> list[str]:
        if col not in cotizaciones_e2.columns:
            return []
        vals = cotizaciones_e2[col].dropna().unique().tolist()
        expandido: list[str] = []
        for v in vals:
            expandido.extend(str(v).split("|"))
        return sorted(set(expandido))

    return {
        "_meta": {
            "pipeline": "e2",
            "generado_utc": ahora_utc,
            "filas_cotizaciones_e2": len(cotizaciones_e2),
            "descripcion": "Grafo de linaje y trazabilidad completa de registros de Capa Oro a Capa Bronce",
        },
        "nodos": {
            "bronce_sniim": archivos_sniim,
            "bronce_banxico": archivos_banxico,
            "bronce_clima": archivos_clima,
            "bronce_reddit": archivos_reddit,
        },
        "aristas": {
            "sniim_en_oro": valores_unicos("archivo_sniim"),
            "banxico_en_oro": valores_unicos("archivo_banxico"),
            "clima_en_oro": valores_unicos("archivo_clima"),
            "reddit_en_oro": valores_unicos("archivo_reddit"),
        },
        "reglas_trazabilidad": {
            "clave_registro_oro": ["fecha", "presentacion", "origen", "mercado"],
            "trazabilidad_primaria": {
                "origen_bronce": "archivo_sniim",
                "fecha_ingesta_bronce": "ingesta_bronce_fecha",
            },
            "trazabilidad_contextual": {
                "origen_tipo_cambio": "archivo_banxico",
                "origen_clima": "archivo_clima",
                "origen_redes_sociales": "archivo_reddit",
            },
        },
        "salidas": {
            "cotizaciones_e2": str(salida / "oro" / "cotizaciones_e2.csv"),
            "reddit_metricas_diarias_oro": str(salida / "oro" / "reddit_metricas_diarias.csv"),
        },
    }


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def ejecutar(bronce: Path, salida: Path) -> None:
    ahora_utc = datetime.now(timezone.utc).isoformat()
    print("=" * 60)
    print("PIPELINE E2 — Observatorio del Aguacate")
    print(f"Inicio UTC: {ahora_utc}")
    print("=" * 60)

    # ------------------------------------------------------------------
    # PASO 1: Ejecutar E1 (genera plata, oro, cuarentena)
    # ------------------------------------------------------------------
    print("\n[1/4] Ejecutando pipeline E1...")
    try:
        ejecutar_e1(bronce, salida)
    except Exception as error:
        print(f"[ERROR] Pipeline E1 falló: {error}")
        raise

    # ------------------------------------------------------------------
    # PASO 2: Transformar Reddit bronce → plata → oro diario
    # ------------------------------------------------------------------
    print("\n[2/4] Transformando métricas Reddit (Bronce → Plata → Oro)...")
    bronce_reddit = bronce / "reddit"
    plata_reddit_csv = salida / "plata" / "reddit_metricas_diarias.csv"
    oro_reddit_csv = salida / "oro" / "reddit_metricas_diarias.csv"

    _, reddit_oro = ejecutar_reddit(
        bronce_dir=bronce_reddit,
        plata_csv=plata_reddit_csv,
        oro_csv=oro_reddit_csv,
    )

    # ------------------------------------------------------------------
    # PASO 3: Join cotizaciones_oro (E1) + reddit_metricas_diarias (E2)
    # ------------------------------------------------------------------
    print("\n[3/4] Integrando cotizaciones E1 con métricas Reddit...")
    cotizaciones_e1_ruta = salida / "oro" / "cotizaciones.csv"

    if not cotizaciones_e1_ruta.exists():
        raise FileNotFoundError(f"No se encontró {cotizaciones_e1_ruta}. ¿Falló E1?")

    cotizaciones = pd.read_csv(cotizaciones_e1_ruta, dtype=str)

    if not reddit_oro.empty:
        cols_reddit = [
            "fecha",
            "posts_mencionando_aguacate",
            "score_total",
            "score_promedio",
            "comentarios_total",
            "ratio_positivo_promedio",
            "archivo_reddit",
            "_ingesta_bronce_utc",
        ]
        cols_disponibles = [c for c in cols_reddit if c in reddit_oro.columns]
        reddit_para_join = reddit_oro[cols_disponibles].copy()
        reddit_para_join["fecha"] = reddit_para_join["fecha"].astype(str)

        cotizaciones_e2 = cotizaciones.merge(
            reddit_para_join,
            on="fecha",
            how="left",
            validate="many_to_one",
        )
    else:
        cotizaciones_e2 = cotizaciones.copy()
        for col in ["posts_mencionando_aguacate", "score_total", "score_promedio",
                    "comentarios_total", "ratio_positivo_promedio", "archivo_reddit",
                    "_ingesta_bronce_utc"]:
            cotizaciones_e2[col] = None

    # Trazabilidad completa garantizada para cada registro en Oro:
    # 1. Archivo origen en Bronce (archivo_sniim ya presente)
    # 2. Fecha de ingesta en Bronce (extraída de la ruta de captura)
    cotizaciones_e2["ingesta_bronce_fecha"] = cotizaciones_e2["archivo_sniim"].apply(extraer_fecha_ingesta_bronce)
    # 3. Timestamp UTC de compilación en Capa Oro
    cotizaciones_e2["_compilacion_oro_utc"] = ahora_utc

    # Guardar cotizaciones_e2.csv
    ruta_e2 = salida / "oro" / "cotizaciones_e2.csv"
    ruta_e2.parent.mkdir(parents=True, exist_ok=True)
    cotizaciones_e2.to_csv(ruta_e2, index=False)
    print(f"Guardado: {ruta_e2} ({len(cotizaciones_e2)} filas)")

    # ------------------------------------------------------------------
    # PASO 4: Generar linaje.json y calidad_e2.json
    # ------------------------------------------------------------------
    print("\n[4/4] Generando linaje.json y calidad_e2.json...")

    linaje = construir_linaje(bronce, salida, cotizaciones_e2)
    ruta_linaje = salida / "oro" / "linaje.json"
    ruta_linaje.write_text(
        json.dumps(linaje, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Guardado: {ruta_linaje}")

    # Métricas de calidad E2
    dias_sniim = cotizaciones_e2["fecha"].nunique() if "fecha" in cotizaciones_e2.columns else 0
    filas_con_reddit = cotizaciones_e2["archivo_reddit"].notna().sum() if "archivo_reddit" in cotizaciones_e2.columns else 0
    dias_con_reddit = cotizaciones_e2[cotizaciones_e2["archivo_reddit"].notna()]["fecha"].nunique() if "archivo_reddit" in cotizaciones_e2.columns else 0

    posts_capturados = 0
    if "posts_mencionando_aguacate" in cotizaciones_e2.columns:
        # Sumar los posts de las fechas únicas con datos de Reddit
        fechas_reddit = cotizaciones_e2.dropna(subset=["posts_mencionando_aguacate"]).drop_duplicates(subset=["fecha"])
        posts_capturados = int(fechas_reddit["posts_mencionando_aguacate"].astype(float).sum())

    # Trazabilidad primaria obligatoria: cada fila tiene su archivo_sniim y su fecha de ingesta en bronce
    origen_existe = cotizaciones_e2["archivo_sniim"].map(
        lambda ruta: isinstance(ruta, str) and (bronce / ruta).is_file()
    )
    fecha_existe = cotizaciones_e2["ingesta_bronce_fecha"].ne("")
    trazabilidad_primaria_completa = float((origen_existe & fecha_existe).mean() * 100)

    calidad = {
        "pipeline": "e2",
        "generado_utc": ahora_utc,
        "filas_totales_oro": len(cotizaciones_e2),
        "dias_sniim_en_oro": int(dias_sniim),
        "trazabilidad_bronce_a_oro_pct": round(float(trazabilidad_primaria_completa), 2),
        "metricas_reddit": {
            "posts_unicos_capturados": int(reddit_oro["posts_mencionando_aguacate"].sum()),
            "posts_en_fechas_sniim": posts_capturados,
            "dias_con_datos_reddit": int(dias_con_reddit),
            "filas_oro_enriquecidas_con_reddit": int(filas_con_reddit),
        },
        "cobertura_fuentes_contextuales": {
            "banxico_fix_pct": round(float(cotizaciones_e2["fix_mxn_usd"].notna().mean() * 100), 2),
            "openmeteo_clima_pct": round(float(cotizaciones_e2["temperatura_c"].notna().mean() * 100), 2),
        },
        "capturas_reddit": len(list(bronce_reddit.glob("reddit_aguacate_*.json"))),
        "estado_fuente_especializada": (
            "con_observaciones" if not reddit_oro.empty else "sin_observaciones"
        ),
    }

    ruta_calidad = salida / "oro" / "calidad_e2.json"
    ruta_calidad.write_text(
        json.dumps(calidad, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Guardado: {ruta_calidad}")

    print("\n" + "=" * 60)
    print("PIPELINE E2 COMPLETADO")
    print(f"  Filas en cotizaciones_e2.csv          : {len(cotizaciones_e2)}")
    print(f"  Trazabilidad Bronce → Oro             : {trazabilidad_primaria_completa:.1f}%")
    print(f"  Días enriquecidos con métricas Reddit : {dias_con_reddit}")
    print(f"  Cotizaciones vinculadas a Reddit      : {filas_con_reddit}")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bronce", type=Path, default=Path("data/bronce"))
    parser.add_argument("--salida", type=Path, default=Path("data"))
    args = parser.parse_args()
    ejecutar(args.bronce, args.salida)
