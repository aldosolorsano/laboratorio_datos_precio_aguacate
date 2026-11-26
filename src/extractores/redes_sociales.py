"""Extractor de métricas agregadas de redes sociales (Mastodon API oficial).

Consulta publicaciones reales sobre 'aguacate' mediante la API pública de Mastodon.
URL: https://mastodon.social/api/v1/timelines/tag/aguacate

Cumplimiento estricto de privacidad (cero datos personales):
  - Solo métricas numéricas agregadas: replies_count, reblogs_count, favourites_count, created_at.
  - Excluye estrictamente nombres de usuario, avatares, perfiles, menciones y contenido de texto.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
import requests

API_URL = "https://mastodon.social/api/v1/timelines/tag/aguacate"
USER_AGENT = "TrustedDataLab-Aguacate/0.3 (academic project; contact: aldosolorsano@users.noreply.github.com)"
BRONCE_DIR = Path("data/bronce/redes")


def extraer_metricas_reales() -> list[dict]:
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(API_URL, headers=headers, timeout=20)
        response.raise_for_status()
        toots = response.json()
    except requests.RequestException as error:
        print(f"[ERROR] Error al consultar Mastodon API: {error}")
        return []

    metricas_anonimas = []
    for toot in toots:
        # Cero datos personales: solo métricas cuantitativas públicas
        post_id = str(toot.get("id"))
        created_at = toot.get("created_at")
        replies = int(toot.get("replies_count", 0))
        reblogs = int(toot.get("reblogs_count", 0))
        favourites = int(toot.get("favourites_count", 0))

        # Convertir fecha ISO a fecha YYYY-MM-DD
        fecha = created_at[:10] if created_at else ""

        metricas_anonimas.append({
            "id": post_id,
            "red_social": "mastodon",
            "fecha": fecha,
            "created_at_utc": created_at,
            "respuestas": replies,
            "compartidos": reblogs,
            "favoritos": favourites,
            "interacciones_totales": replies + reblogs + favourites,
        })

    print(f"Mastodon API: {len(metricas_anonimas)} publicaciones reales extraídas sobre 'aguacate'.")
    return metricas_anonimas


def guardar_bronce(registros: list[dict], salida_dir: Path = BRONCE_DIR) -> Path:
    salida_dir.mkdir(parents=True, exist_ok=True)
    hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    archivo = salida_dir / f"redes_aguacate_{hoy}.json"

    payload = {
        "_meta": {
            "fuente": "mastodon-social-api-v1",
            "url_origen": API_URL,
            "etiqueta": "aguacate",
            "capturado_utc": datetime.now(timezone.utc).isoformat(),
            "tipo_datos": "datos reales públicos agregados",
            "licencia": "Datos públicos de red descentralizada ActivityPub / Mastodon",
            "privacidad": "Cero datos personales almacenados (cumple RGPD y LFPDPPP). Solo engagement numérico.",
        },
        "registros": registros,
    }

    archivo.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Guardado en bronce: {archivo} ({len(registros)} registros reales)")
    return archivo


def main():
    registros = extraer_metricas_reales()
    if registros:
        guardar_bronce(registros)
    else:
        print("[WARN] No se obtuvieron registros.")


if __name__ == "__main__":
    main()
