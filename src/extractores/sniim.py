"""Extractor Bronce: precios mayoristas de Aguacate Hass - Primera (SNIIM).

Automatiza el formulario publico del SNIIM con un navegador (Playwright), igual que una
consulta manual: elige producto y fechas, presiona Consultar y guarda el HTML crudo de
cada pagina de resultados en data/bronce/sniim/.

Variables de entorno opcionales:
  SNIIM_DESDE  fecha inicial AAAA-MM-DD (por defecto: hoy - 60 dias)
  SNIIM_HASTA  fecha final   AAAA-MM-DD (por defecto: hoy)
  SNIIM_HEADED 1 para ver el navegador (depuracion local)
  SNIIM_BROWSER_CHANNEL canal de Playwright opcional, por ejemplo msedge

Carga historica inicial (una vez, en tu compu):
  SNIIM_DESDE=2023-11-09 python src/extractores/sniim.py
"""
import datetime as dt
import os
import pathlib
import re
import sys
import time
import urllib.robotparser

import requests
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

BASE = "https://www.economia-sniim.gob.mx"
FORM = (BASE + "/nuevo/Consultas/MercadosNacionales/PreciosDeMercado/"
        "Agricolas/ConsultaFrutasYHortalizas.aspx?SubOpcion=4")
UA = "TrustedDataLab-Aguacate/0.1 (proyecto academico)"
PRODUCTO = "133"   # Aguacate Hass - Primera
PAUSA = 3          # segundos entre acciones (trato amable al sitio)
VENTANA_DIAS = 180
RE_PAG = re.compile(r"P[áa]gina\s+(\d+)\s+de\s+(\d+)", re.I)


class ConsultaIncompleta(RuntimeError):
    """No se pudo verificar la secuencia completa de resultados."""


def robots_ok(out):
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(BASE + "/robots.txt")
    respuesta = requests.get(rp.url, headers={"User-Agent": UA}, timeout=30)
    respuesta.raise_for_status()
    txt = respuesta.text
    rp.parse(txt.splitlines())
    (out / "robots.txt").write_text(txt, encoding="utf-8")
    return rp.can_fetch(UA, FORM)


def ventanas(desde, hasta):
    ini = desde
    while ini <= hasta:
        fin = min(ini + dt.timedelta(days=VENTANA_DIAS - 1), hasta)
        yield ini, fin
        ini = fin + dt.timedelta(days=1)


def pagina_actual(page, selector="#lblPaginacion"):
    marcador = page.locator(selector)
    m = RE_PAG.search(marcador.inner_text()) if marcador.count() else None
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def guardar_paginas(page, ini, fin, out):
    n, total = pagina_actual(page)
    if n != 1 or not total or total < 1:
        raise ConsultaIncompleta("SNIIM no confirmó la primera página de resultados")

    paginas = []
    for esperada in range(1, total + 1):
        if esperada > 1:
            time.sleep(PAUSA)
            try:
                page.locator("#ibtnSiguiente").click(timeout=15000, no_wait_after=True)
                page.wait_for_function(
                    r"""n => new RegExp('P[áa]gina\\s+' + n + '\\s+de', 'i')
                        .test(document.querySelector('#lblPaginacion')?.textContent || '')""",
                    arg=esperada,
                    timeout=15000,
                )
            except PlaywrightError as error:
                raise ConsultaIncompleta(
                    f"se verificaron {len(paginas)}/{total} páginas. "
                    f"No se pudo llegar a la página {esperada}"
                ) from error
        actual = pagina_actual(page)
        # La navegación inferior aparece después de la tabla. Chromium puede
        # reconstruir etiquetas de cierre aunque la respuesta llegue cortada.
        inferior = pagina_actual(page, "#lblPaginacion2")
        if (actual != (esperada, total) or inferior != actual
                or page.locator("#tblResultados").count() != 1):
            raise ConsultaIncompleta(
                f"se verificaron {len(paginas)}/{total} páginas. "
                f"Marcadores o tabla incompletos en la página {esperada}: "
                f"superior={actual}, inferior={inferior}"
            )
        paginas.append(page.content())
        print(f"[{ini} a {fin}] página {esperada} de {total}", flush=True)

    prefijo = f"aguacate_hass_primera_{ini}_{fin}_p"
    escritas = set()
    for numero, contenido in enumerate(paginas, start=1):
        ruta = out / f"{prefijo}{numero:02d}.html"
        ruta.write_text(contenido, encoding="utf-8")
        escritas.add(ruta)
    for ruta in set(out.glob(f"{prefijo}*.html")) - escritas:
        ruta.unlink()
    return total


def consultar(page, ini, fin, out):
    page.goto(FORM, wait_until="domcontentloaded")
    page.wait_for_selector("#ddlProducto")
    for sel, val in (("#ddlProducto", PRODUCTO), ("#ddlOrigen", "-1"),
                     ("#ddlDestino", "-1"), ("#ddlPrecios", "1")):
        page.select_option(sel, val)
        page.wait_for_load_state("networkidle")
    for sel, d in (("#txtFechaInicio", ini), ("#txtFechaFinal", fin)):
        page.eval_on_selector(sel, "(e, v) => { e.value = v; }", d.strftime("%d/%m/%Y"))
    time.sleep(PAUSA)
    page.locator("#btnBuscar").click(no_wait_after=True)
    page.locator("#lblPaginacion").wait_for(state="visible")

    return guardar_paginas(page, ini, fin, out)


def main():
    hoy = dt.date.today()
    hasta = dt.date.fromisoformat(os.environ.get("SNIIM_HASTA", hoy.isoformat()))
    desde = dt.date.fromisoformat(
        os.environ.get("SNIIM_DESDE", (hoy - dt.timedelta(days=60)).isoformat()))
    if desde > hasta:
        print("SNIIM_DESDE debe ser anterior o igual a SNIIM_HASTA", file=sys.stderr)
        return 1
    out = pathlib.Path("data/bronce/sniim") / hoy.isoformat()
    out.mkdir(parents=True, exist_ok=True)
    if not robots_ok(out):
        print("robots.txt NO permite esta ruta. Se detiene.")
        return 1
    total = 0
    incompletas = 0
    with sync_playwright() as p:
        b = p.chromium.launch(
            headless=os.environ.get("SNIIM_HEADED") != "1",
            channel=os.environ.get("SNIIM_BROWSER_CHANNEL") or None,
        )
        ctx = b.new_context(user_agent=UA)
        page = ctx.new_page()
        page.set_default_timeout(60000)
        for ini, fin in ventanas(desde, hasta):
            try:
                total += consultar(page, ini, fin, out)
            except (ConsultaIncompleta, PlaywrightError) as error:
                incompletas += 1
                print(f"Consulta incompleta [{ini} a {fin}]: {error}", file=sys.stderr)
        b.close()
    if incompletas:
        print(f"SNIIM: {incompletas} ventanas incompletas y {total} páginas "
              "de ventanas completas", file=sys.stderr)
        return 1
    print(f"OK sniim: {total} paginas guardadas en {out}")
    return 0 if total else 1


if __name__ == "__main__":
    sys.exit(main())
