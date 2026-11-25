import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd

from src.transformadores.integrar_reddit import (
    leer_bronce,
    transformar_plata,
    transformar_oro,
)
from pipeline.e2 import construir_linaje
from src.extractores.reddit import buscar_posts
from laboratorio.tablero import seccion_reddit
import requests


class PruebasE2(unittest.TestCase):
    def test_tablero_reddit_vacio_muestra_estado_pendiente(self):
        with TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "reddit.csv"
            pd.DataFrame(columns=["fecha"]).to_csv(ruta, index=False)
            self.assertIn("pendiente", seccion_reddit(ruta))
            self.assertIn("pendiente", seccion_reddit(ruta.with_name("ausente.csv")))

    def setUp(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.bronce_dir = self.base_dir / "data" / "bronce"

    def test_privacidad_sin_datos_personales_en_bronce(self):
        """Verifica que ningún JSON de reddit contenga datos de autor o texto."""
        archivos = list((self.bronce_dir / "reddit").glob("*.json"))
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

    def test_captura_no_verificada_rechazada(self):
        original = self.base_dir / "docs/E2/evidencia-revision/reddit_aguacate_2026-11-22.no-verificado.json"
        with TemporaryDirectory() as carpeta:
            bronce = Path(carpeta) / "reddit"
            bronce.mkdir()
            (bronce / "reddit_aguacate_2026-11-22.json").write_bytes(original.read_bytes())
            with self.assertRaisesRegex(ValueError, "Identificador Reddit"):
                leer_bronce(bronce)

    def test_error_http_no_equivale_a_cero_publicaciones(self):
        with patch("src.extractores.reddit.requests.get") as get, patch(
            "src.extractores.reddit.time.sleep"
        ):
            get.return_value.raise_for_status.side_effect = requests.HTTPError("401")
            with self.assertRaises(requests.HTTPError):
                buscar_posts("token-prueba", "mexico", "aguacate precio")

    def test_fecha_local_y_ruta_relativa(self):
        captura = {
            "_meta": {"capturado_utc": "2026-11-22T14:30:00+00:00"},
            "registros": [{
                "id": "abc123", "subreddit": "mexico", "score": 10,
                "num_comments": 2, "upvote_ratio": 0.8,
                "created_utc": pd.Timestamp("2026-11-22T02:00:00Z").timestamp(),
            }],
        }
        with TemporaryDirectory() as carpeta:
            bronce = Path(carpeta) / "reddit"
            bronce.mkdir()
            ruta = bronce / "reddit_aguacate_2026-11-22.json"
            ruta.write_text(json.dumps(captura), encoding="utf-8")
            datos, _ = leer_bronce(bronce)
            self.assertEqual(datos.iloc[0]["fecha"], "2026-11-21")
            self.assertEqual(datos.iloc[0]["_archivo_bronce"], "reddit/" + ruta.name)

    def test_capturas_ausentes_producen_tablas_vacias(self):
        with TemporaryDirectory() as carpeta:
            datos, origenes = leer_bronce(Path(carpeta) / "reddit")
            plata = transformar_plata(datos)
            oro = transformar_oro(plata, datos)
            self.assertTrue(oro.empty)
            self.assertEqual(origenes, {})
            self.assertIn("posts_mencionando_aguacate", oro.columns)

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
