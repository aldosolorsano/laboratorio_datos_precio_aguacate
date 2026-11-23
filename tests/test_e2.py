import json
import unittest
from pathlib import Path

import pandas as pd

from src.transformadores.integrar_reddit import (
    leer_bronce,
    transformar_plata,
    transformar_oro,
)
from pipeline.e2 import construir_linaje


class PruebasE2(unittest.TestCase):
    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.bronce_dir = self.base_dir / "data" / "bronce"

    def test_privacidad_sin_datos_personales_en_bronce(self):
        """Verifica que ningún JSON de reddit contenga datos de autor o texto."""
        archivos = list((self.bronce_dir / "reddit").glob("*.json"))
        self.assertTrue(len(archivos) > 0, "Debe existir al menos una captura en bronce/reddit")
        campos_prohibidos = {"author", "title", "selftext", "body", "user", "username", "email"}
        for archivo in archivos:
            payload = json.loads(archivo.read_text(encoding="utf-8"))
            for reg in payload.get("registros", []):
                interseccion = campos_prohibidos.intersection(reg.keys())
                self.assertEqual(
                    len(interseccion),
                    0,
                    f"Se encontraron campos con posibles datos personales: {interseccion}",
                )

    def test_transformacion_plata_reddit(self):
        """Verifica que la transformación agregue métricas correctamente por día."""
        datos_prueba = pd.DataFrame([
            {
                "id": "post1",
                "subreddit": "mexico",
                "score": 10,
                "upvote_ratio": 0.8,
                "num_comments": 5,
                "created_utc": 1795305600,
                "_archivo_bronce": "data/bronce/reddit/test.json",
                "_capturado_utc": "2026-11-22T14:30:00Z",
                "fecha": "2026-11-21",
            },
            {
                "id": "post2",
                "subreddit": "mexico",
                "score": 20,
                "upvote_ratio": 1.0,
                "num_comments": 15,
                "created_utc": 1795310000,
                "_archivo_bronce": "data/bronce/reddit/test.json",
                "_capturado_utc": "2026-11-22T14:30:00Z",
                "fecha": "2026-11-21",
            },
        ])
        plata = transformar_plata(datos_prueba)
        self.assertEqual(len(plata), 1)
        fila = plata.iloc[0]
        self.assertEqual(fila["posts_mencionando_aguacate"], 2)
        self.assertEqual(fila["score_total"], 30)
        self.assertEqual(fila["score_promedio"], 15.0)
        self.assertEqual(fila["comentarios_total"], 20)
        self.assertAlmostEqual(fila["ratio_positivo_promedio"], 0.9)
        self.assertIn("data/bronce/reddit/test.json", fila["archivo_reddit"])

    def test_linaje_y_trazabilidad(self):
        """Verifica la construcción del grafo de trazabilidad."""
        df_sim = pd.DataFrame({
            "fecha": ["2026-11-21"],
            "archivo_sniim": ["sniim/test.html"],
            "archivo_banxico": ["banxico/test.json"],
            "archivo_clima": ["openmeteo/test.json"],
            "archivo_reddit": ["reddit/test.json"],
        })
        salida = self.base_dir / "data"
        grafo = construir_linaje(self.bronce_dir, salida, df_sim)
        self.assertIn("nodos", grafo)
        self.assertIn("aristas", grafo)
        self.assertIn("sniim_en_oro", grafo["aristas"])
        self.assertIn("banxico_en_oro", grafo["aristas"])
        self.assertIn("clima_en_oro", grafo["aristas"])
        self.assertIn("reddit_en_oro", grafo["aristas"])


if __name__ == "__main__":
    unittest.main()
