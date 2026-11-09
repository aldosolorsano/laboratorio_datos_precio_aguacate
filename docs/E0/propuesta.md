# Propuesta del Observatorio: Aguacate Hass (Jalisco y Michoacán)

## 1. Ficha del observatorio
- **Laboratorio:** [NOMBRE DE TU LAB]
- **Integrantes:** [NOMBRES]
- **Sector:** Agroindustria, aguacate Hass
- **Región:** Michoacán y sur/occidente de Jalisco
- **Pregunta detonadora:** ¿Cómo evoluciona el precio del aguacate en mercados mayoristas y qué factores (temporada, clima, tipo de cambio) lo explican?
- **Cliente potencial:** productor, empacador o comerciante que decide cuándo cosechar, almacenar o vender.

## 2. Entrevista de campo (mín. 15 min)
**Entrevistado:** [nombre, rol, empresa/huerta, municipio] | **Fecha:** [__] | **Duración:** [__] min | **Medio:** [llamada/presencial]

Preguntas sugeridas (puedes cambiarlas):
1. ¿Qué factores cree que más mueven el precio del aguacate durante el año?
2. ¿De dónde obtiene hoy la información de precios y qué tan confiable le parece?
3. ¿Qué decisión le gustaría poder anticipar (cosecha, venta, almacenamiento)?
4. ¿Cuánta anticipación necesitaría de un pronóstico para que le sirviera?
5. ¿Qué diferencias nota entre mercados, regiones o calibres?

**Respuestas y aprendizajes:** [Resume con tus palabras lo que respondió cada pregunta, y 3 aprendizajes que cambian o confirman tu enfoque.]

## 3. Las 3 preguntas analíticas
- **E1 (pronóstico):** ¿Cuál será el precio mayorista del aguacate en las próximas 4 a 8 semanas?
- **E2 (experimentación):** ¿Cómo afectan la temporada, la precipitación/temperatura y el tipo de cambio USD/MXN al precio?
- **E3 (multivariado):** ¿Qué grupos de mercados o regiones se parecen en precio, volumen y variabilidad (clustering)?

## 4. Plan de recopilación de datos

| Fuente | Datos | Método | Frecuencia |
|---|---|---|---|
| Open-Meteo Archive API | Temperatura media y precipitación diaria (Uruapan, Tancítaro, Cd. Guzmán) | API REST, sin token | Diaria |
| Banxico SIE API (serie SF43718) | Tipo de cambio FIX USD/MXN | API REST con token personal | Diaria |
| SNIIM (por verificar) | Precios mayoristas de aguacate | Consulta web, pendiente de revisión legal | Pendiente |

### Análisis ético y legal
- **Open-Meteo:** datos bajo licencia CC BY 4.0; uso gratuito para fines no comerciales con atribución. Se respeta el límite de peticiones (3 peticiones por ejecución diaria). Consulta realizada el [fecha]: [anota lo que viste en open-meteo.com/en/terms].
- **Banxico:** API pública oficial; token personal almacenado como secreto de GitHub (no en el código). Se cita a Banxico como fuente.
- **SNIIM:** `robots.txt` revisado el [fecha]: [resultado]. Términos de uso: [resultado]. Si no permite automatización, se descarga manualmente o se sustituye por datos abiertos de SIAP.
- **Prácticas del extractor:** User-Agent identificado, pausas entre peticiones, sin datos personales, sin evadir restricciones técnicas.

### Serie histórica inicial
Open-Meteo y Banxico entregan datos diarios desde 2023-01-01, es decir, más de 1,000 periodos, muy por encima del mínimo de 36.

## 5. Objetivos de calidad medibles
1. **Confiabilidad de captura:** al menos 95% de las ejecuciones de GitHub Actions exitosas durante las 5 semanas.
2. **Completitud:** menos de 1% de valores nulos en las columnas clave (fecha, valor) de cada fuente en Bronce.
3. **Disciplina PSP:** registrar al menos 90% de las sesiones de trabajo en `tiempo-*.csv` y todo defecto encontrado en `defectos-*.csv`.
