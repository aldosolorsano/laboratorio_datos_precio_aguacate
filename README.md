# Trusted Data Lab: Observatorio del Aguacate

Observatorio de precios del aguacate Hass en Jalisco y Michoacán.
Arquitectura por capas: Bronce (crudo) → Plata (limpio) → Oro (modelado).

## Estado
- **E0**: Capa Bronce con captura automática (GitHub Actions). Ver [propuesta](docs/E0/propuesta.md) y [ficha E0](docs/E0/ENTREGA.md).
- **E1**: Pipeline reproducible, diagnóstico y evaluación de pronóstico. Ver [ficha E1](docs/E1/ENTREGA.md) y [relatoría E1](docs/relatoria-E1.md).
- **E2**: Código de integración Reddit, linaje y declaración de ética. La captura de Reddit está pendiente de verificación y las tablas actuales tienen cero publicaciones admitidas. Ver [ficha E2](docs/E2/ENTREGA.md), [relatoría E2](docs/relatoria-E2.md) y [declaración de ética](docs/etica-datos.md).

## Uso local y reproducción E2

```bash
# 1. Instalar dependencias
pip install -r requirements-e2.txt

# 2. Configurar variables de entorno (requeridas para ejecutar el extractor de Reddit)
export REDDIT_CLIENT_ID="tu_client_id"
export REDDIT_CLIENT_SECRET="tu_client_secret"
export BANXICO_TOKEN="tu_token"

# 3. Ejecutar extractor de Reddit (o utilizar capturas locales en data/bronce/reddit/)
python src/extractores/reddit.py

# 4. Ejecutar pipeline completo E2 (E1 + Transformador Reddit + Trazabilidad + Linaje)
python -m pipeline.e2

# 5. Ejecutar suite de pruebas unitarias (E1 y E2)
python -m unittest discover -s tests
```

## Estructura del Proyecto
- `src/extractores/`: Extractores éticos (User-Agent transparente, pausas, respeto estricto a robots.txt y APIs OAuth 2.0).
- `src/transformadores/`: Transformadores de datos hacia capas Plata y Oro con preservación de linaje.
- `pipeline/`:
  - `pipeline/e1.py`: Pipeline base de precios SNIIM, Banxico y Open-Meteo.
  - `pipeline/e2.py`: Pipeline extendido E2 con integración de Reddit y generación de `linaje.json` y `calidad_e2.json`.
- `data/`:
  - `data/bronce/`: Datos crudos con metadatos de captura (`sniim`, `banxico`, `openmeteo`, `reddit`).
  - `data/plata/`: Tablas limpias y estandarizadas.
  - `data/oro/`: Tablas integradas (`cotizaciones_e2.csv`), métricas de calidad y grafo de trazabilidad (`linaje.json`).
- `calidad/`: Registros PSP (tiempo y defectos).
- `docs/`:
  - `docs/etica-datos.md`: Declaración completa de ética y legalidad (robots.txt, licencias, mitigación de sesgos, privacidad cero datos personales).
  - `docs/E0/`, `docs/E1/`, `docs/E2/`: Fichas de entrega y documentación técnica por hito.
  - `docs/relatoria-E2.md`: Relatoría formal de la etapa E2.
