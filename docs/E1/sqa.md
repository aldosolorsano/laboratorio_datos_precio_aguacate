# Plan de aseguramiento de la calidad de E1

## Alcance y responsabilidades

El plan cubre captura, limpieza, integración y evaluación del pronóstico de precios del aguacate Hass. Quien prepara un cambio adjunta las comprobaciones en el pull request. La otra persona revisa las reglas de negocio, el origen de los datos y el resultado de CI. Cada integrante registra su tiempo y sus defectos en `calidad/`.

| Requisito verificable | Comprobación y evidencia |
|---|---|
| Captura SNIIM completa | El marcador de cada página debe coincidir arriba y abajo. Una ventana incompleta devuelve código 1. Revisar el log del workflow y ejecutar el diagnóstico. |
| Precios comparables | La unidad de salida es MXN/kg. Verificar que una caja de 9 kg y 450 MXN produce 50 MXN/kg. |
| Datos válidos y trazables | Pandera exige clave única, precios positivos y mínimo ≤ frecuente ≤ máximo. Revisar el CSV de cuarentena y abrir el HTML citado en cada rechazo. |
| Evaluación temporal | Las últimas ocho semanas del bloque elegido quedan reservadas para prueba. Revisar las fechas y MAE, RMSE y MAPE del reporte. |
| Captura reproducible | Regenerar las capas a partir del mismo commit con el flujo de validación. Para ensayar un respaldo, clonar y repetir ambos módulos sin token. |

## Métricas, revisiones y control de cambios

- Tasa de éxito programado = ejecuciones exitosas / ejecuciones programadas observadas. Objetivo de E0 ≥95%. Se observaron cuatro éxitos de cuatro entre el 9 y el 12 de noviembre. La evidencia abarca cuatro días de ejecución programada. No hay un ciclo observado de falla y reparación para estimar MTBF ni MTTR.
- Completitud = valores presentes / celdas esperadas, medida por campo y fuente. Registrar días sin publicación del FIX, zonas sin correspondencia climática y huecos de cobertura SNIIM antes de interpretar la métrica.
- Cada cambio pasa por linter, pruebas y ejecución del pipeline en GitHub Actions. La protección de la rama debe configurarse en GitHub para que la validación sea obligatoria al fusionar.
- Abrir un issue o registrar un defecto PSP cuando falle una regla. Incluir el dato o ventana, responsable, acción correctiva y enlace a la nueva verificación.

## Seguridad y riesgos

El workflow de validación usa permiso de solo lectura y el pipeline de análisis usa archivos locales. La captura de Banxico e INEGI obtiene sus tokens de GitHub Secrets. Queda pendiente verificar el historial con Gitleaks, auditar las dependencias con pip-audit y adjuntar la prueba de restauración. Los riesgos inmediatos son las respuestas truncadas de SNIIM y un tramo de datos demasiado corto para estimar estacionalidad anual. Se registran como limitaciones de la entrega.
