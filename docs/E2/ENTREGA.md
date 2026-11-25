# E2 · Fuente Especializada, Trazabilidad y Ética

## Resumen de entregables

| Requisito | Entregable | Estado |
|-----------|-----------|--------|
| Fuente especializada (Redes Sociales) | `src/extractores/reddit.py` + `src/transformadores/integrar_reddit.py` | Implementado, pendiente de verificación de captura |
| Declaración de ética y legalidad | `docs/etica-datos.md` | Revisión de acceso y licencias pendiente |
| Linaje y trazabilidad (Bronce→Plata→Oro) | Columnas `archivo_*` + `data/oro/linaje.json` | Linaje primario verificado |
| Pipeline E2 | `pipeline/e2.py` | Ejecutado localmente con cero capturas Reddit admitidas |
| Ficha de entrega | `docs/E2/ENTREGA.md` | Actualizada con pendientes por materia |
| Relatoría | `docs/relatoria-E2.md` | Pendientes responsables y tiempos individuales |

## 1. Fuente Especializada: Reddit API (OAuth 2.0)

**Tipo**: Redes Sociales — Métricas agregadas  
**API**: Reddit REST API v1 con autenticación OAuth 2.0 (Client Credentials)  
**Subreddits monitoreados**: r/mexico, r/MexicoFinanciero  
**Query de búsqueda**: "aguacate precio"

### Justificación
Reddit se propone como fuente de conteos de publicaciones y actividad asociada al tema del aguacate. Los votos y comentarios describen interacción. Interpretar demanda o sentimiento requiere una validación adicional.

### Implementación OAuth 2.0
El extractor implementa el flujo **Application-Only** (Client Credentials):
1. POST a `https://www.reddit.com/api/v1/access_token` con Basic Auth (`client_id:client_secret`)
2. Obtiene un `access_token` para la ejecución
3. Usa el token en el header `Authorization: Bearer {token}` para todas las llamadas
4. Si una petición falla, la ejecución propaga el error. Cada ejecución solicita un token nuevo.

### Campos y agregación
Bronce conserva una fila por publicación con `id`, `subreddit` y las siguientes métricas:
- `score` (votos netos)
- `upvote_ratio` (proporción positiva)
- `num_comments` (número de comentarios)
- `created_utc` (timestamp del post, público)

El identificador permite deduplicar y vincular la publicación en la plataforma. La agregación por día ocurre en plata, usando el día calendario de Ciudad de México.

### Variables de entorno requeridas
```bash
REDDIT_CLIENT_ID=tu_client_id
REDDIT_CLIENT_SECRET=tu_client_secret
```

El acceso necesita credenciales y autorización de Reddit. Debe verificarse con la cuenta del equipo antes de registrar la fuente como operativa.

## 2. Trazabilidad de Datos (Linaje Bronce→Plata→Oro)

Cada registro en la Capa Oro incluye columnas de trazabilidad hacia su origen en Bronce:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `archivo_sniim` | Ruta relativa al HTML en bronce | `sniim/2026-11-09/aguacate_hass_...p01.html` |
| `archivo_banxico` | Ruta relativa al JSON en bronce | `banxico/usdmxn_2026-11-22.json` |
| `archivo_clima` | Ruta(s) relativa(s) al JSON en bronce | `openmeteo/uruapan_mich_2026-11-22.json\|...` |
| `archivo_reddit` | Ruta relativa al JSON de Reddit en bronce | `reddit/reddit_aguacate_2026-11-22.json` |
| `ingesta_bronce_fecha` | Fecha de captura SNIIM tomada de su ruta | `2026-11-09` |
| `_ingesta_bronce_utc` | Timestamp de captura Reddit, cuando existe | `2026-11-22T18:12:00+00:00` |

El archivo `data/oro/linaje.json` enumera archivos de bronce con hashes SHA-256 y las rutas referenciadas por oro. La métrica de trazabilidad primaria comprueba que el HTML de SNIIM exista y que haya fecha de ingesta. La cobertura de clima y Reddit se reporta por separado.

## 3. Workflow GitHub Actions

El workflow `.github/workflows/captura-e2.yml` fue añadido para incluir el extractor Reddit:
```yaml
- name: Reddit Métricas
  env:
    REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
    REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
  run: python src/extractores/reddit.py
```

## 4. Reproducción local

Desde la raíz del repositorio:

```bash
python -m pip install -r requirements-e2.txt
python -m unittest discover -s tests
python -m pipeline.e2
```

El pipeline procesa las capturas locales. Para obtener una captura nueva en PowerShell:

```powershell
$env:REDDIT_CLIENT_ID = 'credencial-del-equipo'
$env:REDDIT_CLIENT_SECRET = 'secreto-del-equipo'
python src/extractores/reddit.py
python -m pipeline.e2
```

Las credenciales también se pueden configurar como GitHub Secrets para el workflow de captura.

## 5. Resultado verificado y pendientes

La captura del 22 de noviembre se conservó en [evidencia de revisión](evidencia-revision/reddit_aguacate_2026-11-22.no-verificado.json). Sus identificadores no corresponden al formato del campo id que consume el extractor y cinco registros superan los siete días configurados en la consulta. Su procedencia queda pendiente de acreditación. El pipeline excluye ese archivo de las capturas de producción.

Al regenerar E2 se obtuvieron 15,338 cotizaciones válidas y cero publicaciones de Reddit admitidas. El reporte distingue el total de publicaciones capturadas de las que coinciden con fechas de SNIIM. Con capturas ausentes, las tablas Reddit quedan vacías y el campo `capturas_reddit` vale cero. La fuente especializada sigue pendiente de evidencia operativa.

El linter, las pruebas y el pipeline se verifican localmente. El resultado del workflow de GitHub para estas correcciones queda pendiente de publicación.

## 6. Evidencia por materia

| Materia | Evidencia disponible | Pendiente |
|---|---|---|
| Ingeniería de Datos | Extractor OAuth, transformador, pipeline, linaje y revisión de ética | Captura autorizada y verificable de la fuente especializada, visualización en el tablero y cierre de la revisión de términos |
| Análisis Estadístico | — | Factorial 2³ con réplicas y aleatorización, ANOVA de dos vías, comparación 2⁴ y 2⁴⁻¹, supuestos y confirmación |
| Calidad en SI | Métricas de cobertura y trazabilidad | Evaluaciones ISO/IEC 25010 y 25012, antecedentes normativos y auditoría cruzada |

[Relatoría E2](../relatoria-E2.md)
