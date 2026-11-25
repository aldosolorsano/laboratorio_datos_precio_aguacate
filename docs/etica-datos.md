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

### 1.5 Reddit API (fuente propuesta para E2)

- El extractor usa OAuth 2.0 Client Credentials y solicita un token por ejecución.
- El acceso requiere credenciales y autorización de Reddit. La revisión de las condiciones aplicables a la cuenta y al uso del equipo queda pendiente.
- Bronce conserva id de publicación, subreddit, votos, proporción de votos positivos, comentarios y timestamp. El identificador permite vincular una publicación pública. Plata agrega esas métricas por día de Ciudad de México.
- La búsqueda usa t=week. Los errores HTTP, las respuestas inesperadas y las búsquedas que anuncian otra página se propagan como fallo.
- La captura original se conserva en docs/E2/evidencia-revision por inconsistencias de identificadores y fechas. Las métricas actuales reflejan cero observaciones de Reddit admitidas.
- Los votos y comentarios miden interacción. La relación con demanda, sentimiento y precios requiere validación.

Documentación de referencia para completar la revisión de acceso y términos del equipo. [API de Reddit](https://www.reddit.com/dev/api/) y [términos de desarrolladores](https://redditinc.com/policies/developer-terms).

## 2. Análisis de Robots.txt

| Fuente | Archivo robots.txt | Resultado del análisis |
|--------|-------------------|----------------------|
| SNIIM | Guardado en `data/bronce/sniim/{fecha}/robots.txt` | Acceso permitido al User-Agent identificado. Se verifica en cada ejecución. |
| Banxico | N/A (API con token) | Permitido por diseño de la API. |
| Open-Meteo | N/A (API pública) | Permitido por diseño. |
| INEGI | N/A (API con token) | Permitido por diseño. |
| Reddit | API oficial propuesta | Pendiente acreditar autorización y condiciones aplicables al equipo. |

## 3. Licencias de datos

| Fuente | Licencia | Restricciones |
|--------|----------|--------------|
| SNIIM | Datos Abiertos Gobierno MX | Atribución. No comercial para uso académico. |
| Banxico | Uso libre con atribución | No redistribuir como producto propio. |
| Open-Meteo | CC BY 4.0 | Atribución obligatoria (registrada en `_meta`). |
| INEGI | MX.OGA | Atribución. |
| Reddit | Condiciones de la API y del contenido | Revisión pendiente antes de capturar y redistribuir datos. |

## 4. Privacidad y datos personales

Los extractores de precios, clima e indicadores trabajan con variables económicas y geográficas. La integración propuesta de Reddit conserva un identificador vinculable a una publicación y requiere evaluar ese tratamiento.

- SNIIM: precios mayoristas, sin datos de personas.
- Banxico: tipo de cambio institucional, sin personas.
- Open-Meteo: datos climáticos geográficos, sin personas.
- INEGI: indicador macroeconómico agregado, sin personas.
- Reddit conserva un identificador de publicación y métricas de interacción. La agregación diaria ocurre después de la captura.

El acceso público por sí solo no acredita las condiciones de uso y redistribución. El equipo debe documentar la revisión por fuente.

## 5. Mitigación de sesgos y limitaciones

### Sesgos identificados

| Sesgo | Descripción | Mitigación |
|-------|-------------|-----------|
| Cobertura geográfica | Solo mercados mayoristas formales de Jalisco y Michoacán. | Se documenta explícitamente el alcance. |
| Sesgo de selección (Reddit) | Usuarios de Reddit son demográficamente jóvenes y tecnológicos. | Evaluar la representatividad y utilidad de los conteos antes de usarlos como variable contextual. |
| Sesgo temporal (SNIIM) | Días festivos y fines de semana tienen menos cotizaciones. | El pipeline usa mediana semanal ponderando cada día igual. |
| Sesgo de presentación | No todas las presentaciones comerciales se registran igual. | La conversión a MXN/kg normaliza la unidad. |
| Sesgo de modelo | Los modelos de pronóstico asumen estacionariedad o ciertos supuestos. | Se reportan métricas de error y se publica el intervalo de confianza con advertencia explícita. |

### Uso ético del pronóstico
El pronóstico generado es **exploratorio y académico**. No debe usarse para decisiones comerciales sin validación adicional. Se comunica explícitamente su carácter exploratorio en el tablero.

## 6. Estado de la revisión

La captura Reddit del 22 de noviembre tiene procedencia pendiente de verificación y se conserva como evidencia documental. Para operar la fuente se requiere una captura autorizada que supere las validaciones del extractor y del transformador. Las licencias y bases de uso de las demás fuentes listadas arriba necesitan adjuntar su evidencia específica antes de declarar conformidad de la entrega.

Fecha de revisión del código y la evidencia local, 23 de noviembre de 2026. El equipo completa la revisión de acceso, licencias y responsabilidades.
