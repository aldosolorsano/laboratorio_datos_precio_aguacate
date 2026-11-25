# Relatoría E2 · Observatorio del Aguacate

## 1. Qué nos propusimos

Integrar una fuente de redes sociales (Reddit) mediante OAuth 2.0, garantizar la trazabilidad completa de registros desde Bronce hasta Oro, y formalizar la declaración de ética y legalidad del observatorio.

## 2. Qué hicimos

**Semana del 17 al 22 de noviembre de 2026**

Se diseñó e implementó el extractor de Reddit (`src/extractores/reddit.py`) usando el flujo OAuth 2.0 Client Credentials de la Reddit API oficial. Bronce conserva identificadores técnicos de publicaciones y métricas de actividad. Plata agrega por día.

Se construyó el transformador (`src/transformadores/integrar_reddit.py`) que convierte los JSON bronce en métricas diarias agregadas para la capa Oro.

Se redactó la declaración de ética (`docs/etica-datos.md`) con análisis de robots.txt, licencias y mitigación de sesgos para las cinco fuentes del observatorio.

Se actualizó el pipeline (`pipeline/e2.py`) para integrar Reddit con la capa Oro existente, añadiendo columnas de trazabilidad y generando `linaje.json`.

El 23 de noviembre se corrigieron el linter, el tratamiento de fallas HTTP, la validación de capturas y la correspondencia de fechas y rutas. El pipeline regenerado tiene cero publicaciones de Reddit admitidas. Los integrantes deben registrar sus tiempos reales y responsables en PSP.

## 3. Qué decidimos y por qué

**OAuth 2.0 Client Credentials (Application-Only)**: Se eligió este flujo porque el observatorio consume datos públicos de Reddit sin necesidad de actuar en nombre de un usuario. El acceso autorizado y las credenciales del equipo quedan pendientes de comprobar.

**Métricas agregadas sin datos personales**: Para cumplir con la ética de privacidad y los términos de Reddit, se decidió almacenar solo métricas numéricas de engagement (score, ratio, comentarios) sin ningún dato textual ni identificador de usuario. El identificador de publicación permite vinculación externa y requiere revisar los términos y el tratamiento de privacidad.

**Subreddits r/mexico y r/MexicoFinanciero**: Elegidos por mayor probabilidad de discusión de precios de alimentos en contexto mexicano. Se excluyen subreddits en inglés para mantener relevancia geográfica.

**Agregación diaria de actividad**: Reddit usa sumas y promedios de votos y comentarios por día. Los precios de E1 conservan sus medianas.

## 4. Qué salió mal

El extractor configura una búsqueda semanal con t=week. Esta ventana es una elección del código. La captura entregada incluye cinco registros anteriores a esa ventana y seis identificadores incompatibles con el formato esperado. Se conservó para revisión documental y se excluyó de bronce operativo.

El extractor solicita un token al iniciar. Los errores HTTP se propagan y las búsquedas incompletas se rechazan para evitar registrar una captura fallida como cero resultados.

## 5. Qué aprendimos

- **Ingeniería de Datos**: Las APIs con OAuth 2.0 requieren manejo explícito del ciclo de vida del token. La implementación actual obtiene un token por ejecución y hace visibles las fallas de acceso.
- **Privacidad**: El diseño "privacy-by-default" (capturar solo lo mínimo necesario) es más fácil de implementar desde el inicio que añadirlo después.
- **Trazabilidad**: Usar rutas relativas en lugar de absolutas para los campos `archivo_*` hace el pipeline reproducible en cualquier máquina.
- **Redes Sociales como señal económica**: Los conteos de votos y comentarios describen actividad. Evaluar su utilidad económica requiere datos verificables y contrastar su relación con los precios.

## 6. Evidencias

- Extractor: [`src/extractores/reddit.py`](../src/extractores/reddit.py)
- Transformador: [`src/transformadores/integrar_reddit.py`](../src/transformadores/integrar_reddit.py)
- Pipeline: [`pipeline/e2.py`](../pipeline/e2.py)
- Ética: [`docs/etica-datos.md`](etica-datos.md)
- Ficha: [`docs/E2/ENTREGA.md`](E2/ENTREGA.md)

## Uso de IA generativa

Codex apoyó la revisión y corrección local del 23 de noviembre, las pruebas y la actualización de métricas. Antigravity (Gemini) apoyó la implementación del extractor OAuth, el diseño del pipeline de trazabilidad y la redacción de la declaración de ética. Cada integrante debe revisar el código, ejecutarlo localmente y completar su bitácora individual.
