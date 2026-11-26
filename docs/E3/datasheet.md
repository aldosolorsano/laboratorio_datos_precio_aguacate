# Ficha Técnica Estandarizada del Dataset (Datasheet for Datasets)

**Dataset**: Precios Mayoristas del Aguacate Hass en México y Variables de Contexto (2024–2026)  
**Versión**: 3.0 (Curado - E3)  
**Fecha de Publicación**: Noviembre 2026  
**Licencia**: [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)  
**Archivos publicados**:
- `data/curado/precios_aguacate_mexico.csv` (CSV delimitado por comas, UTF-8)
- `data/curado/precios_aguacate_mexico.parquet` (Apache Parquet columnar, compresión Snappy)

---

## 📌 Guía Rápida para el Público en General (¿Cómo entender este dataset sin tecnicismos?)

Si no eres especialista en ciencia de datos ni en economía agrícola, esta sección te explica de qué trata la información en palabras sencillas:

1. **¿Qué es este precio?**
   - **Es precio de mayoreo, NO de supermercado**: Los precios que ves aquí son los que pagan los comerciantes y bodegueros en las **Centrales de Abasto** (como Iztapalapa en CDMX o Guadalajara) al comprar cajas de 9 a 20 kg de aguacate. No refleja directamente el precio al que compras un aguacate en la tienda de la esquina o en el supermercado, el cual suele ser entre 30% y 60% más caro debido al margen minorista.
2. **¿Por qué hay tres precios (mínimo, frecuente y máximo)?**
   - En una central de abasto el precio cambia durante la madrugada según la calidad y el tamaño del fruto. El **precio frecuente** es el valor al que se cerró la gran mayoría de las ventas de ese día.
3. **¿Por qué importan el Dólar y el Clima?**
   - El aguacate es el principal fruto de exportación de México hacia EE.UU. Si el dólar sube, a los productores les conviene más exportar, reduciendo la oferta nacional y encareciendo el fruto en México. Si llueve o hay heladas en Michoacán o Jalisco (donde se produce el 80% del país), la cosecha se frena y el precio sube.
4. **¿Qué hacen aquí las redes sociales?**
   - Muestra cuántas personas están hablando o reaccionando en redes sobre el precio del aguacate en días específicos. **No contiene nombres, fotos ni perfiles personales**, solo números de interacciones para saber qué tan sensible está el público ante las subidas de precio.

---

## 1. Motivación (Motivation)

- **¿Con qué propósito se creó el dataset?**  
  Proveer un repositorio curado, reproducible y libre de costo que unifique la serie histórica de precios mayoristas del aguacate Hass en México con variables exógenas fundamentales (tipo de cambio FIX, temperatura y precipitación en zonas de cultivo, y sentimiento agregado en redes sociales).
- **¿Quién creó y financió el dataset?**  
  Desarrollado por el equipo de investigación del *Trusted Data Lab: Observatorio del Aguacate*, en el marco de la Unidad 4 de Ingeniería de Datos.
- **¿Quién financió la recolección?**  
  Proyecto académico independiente sin financiamiento comercial.

---

## 2. Composición (Composition)

- **¿Qué representan las instancias?**  
  Cada fila representa una cotización comercial diaria de aguacate Hass clasificada por entidad de origen (productor), mercado de destino (central de abasto) y presentación comercial (kilos o tipo de caja).
- **¿Cuántas instancias contiene el dataset?**  
  **15,338 cotizaciones válidas** que cubren **391 fechas observadas** en **44 mercados mayoristas** de toda la República Mexicana.
- **¿Qué atributos tiene cada registro?**
  
| Columna | Tipo de Dato | Unidad | Descripción Accesible |
|---|---|---|---|
| `fecha` | Date (ISO 8601) | AAAA-MM-DD | Día en que se registró la cotización en la central de abasto. |
| `presentacion` | Category | Texto | Empaque original (ej. "Caja de 9 kg.", "Caja de 10 kg.", "Kilogramo"). |
| `origen` | Category | Estado | Entidad federativa donde se cosechó el aguacate (ej. Michoacán, Jalisco, Puebla). |
| `mercado` | Category | Mercado | Central de abasto o mercado receptor (ej. "DF: Central de Abasto de Iztapalapa"). |
| `minimo_mxn_kg` | Float32 | MXN/kg | Precio más bajo observado en el día normalizado por kilogramo. |
| `maximo_mxn_kg` | Float32 | MXN/kg | Precio más alto observado en el día normalizado por kilogramo. |
| `frecuente_mxn_kg` | Float32 | MXN/kg | Precio al que se realizó el mayor volumen de transacciones (moda comercial). |
| `fix_mxn_usd` | Float32 | MXN por USD | Tipo de cambio oficial FIX del Banco de México para esa fecha. |
| `temperatura_c` | Float32 | °C | Temperatura media diaria en las zonas productoras del origen reportado. |
| `precipitacion_mm` | Float32 | mm | Lluvia acumulada diaria en las zonas productoras asociadas. |
| `menciones_redes` | Int32 | Conteo | Cantidad de publicaciones públicas sobre aguacate registradas ese día en redes sociales. |
| `interacciones_totales`| Int32 | Conteo | Suma de favoritos, compartidos y respuestas públicas. |
| `archivo_sniim` | String | Ruta | Archivo HTML crudo en la Capa Bronce de donde se extrajo la cotización. |
| `ingesta_bronce_fecha` | Date | AAAA-MM-DD | Fecha en que el extractor capturó el lote crudo. |
| `_procesado_utc` | Timestamp | ISO UTC | Marca temporal exacta de compilación del dataset curado. |

- **¿Hay datos confidenciales o personales?**  
  **No.** El dataset contiene cero información confidencial o de identificación personal (PII). Todos los registros proceden de fuentes públicas oficiales y de APIs abiertas de redes con agregación estadística.

---

## 3. Proceso de Recolección (Collection Process)

- **¿Cómo se obtuvieron los datos?**  
  Mediante cuatro extractores automatizados en la Capa Bronce:
  1. **Precios**: Consultas automatizadas con Playwright al Sistema Nacional de Información e Integración de Mercados (SNIIM) de la Secretaría de Economía.
  2. **Tipo de cambio**: Consumo autenticado vía token institucional a la API SIE de Banco de México (serie FIX `SF43718`).
  3. **Clima**: Consumo directo a la API de Archivo Histórico de Open-Meteo para las coordenadas de Uruapan, Tancítaro y Ciudad Guzmán.
  4. **Redes Sociales**: Consumo directo vía API oficial abierta (Mastodon ActivityPub / Reddit) de publicaciones públicas bajo la etiqueta `#aguacate`.
- **Mecanismos éticos de recolección**:
  - Respeto irrestricto al archivo `robots.txt` del portal SNIIM y de redes.
  - User-Agent transparente identificando el proyecto académico y contacto.
  - Pausas de cortesía (3 segundos) entre peticiones para evitar saturación de servidores gubernamentales.

---

## 4. Preprocesamiento y Limpieza (Preprocessing / Cleaning)

1. **Conversión y normalización de unidad comercial**:
   Todas las presentaciones (cajas de 9, 10, 15, 18, 20 kg) se dividieron vectorialmente entre su peso neto para expresar de forma universal el precio en **pesos mexicanos por kilogramo (MXN/kg)**.
2. **Validación de reglas de consistencia de negocio**:
   Se validó formalmente que para cada fila se cumpla la desigualdad matemática estricta:
   $$\text{minimo\_mxn\_kg} \le \text{frecuente\_mxn\_kg} \le \text{maximo\_mxn\_kg}$$
3. **Manejo de anomalías y Cuarentena**:
   Registros con formatos rotos o duplicados con precios contradictorios se aislaron automáticamente en `data/cuarentena/precios_sniim.csv`. De 15,342 filas brutas analizadas, solo 4 fueron enviadas a cuarentena (tasa de error de 0.02%).
4. **Deduplicación**:
   Se eliminaron 1,180 cotizaciones idénticas producto de recapturas históricas en ventanas de consulta sobrepuestas.

---

## 5. Casos de Uso Recomendados y No Recomendados (Uses)

### Casos de uso recomendados:
- Modelado estadístico y econométrico de series de tiempo (ARIMA, SARIMAX, Holt-Winters).
- Análisis de elasticidad y transmisión de volatilidad cambiaria hacia precios agrícolas.
- Estudios académicos sobre el impacto de eventos climáticos extremos en el costo de los alimentos.
- Investigación de mercados y proyecciones de precios mayoristas para bodegas y empacadoras.

### Casos de uso NO recomendados:
- **Especulación financiera de alta frecuencia**: Los datos son de frecuencia diaria y reflejan mercados físicos de contado, no futuros bursátiles.
- **Predicción de precios al consumidor final de autoservicio**: Este dataset mide el escalón mayorista en centrales de abasto; no contempla costos de última milla, empaque comercial ni márgenes de cadenas de retail.
- **Inferencia causal univariada**: El precio del aguacate depende también de costos de fertilizantes y fletes logísticos no incluidos directamente en este dataset.

---

## 6. Distribución, Licencia y Citación (Distribution & Citation)

El dataset se distribuye bajo la licencia **Creative Commons Atribución 4.0 Internacional (CC BY 4.0)**. Puedes compartir, copiar, redistribuir y adaptar el material para cualquier propósito, incluso comercial, siempre y cuando des el crédito apropiado al proyecto.

**Forma de citar este dataset**:
```bibtex
@dataset{solorzano2026_observatorio_aguacate,
  author    = {Solórzano Sánchez, Aldo Israel and Colaboradores},
  title     = {Dataset Curado de Precios Mayoristas del Aguacate Hass en México y Variables de Contexto (2024-2026)},
  year      = {2026},
  publisher = {GitHub},
  version   = {3.0 (E3)},
  url       = {https://github.com/aldosolorsano/laboratorio_datos_precio_aguacate}
}
```
