"""Extractor de métricas agregadas de redes sociales (Mastodon API oficial).

Consulta publicaciones reales mediante la API pública de Mastodon con paginación
multietiqueta para capturar un volumen representativo de interacciones y comentarios.
Tags: 'aguacate', 'palta', 'avocado'
"""

import json
from datetime import datetime, timezone
from pathlib import Path
import requests

API_BASE = "https://mastodon.social/api/v1/timelines/tag"
USER_AGENT = "TrustedDataLab-Aguacate/0.3 (academic project; contact: aldosolorsano@users.noreply.github.com)"
BRONCE_DIR = Path("data/bronce/redes")
TAGS = ["aguacate", "palta", "avocado"]
PAGINAS_POR_TAG = 4


def extraer_metricas_reales() -> list[dict]:
    headers = {"User-Agent": USER_AGENT}
    todos = []
    ids_vistos = set()

    for tag in TAGS:
        url = f"{API_BASE}/{tag}?limit=40"
        for _ in range(PAGINAS_POR_TAG):
            try:
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code != 200:
                    break
                posts = response.json()
                if not posts:
                    break
                for toot in posts:
                    post_id = str(toot.get("id"))
                    if post_id in ids_vistos:
                        continue
                    ids_vistos.add(post_id)

                    created_at = toot.get("created_at", "")
                    replies = int(toot.get("replies_count", 0))
                    reblogs = int(toot.get("reblogs_count", 0))
                    favourites = int(toot.get("favourites_count", 0))
                    fecha = created_at[:10] if created_at else ""

                    todos.append({
                        "id": post_id,
                        "red_social": "mastodon",
                        "tag_busqueda": tag,
                        "fecha": fecha,
                        "created_at_utc": created_at,
                        "respuestas": replies,
                        "compartidos": reblogs,
                        "favoritos": favourites,
                        "interacciones_totales": replies + reblogs + favourites,
                    })

                max_id = posts[-1]["id"]
                url = f"{API_BASE}/{tag}?limit=40&max_id={max_id}"
            except Exception as error:
                print(f"[WARN] Error en tag {tag}: {error}")
                break

    total_comentarios = sum(p["respuestas"] for p in todos)
    print(f"Mastodon API: {len(todos)} publicaciones extraídas con {total_comentarios} comentarios y {sum(p['interacciones_totales'] for p in todos)} interacciones totales.")
    return todos


def guardar_bronce(registros: list[dict], salida_dir: Path = BRONCE_DIR) -> Path:
    salida_dir.mkdir(parents=True, exist_ok=True)
    hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    archivo = salida_dir / f"redes_aguacate_{hoy}.json"

    payload = {
        "_meta": {
            "fuente": "mastodon-social-api-v1",
            "tags_consultados": TAGS,
            "capturado_utc": datetime.now(timezone.utc).isoformat(),
            "total_publicaciones": len(registros),
            "total_comentarios": sum(r["respuestas"] for r in registros),
            "tipo_datos": "metricas cuantitativas agregadas",
        },
        "registros": registros,
    }

    archivo.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Guardado en bronce: {archivo} ({len(registros)} registros)")
    return archivo


def main():
    registros = extraer_metricas_reales()
    if registros:
        guardar_bronce(registros)


if __name__ == "__main__":
    main()
