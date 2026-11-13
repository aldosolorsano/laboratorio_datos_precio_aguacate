import unittest

import pandas as pd
import pandera.pandas as pa

from pipeline.e1 import COLUMNAS, ESQUEMA, precios_por_kg, semanal
from laboratorio.pronostico import evaluar


class PruebasE1(unittest.TestCase):
    def test_convierte_caja_a_kilos(self):
        self.assertEqual(precios_por_kg(("450.00", "900.00", "630.00"), 9), [50, 100, 70])
        self.assertAlmostEqual(precios_por_kg(("1,200.00",), 9)[0], 1200 / 9)

    def test_valida_precio_frecuente(self):
        tabla = pd.DataFrame(
            [["2026-10-01", "Kilogramo", "Jalisco", "Mercado", 20., 30., 31., "sniim/a.html"]],
            columns=COLUMNAS,
        )
        with self.assertRaises(pa.errors.SchemaError):
            ESQUEMA.validate(tabla)

    def test_peso_igual_por_dia(self):
        mercado = "Jalisco: Mercado de Abasto de Guadalajara"
        tabla = pd.DataFrame({
            "mercado": [mercado] * 4,
            "fecha": ["2026-10-01"] * 3 + ["2026-10-02"],
            "frecuente_mxn_kg": [20, 20, 20, 40],
            "fix_mxn_usd": [18, 18, 18, 20],
        })
        resultado = semanal(tabla).iloc[0]
        self.assertEqual(resultado["precio_frecuente_mxn_kg"], 30)
        self.assertEqual(resultado["dias_cotizados"], 2)

    def test_no_entrena_si_hay_huecos(self):
        semanas = pd.date_range("2025-01-06", periods=39, freq="W-MON").delete(20)
        reporte, archivos = evaluar("Mercado", pd.DataFrame({"semana": semanas}))
        self.assertEqual(reporte["semanas_contiguas"], 20)
        self.assertEqual(archivos, [])
