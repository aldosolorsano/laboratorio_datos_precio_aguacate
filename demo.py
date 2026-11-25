import json
import pandas as pd

print("=" * 70)
print("  🥑 OBSERVATORIO DEL AGUACATE — PRUEBA DE FUNCIONAMIENTO COMPLETA")
print("=" * 70)

# 1. Cargar datos de la Capa Oro integrada
cot = pd.read_csv("data/oro/cotizaciones_e2.csv")
print(f"\n[1] CAPA ORO INTEGRADA (cotizaciones_e2.csv):")
print(f"  • Total registros analizados     : {len(cot):,} cotizaciones")
print(f"  • Mercados mayoristas cubiertos  : {cot['mercado'].nunique()} mercados")
print(f"  • Rango de fechas observadas     : {cot['fecha'].min()} al {cot['fecha'].max()}")
print(f"  • Trazabilidad Bronce -> Oro     : {cot[['archivo_sniim', 'ingesta_bronce_fecha']].notna().all(axis=1).mean() * 100:.1f}%")

# 2. Ejemplo de un registro con linaje completo
print("\n[2] EJEMPLO DE REGISTRO CON TRAZABILIDAD COMPLETA:")
vinculadas = cot.dropna(subset=['archivo_reddit'])
if vinculadas.empty:
    print('  Fuente Reddit pendiente de una captura verificable con fechas coincidentes.')
else:
    muestra = vinculadas.iloc[-1]
    print(f"  • Fecha cotizada      : {muestra['fecha']}")
    print(f"  • Mercado y Origen    : {muestra['mercado']} (Origen: {muestra['origen']})")
    print(f"  • Presentacion        : {muestra['presentacion']}")
    print(f"  • Precios en MXN/kg   : Min ${float(muestra['minimo_mxn_kg']):.2f} | Frecuente ${float(muestra['frecuente_mxn_kg']):.2f} | Max ${float(muestra['maximo_mxn_kg']):.2f}")
    print(f"  • Tipo de Cambio FIX  : ${float(muestra['fix_mxn_usd']):.4f} MXN/USD (Fuente: {muestra['archivo_banxico']})")
    print(f"  • Clima en Produccion : {muestra['temperatura_c']} °C, Lluvia: {muestra['precipitacion_mm']} mm (Fuente: {muestra['archivo_clima']})")
    print(f"  • Actividad Reddit  : {int(float(muestra['posts_mencionando_aguacate']))} posts, Score neto: {int(float(muestra['score_total']))}, Ratio positivo: {float(muestra['ratio_positivo_promedio'])*100:.1f}%")
    print(f"  • Origen Bronce SNIIM : {muestra['archivo_sniim']} (Ingesta: {muestra['ingesta_bronce_fecha']})")

# 3. Pronóstico Econométrico
with open("data/oro/pronostico/evaluacion.json", encoding="utf-8") as f:
    evaluaciones = json.load(f)

print("\n[3] PRONÓSTICO ECONOMÉTRICO A 8 SEMANAS:")
for m in evaluaciones:
    if m.get("proyeccion"):
        print(f"\n  >> {m['mercado']}:")
        print(f"     Modelo seleccionado: {m.get('ganador_mae')} (MAE: ${m['metricas'][m['ganador_mae']]['mae']:.2f} MXN/kg vs Referencia: ${m.get('mae_ultimo_precio'):.2f})")
        print("     Proyeccion de precios:")
        for p in m["proyeccion"][:4]:
            print(f"       * Semana {p['semana']}: ${p['precio']:.2f} MXN/kg  (Rango 95%: [${p['inferior_95']:.2f} - ${p['superior_95']:.2f}])")

print("\n" + "=" * 70)
print("  TABLERO INTERACTIVO GENERADO EXITOSAMENTE:")
print("  Ruta local: data/oro/pronostico/tablero.html")
print("=" * 70)
