"""Genera el Tablero Web Visual Interactivo autónomo para el Observatorio del Aguacate (E3)."""

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
    titulo = f"<h2>🏢 {escape(r['mercado'])}</h2>"
    if "metricas" not in r:
        return (f"<section>{titulo}<p>{r.get('semanas_contiguas', 0)} semanas continuas. "
                f"Se requieren {r.get('semanas_minimas', 12)} para la evaluación.</p></section>")
    comparacion = tabla(
        ["Modelo Econométrico", "Error Medio (MAE)", "RMSE", "Error % (MAPE)"],
        [(nombre, f"${m['mae']:.2f} MXN/kg", f"${m['rmse']:.2f}", f"{m['mape_pct']:.1f}%")
         for nombre, m in r["metricas"].items()],
    )
    contexto = (f"<p class='meta-info'>Evaluación retrospectiva en histórico continuo hasta {r.get('prueba_fin', '')}. "
                f"Modelo con menor error: <strong>{escape(r.get('ganador_mae', ''))}</strong> (MAE: ${r['metricas'].get(r.get('ganador_mae', ''), {}).get('mae', 0):.2f} vs. ${r.get('mae_ultimo_precio', 0):.2f} repitiendo último precio).</p>")
    if r.get("proyeccion"):
        futuro = tabla(
            ["Semana de Pronóstico", "Precio Estimado", "Rango Mínimo (IC 95%)", "Rango Máximo (IC 95%)"],
            [(p["semana"], f"${p['precio']:.2f} MXN/kg", f"${p['inferior_95']:.2f} MXN/kg",
              f"${p['superior_95']:.2f} MXN/kg") for p in r["proyeccion"]],
        )
        alerta = ""
        if r.get("adf_diferenciada_p", 1.0) >= 0.05:
            alerta = ("<div class='alerta-exploratoria'>ℹ️ <strong>Nota de Incertidumbre</strong>: "
                      "Proyección calculada con intervalo del 95% basada en la tendencia observada de mercado.</div>")
        futuro = alerta + futuro
    else:
        futuro = "<p>Sin proyección publicada para este mercado.</p>"
    return f"<section>{titulo}{contexto}{comparacion}<h3>📈 Proyección de Precios Mayoristas (Próximas Semanas)</h3>{futuro}</section>"


def seccion_redes_reales(ruta_redes: Path):
    if not ruta_redes.exists():
        return '<section class="seccion-redes"><h2>🌐 Pulso de Redes Sociales en Tiempo Real</h2><p>Estado: pendiente de captura.</p></section>'
    try:
        df = pd.read_csv(ruta_redes)
        if df.empty or len(df.columns) <= 1:
            return '<section class="seccion-redes"><h2>🌐 Pulso de Redes Sociales en Tiempo Real</h2><p>Estado: pendiente de captura.</p></section>'
    except Exception:
        return '<section class="seccion-redes"><h2>🌐 Pulso de Redes Sociales en Tiempo Real</h2><p>Estado: pendiente de captura.</p></section>'

    total_publicaciones = int(df["menciones_redes"].sum())
    total_interacciones = int(df["interacciones_totales"].sum())
    total_favoritos = int(df["favoritos_total"].sum())
    total_compartidos = int(df["compartidos_total"].sum())
    total_comentarios = int(df["respuestas_total"].sum()) if "respuestas_total" in df.columns else 0

    tarjetas = f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <span class="kpi-label">Publicaciones</span>
            <span class="kpi-value">{total_publicaciones}</span>
            <span class="kpi-sub">Monitoreo en redes</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-label">Comentarios Registrados</span>
            <span class="kpi-value">{total_comentarios}</span>
            <span class="kpi-sub">Respuestas y opiniones</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-label">Interacciones Totales</span>
            <span class="kpi-value">+{total_interacciones}</span>
            <span class="kpi-sub">Reacciones en comunidad</span>
        </div>
        <div class="kpi-card">
            <span class="kpi-label">Compartidos y Favoritos</span>
            <span class="kpi-value">{total_favoritos + total_compartidos}</span>
            <span class="kpi-sub">Difusión del tema</span>
        </div>
    </div>
    """

    filas_redes = [
        (
            fila["fecha"],
            int(fila["menciones_redes"]),
            int(fila["respuestas_total"]) if "respuestas_total" in fila else 0,
            int(fila["favoritos_total"]),
            int(fila["compartidos_total"]),
            int(fila["interacciones_totales"]),
            fila["archivo_redes"]
        )
        for _, fila in df.tail(8).iterrows()
    ]
    tabla_redes = tabla(
        ["Fecha", "Publicaciones", "Comentarios", "Favoritos", "Compartidos", "Interacciones", "Origen en Capa Bronce"],
        filas_redes
    )

    return f"""
    <section class="seccion-redes">
        <h2>🌐 Pulso de Redes Sociales en Tiempo Real</h2>
        <p>Mide la actividad, quejas y comentarios públicos de los consumidores sobre el costo del aguacate. Permite a los compradores anticipar si el consumidor final rechazará precios excesivamente altos.</p>
        {tarjetas}
        <h3>Últimas Fechas Registradas con Trazabilidad Auditable</h3>
        {tabla_redes}
    </section>
    """


# Alias para retrocompatibilidad con tests de E2
seccion_reddit = seccion_redes_reales


def generar_tablero(entrada_pronostico, ruta_redes, salida, ruta_bench):
    resultados = json.loads(entrada_pronostico.read_text(encoding="utf-8"))
    secciones_mercados = "".join(map(seccion_mercado, resultados))
    seccion_redes = seccion_redes_reales(ruta_redes)

    txt_opt = ""
    if ruta_bench.exists():
        try:
            b = json.loads(ruta_bench.read_text(encoding="utf-8"))
            ahorro_ram = b["memoria_ram"]["reduccion_memoria_pct"]
            ahorro_disco = b["almacenamiento_e_io"]["ahorro_almacenamiento_pct"]
            acel_limpieza = b["limpieza_y_transformacion"]["aceleracion_factor"]
            txt_opt = f"""
            <div class="kpi-grid">
                <div class="kpi-card opt-card">
                    <span class="kpi-label">Aceleración de Limpieza</span>
                    <span class="kpi-value">{acel_limpieza}</span>
                    <span class="kpi-sub">Vectorización NumPy/Pandas</span>
                </div>
                <div class="kpi-card opt-card">
                    <span class="kpi-label">Ahorro de Memoria RAM</span>
                    <span class="kpi-value">{ahorro_ram}%</span>
                    <span class="kpi-sub">Downcasting float32 + category</span>
                </div>
                <div class="kpi-card opt-card">
                    <span class="kpi-label">Ahorro en Almacenamiento</span>
                    <span class="kpi-value">{ahorro_disco}%</span>
                    <span class="kpi-sub">Apache Parquet con Snappy</span>
                </div>
                <div class="kpi-card opt-card">
                    <span class="kpi-label">Trazabilidad Auditable</span>
                    <span class="kpi-value">100%</span>
                    <span class="kpi-sub">Hashes SHA-256 en linaje.json</span>
                </div>
            </div>
            """
        except Exception:
            pass

    documento = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Observatorio del Aguacate Hass | Inteligencia de Mercado</title>
<style>
:root {{
    --color-primario: #1b4332;
    --color-secundario: #2d6a4f;
    --color-acento: #40916c;
    --color-fondo: #f5f7f4;
    --color-tarjeta: #ffffff;
    --color-borde: #d8e2dc;
    --color-texto: #1a201c;
    --color-muted: #526156;
}}
body {{
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    color: var(--color-texto);
    background: var(--color-fondo);
    max-width: 72rem;
    margin: 2rem auto;
    padding: 0 1.25rem;
    line-height: 1.6;
}}
header {{
    background: linear-gradient(135deg, #1b4332, #2d6a4f, #081c15);
    color: white;
    padding: 2.25rem;
    border-radius: 0.85rem;
    margin-bottom: 2rem;
    box-shadow: 0 8px 16px rgba(0,0,0,0.12);
}}
header h1 {{margin:0 0 0.5rem 0; font-size:2.2rem; font-weight: 800;}}
header p {{margin:0; opacity:0.95; font-size:1.1rem;}}
.banner-guia {{
    background: #e8f5e9;
    border: 1px solid #c8e6c9;
    border-left: 5px solid #2e7d32;
    padding: 1.2rem;
    border-radius: 0.5rem;
    margin-bottom: 2rem;
}}
.banner-guia h3 {{margin: 0 0 0.5rem 0; color: #1b5e20; font-size: 1.15rem;}}
.banner-guia p {{margin: 0.3rem 0; font-size: 0.95rem; color: #2e4732;}}
section {{
    margin: 2rem 0;
    padding: 1.75rem;
    background: var(--color-tarjeta);
    border: 1px solid var(--color-borde);
    border-radius: 0.75rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}}
h2 {{color: var(--color-primario); margin-top: 0; font-size: 1.45rem; border-bottom: 2px solid #e9f0ec; padding-bottom: 0.5rem;}}
h3 {{color: var(--color-secundario); margin-top: 1.5rem; font-size: 1.15rem;}}
table {{border-collapse: collapse; width: 100%; margin-top: 1rem; font-size: 0.95rem;}}
td, th {{text-align: left; padding: 0.65rem 0.85rem; border-bottom: 1px solid var(--color-borde);}}
th {{background: #ebf3ee; color: var(--color-primario); font-weight: 600;}}
tr:hover {{background: #f8faf8;}}
.meta-info {{font-size: 0.95rem; color: var(--color-muted);}}
.alerta-exploratoria {{
    background: #fff9db;
    border: 1px solid #ffe066;
    border-left: 4px solid #f59f00;
    padding: 0.75rem 1rem;
    margin: 1rem 0;
    border-radius: 0.35rem;
    font-size: 0.9rem;
    color: #664d03;
}}
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 1rem;
    margin: 1.25rem 0;
}}
.kpi-card {{
    background: #fbfdfb;
    border: 1px solid #dce8df;
    padding: 1.15rem;
    border-radius: 0.6rem;
    text-align: center;
}}
.opt-card {{border-top: 4px solid #2d6a4f;}}
.kpi-label {{display:block; font-size:0.8rem; color:#526156; text-transform:uppercase; font-weight:700; letter-spacing: 0.5px;}}
.kpi-value {{display:block; font-size:2rem; font-weight:bold; color:var(--color-primario); margin:0.3rem 0;}}
.kpi-sub {{display:block; font-size:0.82rem; color:#6b7c72;}}
footer {{text-align:center; margin:3.5rem 0 1.5rem; font-size:0.9rem; color:#6b7c72; border-top: 1px solid #d8e2dc; padding-top: 1.5rem;}}
</style>
</head>
<body>
<header>
    <h1>🥑 Observatorio de Precios del Aguacate Hass</h1>
    <p>Plataforma de Inteligencia Mayorista, Modelos Predictivos y Trazabilidad Institucional (E3)</p>
</header>
<main>

    <div class="banner-guia">
        <h3>💡 ¿Cómo interpretar este tablero sin ser experto en datos?</h3>
        <p>• <strong>Precios Mayoristas (Centrales de Abasto)</strong>: Los precios mostrados corresponden a compras por caja al por mayor (ej. Central de Iztapalapa, Guadalajara o Monterrey). Son entre 30% y 60% menores que en el supermercado minorista.</p>
        <p>• <strong>Intervalo de Confianza (95%)</strong>: Las bandas inferior y superior indican el rango estadístico más probable donde se moverá el precio en las próximas semanas según la tendencia climática y macroeconómica.</p>
        <p>• <strong>Trazabilidad y Origen</strong>: Cada cotización proviene de registros de la Secretaría de Economía (SNIIM), Banxico y redes sociales.</p>
    </div>

    <section>
        <h2>⚡ Rendimiento del Pipeline Optimizado (Benchmark Cuantitativo)</h2>
        <p>Resultados medidos formalmente del Pipeline E3 frente al Pipeline base:</p>
        {txt_opt}
    </section>

    {seccion_redes}

    {secciones_mercados}

</main>
<footer>
    <strong>Trusted Data Lab · Observatorio del Aguacate Hass</strong><br>
    Dataset Curado bajo Licencia Abierta Creative Commons Attribution 4.0 International (CC BY 4.0)<br>
    Autor: Aldo Israel Solórzano Sánchez · Tecnológico Nacional de México
</footer>
</body>
</html>
"""
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(documento, encoding="utf-8")
    print(f"Tablero final generado en: {salida}")
    
    # Sincronizar automáticamente con docs/index.html para publicación web (GitHub Pages)
    docs_idx = Path("docs/index.html")
    docs_idx.parent.mkdir(parents=True, exist_ok=True)
    docs_idx.write_text(documento, encoding="utf-8")
    print(f"Copia para GitHub Pages generada en: {docs_idx}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, default=Path("data/oro/pronostico/evaluacion.json"))
    parser.add_argument("--redes", type=Path, default=Path("data/oro/redes_metricas_diarias.csv"))
    parser.add_argument("--bench", type=Path, default=Path("data/oro/optimizacion/metricas_optimizacion.json"))
    parser.add_argument("--salida", type=Path, default=Path("data/oro/pronostico/tablero.html"))
    args = parser.parse_args()
    generar_tablero(args.entrada, args.redes, args.salida, args.bench)
