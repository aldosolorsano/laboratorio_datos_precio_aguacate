"""Extractor Bronce: INPC genérico 'Aguacate' (precio al consumidor) con la API de Indicadores de INEGI.
Variables de entorno: INEGI_TOKEN y INEGI_INDICADOR (clave del indicador, ver README)."""
import datetime as dt
import json
import os
import pathlib

import requests

UA = "TrustedDataLab-Aguacate/0.1 (proyecto academico)"


def main():
    token = os.environ.get("INEGI_TOKEN", "").strip()
    ind = os.environ.get("INEGI_INDICADOR", "").strip()
    if not token or not ind:
        print("INEGI_TOKEN o INEGI_INDICADOR no definidos: se omite esta fuente.")
        return
    url = (
        "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/"
        f"INDICATOR/{ind}/es/00/false/BIE/2.0/{token}?type=json"
    )
    r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
    r.raise_for_status()
    payload = {
        "_meta": {
            "fuente": "inegi-api-indicadores",
            "indicador": ind,
            "capturado_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        },
        "respuesta": r.json(),
    }
    out = pathlib.Path("data/bronce/inegi")
    out.mkdir(parents=True, exist_ok=True)
    hoy = dt.date.today()
    (out / f"inpc_aguacate_{hoy}.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )
    try:
        n = len(payload["respuesta"]["Series"][0]["OBSERVATIONS"])
        print(f"OK inegi: {n} periodos")
    except (KeyError, IndexError):
        print("Guardado, pero revisa la estructura de la respuesta.")


if __name__ == "__main__":
    main()
