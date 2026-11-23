# Relatoría E2 · Observatorio del Aguacate

## 1. Qué nos propusimos

Integrar una fuente de redes sociales (Reddit) mediante OAuth 2.0, garantizar la trazabilidad completa de registros desde Bronce hasta Oro, y formalizar la declaración de ética y legalidad del observatorio.

## 2. Qué hicimos

**Semana del 17 al 22 de noviembre de 2026**

Se diseñó e implementó el extractor de Reddit (`src/extractores/reddit.py`) usando el flujo OAuth 2.0 Client Credentials de la Reddit API oficial. Se decidió capturar únicamente métricas de engagement anónimas para garantizar privacidad total.

Se construyó el transformador (`src/transformadores/integrar_reddit.py`) que convierte los JSON bronce en métricas diarias agregadas para la capa Oro.

Se redactó la declaración de ética (`docs/etica-datos.md`) con análisis de robots.txt, licencias y mitigación de sesgos para las cinco fuentes del observatorio.

Se actualizó el pipeline (`pipeline/e2.py`) para integrar Reddit con la capa Oro existente, añadiendo columnas de trazabilidad y generando `linaje.json`.

## 3. Qué decidimos y por qué

**OAuth 2.0 Client Credentials (Application-Only)**: Se eligió este flujo porque el observatorio consume datos públicos de Reddit sin necesidad de actuar en nombre de un usuario. Es el flujo más seguro y adecuado para bots académicos según la documentación oficial de Reddit.

**Métricas agregadas sin datos personales**: Para cumplir con la ética de privacidad y los términos de Reddit, se decidió almacenar solo métricas numéricas de engagement (score, ratio, comentarios) sin ningún dato textual ni identificador de usuario. Esto hace innecesario el consentimiento informado.

**Subreddits r/mexico y r/MexicoFinanciero**: Elegidos por mayor probabilidad de discusión de precios de alimentos en contexto mexicano. Se excluyen subreddits en inglés para mantener relevancia geográfica.

**Mediana diaria como métrica principal**: Consistente con la decisión de E1 de usar medianas para reducir el impacto de outliers virales.

## 4. Qué salió mal

La Reddit API tiene un límite de búsqueda temporal: la búsqueda de posts no puede ir más de 7 días atrás sin usar endpoints de pago (Pushshift/Arctic Shift). Por esto, la cobertura histórica de Reddit es más corta que la de SNIIM. Se documenta esta limitación en el diccionario de datos.

La autenticación OAuth 2.0 requiere que el token sea renovado cada hora. Se implementó renovación automática en el extractor.

## 5. Qué aprendimos

- **Ingeniería de Datos**: Las APIs con OAuth 2.0 requieren manejo explícito del ciclo de vida del token. La lógica de renovación automática es más robusta que reutilizar el mismo token indefinidamente.
- **Privacidad**: El diseño "privacy-by-default" (capturar solo lo mínimo necesario) es más fácil de implementar desde el inicio que añadirlo después.
- **Trazabilidad**: Usar rutas relativas en lugar de absolutas para los campos `archivo_*` hace el pipeline reproducible en cualquier máquina.
- **Redes Sociales como señal económica**: Reddit tiene baja cobertura sobre aguacate comparado con Twitter/X, pero la API gratuita y sin restricciones de acceso la hacen preferible para proyectos académicos.

## 6. Evidencias

- Extractor: [`src/extractores/reddit.py`](../../src/extractores/reddit.py)
- Transformador: [`src/transformadores/integrar_reddit.py`](../../src/transformadores/integrar_reddit.py)
- Pipeline: [`pipeline/e2.py`](../../pipeline/e2.py)
- Ética: [`docs/etica-datos.md`](../etica-datos.md)
- Ficha: [`docs/E2/ENTREGA.md`](ENTREGA.md)

## Uso de IA generativa

Antigravity (Gemini) apoyó la implementación del extractor OAuth, el diseño del pipeline de trazabilidad y la redacción de la declaración de ética. Cada integrante debe revisar el código, ejecutarlo localmente y completar su bitácora individual.
