# E2 · Fuente Especializada, Trazabilidad y Ética

## Resumen de entregables

| Requisito | Entregable | Estado |
|-----------|-----------|--------|
| Fuente especializada (Redes Sociales) | `src/extractores/reddit.py` + `src/transformadores/integrar_reddit.py` | ✅ |
| Declaración de ética y legalidad | `docs/etica-datos.md` | ✅ |
| Linaje y trazabilidad (Bronce→Plata→Oro) | Columnas `archivo_*` + `data/oro/linaje.json` | ✅ |
| Pipeline E2 | `pipeline/e2.py` | ✅ |
| Ficha de entrega | `docs/E2/ENTREGA.md` | ✅ |
| Relatoría | `docs/relatoria-E2.md` | ✅ |

## 1. Fuente Especializada: Reddit API (OAuth 2.0)

**Tipo**: Redes Sociales — Métricas agregadas  
**API**: Reddit REST API v1 con autenticación OAuth 2.0 (Client Credentials)  
**Subreddits monitoreados**: r/mexico, r/MexicoFinanciero  
**Query de búsqueda**: "aguacate precio"

### Justificación
Reddit permite capturar el sentimiento público sobre el precio del aguacate desde la perspectiva del consumidor. Complementa la capa de precios mayoristas (SNIIM) con una señal de demanda y percepción pública.

### Implementación OAuth 2.0
El extractor implementa el flujo **Application-Only** (Client Credentials):
1. POST a `https://www.reddit.com/api/v1/access_token` con Basic Auth (`client_id:client_secret`)
2. Obtiene `access_token` con 1 hora de vigencia
3. Usa el token en el header `Authorization: Bearer {token}` para todas las llamadas
4. Renueva automáticamente el token cuando expira

### Privacidad (CERO datos personales)
Solo se almacenan métricas agregadas anónimas:
- `score` (votos netos)
- `upvote_ratio` (proporción positiva)
- `num_comments` (número de comentarios)
- `created_utc` (timestamp del post, público)

**NO se almacena**: nombre de usuario, título del post, contenido, URL directa del post.

### Variables de entorno requeridas
```bash
REDDIT_CLIENT_ID=tu_client_id
REDDIT_CLIENT_SECRET=tu_client_secret
```

Registro gratuito en: https://www.reddit.com/prefs/apps (tipo: "script")

## 2. Trazabilidad de Datos (Linaje Bronce→Plata→Oro)

Cada registro en la Capa Oro incluye columnas de trazabilidad hacia su origen en Bronce:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `archivo_sniim` | Ruta relativa al HTML en bronce | `sniim/2026-11-09/aguacate_hass_...p01.html` |
| `archivo_banxico` | Ruta relativa al JSON en bronce | `banxico/usdmxn_2026-11-22.json` |
| `archivo_clima` | Ruta(s) relativa(s) al JSON en bronce | `openmeteo/uruapan_mich_2026-11-22.json\|...` |
| `archivo_reddit` | Ruta relativa al JSON de Reddit en bronce | `reddit/reddit_aguacate_2026-11-22.json` |
| `_ingesta_fecha_utc` | Timestamp UTC de ingesta en bronce | `2026-11-22T18:12:00+00:00` |

El archivo `data/oro/linaje.json` documenta el grafo completo de trazabilidad, incluyendo hashes SHA-256 de los archivos bronce usados.

## 3. Workflow GitHub Actions

El workflow `.github/workflows/captura-e2.yml` fue añadido para incluir el extractor Reddit:
```yaml
- name: Reddit Métricas
  env:
    REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
    REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
  run: python src/extractores/reddit.py
```

## 4. Reproducción

```bash
pip install -r requirements-e2.txt

# Configurar variables de entorno
export REDDIT_CLIENT_ID=tu_client_id
export REDDIT_CLIENT_SECRET=tu_client_secret
export BANXICO_TOKEN=tu_token

# Ejecutar pipeline completo E2
python -m pipeline.e2

# Solo extractor Reddit (sin token Banxico)
python src/extractores/reddit.py
```

## 5. Métricas de calidad E2

El pipeline E2 genera `data/oro/calidad_e2.json` con:
- `posts_capturados`: total de posts únicos de Reddit
- `dias_con_datos_reddit`: cobertura temporal en la capa oro
- `cobertura_reddit_vs_sniim`: porcentaje de fechas SNIIM con dato Reddit
- `trazabilidad_completa`: porcentaje de filas con todos los archivos de origen presentes
