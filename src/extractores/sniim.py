"""Extractor Bronce: precios mayoristas de Aguacate Hass - Primera (SNIIM).

Automatiza el formulario publico del SNIIM con un navegador (Playwright), igual que una
consulta manual: elige producto y fechas, presiona Consultar y guarda el HTML crudo de
cada pagina de resultados en data/bronce/sniim/.

Variables de entorno opcionales:
  SNIIM_DESDE  fecha inicial AAAA-MM-DD (por defecto: hoy - 60 dias)
  SNIIM_HASTA  fecha final   AAAA-MM-DD (por defecto: hoy)
  SNIIM_HEADED 1 para ver el navegador (depuracion local)

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

from playwright.sync_api import sync_playwright

BASE = "https://www.economia-sniim.gob.mx"
FORM = (BASE + "/nuevo/Consultas/MercadosNacionales/PreciosDeMercado/"
        "Agricolas/ConsultaFrutasYHortalizas.aspx?SubOpcion=4")
UA = "TrustedDataLab-Aguacate/0.1 (proyecto academico)"
PRODUCTO = "133"   # Aguacate Hass - Primera
PAUSA = 3          # segundos entre acciones (trato amable al sitio)
VENTANA_DIAS = 180
RE_PAG = re.compile(r"P[áa]gina\s+(\d+)\s+de\s+(\d+)", re.I)
SIGUIENTE = [
    "[id*='iguiente' i]", "[id*='next' i]", "[id*='adelante' i]",
    "[alt*='iguiente' i]", "[title*='iguiente' i]", "[alt*='next' i]",
    "[id*='Sig' i]",
]


def robots_ok(out):
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(BASE + "/robots.txt")
    rp.read()
    import requests
    txt = requests.get(BASE + "/robots.txt", headers={"User-Agent": UA}, timeout=30).text
    (out / "robots.txt").write_text(txt, encoding="utf-8")
    return rp.can_fetch(UA, FORM)


def ventanas(desde, hasta):
    ini = desde
    while ini <= hasta:
        fin = min(ini + dt.timedelta(days=VENTANA_DIAS - 1), hasta)
        yield ini, fin
        ini = fin + dt.timedelta(days=1)


def pagina_actual(page):
    m = RE_PAG.search(page.inner_text("body"))
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


EXCLUIR = re.compile(r"regresar|home|buscar|menuencabezado|calendario|excel|imprimir", re.I)
PREFERIR = re.compile(r"sig|next|adel|forward|der", re.I)


def info(e):
    return e.evaluate(
        "e => ({tag:e.tagName, id:e.id, name:e.name||'', alt:e.alt||'', "
        "title:e.title||'', src:e.src||'', href:e.href||''})")


def candidatos(page):
    loc = page.locator("input[type=image], a:has(img), img[onclick]")
    res = []
    for i in range(loc.count()):
        e = loc.nth(i)
        try:
            if not e.is_visible():
                continue
            d = info(e)
        except Exception:
            continue
        texto = " ".join(str(v) for v in d.values())
        if EXCLUIR.search(texto):
            continue
        res.append((i, e, d, texto))
    return res


def avanzar(page, n, out):
    """Intenta pasar a la pagina n+1 probando candidatos; devuelve el nuevo numero o None."""
    cands = candidatos(page)
    pref = [c for c in cands if PREFERIR.search(c[3])]
    resto = [c for c in reversed(cands) if c not in pref]
    for _, e, d, _t in pref + resto:
        try:
            e.click()
            page.wait_for_function(
                "n => new RegExp('P[áa]gina\\\\s+' + n + '\\\\s+de', 'i').test(document.body.innerText)",
                arg=n + 1, timeout=10000)
            page.wait_for_load_state("networkidle")
            print(f"  avance con: {d}")
            return n + 1
        except Exception:
            if pagina_actual(page)[0] is None:
                print("  se salio de los resultados; se detiene")
                return None
            continue
    (out / "depuracion_paginacion.txt").write_text(
        "\n".join(str(c[2]) for c in cands), encoding="utf-8")
    return None


def volcar_depuracion(page, ruta):
    filas = []
    for sel in ("input[type=image]", "a", "img"):
        loc = page.locator(sel)
        for i in range(min(loc.count(), 80)):
            e = loc.nth(i)
            filas.append(sel + " " + str(e.evaluate(
                "e => ({id:e.id,name:e.name,alt:e.alt,title:e.title,src:e.src,href:e.href})")))
    ruta.write_text("\n".join(filas), encoding="utf-8")


def consultar(page, ini, fin, out, hoy):
    page.goto(FORM, wait_until="domcontentloaded")
    page.wait_for_selector("#ddlProducto")
    for sel, val in (("#ddlProducto", PRODUCTO), ("#ddlOrigen", "-1"),
                     ("#ddlDestino", "-1"), ("#ddlPrecios", "1")):
        page.select_option(sel, val)
        page.wait_for_load_state("networkidle")
    for sel, d in (("#txtFechaInicio", ini), ("#txtFechaFinal", fin)):
        page.eval_on_selector(sel, "(e, v) => { e.value = v; }", d.strftime("%d/%m/%Y"))
    time.sleep(PAUSA)
    page.click("#btnBuscar")
    page.wait_for_load_state("networkidle")

    n, total = pagina_actual(page)
    if n is None:
        (out / f"sin_resultados_{ini}_{fin}.html").write_text(page.content(), encoding="utf-8")
        print(f"[{ini} a {fin}] sin paginacion detectada (guardado para revision)")
        return 0
    guardadas = 0
    while True:
        nombre = f"aguacate_hass_primera_{ini}_{fin}_p{n:02d}.html"
        (out / nombre).write_text(page.content(), encoding="utf-8")
        guardadas += 1
        print(f"[{ini} a {fin}] pagina {n} de {total}")
        if n >= total:
            break
        time.sleep(PAUSA)
        nuevo = avanzar(page, n, out)
        if nuevo is None:
            print("No pude avanzar de pagina; revisa depuracion_paginacion.txt")
            break
        n = nuevo
    return guardadas


def main():
    hoy = dt.date.today()
    hasta = dt.date.fromisoformat(os.environ.get("SNIIM_HASTA", hoy.isoformat()))
    desde = dt.date.fromisoformat(
        os.environ.get("SNIIM_DESDE", (hoy - dt.timedelta(days=60)).isoformat()))
    out = pathlib.Path("data/bronce/sniim") / hoy.isoformat()
    out.mkdir(parents=True, exist_ok=True)
    if not robots_ok(out):
        print("robots.txt NO permite esta ruta. Se detiene.")
        return 1
    total = 0
    with sync_playwright() as p:
        b = p.chromium.launch(headless=os.environ.get("SNIIM_HEADED") != "1")
        ctx = b.new_context(user_agent=UA)
        page = ctx.new_page()
        page.set_default_timeout(60000)
        for ini, fin in ventanas(desde, hasta):
            total += consultar(page, ini, fin, out, hoy)
        b.close()
    print(f"OK sniim: {total} paginas guardadas en {out}")
    return 0 if total else 1


if __name__ == "__main__":
    sys.exit(main())