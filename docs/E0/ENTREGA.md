# Ficha de entrega E0

- **Laboratorio:** [NOMBRE]
- **Integrantes:** [NOMBRES]
- **Repositorio:** [URL]
- **Tag:** `e0`
- **Profesores agregados como colaboradores:** [ ] Joel  [ ] Isis  [ ] [tercer profesor]

## Cómo ejecutar
```bash
pip install -r requirements.txt
python src/extractores/openmeteo.py
BANXICO_TOKEN=xxx python src/extractores/banxico.py
```

## Evidencias
| Entregable | Ubicación | Estado |
|---|---|---|
| Propuesta | docs/E0/propuesta.md | [ ] |
| Extractores | src/extractores/ | [ ] |
| Workflow automático | .github/workflows/captura.yml | [ ] |
| Datos Bronce (>= 36 periodos) | data/bronce/ | [ ] |
| Registros PSP | calidad/ | [ ] |

## Periodos capturados por fuente
- Open-Meteo: [__] periodos por lugar
- Banxico USD/MXN: [__] periodos

## Pendientes / limitaciones
- Fuente de precios (SNIIM) pendiente de revisión legal y técnica.
