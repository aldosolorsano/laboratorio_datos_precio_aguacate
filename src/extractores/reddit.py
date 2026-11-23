"""Extractor de métricas agregadas de Reddit vía API oficial (OAuth 2.0 Client Credentials).

Subreddits: r/mexico y r/MexicoFinanciero
Query:      "aguacate precio"
Salida:     data/bronce/reddit/reddit_aguacate_{fecha}.json

Solo se almacenan métricas de engagement anónimas:
  id, subreddit, score, upvote_ratio, num_comments, created_utc
NO se almacena: título, autor, cuerpo, URL del post.
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
SEARCH_URL = "https://oauth.reddit.com/search"
USER_AGENT = "TrustedDataLab-Aguacate/0.2 (proyecto academico; contact: datos@lab.mx)"
SUBREDDITS = ["mexico", "MexicoFinanciero"]
QUERY = "aguacate precio"
BRONCE_DIR = Path("data/bronce/reddit")
PAUSA_SEGUNDOS = 1          # respetar rate limit
LIMITE_POR_LLAMADA = 100    # máximo permitido por Reddit


# ---------------------------------------------------------------------------
# Autenticación OAuth 2.0 — Application-Only (Client Credentials)
# ---------------------------------------------------------------------------

def obtener_token(client_id: str, client_secret: str) -> str:
    """Solicita un access_token mediante Client Credentials flow.

    POST https://www.reddit.com/api/v1/access_token
    Con Basic Auth (client_id : client_secret) y grant_type=client_credentials.
    Devuelve el token de acceso (válido ~1 hora).
    """
    respuesta = requests.post(
        TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    respuesta.raise_for_status()
    datos = respuesta.json()
    if "access_token" not in datos:
        raise RuntimeError(f"Reddit no devolvió access_token: {datos}")
    return datos["access_token"]


# ---------------------------------------------------------------------------
# Búsqueda de posts
# ---------------------------------------------------------------------------

def buscar_posts(token: str, subreddit: str, query: str) -> list[dict]:
    """Busca posts en un subreddit y devuelve solo métricas anónimas.

    Parámetros:
        token:     Bearer token de OAuth 2.0.
        subreddit: Nombre del subreddit (sin r/).
        query:     Texto de búsqueda.

    Devuelve lista de dicts con métricas anónimas por post.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT,
    }
    params = {
        "q": query,
        "restrict_sr": "true",
        "sort": "new",
        "t": "week",          # últimos 7 días
        "limit": LIMITE_POR_LLAMADA,
        "type": "link",
    }
    url = f"https://oauth.reddit.com/r/{subreddit}/search"

    try:
        time.sleep(PAUSA_SEGUNDOS)
        respuesta = requests.get(url, headers=headers, params=params, timeout=30)
        respuesta.raise_for_status()
        datos = respuesta.json()
    except requests.RequestException as error:
        print(f"  [WARN] Error buscando en r/{subreddit}: {error}")
        return []

    posts = datos.get("data", {}).get("children", [])
    metricas = []
    for post in posts:
        p = post.get("data", {})
        # Solo guardamos métricas numéricas/anónimas; NO título, autor ni URL
        metricas.append({
            "id": p.get("id"),
            "subreddit": p.get("subreddit"),
            "score": p.get("score"),
            "upvote_ratio": p.get("upvote_ratio"),
            "num_comments": p.get("num_comments"),
            "created_utc": p.get("created_utc"),   # timestamp Unix público
        })

    print(f"  r/{subreddit}: {len(metricas)} posts encontrados")
    return metricas


# ---------------------------------------------------------------------------
# Persistencia en Bronce
# ---------------------------------------------------------------------------

def guardar_bronce(registros: list[dict], subreddits: list[str], query: str) -> Path:
    """Serializa los registros en data/bronce/reddit/reddit_aguacate_{fecha}.json."""
    BRONCE_DIR.mkdir(parents=True, exist_ok=True)
    fecha_hoy = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ruta = BRONCE_DIR / f"reddit_aguacate_{fecha_hoy}.json"

    payload = {
        "_meta": {
            "fuente": "reddit-api-v1",
            "oauth": "client_credentials",
            "capturado_utc": datetime.now(timezone.utc).isoformat(),
            "subreddits": subreddits,
            "query": query,
            "campos_capturados": ["id", "subreddit", "score", "upvote_ratio",
                                  "num_comments", "created_utc"],
            "campos_excluidos": ["title", "author", "selftext", "url", "permalink"],
            "privacidad": "solo metricas anonimas de engagement; cero datos personales",
        },
        "registros": registros,
    }
    ruta.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Guardado: {ruta} ({len(registros)} registros)")
    return ruta


# ---------------------------------------------------------------------------
# Punto de entrada principal
# ---------------------------------------------------------------------------

def ejecutar() -> Path:
    """Extrae métricas de Reddit y guarda en bronce. Devuelve la ruta del archivo."""
    client_id = os.environ.get("REDDIT_CLIENT_ID", "")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        raise EnvironmentError(
            "Faltan variables de entorno: REDDIT_CLIENT_ID y/o REDDIT_CLIENT_SECRET. "
            "Regístralas en https://www.reddit.com/prefs/apps (tipo: script)."
        )

    print("=== Extractor Reddit (OAuth 2.0 Client Credentials) ===")
    print(f"Query: '{QUERY}' | Subreddits: {SUBREDDITS}")

    # 1. Obtener token
    print("Obteniendo access_token...")
    try:
        token = obtener_token(client_id, client_secret)
        print("Token obtenido correctamente.")
    except Exception as error:
        raise RuntimeError(f"Error al obtener token OAuth: {error}") from error

    # 2. Buscar en cada subreddit
    todos_los_registros: list[dict] = []
    for sub in SUBREDDITS:
        registros = buscar_posts(token, sub, QUERY)
        todos_los_registros.extend(registros)
        time.sleep(PAUSA_SEGUNDOS)  # pausa adicional entre subreddits

    # 3. Deduplicar por id (un mismo post podría aparecer en búsquedas cruzadas)
    vistos: set[str] = set()
    unicos: list[dict] = []
    for r in todos_los_registros:
        rid = r.get("id")
        if rid and rid not in vistos:
            vistos.add(rid)
            unicos.append(r)

    print(f"Total posts únicos: {len(unicos)} (de {len(todos_los_registros)} brutos)")

    # 4. Guardar en bronce
    return guardar_bronce(unicos, SUBREDDITS, QUERY)


if __name__ == "__main__":
    ejecutar()
