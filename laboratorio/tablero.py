"""Genera un tablero HTML autónomo a partir del reporte de E1."""

import argparse
import json
from html import escape
from pathlib import Path


def tabla(cabeceras, filas):
    titulos = "".join(f"<th scope='col'>{escape(titulo)}</th>" for titulo in cabeceras)
    cuerpo = "".join(
        "<tr>" + "".join(f"<td>{escape(str(valor))}</td>" for valor in fila) + "</tr>"
        for fila in filas
    )
    return f"<table><thead><tr>{titulos}</tr></thead><tbody>{cuerpo}</tbody></table>"


def seccion(r):
    titulo = f"<h2>{escape(r['mercado'])}</h2>"
    if "metricas" not in r:
        return (f"<section>{titulo}<p>{r['semanas_contiguas']} semanas continuas. "
                f"Se requieren {r['semanas_minimas']} para la evaluación.</p></section>")
    comparacion = tabla(
        ["Modelo", "MAE", "RMSE", "MAPE"],
        [(nombre, f"{m['mae']:.2f}", f"{m['rmse']:.2f}", f"{m['mape_pct']:.1f}%")
         for nombre, m in r["metricas"].items()],
    )
    contexto = (f"<p>Prueba de ocho semanas hasta {r['prueba_fin']}. "
                f"Menor MAE: {escape(r['ganador_mae'])}. Referencia del último precio: "
                f"{r['mae_ultimo_precio']:.2f} MXN/kg. Ljung–Box p={r['ljung_box_p']:.3f}, "
                f"ARCH p={r['arch_p']:.3f}.</p>")
    if r["proyeccion"]:
        futuro = tabla(
            ["Semana (lunes)", "Estimación", "Límite inferior 95%", "Límite superior 95%"],
            [(p["semana"], f"{p['precio']:.2f}", f"{p['inferior_95']:.2f}",
              f"{p['superior_95']:.2f}") for p in r["proyeccion"]],
        )
        if r["adf_diferenciada_p"] >= 0.05:
            futuro = ("<p>Proyección exploratoria. La prueba ADF no confirmó "
                      "estacionariedad en la serie utilizada para el diagnóstico.</p>" + futuro)
    else:
        futuro = "<p>Sin proyección publicada para este mercado.</p>"
    return f"<section>{titulo}{contexto}{comparacion}<h3>Proyección en MXN/kg</h3>{futuro}</section>"


def generar(entrada, salida):
    resultados = json.loads(entrada.read_text(encoding="utf-8"))
    secciones = "".join(map(seccion, resultados))
    documento = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Precios del aguacate Hass | E1</title>
<style>
:root {{font-family:system-ui,sans-serif;color:#213831;background:#f6f8f3}}
body {{max-width:66rem;margin:2rem auto;padding:0 1rem;line-height:1.5}}
section {{margin:2rem 0;padding:1.25rem;background:white;border:1px solid #d7e2db;border-radius:.5rem}}
table {{border-collapse:collapse;width:100%}}
td,th {{text-align:left;padding:.45rem;border-bottom:1px solid #d7e2db}}
th {{background:#e7f1e8}}
</style>
</head>
<body><main>
<h1>Precios mayoristas del aguacate Hass</h1>
<p>Cotizaciones de SNIIM en MXN/kg. Un intervalo de predicción del 95% expresa la
incertidumbre para cada semana bajo los supuestos del modelo.</p>
{secciones}
</main></body></html>
"""
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(documento, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=Path("data/oro/pronostico/evaluacion.json"))
    parser.add_argument("--salida", type=Path, default=Path("data/oro/pronostico/tablero.html"))
    args = parser.parse_args()
    generar(args.entrada, args.salida)
