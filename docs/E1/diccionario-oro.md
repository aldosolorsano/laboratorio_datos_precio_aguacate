# Diccionario de datos de E1

Los CSV se generan a partir de bronce mediante `python -m pipeline.e1`.

| Campo de cotizaciones.csv | Definición |
|---|---|
| `fecha` | Fecha SNIIM en ISO 8601. Parte de la clave. |
| `presentacion`, `origen`, `mercado` | Presentación comercial, entidad productora reportada y mercado de destino. Completan la clave. |
| `minimo_mxn_kg`, `maximo_mxn_kg`, `frecuente_mxn_kg` | Precios en MXN/kg. Se divide el precio original entre el peso de la presentación. |
| `fix_mxn_usd` | Pesos mexicanos por dólar, serie FIX de Banxico de la misma fecha. Nulo si falta cotización para ese día. |
| `temperatura_c`, `precipitacion_mm` | Temperatura media diaria y precipitación acumulada diaria de las localidades asociadas al origen. Cuando hay dos localidades se promedian sus valores. Nulos para orígenes fuera de la correspondencia o fechas sin cobertura. |
| `archivo_sniim`, `archivo_banxico`, `archivo_clima` | Rutas relativas a `data/bronce`. Las rutas de clima se separan con barra vertical. |

| Campo de precios_semanales.csv | Definición |
|---|---|
| `mercado`, `semana` | Clave. La semana se identifica con la fecha del lunes. |
| `precio_frecuente_mxn_kg` | Mediana semanal de las medianas diarias. Cada día con cotizaciones tiene el mismo peso. |
| `dias_cotizados` | Número de fechas con cotización admitida. |
| `fix_mxn_usd` | Promedio del FIX publicado en los días cotizados de esa semana. |

Los días sin FIX y las semanas sin precios conservan su ausencia. El resumen `calidad.json` registra valores presentes por campo para distinguir cobertura de cotizaciones, clima y tipo de cambio.

## Perfil exploratorio

`perfil_precios.csv` añade cuatro campos a la clave y al precio frecuente. Min-max escala al intervalo 0–1 dentro de cada mercado y resulta sensible a extremos. Z-score expresa la distancia a la media en desviaciones estándar. Ambos quedan vacíos cuando su denominador es cero o no se puede estimar. La banda de precio usa cortes fijos de 25 MXN/kg hasta 100 y una banda superior abierta. `atipico_iqr` marca precios fuera de 1.5 rangos intercuartílicos por mercado para revisión, conservando el valor original. Estos cálculos describen el lote completo y quedan fuera del ajuste del pronóstico. La jerarquía territorial usa entidad de origen y mercado de destino.
