import json
import unittest
from pathlib import Path
import pandas as pd


class PruebasE3(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.curado_dir = self.base_dir / "data" / "curado"
        self.opt_dir = self.base_dir / "data" / "oro" / "optimizacion"

    def test_existencia_dataset_curado_dual(self):
        """Verifica que el dataset curado esté publicado en CSV y Parquet."""
        ruta_csv = self.curado_dir / "precios_aguacate_mexico.csv"
        ruta_parq = self.curado_dir / "precios_aguacate_mexico.parquet"
        self.assertTrue(ruta_csv.exists(), "Debe existir el dataset curado en CSV")
        self.assertTrue(ruta_parq.exists(), "Debe existir el dataset curado en Parquet")

    def test_paridad_csv_y_parquet(self):
        """Verifica que los datos leídos de CSV y Parquet tengan el mismo número de filas."""
        df_csv = pd.read_csv(self.curado_dir / "precios_aguacate_mexico.csv")
        df_parq = pd.read_parquet(self.curado_dir / "precios_aguacate_mexico.parquet")
        self.assertEqual(len(df_csv), len(df_parq))
        self.assertGreater(len(df_csv), 15000, "El dataset curado debe tener más de 15,000 registros")

    def test_optimizacion_tamano_parquet(self):
        """Verifica que el archivo Parquet sea sustancialmente más liviano que el CSV."""
        tam_csv = (self.curado_dir / "precios_aguacate_mexico.csv").stat().st_size
        tam_parq = (self.curado_dir / "precios_aguacate_mexico.parquet").stat().st_size
        ahorro_pct = ((tam_csv - tam_parq) / tam_csv) * 100
        self.assertGreater(ahorro_pct, 70.0, "Parquet debe ahorrar al menos 70% de espacio frente a CSV")

    def test_metricas_benchmark_validas(self):
        """Verifica que el reporte de benchmark exista y reporte aceleración."""
        ruta_json = self.opt_dir / "metricas_optimizacion.json"
        self.assertTrue(ruta_json.exists(), "Debe existir metricas_optimizacion.json")
        datos = json.loads(ruta_json.read_text(encoding="utf-8"))
        self.assertIn("limpieza_y_transformacion", datos)
        self.assertIn("memoria_ram", datos)
        self.assertIn("almacenamiento_e_io", datos)
        self.assertGreater(datos["memoria_ram"]["reduccion_memoria_pct"], 30.0)

    def test_privacidad_redes_reales(self):
        """Verifica que las capturas de redes en bronce no contengan PII."""
        dir_redes = self.base_dir / "data" / "bronce" / "redes"
        if dir_redes.exists():
            archivos = list(dir_redes.glob("*.json"))
            for archivo in archivos:
                payload = json.loads(archivo.read_text(encoding="utf-8"))
                for r in payload.get("registros", []):
                    self.assertNotIn("username", r)
                    self.assertNotIn("email", r)
                    self.assertNotIn("account", r)
                    self.assertIn("interacciones_totales", r)


if __name__ == "__main__":
    unittest.main()
