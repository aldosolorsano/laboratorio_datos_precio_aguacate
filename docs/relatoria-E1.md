# Relatoría E1 · Observatorio del Aguacate

## 1. Qué nos propusimos

Construir una tabla semanal trazable en MXN/kg y comprobar si permite reservar ocho semanas para evaluar el pronóstico.

## 2. Qué hicimos

El 13 de noviembre se reprodujo el diagnóstico de captura, se implementó el pipeline y se ejecutaron las comprobaciones locales. Cada integrante debe completar su bitácora individual con el tiempo real de sus actividades.

## 3. Qué decidimos y por qué

Se admitieron únicamente ventanas de SNIIM con paginación completa. Se usó la mediana diaria antes de la semanal para que los días con más cotizaciones no dominen el resultado. Se conservaron los huecos al delimitar los bloques de evaluación.

## 4. Qué salió mal

Tres consultas fallaron al avanzar y otra devolvió HTML truncado. La validación de los marcadores superior e inferior evita incorporar esas respuestas como páginas completas. Sigue pendiente recuperar las ventanas.

## 5. Qué aprendimos

- **Ingeniería de Datos.** La paginación y la unidad comercial se deben verificar antes de integrar o agregar precios.
- **Análisis Estadístico.** Una serie con muchas fechas observadas puede tener un bloque continuo demasiado corto para probar modelos estacionales.
- **Calidad.** Cuatro ejecuciones exitosas miden la tasa observada de éxito. Las métricas de fallas y reparación requieren evidencia adicional.

## 6. Evidencias

Consultar la [ficha E1](E1/ENTREGA.md) y el [diagnóstico](E1/diagnostico-bronce.md).

## Uso de IA generativa

Codex apoyó la revisión del repositorio, la implementación del pipeline, las pruebas y la redacción de este borrador. Cada integrante debe revisar la evidencia y completar su aportación y su bitácora.
