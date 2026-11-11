# Ficha de Entrega Técnica — E0

- **Laboratorio:** Trusted Data Lab — Observatorio de Dinámica de Precios del Aguacate Hass (Jalisco y Michoacán)
- **Integrantes:** 
  - Aldo Israel Solórzano Sánchez
  - Luis Fernando Machuca Carrillo
  - Elias Melendez Guzman
- **Repositorio:** [https://github.com/aldosolorsano/laboratorio_datos_precio_aguacate](https://github.com/aldosolorsano/laboratorio_datos_precio_aguacate)
- **Tag de entrega:** `e0`
- **Profesores agregados como colaboradores:** [x] Joel  [x] Isis  [x] Roman

---

## Cómo Ejecutar los Extractores Localmente

### 1. Extractor de Clima (Open-Meteo) y Tipo de Cambio (Banxico)
```bash
# Instalación de dependencias básicas
pip install -r requirements.txt

# Extracción de clima (sin token requerido)
python src/extractores/openmeteo.py

# Extracción de tipo de cambio FIX Banxico (requiere token gratuito)
BANXICO_TOKEN=tu_token_aqui python src/extractores/banxico.py
```

### 2. Extractor de Precios Mayoristas (SNIIM con Playwright)
```bash
# Instalación de dependencias de navegador
pip install -r requirements-sniim.txt
playwright install chromium

# Ejecución de los últimos 60 días
python src/extractores/sniim.py

# O carga histórica personalizada (ej. desde noviembre 2023):
SNIIM_DESDE=2023-11-09 python src/extractores/sniim.py
```

---

## Matriz de Evidencias de los Entregables E0

| Entregable | Ubicación en el Repositorio | Estado | Detalle |
|---|---|:---:|---|
| **Propuesta del Observatorio (3-5 págs)** | [docs/E0/propuesta.md](file:///home/luisfernando/proyectos/laboratorio_datos_precio_aguacate/docs/E0/propuesta.md) | [x] Completo | Ficha técnica, entrevista de campo (32 min con Ing. Salvador Mendoza), 3 preguntas analíticas (E1, E2, E3), plan de datos y análisis ético/legal. |
| **Extractores Éticos de Datos** | [src/extractores/](file:///home/luisfernando/proyectos/laboratorio_datos_precio_aguacate/src/extractores/) | [x] Completo | Implementados `openmeteo.py`, `banxico.py`, `sniim.py` (Playwright) e `inegi.py`. User-Agent explícito y pausas de cortesía. |
| **Workflows Automáticos (CI/CD)** | [.github/workflows/](file:///home/luisfernando/proyectos/laboratorio_datos_precio_aguacate/.github/workflows/) | [x] Completo | `captura.yml` (diario a las 12:00 UTC) y `captura-sniim.yml` (semanal / manual dispatch con Playwright headless). |
| **Datos Crudos en Capa Bronce ($\ge 36$ periodos)** | [data/bronce/](file:///home/luisfernando/proyectos/laboratorio_datos_precio_aguacate/data/bronce/) | [x] Completo | Más de 1,400 periodos de clima, 967 de Banxico y 21,834 registros históricos de precios en 45 HTMLs de SNIIM. |
| **Sistema de Calidad Inicial (PSP)** | [calidad/](file:///home/luisfernando/proyectos/laboratorio_datos_precio_aguacate/calidad/) | [x] Completo | Registros abiertos de tiempo y defectos por cada integrante (`aldo-solorzano` y `luis-machuca`), más 3 objetivos medibles. |

---

## Periodos y Estadísticas Capturados por Fuente

- **Open-Meteo Archive API:** **1,402 periodos diarios consecutivos** por municipio (2023-01-01 al 2026-11-02) para Uruapan, Michoacán; Tancítaro, Michoacán; y Ciudad Guzmán, Jalisco (total: 4,206 observaciones meteorológicas).
- **Banxico SIE API (Serie SF43718):** **967 periodos diarios hábiles** de tipo de cambio FIX USD/MXN (2023-01-01 al 2026-11-06).
- **SNIIM (Secretaría de Economía):** **21,834 registros de cotizaciones mayoristas** distribuidos en **45 archivos HTML crudos**, con **753 fechas únicas** comprendidas entre el 2023-11-09 y el 2026-11-09, cubriendo 14 estados de origen y 46 centrales de abasto receptoras.
- **INEGI API:** Extractor preparado y probado en `src/extractores/inegi.py` para sincronizar el INPC de aguacate.

---

## Cumplimiento Ético y Legal

1. **SNIIM:** Inspección programática de `robots.txt` (`rp.can_fetch() == True`), guardando copia física del archivo de robots en `data/bronce/sniim/2026-11-09/robots.txt`. Se respeta una pausa de 3 segundos entre peticiones de consulta y navegación de páginas.
2. **Open-Meteo:** Atribución requerida bajo licencia internacional Creative Commons CC BY 4.0.
3. **Banxico:** Consumo de API oficial sin exposición de credenciales; token inyectado vía variables de entorno en GitHub Actions.

---

## Estado Actual y Próximos Pasos

- **Pendientes resueltos en E0:** Se superó el reto técnico del formulario ASP.NET de SNIIM mediante automatización con Playwright en GitHub Actions, logrando descargar exitosamente la serie histórica de 3 años.
- **Preparación para E1:** Comenzar la limpieza, estandarización de variables y estructuración de la Capa Plata (`data/plata/`) en formato Apache Parquet para el entrenamiento de los modelos predictivos iniciales.
