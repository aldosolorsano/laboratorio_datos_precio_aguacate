# Trusted Data Lab: Observatorio del Aguacate

Observatorio de precios del aguacate Hass en Jalisco y Michoacán.
Arquitectura por capas: Bronce (crudo) → Plata (limpio) → Oro (modelado).

## Estado
- E0: capa Bronce con captura automática (GitHub Actions).
- E1: pipeline reproducible y evaluación de cobertura. Ver [ficha de trabajo](docs/E1/ENTREGA.md).

## Uso local
```bash
pip install -r requirements.txt
python src/extractores/openmeteo.py
BANXICO_TOKEN=tu_token python src/extractores/banxico.py
```

## Estructura
- `src/extractores/`: extractores éticos (User-Agent identificado, pausas, sin saltarse robots.txt)
- `data/bronce/`: datos crudos con metadatos de captura
- `calidad/`: registros PSP (tiempo y defectos)
- `docs/E0/`: propuesta y ficha de entrega
