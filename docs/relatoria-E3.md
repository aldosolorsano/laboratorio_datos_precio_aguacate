# Relatoría E3 · Observatorio del Aguacate

## 1. Qué nos propusimos

Optimizar formalmente el pipeline de datos demostrando mejoras cuantitativas medibles en tiempo de ejecución, uso de memoria RAM y almacenamiento, además de publicar el dataset curado con su ficha técnica estandarizada (Datasheet for Datasets) bajo licencia abierta, garantizando que todos los datos sean 100% reales y comprensibles para el público en general.

## 2. Qué hicimos

**Semana del 23 al 26 de noviembre de 2026**

1. **Implementación de Redes Sociales con Datos 100% Reales**: Se sustituyó cualquier muestra simulada implementando [`src/extractores/redes_sociales.py`](../src/extractores/redes_sociales.py), el cual consulta en vivo la API oficial de Mastodon (`mastodon.social/api/v1/timelines/tag/aguacate`), extrayendo publicaciones públicas reales con IDs, fechas e interacciones verídicas.
2. **Desarrollo del Pipeline E3 Optimizado**: Se programó [`pipeline/e3.py`](../pipeline/e3.py), implementando vectorización de precios, downcasting de tipos numéricos a `float32` y dimensiones a `category`, reduciendo drásticamente el consumo de memoria.
3. **Persistencia Columnar con Apache Parquet**: Se incorporó PyArrow para serializar el dataset curado en `data/curado/precios_aguacate_mexico.parquet` con compresión Snappy, además de su versión abierta en CSV.
4. **Construcción del Benchmark Cuantitativo**: Se creó [`tools/benchmark_optimizacion.py`](../tools/benchmark_optimizacion.py), registrando formalmente las métricas de antes vs. después en [`data/oro/optimizacion/metricas_optimizacion.json`](../data/oro/optimizacion/metricas_optimizacion.json).
5. **Redacción de la Ficha Técnica**: Se elaboró [`docs/E3/datasheet.md`](E3/datasheet.md) siguiendo el estándar de Timnit Gebru et al. (2021), añadiendo una guía introductoria para el público no especializado.
6. **Pruebas y Verificación**: Se construyó [`tests/test_e3.py`](../tests/test_e3.py) y se ejecutó la suite completa de pruebas.

## 3. Qué decidimos y por qué

- **Mastodon como fuente social en vivo**: La API oficial de Mastodon ofrece acceso público sin costo ni barreras de llaves privadas vencidas, permitiendo extraer datos 100% reales de forma automatizada y verificable por terceros.
- **Downcasting selectivo (`float32` y `category`)**: En un dataset de más de 15,000 registros, columnas de texto como `mercado` y `origen` se repiten miles de veces. Convertirlas a `category` ahorró un **59.4% de memoria RAM** sin perder un solo dato.
- **Publicación dual (CSV + Parquet)**: Parquet ahorra **97.1% de espacio en disco** (0.07 MB frente a 2.47 MB) y acelera lecturas analíticas, mientras que CSV garantiza accesibilidad universal para usuarios de Excel o herramientas de oficina.
- **Enfoque divulgativo para el público general**: Se redactó una sección en el Datasheet que explica las diferencias esenciales entre precio de central de abasto y precio de supermercado, evitando confusiones sobre por qué los precios reportados difieren de las tiendas minoristas.

## 4. Qué salió mal

- Durante las pruebas iniciales de API, los endpoints públicos no autenticados de Reddit devolvieron error HTTP 403 debido a las restricciones de scraping implementadas por Reddit en 2023. Se solucionó adoptando la API abierta y descentralizada de Mastodon, la cual entregó respuesta exitosa inmediata (HTTP 200) con publicaciones reales.
- El cálculo de hashes SHA-256 sobre cientos de archivos HTML de la capa Bronce consumía tiempo sustancial de disco si se ejecutaba repetidamente en cada benchmark. Se separó la medición de la fase de transformación analítica para reflejar con precisión el beneficio de la vectorización en memoria.

## 5. Qué aprendimos

- **Ingeniería de Datos**: La optimización no es teórica; debe medirse con temporizadores de alta resolución (`time.perf_counter()`) y monitoreo de memoria (`tracemalloc`).
- **Formatos de Almacenamiento**: La transición de formatos de texto plano (CSV) a formatos binarios columnares (Parquet) reduce exponencialmente costos de almacenamiento y transferencia en la nube.
- **Divulgación Responsable**: Un dataset técnico debe ser interpretable tanto por un científico de datos como por un tomador de decisiones o consumidor común. Explicar el contexto del dato (mayoreo vs. menudeo) es tan vital como limpiar los nulos.

## 6. Evidencias

- Pipeline Optimizado: [`pipeline/e3.py`](../pipeline/e3.py)
- Benchmark Formal: [`tools/benchmark_optimizacion.py`](../tools/benchmark_optimizacion.py)
- Dataset Curado CSV: [`data/curado/precios_aguacate_mexico.csv`](../data/curado/precios_aguacate_mexico.csv)
- Dataset Curado Parquet: [`data/curado/precios_aguacate_mexico.parquet`](../data/curado/precios_aguacate_mexico.parquet)
- Datasheet for Datasets: [`docs/E3/datasheet.md`](E3/datasheet.md)
- Ficha de Entrega E3: [`docs/E3/ENTREGA.md`](E3/ENTREGA.md)

## Uso de IA generativa

Antigravity (Gemini) asistió en el diseño de los scripts de vectorización, la estructuración del benchmark cuantitativo y la redacción de la ficha técnica bajo el estándar Datasheet for Datasets. Cada integrante revisó y validó los resultados cuantitativos y la veracidad de los datos en el repositorio.
