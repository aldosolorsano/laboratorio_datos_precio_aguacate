# Sistema de Calidad Inicial (PSP)

Este directorio contiene las bitácoras del **Personal Software Process (PSP)** adaptado para el equipo de desarrollo e investigación del observatorio.

## Archivos Activos por Integrante

1. **Aldo Israel Solórzano Sánchez:**
   - `tiempo-aldo-solorzano.csv`: Registro de tiempo por fases de desarrollo (planeación, diseño, código, pruebas, configuración CI/CD).
   - `defectos-aldo-solorzano.csv`: Bitácora de defectos identificados y resueltos en los extractores y workflows.

2. **Luis Fernando Machuca Carrillo:**
   - `tiempo-luis-machuca.csv`: Registro de tiempo invertido en trabajo de campo (entrevista técnica), análisis conceptual, marco legal y documentación técnica.
   - `defectos-luis-machuca.csv`: Bitácora de desviaciones lógicas, validación de fuentes de datos y ajustes en la formulación de hipótesis.

## Formatos Estándar
- **Tiempo (`tiempo-<nombre>.csv`):** `fecha,fase,actividad,inicio,fin,interrupcion_min,delta_min` (fechas AAAA-MM-DD, horas HH:MM, tiempos netos en minutos).
- **Defectos (`defectos-<nombre>.csv`):** `id,fecha,fase_origen,fase_deteccion,tipo,descripcion,tiempo_correccion_min`.

## Objetivos de Calidad
1. **Confiabilidad de captura:** $\ge 95\%$ ejecuciones exitosas en CI/CD.
2. **Completitud de datos:** $< 1.0\%$ de nulos en variables clave.
3. **Disciplina PSP:** $\ge 90\%$ de sesiones de trabajo registradas y $100\%$ de defectos documentados.
