# Trusted Data Lab: Observatorio del Aguacate

Observatorio de precios mayoristas del aguacate Hass en Jalisco, Michoacán y centrales de abasto de México.
Arquitectura por capas: Bronce (crudo) → Plata (limpio) → Oro (modelado) → Curado (publicación).

## Estado del Proyecto
- **E0**: Capa Bronce con captura automática diaria (GitHub Actions). Ver [propuesta](docs/E0/propuesta.md) y [ficha E0](docs/E0/ENTREGA.md).
- **E1**: Pipeline reproducible, diagnóstico y evaluación de pronósticos. Ver [ficha E1](docs/E1/ENTREGA.md) y [relatoría E1](docs/relatoria-E1.md).
- **E2**: Fuente especializada de redes sociales, linaje y trazabilidad 100% auditable Bronce→Oro, y declaración formal de ética y legalidad. Ver [ficha E2](docs/E2/ENTREGA.md), [relatoría E2](docs/relatoria-E2.md) y [declaración de ética](docs/etica-datos.md).
- **E3**: Optimización formal del pipeline (vectorización, 59.4% menos RAM, 97% menos disco) y publicación del dataset curado dual (CSV + Apache Parquet) con su ficha técnica estandarizada (*Datasheet for Datasets*). Ver [ficha E3](docs/E3/ENTREGA.md), [datasheet](docs/E3/datasheet.md) y [relatoría E3](docs/relatoria-E3.md).

## Uso Rápido y Reproducción E3

```bash
# 1. Instalar dependencias completas
pip install -r requirements-e3.txt

# 2. Extraer datos reales en vivo de redes sociales (Mastodon API oficial)
python src/extractores/redes_sociales.py

# 3. Ejecutar el pipeline E3 optimizado
python -m pipeline.e3

# 4. Ejecutar el benchmark formal cuantitativo (E2 vs E3)
python tools/benchmark_optimizacion.py

# 5. Ejecutar la suite completa de pruebas unitarias (E1, E2 y E3)
python -m unittest discover -s tests -v

# 6. Probar el script demostrativo interactivo
python demo.py
```

## Dataset Curado Publicado
El dataset limpio y estandarizado está disponible en la carpeta `data/curado/` bajo licencia abierta **CC BY 4.0**:
- [`data/curado/precios_aguacate_mexico.csv`](data/curado/precios_aguacate_mexico.csv): Formato abierto universal (15,338 cotizaciones en 44 mercados).
- [`data/curado/precios_aguacate_mexico.parquet`](data/curado/precios_aguacate_mexico.parquet): Formato columnar binario comprimido con Snappy (apenas 110 KB con tipos estrictos).
- Consulta la ficha técnica completa y guía para el público en general en [`docs/E3/datasheet.md`](docs/E3/datasheet.md).

## 🔄 Automatización Semanal Desatendida (Sin Intervención Humana)
Dado que el mercado mayorista del aguacate actualiza precios y cotizaciones continuamente, el sistema está configurado para actualizarse **de forma 100% automática semana a semana sin que el usuario tenga que ejecutar código**:

1. **En la Nube (GitHub Actions - Recomendado)**:
   - El flujo [`.github/workflows/actualizacion-automatica.yml`](.github/workflows/actualizacion-automatica.yml) se ejecuta automáticamente en los servidores de GitHub **todos los lunes a las 8:00 AM hora de la Ciudad de México**.
   - Descarga las cotizaciones del SNIIM, Banxico, Open-Meteo y redes sociales, regenera el pipeline optimizado E3, reentrena los modelos econométricos (ARIMA y Holt), produce el nuevo tablero interactivo y guarda los cambios en el repositorio.
   - **Visualización en Vivo**: El tablero se publica directamente vía GitHub Pages en:  
     👉 **[https://aldosolorsano.github.io/laboratorio_datos_precio_aguacate/](https://aldosolorsano.github.io/laboratorio_datos_precio_aguacate/)** (o abriendo [`docs/index.html`](docs/index.html) / [`data/oro/pronostico/tablero.html`](data/oro/pronostico/tablero.html)).
   - **Ejecución Manual en 1 Clic**: También puedes ir a la pestaña **Actions** en GitHub, seleccionar *Actualización Semanal Automática* y presionar **Run workflow** para forzar la actualización en cualquier instante desde tu celular o computadora sin tocar la consola.

2. **En tu Computadora (Local / Windows)**:
   - Si prefieres ejecutar la actualización en tu equipo de forma desatendida, simplemente dale doble clic al archivo ejecutable [`actualizar_semanal.bat`](actualizar_semanal.bat).
   - Puedes programarlo en el **Programador de Tareas de Windows (Task Scheduler)** para que se abra cada lunes en segundo plano.

## Estructura del Repositorio
- `src/extractores/`: Extractores éticos (SNIIM, Banxico, Open-Meteo, Mastodon API real, Reddit).
- `src/transformadores/`: Transformadores de limpieza, normalización y linaje.
- `pipeline/`:
  - `pipeline/e1.py`: Pipeline base de precios, Banxico y clima.
  - `pipeline/e2.py`: Pipeline con trazabilidad y linaje JSON.
  - `pipeline/e3.py`: Pipeline optimizado de alta velocidad con exportación Parquet.
- `tools/`:
  - `tools/benchmark_optimizacion.py`: Medición cuantitativa de tiempo, RAM y almacenamiento.
  - `tools/perfilar_sniim.py` e `inspeccionar_sniim.py`: Perfilado de calidad de capturas crudas.
- `data/`:
  - `data/bronce/`: Datos crudos con metadatos de captura (`sniim`, `banxico`, `openmeteo`, `redes`, `reddit`).
  - `data/plata/`: Tablas limpias intermedias.
  - `data/oro/`: Tablas analíticas integradas, linaje JSON y métricas de optimización.
  - `data/curado/`: Datasets finales curados para distribución a terceros (CSV y Parquet).
- `docs/`: Fichas técnicas de entrega (`E0`, `E1`, `E2`, `E3`), relatorías formales y [declaración de ética](docs/etica-datos.md).
