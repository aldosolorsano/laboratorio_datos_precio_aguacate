"""Extractor Bronce: tipo de cambio FIX USD/MXN (Banxico SIE API, serie SF43718).
Requiere token gratuito en la variable de entorno BANXICO_TOKEN."""
import datetime as dt
import json
import os
import pathlib

import requests

SERIE = "SF43718"
UA = "TrustedDataLab-Aguacate/0.1 (proyecto academico)"


def main():
    token = os.environ.get("BANXICO_TOKEN")
    if not token:
        raise SystemExit("Falta BANXICO_TOKEN")
    hoy = dt.date.today()
    url = (
        "https://www.banxico.org.mx/SieAPIRest/service/v1/series/"
        f"{SERIE}/datos/2023-01-01/{hoy.isoformat()}"
    )
    r = requests.get(url, headers={"Bmx-Token": token, "User-Agent": UA}, timeout=60)
    r.raise_for_status()
    payload = {
        "_meta": {
            "fuente": "banxico-sie",
            "serie": SERIE,
            "capturado_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        },
        "respuesta": r.json(),
    }
    out = pathlib.Path("data/bronce/banxico")
    out.mkdir(parents=True, exist_ok=True)
    (out / f"usdmxn_{hoy}.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )
    datos = payload["respuesta"]["bmx"]["series"][0]["datos"]
    print(f"OK banxico: {len(datos)} periodos")


if __name__ == "__main__":
    main()
