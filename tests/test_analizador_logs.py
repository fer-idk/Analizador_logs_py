"""Pruebas automáticas con la biblioteca estándar de Python."""
import json
import tempfile
import unittest
from pathlib import Path

from analizador_logs import (
    Reglas, analizar_archivo, analizar_linea, cargar_reglas,
    generar_resumen, validar_fecha,
)

RAIZ = Path(__file__).resolve().parents[1]


class PruebasAnalizador(unittest.TestCase):
    def setUp(self):
        self.reglas = Reglas(fecha_obligatoria=True, contar_lineas_vacias=True)

    def test_fecha_real(self):
        self.assertTrue(validar_fecha("2024-02-29"))

    def test_fecha_inexistente(self):
        self.assertFalse(validar_fecha("2025-02-29"))
        self.assertFalse(validar_fecha("2025-02-30"))

    def test_formato_fecha_estricto(self):
        self.assertFalse(validar_fecha("2025/01/10"))
        self.assertFalse(validar_fecha("2025-1-10"))

    def test_linea_completa(self):
        resultado = analizar_linea(1, "[ERROR] 2025-01-10 Sin conexión", self.reglas)
        self.assertTrue(resultado.es_valida)
        self.assertEqual(resultado.nivel, "ERROR")
        self.assertEqual(resultado.estado_fecha, "válida")

    def test_falta_fecha_obligatoria(self):
        resultado = analizar_linea(1, "[WARNING] Intento fallido", self.reglas)
        self.assertFalse(resultado.es_valida)
        self.assertIn("fecha obligatoria ausente", resultado.errores)

    def test_fecha_opcional(self):
        reglas = Reglas(fecha_obligatoria=False, contar_lineas_vacias=True)
        resultado = analizar_linea(1, "[WARNING] Intento fallido", reglas)
        self.assertTrue(resultado.es_valida)
        self.assertEqual(resultado.estado_fecha, "ausente")

    def test_fecha_invalida_aun_opcional(self):
        reglas = Reglas(fecha_obligatoria=False, contar_lineas_vacias=True)
        resultado = analizar_linea(1, "[ERROR] 2025-02-30 Error", reglas)
        self.assertFalse(resultado.es_valida)

    def test_severidad_desconocida(self):
        resultado = analizar_linea(1, "[DEBUG] 2025-01-10 Mensaje", self.reglas)
        self.assertIsNone(resultado.nivel)
        self.assertFalse(resultado.es_valida)

    def test_mensaje_ausente(self):
        resultado = analizar_linea(1, "[INFO] 2025-01-10", self.reglas)
        self.assertIn("mensaje ausente", resultado.errores)

    def test_archivo_correcto(self):
        resultados, ignoradas = analizar_archivo(RAIZ / "pruebas/log_bien_formado.txt", self.reglas)
        r = generar_resumen(resultados, ignoradas)
        self.assertEqual((r["total"], r["validas"], r["mal_formadas"]), (6, 6, 0))
        self.assertEqual(r["por_nivel"], {"INFO": 3, "WARNING": 2, "ERROR": 1})
        self.assertEqual(r["fechas"], {"válida": 6, "inválida": 0, "ausente": 0})

    def test_archivo_con_errores(self):
        resultados, ignoradas = analizar_archivo(RAIZ / "pruebas/log_con_errores.txt", self.reglas)
        r = generar_resumen(resultados, ignoradas)
        self.assertEqual((r["total"], r["validas"], r["mal_formadas"]), (10, 3, 7))
        self.assertEqual(r["por_nivel"], {"INFO": 2, "WARNING": 2, "ERROR": 3})
        self.assertEqual(r["sin_nivel_reconocido"], 3)
        self.assertEqual(r["fechas"], {"válida": 5, "inválida": 2, "ausente": 3})

    def test_ignorar_linea_vacia(self):
        reglas = Reglas(fecha_obligatoria=True, contar_lineas_vacias=False)
        resultados, ignoradas = analizar_archivo(RAIZ / "pruebas/log_con_errores.txt", reglas)
        r = generar_resumen(resultados, ignoradas)
        self.assertEqual((r["total"], r["mal_formadas"], r["lineas_ignoradas"]), (9, 6, 1))

    def test_archivo_vacio(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "vacio.log"
            ruta.write_text("", encoding="utf-8")
            resultados, ignoradas = analizar_archivo(ruta, self.reglas)
        self.assertEqual(generar_resumen(resultados, ignoradas)["total"], 0)

    def test_configuracion_incorrecta(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "reglas.json"
            ruta.write_text(json.dumps({"fecha_obligatoria": "sí", "contar_lineas_vacias": True}), encoding="utf-8")
            with self.assertRaises(ValueError):
                cargar_reglas(ruta)


if __name__ == "__main__":
    unittest.main()
