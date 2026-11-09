"""Analizador sencillo de logs para consola, sin dependencias externas.

Reglas de evaluación separadas del código en config/reglas.json.
La persona que entrega el proyecto debe revisar y justificar esas reglas.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

NIVELES = ("INFO", "WARNING", "ERROR")
PATRON_CABECERA = re.compile(r"^\[([A-Za-z]+)\](?:\s+(.*))?$")
PATRON_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PATRON_FECHA_PARECIDA = re.compile(r"^\d{4}[-/]\d")
REGLAS_PREDETERMINADAS = Path(__file__).resolve().parent / "config" / "reglas.json"


@dataclass(frozen=True)
class Reglas:
    # Propuestas explícitas para que el estudiante las confirme o ajuste.
    fecha_obligatoria: bool = True
    contar_lineas_vacias: bool = True


@dataclass(frozen=True)
class ResultadoLinea:
    numero: int
    texto: str
    nivel: str | None
    estado_fecha: str  # válida, inválida o ausente
    errores: tuple[str, ...]

    @property
    def es_valida(self) -> bool:
        return not self.errores


def cargar_reglas(ruta: Path) -> Reglas:
    """Comprueba tipos y nombres para no aceptar configuración ambigua."""
    with ruta.open("r", encoding="utf-8-sig") as archivo:
        contenido = json.load(archivo)
    if not isinstance(contenido, dict):
        raise ValueError("El archivo de reglas debe contener un objeto JSON.")
    permitidas = {"fecha_obligatoria", "contar_lineas_vacias"}
    desconocidas = set(contenido) - permitidas
    if desconocidas:
        raise ValueError(f"Reglas desconocidas: {', '.join(sorted(desconocidas))}.")
    for nombre in permitidas:
        if nombre not in contenido or not isinstance(contenido[nombre], bool):
            raise ValueError(f"La regla '{nombre}' debe existir y ser true o false.")
    return Reglas(**contenido)


def validar_fecha(texto: str) -> bool:
    """Una coincidencia de patrón NO garantiza una fecha real del calendario."""
    if not PATRON_FECHA.fullmatch(texto):
        return False
    try:
        datetime.strptime(texto, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def analizar_linea(numero: int, texto: str, reglas: Reglas) -> ResultadoLinea:
    """Inspecciona una línea sin detener el procesamiento ante errores de formato."""
    linea = texto.strip()
    errores: list[str] = []
    nivel: str | None = None
    estado_fecha = "ausente"
    contenido = ""

    cabecera = PATRON_CABECERA.fullmatch(linea)
    if cabecera is None:
        errores.append("encabezado de severidad ausente o mal formado")
    else:
        candidato = cabecera.group(1)
        if candidato not in NIVELES:
            errores.append(f"severidad desconocida: {candidato}")
        else:
            nivel = candidato
        contenido = (cabecera.group(2) or "").strip()

    # Política propuesta: fecha solo al inicio del contenido, en AAAA-MM-DD.
    # Si el primer token no parece fecha, el contenido es el mensaje sin fecha.
    mensaje = contenido
    if contenido:
        primero, _, resto = contenido.partition(" ")
        if PATRON_FECHA.fullmatch(primero) or PATRON_FECHA_PARECIDA.match(primero):
            estado_fecha = "válida" if validar_fecha(primero) else "inválida"
            mensaje = resto.strip()
            if estado_fecha == "inválida":
                errores.append("fecha inválida (formato o calendario)")

    if estado_fecha == "ausente" and reglas.fecha_obligatoria:
        errores.append("fecha obligatoria ausente")
    if not mensaje:
        errores.append("mensaje ausente")

    return ResultadoLinea(numero, texto.rstrip("\r\n"), nivel, estado_fecha, tuple(errores))


def analizar_archivo(ruta: Path, reglas: Reglas) -> tuple[list[ResultadoLinea], int]:
    resultados: list[ResultadoLinea] = []
    ignoradas = 0
    with ruta.open("r", encoding="utf-8-sig") as archivo:
        for numero, texto in enumerate(archivo, start=1):
            if not texto.strip() and not reglas.contar_lineas_vacias:
                ignoradas += 1
                continue
            resultados.append(analizar_linea(numero, texto, reglas))
    return resultados, ignoradas


def generar_resumen(resultados: list[ResultadoLinea], ignoradas: int = 0) -> dict:
    niveles = Counter(r.nivel for r in resultados if r.nivel is not None)
    fechas = Counter(r.estado_fecha for r in resultados)
    validas = sum(r.es_valida for r in resultados)
    total = len(resultados)
    return {
        "total": total,
        "validas": validas,
        "mal_formadas": total - validas,
        "por_nivel": {nivel: niveles[nivel] for nivel in NIVELES},
        "sin_nivel_reconocido": total - sum(niveles.values()),
        "fechas": {estado: fechas[estado] for estado in ("válida", "inválida", "ausente")},
        "lineas_ignoradas": ignoradas,
    }


def mostrar_resumen(ruta: Path, resumen: dict, resultados: list[ResultadoLinea], detalles: bool) -> None:
    print("=" * 56)
    print("               ANALIZADOR DE LOGS")
    print("=" * 56)
    print(f"Archivo: {ruta}")
    print(f"Total de eventos analizados: {resumen['total']}")
    print(f"Eventos válidos: {resumen['validas']}")
    print(f"Líneas mal formateadas o incompletas: {resumen['mal_formadas']}")
    print("Eventos por severidad (incluye líneas incompletas):")
    for nivel, cantidad in resumen["por_nivel"].items():
        print(f"  {nivel:<8}: {cantidad}")
    print(f"  SIN NIVEL: {resumen['sin_nivel_reconocido']}")
    print("Estado de las fechas:")
    for estado, cantidad in resumen["fechas"].items():
        print(f"  {estado.capitalize():<8}: {cantidad}")
    print(f"Líneas vacías ignoradas: {resumen['lineas_ignoradas']}")
    if detalles:
        defectuosas = [r for r in resultados if not r.es_valida]
        print("\nDETALLE DE LÍNEAS CON PROBLEMAS")
        if not defectuosas:
            print("  Ninguna.")
        for r in defectuosas:
            print(f"  Línea {r.numero}: {r.texto or '(vacía)'}")
            print(f"    Motivo(s): {'; '.join(r.errores)}")
    print("=" * 56)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analiza severidad, fecha y formato de eventos en un archivo de logs."
    )
    parser.add_argument("--archivo", type=Path, help="Ruta del archivo .txt o .log")
    parser.add_argument("--reglas", type=Path, default=REGLAS_PREDETERMINADAS,
                        help="Archivo JSON de reglas (predeterminado: config/reglas.json)")
    parser.add_argument("--detalles", action="store_true", help="Muestra los errores por línea")
    args = parser.parse_args(argv)
    if args.archivo is None:
        try:
            respuesta = input("Escriba la ruta del archivo que desea analizar: ").strip().strip('"')
        except EOFError:
            print("Error: no se proporcionó una ruta.", file=sys.stderr)
            return 2
        if not respuesta:
            print("Error: la ruta no puede estar vacía.", file=sys.stderr)
            return 2
        ruta = Path(respuesta)
    else:
        ruta = args.archivo

    try:
        reglas = cargar_reglas(args.reglas)
        if not ruta.is_file():
            raise FileNotFoundError(f"No existe un archivo en: {ruta}")
        resultados, ignoradas = analizar_archivo(ruta, reglas)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    resumen = generar_resumen(resultados, ignoradas)
    mostrar_resumen(ruta, resumen, resultados, args.detalles)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
