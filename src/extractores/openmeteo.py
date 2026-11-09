"""Extractor Bronce: clima diario histórico (Open-Meteo Archive API).
Guarda la respuesta cruda + metadatos de captura. Sin token."""
import datetime as dt
import json
import pathlib
import time

import requests

URL = "https://archive-api.open-meteo.com/v1/archive"
UA = "TrustedDataLab-Aguacate/0.1 (proyecto academico)"
LUGARES = {
    "uruapan_mich": (19.4167, -102.0667),
    "tancitaro_mich": (19.3403, -102.3664),
    "ciudad_guzman_jal": (19.7047, -103.4617),
}
INICIO = dt.date(2023, 1, 1)


def main():
    hoy = dt.date.today()
    fin = hoy - dt.timedelta(days=7)  # el archivo tiene unos días de retraso
    out = pathlib.Path("data/bronce/openmeteo")
    out.mkdir(parents=True, exist_ok=True)
    for nombre, (lat, lon) in LUGARES.items():
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": INICIO.isoformat(),
            "end_date": fin.isoformat(),
            "daily": "temperature_2m_mean,precipitation_sum",
            "timezone": "America/Mexico_City",
        }
        r = requests.get(URL, params=params, headers={"User-Agent": UA}, timeout=60)
        r.raise_for_status()
        payload = {
            "_meta": {
                "fuente": "open-meteo-archive",
                "url": r.url,
                "capturado_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "lugar": nombre,
                "licencia": "CC BY 4.0 (atribución a Open-Meteo.com)",
            },
            "respuesta": r.json(),
        }
        (out / f"{nombre}_{hoy}.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )
        print(f"OK {nombre}: {len(payload['respuesta']['daily']['time'])} periodos")
        time.sleep(2)


if __name__ == "__main__":
    main()
