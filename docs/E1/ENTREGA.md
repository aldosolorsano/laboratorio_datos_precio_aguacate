# E1 · Datos de confianza y pronóstico

Observatorio de precios mayoristas del aguacate Hass. Ficha de trabajo pendiente de cierre. El [diagnóstico de bronce](diagnostico-bronce.md) registra las ventanas incompletas que se identificaron en E0.

| Materia | Evidencia reproducible | Estado |
|---|---|---|
| Ingeniería de Datos | [Diagnóstico de bronce](diagnostico-bronce.md), [pipeline](../../pipeline/e1.py), [diccionario de oro](diccionario-oro.md) | Genera plata, oro, cuarentena y perfil de precios. Quedan por recuperar cuatro ventanas de SNIIM. |
| Análisis Estadístico | [Evaluación semanal](../../laboratorio/pronostico.py) | El histórico admitido tiene 29 semanas continuas en Iztapalapa, 28 en cada mercado de Guadalajara y 14 en Estrella. El protocolo actual necesita 34, incluidas ocho de prueba. No hay métricas de modelos ni pronóstico de negocio con estas series. |
| Calidad en los Sistemas de Información | [Plan SQA](sqa.md), [pruebas](../../tests/test_e1.py), [workflow](../../.github/workflows/validacion-e1.yml) | Verificación local. Pendientes ejecución en GitHub, evidencia de siete días, auditoría de dependencias y secretos y respaldo restaurado. |

## Reproducción

Desde la raíz del repositorio, con Python 3.12:

```bash
python -m pip install -r requirements-e1.txt
python -m pipeline.e1
python -m unittest discover -s tests
python -m laboratorio.pronostico
```

El pipeline solo admite consultas de SNIIM con todas sus páginas verificadas. El lote evaluado produjo 15,338 cotizaciones válidas, cuatro en cuarentena y 292 combinaciones mercado-semana. Se descartaron 992 repeticiones exactas. El reporte de cobertura se escribe en `data/oro/pronostico/evaluacion.json`.

En los mercados objetivo se agregaron 2,163 cotizaciones a 292 filas, una reducción de 86.5%. La serie semanal pierde los precios diarios y las diferencias por origen. El perfil exploratorio marcó 37 precios atípicos por IQR para revisión. Se conservan para evitar eliminar variaciones reales por una regla estadística. El clima tiene cobertura en 10,244 de 15,338 filas. Los nulos incluyen orígenes fuera de la correspondencia y posibles fechas sin observación. El lote admitido tuvo FIX en todas sus fechas cotizadas.

Para el modelo exploratorio se definió un ciclo de 13 semanas y un bloque de prueba de ocho. El mínimo de 34 semanas deja dos ciclos completos para ajustar Holt-Winters. Este criterio es una decisión metodológica, además del mínimo de 36 periodos de E0. El ciclo de 13 semanas queda como hipótesis a contrastar con un histórico más largo. La selección por MAE y los intervalos retrospectivos solo se calculan en bloques elegibles.

[Relatoría de etapa](../relatoria-E1.md)
