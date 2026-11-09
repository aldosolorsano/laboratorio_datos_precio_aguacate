"""Herramienta de una sola vez: abre el formulario del SNIIM y escribe en
sniim_inspeccion.txt los campos (ids, nombres, opciones) y los frames de la pagina.
Con ese archivo se escribe el extractor automatico exacto.

Uso:
  pip install playwright
  playwright install chromium
  python tools/inspeccionar_sniim.py
"""
from playwright.sync_api import sync_playwright

URL = ("https://www.economia-sniim.gob.mx/nuevo/Home.aspx?opcion=Consultas/"
       "MercadosNacionales/PreciosDeMercado/Agricolas/ConsultaFrutasYHortalizas.aspx?SubOpcion=4|0")

JS = """
() => {
  const out = [];
  document.querySelectorAll('select').forEach(s => out.push({
    tag:'select', id:s.id, name:s.name,
    options:[...s.options].slice(0,80).map(o => o.value + ' | ' + o.text.trim())}));
  document.querySelectorAll('input, button').forEach(i => out.push({
    tag:i.tagName.toLowerCase(), id:i.id, name:i.name, type:i.type, value:(i.value||'').slice(0,40)}));
  document.querySelectorAll('form').forEach(f => out.push({tag:'form', action:f.action, method:f.method}));
  return out;
}
"""

with sync_playwright() as p:
    b = p.chromium.launch(headless=False)
    page = b.new_page()
    page.goto(URL, wait_until="networkidle")
    page.wait_for_timeout(3000)
    lines = []
    for i, fr in enumerate(page.frames):
        lines.append(f"=== FRAME {i}: {fr.url}")
        try:
            for e in fr.evaluate(JS):
                lines.append(str(e))
        except Exception as ex:
            lines.append(f"(error: {ex})")
    open("sniim_inspeccion.txt", "w", encoding="utf-8").write("\n".join(lines))
    print("Listo: revisa sniim_inspeccion.txt")
    b.close()
