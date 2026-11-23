# Declaración de Ética y Legalidad de Datos

## 1. Fuentes de datos y términos de uso

### 1.1 SNIIM (Secretaría de Economía)
- **URL**: https://www.economia-sniim.gob.mx
- **Robots.txt analizado**: Se guarda copia en cada snapshot en `data/bronce/sniim/{fecha}/robots.txt`. El extractor verifica `robots_ok()` antes de cada sesión. El User-Agent `TrustedDataLab-Aguacate/0.1` es transparente.
- **Términos de uso**: Datos públicos del gobierno federal mexicano (Ley General de Transparencia). Uso académico no comercial permitido.
- **Licencia de los datos**: Dominio público / datos abiertos del gobierno (licencia MX.OGA.gob.mx o equivalente).
- **Mitigación de sesgos**: El SNIIM cubre mercados mayoristas formales; excluye mercados informales y precios al consumidor.

### 1.2 Banxico SIE API
- **URL**: https://www.banxico.org.mx/SieAPIRest/
- **Autenticación**: Token API gratuito (registro institucional).
- **Robots.txt**: No aplica (API REST con autenticación).
- **Términos de uso**: Banco de México autoriza uso de datos con atribución. Ver https://www.banxico.org.mx/politica-de-privacidad.html
- **Licencia**: Uso libre con atribución a Banxico.
- **Mitigación de sesgos**: El FIX es el tipo de cambio interbancario, no el de ventanilla.

### 1.3 Open-Meteo Archive API
- **URL**: https://archive-api.open-meteo.com
- **Autenticación**: Sin token (libre).
- **Robots.txt**: API pública.
- **Términos de uso**: Open-Meteo es de código abierto bajo Apache 2.0. Los datos históricos provienen de Copernicus/ECMWF.
- **Licencia**: CC BY 4.0 (atribución requerida). La licencia se registra en cada archivo bronce en `_meta.licencia`.
- **Mitigación de sesgos**: Las coordenadas cubren solo tres localidades productoras; zonas como Veracruz o Guerrero están excluidas.

### 1.4 INEGI API de Indicadores (INPC Aguacate)
- **URL**: https://www.inegi.org.mx/app/api/indicadores/
- **Autenticación**: Token gratuito (registro en portal INEGI).
- **Robots.txt**: No aplica (API REST).
- **Términos de uso**: INEGI publica datos bajo licencia de Datos Abiertos del Gobierno de México (MX.OGA).
- **Licencia**: Libre uso con atribución.
- **Mitigación de sesgos**: El INPC es un índice de precios al consumidor, no al mayorista.

### 1.5 Reddit API (nueva fuente E2)
- **URL**: https://www.reddit.com/dev/api/
- **Autenticación**: OAuth 2.0 Client Credentials (Application-Only). Token de acceso con duración de 1 hora, renovado automáticamente.
- **Robots.txt**: https://www.reddit.com/robots.txt — permite crawling de contenido público con autenticación.
- **Términos de uso**: Reddit Developer Terms of Service (https://www.redditinc.com/policies/developer-terms). Se cumple: sin scraping masivo, respetando rate limits (60 req/min), sin redistribución de datos personales, uso académico.
- **Licencia de los datos**: Reddit User Agreement. Los posts son públicos pero pertenecen a sus autores. **Solo se capturan métricas agregadas anónimas** (score, ratio, num_comments, timestamp).
- **Privacidad y datos personales**: CERO datos personales almacenados. No se guarda nombre de usuario, título del post, contenido, ni URL directa. Solo métricas de engagement anónimas por día.
- **Mitigación de sesgos**: Reddit tiene sesgo demográfico (usuarios jóvenes, urbanos, tecnológicos). Las métricas de redes sociales son correlativas, no causales, del precio del aguacate.

## 2. Análisis de Robots.txt

| Fuente | Archivo robots.txt | Resultado del análisis |
|--------|-------------------|----------------------|
| SNIIM | Guardado en `data/bronce/sniim/{fecha}/robots.txt` | Acceso permitido al User-Agent identificado. Se verifica en cada ejecución. |
| Banxico | N/A (API con token) | Permitido por diseño de la API. |
| Open-Meteo | N/A (API pública) | Permitido por diseño. |
| INEGI | N/A (API con token) | Permitido por diseño. |
| Reddit | https://www.reddit.com/robots.txt | Permite acceso con API oficial y autenticación OAuth. Se prohíbe scraping sin autenticación. |

## 3. Licencias de datos

| Fuente | Licencia | Restricciones |
|--------|----------|--------------|
| SNIIM | Datos Abiertos Gobierno MX | Atribución. No comercial para uso académico. |
| Banxico | Uso libre con atribución | No redistribuir como producto propio. |
| Open-Meteo | CC BY 4.0 | Atribución obligatoria (registrada en `_meta`). |
| INEGI | MX.OGA | Atribución. |
| Reddit | Reddit User Agreement | Solo métricas agregadas; sin datos personales. |

## 4. Privacidad y datos personales

Este observatorio **no recopila, almacena ni procesa datos personales** de ningún individuo.

- SNIIM: precios mayoristas, sin datos de personas.
- Banxico: tipo de cambio institucional, sin personas.
- Open-Meteo: datos climáticos geográficos, sin personas.
- INEGI: indicador macroeconómico agregado, sin personas.
- Reddit: **solo métricas de engagement** (score, ratio, número de comentarios, timestamp público). No se guarda nombre de usuario, contenido textual, ni ningún identificador personal.

Ninguna fuente requiere consentimiento informado de usuarios finales porque todos los datos son públicos, agregados e institucionales.

## 5. Mitigación de sesgos y limitaciones

### Sesgos identificados

| Sesgo | Descripción | Mitigación |
|-------|-------------|-----------|
| Cobertura geográfica | Solo mercados mayoristas formales de Jalisco y Michoacán. | Se documenta explícitamente el alcance. |
| Sesgo de selección (Reddit) | Usuarios de Reddit son demográficamente jóvenes y tecnológicos. | Las métricas Reddit son indicadores de sentimiento, no de precio. Se usan solo como variable contextual. |
| Sesgo temporal (SNIIM) | Días festivos y fines de semana tienen menos cotizaciones. | El pipeline usa mediana semanal ponderando cada día igual. |
| Sesgo de presentación | No todas las presentaciones comerciales se registran igual. | La conversión a MXN/kg normaliza la unidad. |
| Sesgo de modelo | Los modelos de pronóstico asumen estacionariedad o ciertos supuestos. | Se reportan métricas de error y se publica el intervalo de confianza con advertencia explícita. |

### Uso ético del pronóstico
El pronóstico generado es **exploratorio y académico**. No debe usarse para decisiones comerciales sin validación adicional. Se comunica explícitamente su carácter exploratorio en el tablero.

## 6. Declaración de conformidad

Los autores de este observatorio declaran que:
1. Todos los datos se obtienen de fuentes públicas o mediante APIs oficiales con autenticación autorizada.
2. No se recopilan, procesan ni almacenan datos personales.
3. Se respetan los `robots.txt` y los términos de servicio de cada fuente.
4. Las licencias de datos son compatibles con el uso académico no comercial.
5. Los sesgos conocidos están documentados y comunicados.
6. El código fuente es reproducible y auditado.

**Fecha de revisión**: 2026-11-22  
**Responsables**: Equipo TrustedDataLab-Aguacate
