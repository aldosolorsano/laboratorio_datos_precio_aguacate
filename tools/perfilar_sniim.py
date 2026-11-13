"""Comprueba las capturas históricas antes de construir la serie semanal."""

import argparse
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from lxml import html


PAGINA = re.compile(r"P[áa]gina\s+(\d+)\s+de\s+(\d+)", re.IGNORECASE)
ARCHIVO = re.compile(r"(aguacate_hass_primera_[\d-]+_[\d-]+)_p(\d+)\.html")
PRECIO = re.compile(r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?")
CAJA = re.compile(r"Caja de ([1-9]\d*) kg\.", re.IGNORECASE)
MERCADOS = (
    "Jalisco: Mercado de Abasto de Guadalajara",
    "Jalisco: Mercado Felipe Ángeles de Guadalajara",
    "DF: Central de Abasto de Iztapalapa DF",
    'Nuevo León: Mercado de Abasto "Estrella" de San Nicolás de los Garza',
)


def leer_capturas(bronce):
    consultas = defaultdict(dict)
    cotizaciones = {}
    total_filas = 0
    for ruta in sorted(bronce.glob("*/*.html")):
        coincidencia = ARCHIVO.fullmatch(ruta.name)
        if not coincidencia:
            print(f"HTML fuera del patrón de cotizaciones: {ruta}")
            continue
        consulta, numero = coincidencia.groups()
        pagina = html.fromstring(ruta.read_text(encoding="utf-8"))
        superior = PAGINA.search(pagina.xpath('string(//*[@id="lblPaginacion"])'))
        inferior = PAGINA.search(pagina.xpath('string(//*[@id="lblPaginacion2"])'))
        tablas = pagina.xpath('//table[@id="tblResultados"]')
        if (not superior or not inferior or superior.groups() != inferior.groups()
                or int(superior[1]) != int(numero) or len(tablas) != 1):
            raise ValueError(f"Marcador o tabla inesperados en {ruta}")
        consultas[ruta.parent.name, consulta][int(numero)] = int(superior[2])

        for fila in tablas[0].xpath("./tbody/tr | ./tr"):
            celdas = fila.xpath('./td[@class="Datos2"]')
            if not celdas:
                continue
            if len(celdas) != 8:
                raise ValueError(f"Se esperaban ocho celdas de cotización en {ruta}")
            valores = tuple(" ".join(celda.text_content().split()) for celda in celdas)
            cotizaciones.setdefault(valores, ruta)
            total_filas += 1
    if not cotizaciones:
        raise ValueError(f"Sin cotizaciones en {bronce}")
    return consultas, cotizaciones, total_filas


def kilos(presentacion):
    if presentacion == "Kilogramo":
        return 1
    caja = CAJA.fullmatch(presentacion)
    if caja:
        return int(caja[1])
    raise ValueError("presentación sin peso explícito")


def precio_por_kg(textos, peso):
    if not all(PRECIO.fullmatch(texto) for texto in textos):
        raise ValueError("formato de precio inesperado")
    minimo, maximo, frecuente = (Decimal(texto.replace(",", "")) / peso for texto in textos)
    if not 0 < minimo <= frecuente <= maximo:
        raise ValueError("fuera del orden 0 < mínimo ≤ frecuente ≤ máximo")
    return frecuente


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bronce", type=Path, default=Path("data/bronce/sniim"))
    args = parser.parse_args()
    consultas, cotizaciones, total_filas = leer_capturas(args.bronce)
    print(f"Páginas: {sum(map(len, consultas.values()))}. Filas: {total_filas}. "
          f"Filas distintas: {len(cotizaciones)}. Repeticiones: {total_filas-len(cotizaciones)}.")
    completas = {}
    incompletas = []
    for (captura, consulta), paginas in consultas.items():
        totales = set(paginas.values())
        if len(totales) != 1:
            raise ValueError(f"Totales de páginas inconsistentes: {captura}/{consulta}")
        total = totales.pop()
        faltantes = sorted(set(range(1, total + 1)) - paginas.keys())
        if faltantes:
            incompletas.append((captura, consulta, len(paginas), total, faltantes))
        else:
            completas[consulta] = captura
    for captura, consulta, guardadas, total, faltantes in incompletas:
        posterior = completas.get(consulta, "")
        if posterior > captura:
            print(f"Consulta {captura}/{consulta} recuperada en {posterior}.")
        else:
            print(f"Consulta incompleta {captura}/{consulta}: {guardadas}/{total}. "
                  f"Faltan {', '.join(map(str, faltantes))}.")

    claves = Counter(fila[:4] for fila in cotizaciones)
    print(f"Claves con versiones distintas: {sum(n > 1 for n in claves.values())}.")
    fechas = set()
    semanas = defaultdict(set)
    rechazadas = 0
    for fila, ruta in cotizaciones.items():
        fecha, presentacion, origen, mercado, minimo, maximo, frecuente, _ = fila
        try:
            dia = datetime.strptime(fecha, "%d/%m/%Y").date()
            fechas.add(dia)
            precio_por_kg((minimo, maximo, frecuente), kilos(presentacion))
        except ValueError as error:
            rechazadas += 1
            print(f"Cotización inválida ({error}): {fila[:7]} [{ruta.as_posix()}]")
            continue
        semanas[mercado].add(dia - timedelta(days=dia.weekday()))
    print(f"Inválidas distintas: {rechazadas}.")
    if fechas:
        print(f"Fechas observadas: {len(fechas)} ({min(fechas)} a {max(fechas)}).")
    for mercado in MERCADOS:
        observadas = semanas[mercado]
        if not observadas:
            print(f"{mercado}: sin semanas observadas.")
            continue
        primera, ultima = min(observadas), max(observadas)
        semanas_calendario = (ultima - primera).days // 7 + 1
        sin_dato = semanas_calendario - len(observadas)
        print(f"{mercado}: {len(observadas)}/{semanas_calendario} semanas ({sin_dato} "
              f"sin dato), desde {primera} hasta {ultima} (lunes).")


if __name__ == "__main__":
    main()
