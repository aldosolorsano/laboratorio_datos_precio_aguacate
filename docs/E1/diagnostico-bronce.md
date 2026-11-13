# Diagnóstico de bronce para E1

La revisión parte del commit `acf779c` de `main`. El script lee los HTML ya guardados y no requiere credenciales. Desde la raíz del repositorio:

```bash
python -m pip install lxml==6.1.1
python -X utf8 tools/perfilar_sniim.py
```

## Integridad del histórico de precios

| Captura | Ventana consultada | Páginas guardadas | Páginas faltantes |
|---|---|---:|---|
| 8 nov. | 2026-10-01 a 2026-11-08 | 1/2 | 2 |
| 9 nov. | 2023-11-09 a 2024-05-06 | 2/10 | 3–10 |
| 9 nov. | 2024-11-03 a 2025-05-01 | 7/10 | 8–10 |
| 9 nov. | 2025-10-29 a 2026-04-26 | 1/10 | 2–10 |

Los 45 HTML contienen 21,834 filas, 20,342 filas distintas y 753 fechas observadas. Hay 1,492 repeticiones exactas. La combinación fecha, presentación, origen y mercado no tiene versiones distintas en este lote. Cuatro cotizaciones distintas incumplen el orden de precios `0 < mínimo ≤ frecuente ≤ máximo`. El script muestra el valor original y su archivo para revisión.

El encabezado de SNIIM indica que cada precio está en pesos por presentación comercial. En los mercados objetivo todas las filas observadas corresponden a cajas de 9 kg. Un precio frecuente de `1,200.00` equivale a 133.33 MXN/kg después de dividir entre nueve y redondear para mostrar. Una caja sin peso explícito se debe revisar antes de convertirla.

| Mercado | Semanas observadas | Semanas calendario entre primera y última | Semanas sin dato |
|---|---:|---:|---:|
| Mercado de Abasto de Guadalajara | 106 | 131 | 25 |
| Mercado Felipe Ángeles de Guadalajara | 106 | 131 | 25 |
| Central de Abasto de Iztapalapa | 115 | 158 | 43 |
| Mercado de Abasto Estrella, área de Monterrey | 53 | 116 | 63 |

El conteo semanal exige al menos una cotización válida en la semana, con lunes como inicio. Una semana con dato puede tener cobertura parcial. Las capturas incompletas impiden atribuir los huecos a la operación de los mercados. El extractor conserva páginas parciales y puede terminar con código cero si guardó alguna página, por lo que el resultado de la ejecución requiere una comprobación adicional de completitud.

## Decisiones pendientes para E1

1. Recuperar las páginas faltantes y volver a ejecutar el diagnóstico. Verificar que el conjunto de páginas guardadas coincida con los números anunciados por SNIIM antes de aceptar cada consulta.
2. Construir plata con la clave candidata anterior, conservar el vínculo al HTML y enviar a cuarentena los registros inválidos con su motivo. Definir cómo tratar cotizaciones repetidas o contradictorias antes de agregar por semana.
3. Construir la serie semanal para cada mercado con una regla explícita de agregación y cobertura. Congelar un tramo final de prueba, medir MAE, RMSE y MAPE y comparar suavizamiento simple, Holt, Holt-Winters y ARIMA o SARIMA, según la rúbrica. Evaluar el horizonte de cuatro a ocho semanas con base en la cobertura recuperada.
4. Open-Meteo y Banxico tienen históricos en bronce. En las instantáneas del 12 de noviembre hay 1,405 días por localidad y 971 cotizaciones FIX. Se necesita definir la unión temporal y territorial. Las fechas sin publicación de FIX se distinguen de los datos faltantes de una captura.

## Cómo repetir una ventana histórica

En GitHub Actions, el workflow `captura-sniim` acepta los campos `desde` y `hasta`. Para ejecutarlo en PowerShell desde la raíz del repositorio:

```powershell
python -m pip install -r requirements-sniim.txt
python -m playwright install chromium
$env:SNIIM_DESDE = '2023-11-09'
$env:SNIIM_HASTA = '2024-05-06'
python src/extractores/sniim.py
```

Repetir con cada intervalo de la tabla. Una ventana se guarda cuando el marcador y la tabla se verifican para todas las páginas anunciadas. Si alguna ventana queda incompleta, el proceso devuelve código 1 y el workflow omite el paso de publicación. Los archivos recuperados quedan en la carpeta de la fecha de captura. Las carpetas anteriores sirven de evidencia del estado original.

## Evidencia de fiabilidad

Al revisar GitHub Actions el 13 de noviembre, el historial visible mostró cuatro ejecuciones programadas de `captura-bronce` del 9 al 12 de noviembre, todas exitosas, y una ejecución manual exitosa del 8 de noviembre en horario de Ciudad de México. No había ejecuciones visibles de `captura-sniim`. La tasa observada de éxito programado es 4/4 para `captura-bronce`. La ventana de siete días de la rúbrica y los tiempos entre fallas y de reparación siguen sin evidencia suficiente.

Historial consultado en [GitHub Actions](https://github.com/aldosolorsano/laboratorio_datos_precio_aguacate/actions).
