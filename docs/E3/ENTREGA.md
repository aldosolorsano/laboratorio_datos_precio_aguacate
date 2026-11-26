# E3 · Optimización Medida y Publicación del Dataset Curado

**Materia**: Ingeniería de Datos / Calidad en los Sistemas de Información  
**Ponderación**: 15% de la Unidad 4  
**Tag de Entrega**: `e3`  
**Repositorio**: [https://github.com/aldosolorsano/laboratorio_datos_precio_aguacate](https://github.com/aldosolorsano/laboratorio_datos_precio_aguacate)

---

## 📋 Resumen de Entregables Cumplidos

| Requisito E3 | Evidencia en el Repositorio | Estado |
|---|---|---|
| **1. Optimización Medida del Pipeline** | • [`pipeline/e3.py`](../../pipeline/e3.py) (Pipeline optimizado)<br>• [`tools/benchmark_optimizacion.py`](../../tools/benchmark_optimizacion.py) (Script de benchmark)<br>• [`data/oro/optimizacion/metricas_optimizacion.json`](../../data/oro/optimizacion/metricas_optimizacion.json) (Métricas cuantitativas) | ✅ Medido cuantitativamente |
| **2. Publicación de Dataset Curado** | • [`data/curado/precios_aguacate_mexico.csv`](../../data/curado/precios_aguacate_mexico.csv)<br>• [`data/curado/precios_aguacate_mexico.parquet`](../../data/curado/precios_aguacate_mexico.parquet) | ✅ Publicado dual (CSV + Parquet) |
| **3. Ficha Técnica Estandarizada** | • [`docs/E3/datasheet.md`](datasheet.md) (Formato Gebru et al., 2021 + Guía para público general) | ✅ Documentado y accesible |
| **4. Ficha de Entrega y Relatoría** | • [`docs/E3/ENTREGA.md`](ENTREGA.md)<br>• [`docs/relatoria-E3.md`](../relatoria-E3.md) | ✅ Completado |
| **5. Datos 100% Reales y Verificables** | • [`src/extractores/redes_sociales.py`](../../src/extractores/redes_sociales.py) (Mastodon API oficial en vivo)<br>• [`data/bronce/redes/`](../../data/bronce/redes/) (Capturas JSON con IDs reales) | ✅ 100% verídico (cero datos inventados) |

---

## 1. Comparativa Cuantitativa: Antes (E2) vs. Después (E3)

El benchmark formal fue ejecutado sobre el lote completo de **15,338 cotizaciones** y **391 fechas observadas**:

| Dimensión de Rendimiento | Pipeline Base (E2) | Pipeline Optimizado (E3) | Ganancia / Mejora Cuantitativa | Técnica de Optimización Aplicada |
|---|---|---|---|---|
| **Tiempo de Limpieza y Transformación** | 4.563 segundos | 2.689 segundos | **41.1% más rápido (1.70x)** | Vectorización NumPy/Pandas en lugar de bucles `Decimal` y parsing condicional fila por fila. |
| **Uso de Memoria RAM en DataFrame** | 6.94 MB | 2.82 MB | **59.4% de reducción en RAM** | Downcasting de variables numéricas a `float32` y dimensiones repetitivas a `category`. |
| **Tamaño de Almacenamiento en Disco** | 2.47 MB (CSV) | 0.07 MB (Parquet) | **97.1% de ahorro en disco** | Persistencia columnar en Apache Parquet con compresión Snappy. |
| **Velocidad de Escritura a Disco** | 0.078 segundos | 0.032 segundos | **2.4x más veloz** | Serialización binaria de alta velocidad con PyArrow. |
| **Velocidad de Lectura para Análisis** | 0.025 segundos | 0.026 segundos | **Paridad sub-segundo (<30 ms)** | Estructura columnar indexada optimizada para consultas selectivas. |
| **Throughput de Procesamiento** | 3,361 filas/s | 5,703 filas/s | **+69.7% más filas/segundo** | Eliminación de cuellos de botella en la fase de extracción de texto. |
| **Tasa de Errores e Integridad** | 0.026% (4 rechazos) | 0.026% (4 rechazos) | **100% trazable sin pérdida** | Validación matemática temprana y aislamiento estricto en cuarentena. |

---

## 2. Publicación del Dataset Curado

El dataset se encuentra publicado y versionado en la carpeta `data/curado/` bajo la licencia abierta **Creative Commons Atribución 4.0 Internacional (CC BY 4.0)**:

1. **`data/curado/precios_aguacate_mexico.csv`**:
   - Formato abierto universalmente legible en cualquier software (Excel, R, Python, PowerBI, Tableau).
   - Codificación UTF-8 estándar, sin caracteres corrompidos.
2. **`data/curado/precios_aguacate_mexico.parquet`**:
   - Formato columnar estándar en la industria de Big Data (Apache Parquet).
   - Ocupa apenas **110 KB** (frente a casi 5 MB del CSV crudo enriquecido), preservando tipos nativos estrictos sin ambigüedades.

---

## 3. Datos 100% Reales y Verificables (Fuentes Oficiales y Redes)

En atención a la instrucción de utilizar **únicamente datos reales**:
* **Precios**: 100% reales extraídos del portal gubernamental del SNIIM (Secretaría de Economía de México).
* **Tipo de cambio**: 100% real proveniente de la serie oficial FIX del Banco de México (Banxico).
* **Clima**: 100% real del reanálisis ERA5 / Open-Meteo para los municipios productores de Michoacán y Jalisco.
* **Redes Sociales**: Se integró el extractor [`src/extractores/redes_sociales.py`](../../src/extractores/redes_sociales.py) que consulta en tiempo real la API oficial y pública de **Mastodon** (`https://mastodon.social/api/v1/timelines/tag/aguacate`), capturando publicaciones reales con IDs, marcas de tiempo y métricas de interacción auténticas, garantizando cero datos ficticios y cero invasión a la privacidad individual.

---

## 4. Comprensión para el Público en General

Para que cualquier persona sin formación técnica ni en agronomía comprenda el proyecto:
- El [`datasheet.md`](datasheet.md) incluye una sección inicial de **"Guía Rápida para el Público en General"** explicando:
  - La diferencia entre **precio mayorista de central de abasto** y **precio minorista de supermercado**.
  - Por qué el **tipo de cambio** y las **lluvias/heladas** mueven el precio del aguacate.
  - Qué significan las **métricas de redes sociales** y cómo protegen la privacidad.
- Glosario de términos claros y concisos.

---

## 5. Instrucciones de Reproducción Local

```bash
# 1. Instalar dependencias optimizadas de E3
pip install -r requirements-e3.txt

# 2. Ejecutar extracción de datos reales de redes sociales
python src/extractores/redes_sociales.py

# 3. Ejecutar pipeline E3 optimizado
python -m pipeline.e3

# 4. Ejecutar benchmark cuantitativo formal
python tools/benchmark_optimizacion.py

# 5. Correr suite completa de pruebas unitarias
python -m unittest discover -s tests
```
