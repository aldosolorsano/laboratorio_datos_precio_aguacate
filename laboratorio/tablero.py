"""Genera un tablero HTML autónomo a partir del reporte de pronóstico e incorpora métricas de E2."""

import argparse
import json
from html import escape
from pathlib import Path
import pandas as pd


def tabla(cabeceras, filas):
    titulos = "".join(f"<th scope='col'>{escape(titulo)}</th>" for titulo in cabeceras)
    cuerpo = "".join(
        "<tr>" + "".join(f"<td>{escape(str(valor))}</td>" for valor in fila) + "</tr>"
        for fila in filas
    )
    return f"<table><thead><tr>{titulos}</tr></thead><tbody>{cuerpo}</tbody></table>"


def seccion_mercado(r):
    titulo = f"<h2>{escape(r['mercado'])}</h2>"
    if "metricas" not in r:
        return (f"<section>{titulo}<p>{r['semanas_contiguas']} semanas continuas. "
                f"Se requieren {r.get('semanas_minimas', 24)} para la evaluación.</p></section>")
    comparacion = tabla(
        ["Modelo", "MAE", "RMSE", "MAPE"],
        [(nombre, f"{m['mae']:.2f}", f"{m['rmse']:.2f}", f"{m['mape_pct']:.1f}%")
         for nombre, m in r["metricas"].items()],
    )
    contexto = (f"<p>Prueba de ocho semanas hasta {r['prueba_fin']}. "
                f"Menor MAE: <strong>{escape(r['ganador_mae'])}</strong>. Referencia del último precio: "
                f"{r['mae_ultimo_precio']:.2f} MXN/kg. Ljung–Box p={r['ljung_box_p']:.3f}, "
                f"ARCH p={r['arch_p']:.3f}.</p>")
    if r["proyeccion"]:
        futuro = tabla(
            ["Semana (lunes)", "Estimación (MXN/kg)", "Límite inferior 95%", "Límite superior 95%"],
            [(p["semana"], f"${p['precio']:.2f}", f"${p['inferior_95']:.2f}",
              f"${p['superior_95']:.2f}") for p in r["proyeccion"]],
        )
        if r.get("adf_diferenciada_p", 1.0) >= 0.05:
            futuro = ("<p class='alerta'>⚠️ Proyección exploratoria. La prueba ADF no confirmó "
                      "estacionariedad en la serie utilizada para el diagnóstico.</p>" + futuro)
    else:
        futuro = "<p>Sin proyección publicada para este mercado.</p>"
    return f"<section>{titulo}{contexto}{comparacion}<h3>Proyección en MXN/kg</h3>{futuro}</section>"


def seccion_reddit(ruta_reddit: Path):
    pendiente = (
        '<section class="seccion-reddit"><h2>Actividad de Reddit</h2>'
        '<p>Fuente pendiente de una captura verificable con observaciones.</p></section>'
    )
    if not ruta_reddit.exists():
        return pendiente
    df = pd.read_csv(ruta_reddit)
    if df.empty:
        return pendiente

    total_posts = int(df["posts_mencionando_aguacate"].sum())
    score_total = int(df["score_total"].sum())
    comentarios_total = int(df["comentarios_total"].sum())
    ratio_promedio = float(df["ratio_positivo_promedio"].mean() * 100)

    tarjetas = f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <span class="kpi-label">Posts Analizados</span>
            <span class="kpi-value">{total_posts}</span>
            <span class="kpi-sub">r/mexico y r/MexicoFinanciero</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-label">Score Neto Acumulado</span>
            <span class="kpi-value">{score_total:+d}</span>
            <span class="kpi-sub">Upvotes netos recibidos</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-label">Comentarios de Usuarios</span>
            <span class="kpi-value">{comentarios_total}</span>
            <span class="kpi-sub">Interacción en la comunidad</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-label">Aprobación Positiva</span>
            <span class="kpi-value">{ratio_promedio:.1f}%</span>
            <span class="kpi-sub">Upvote ratio promedio</span>
        </div>
    </div>
    """

    filas_reddit = [
        (
            fila["fecha"],
            int(fila["posts_mencionando_aguacate"]),
            int(fila["score_total"]),
            f"{float(fila['score_promedio']):.1f}",
            int(fila["comentarios_total"]),
            f"{float(fila['ratio_positivo_promedio'])*100:.1f}%",
            fila["archivo_reddit"]
        )
        for _, fila in df.iterrows()
    ]
    tabla_reddit = tabla(
        ["Fecha", "Posts", "Score Total", "Score Promedio", "Comentarios", "% Aprobación", "Origen Bronce (Trazabilidad)"],
        filas_reddit
    )

    return f"""
    <section class="seccion-reddit">
        <h2>📱 Métricas Agregadas de Redes Sociales (Reddit API · E2)</h2>
        <p>Conteos diarios de publicaciones, votos y comentarios en comunidades mexicanas
        para la búsqueda <em>"aguacate precio"</em>. La relación de esta actividad con los
        precios mayoristas requiere validación.</p>
        {tarjetas}
        <h3>Detalle Diario Agregado y Trazabilidad</h3>
        {tabla_reddit}
    </section>
    """


def generar(entrada_pronostico, ruta_reddit, salida):
    resultados = json.loads(entrada_pronostico.read_text(encoding="utf-8"))
    secciones_mercados = "".join(map(seccion_mercado, resultados))
    seccion_redes = seccion_reddit(ruta_reddit)

    documento = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Observatorio del Aguacate Hass | Inteligencia de Precios y Redes</title>
<style>
:root {{
    --color-primario: #1c3d2f;
    --color-acento: #2d6a4f;
    --color-fondo: #f4f6f0;
    --color-tarjeta: #ffffff;
    --color-borde: #d5ded9;
    --color-texto: #1f2923;
}}
body {{
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    color: var(--color-texto);
    background: var(--color-fondo);
    max-width: 68rem;
    margin: 2rem auto;
    padding: 0 1.25rem;
    line-height: 1.5;
}}
header {{
    background: linear-gradient(135deg, #1c3d2f, #2d6a4f);
    color: white;
    padding: 2rem;
    border-radius: 0.75rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
}}
header h1 {{margin:0 0 0.5rem 0; font-size:1.85rem}}
header p {{margin:0; opacity:0.9; font-size:1.05rem}}
section {{
    margin: 2rem 0;
    padding: 1.5rem;
    background: var(--color-tarjeta);
    border: 1px solid var(--color-borde);
    border-radius: 0.65rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}
h2 {{color: var(--color-primario); margin-top: 0; font-size: 1.4rem; border-bottom: 2px solid #e2ede6; padding-bottom: 0.4rem;}}
h3 {{color: var(--color-acento); margin-top: 1.5rem; font-size: 1.15rem;}}
table {{border-collapse: collapse; width: 100%; margin-top: 1rem; font-size: 0.95rem;}}
td, th {{text-align: left; padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--color-borde);}}
th {{background: #eaf3ec; color: var(--color-primario); font-weight: 600;}}
tr:hover {{background: #fbfdfb;}}
.alerta {{background: #fff8e6; border-left: 4px solid #e09f3e; padding: 0.6rem 0.8rem; margin: 1rem 0; border-radius: 0.25rem; font-size: 0.9rem;}}
.badge-privacidad {{
    display: inline-block;
    background: #e1f5fe;
    color: #0277bd;
    padding: 0.35rem 0.75rem;
    border-radius: 2rem;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
}}
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1.25rem 0;
}}
.kpi-card {{
    background: #f8faf8;
    border: 1px solid #dce8df;
    padding: 1rem;
    border-radius: 0.5rem;
    text-align: center;
}}
.kpi-label {{display:block; font-size:0.85rem; color:#5c6b63; text-transform:uppercase; font-weight:600}}
.kpi-value {{display:block; font-size:1.85rem; font-weight:bold; color:var(--color-acento); margin:0.25rem 0}}
.kpi-sub {{display:block; font-size:0.8rem; color:#7d8c83}}
footer {{text-align:center; margin:3rem 0 1rem; font-size:0.85rem; color:#6b7c72}}
</style>
</head>
<body>
<header>
    <h1>🥑 Observatorio del Aguacate Hass</h1>
    <p>Plataforma de Inteligencia Mayorista, Modelos Predictivos y Pulso de Redes Sociales</p>
</header>
<main>
{seccion_redes}
{secciones_mercados}
</main>
<footer>
    Observatorio del Aguacate · Trusted Data Lab · Entrega E2 (Trazabilidad y Ética)
</footer>
</body>
</html>
"""
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(documento, encoding="utf-8")
    print(f"Tablero generado: {salida}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=Path("data/oro/pronostico/evaluacion.json"))
    parser.add_argument("--reddit", type=Path, default=Path("data/oro/reddit_metricas_diarias.csv"))
    parser.add_argument("--salida", type=Path, default=Path("data/oro/pronostico/tablero.html"))
    args = parser.parse_args()
    generar(args.entrada, args.reddit, args.salida)
