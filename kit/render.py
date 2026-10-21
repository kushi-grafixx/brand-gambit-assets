"""Render a Brand Gambit HTML frame to PNG.

Usage:
  python3 render.py <template.html> <out.png> [KEY=VALUE ...]

Placeholders like {{KEY}} in the template are replaced with the values given.
The element with id="frame" is screenshotted at 1200px wide (2x a 600px email column).
"""
import sys, pathlib, tempfile
from playwright.sync_api import sync_playwright

def render(template, out, subs):
    tpl = pathlib.Path(template).resolve()
    html = tpl.read_text()
    for k, v in subs.items():
        html = html.replace("{{" + k + "}}", v)
    # write next to the template so relative asset paths resolve
    tmp = tpl.parent / f".render_{pathlib.Path(out).stem}.html"
    tmp.write_text(html)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 1200, "height": 800}, device_scale_factor=1)
            pg.goto(tmp.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(250)
            left = pg.evaluate("[...document.body.innerHTML.matchAll(/\\{\\{[A-Z_]+\\}\\}/g)].map(m=>m[0])")
            if left:
                raise SystemExit(f"Unfilled placeholders: {sorted(set(left))}")
            pg.locator("#frame").screenshot(path=out)
            b.close()
    finally:
        tmp.unlink(missing_ok=True)

if __name__ == "__main__":
    template, out, *pairs = sys.argv[1:]
    subs = dict(p.split("=", 1) for p in pairs)
    render(template, out, subs)
    print("wrote", out)
