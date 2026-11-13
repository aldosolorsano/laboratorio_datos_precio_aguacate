# E1 · Datos de confianza y pronóstico

Observatorio de precios mayoristas del aguacate Hass. El [diagnóstico de bronce](diagnostico-bronce.md) registra las ventanas incompletas que se identificaron en E0.

| Materia | Evidencia reproducible | Estado |
|---|---|---|
| Ingeniería de Datos | [Diagnóstico de bronce](diagnostico-bronce.md), [pipeline](../../pipeline/e1.py), [diccionario de oro](diccionario-oro.md) | Genera plata, oro, cuarentena y perfil de precios. La recaptura del 1 al 7 de octubre de 2026 fue completa y contenía 188 filas ya presentes. Quedan ventanas históricas por completar. |
| Análisis Estadístico | [Evaluación semanal](../../laboratorio/pronostico.py), [generador del tablero](../../laboratorio/tablero.py) | Cuatro modelos evaluados en tres mercados. Se obtuvo una proyección de ocho semanas para Iztapalapa con intervalo del 95%. |
| Calidad en los Sistemas de Información | [Plan SQA](sqa.md), [pruebas](../../tests/test_e1.py), [workflow](../../.github/workflows/validacion-e1.yml) | Verificación local. Pendientes los resultados de CI y de los escaneos de seguridad en GitHub, así como acreditar los siete días requeridos. |

## Reproducción

Desde la raíz del repositorio, con Python 3.12:

```bash
python -m pip install -r requirements-e1.txt
python -m pipeline.e1
python -m unittest discover -s tests
python -m laboratorio.pronostico
python -m laboratorio.tablero
```

El pipeline solo admite consultas de SNIIM con todas sus páginas verificadas. El lote evaluado produjo 15,338 cotizaciones válidas, cuatro en cuarentena y 292 combinaciones mercado-semana. Se descartaron 1,180 repeticiones exactas. Las métricas y la proyección se guardan en `data/oro/pronostico/evaluacion.json`. El tablero local se escribe en `data/oro/pronostico/tablero.html`.

En los mercados objetivo se agregaron 2,163 cotizaciones a 292 filas, una reducción de 86.5%. La serie semanal pierde los precios diarios y las diferencias por origen. El perfil exploratorio marcó 37 precios atípicos por IQR para revisión. Se conservan para evitar eliminar variaciones reales por una regla estadística. El clima tiene cobertura en 10,244 de 15,338 filas. Los nulos incluyen orígenes fuera de la correspondencia y posibles fechas sin observación. El lote admitido tuvo FIX en todas sus fechas cotizadas.

## Evaluación y alcance del pronóstico

Se usó un ciclo exploratorio de cuatro semanas para el ajuste aditivo de Holt-Winters, un mínimo de 16 semanas de entrenamiento y ocho de prueba. La estacionalidad anual queda sin estimar. Se excluyó la última semana cuando tenía menos de tres días cotizados. Se seleccionó por MAE en el bloque de prueba y se comparó con repetir el último precio del entrenamiento. ARIMA usa ADF para elegir si diferencia y AIC para comparar órdenes pequeños. La descomposición aditiva, ACF, PACF y correlación rezagada con cambios del FIX se guardan para inspección. La correlación es descriptiva.

| Mercado | Semanas continuas | Menor MAE (MXN/kg) | Último precio (MAE) | Resultado |
|---|---:|---:|---:|---|
| Iztapalapa | 28 | ARIMA, 2.13 | 2.85 | Proyección con intervalo del 95%. ADF después de diferenciar sigue por encima de 0.05. Interpretar como exploratoria. |
| Mercado de Abasto de Guadalajara | 28 | ARIMA, 1.91 | 1.91 | Empata con la referencia. |
| Felipe Ángeles | 28 | Holt, 1.63 | 4.38 | Prueba ARCH significativa. |
| Mercado Estrella | 14 | — | — | Cobertura insuficiente para el protocolo. |

El modelo de Iztapalapa se ajustó con observaciones hasta la semana del 2 de noviembre de 2026. Los intervalos cuantifican incertidumbre semanal bajo los supuestos del modelo. La comparación utiliza un solo tramo de prueba.

El tablero funciona como HTML autónomo. El workflow adjunta el HTML y los resultados como artefactos de la ejecución. La publicación del tablero en una URL pública queda pendiente.

[Relatoría de etapa](../relatoria-E1.md)
