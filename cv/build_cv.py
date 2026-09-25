#!/usr/bin/env python3
"""Build the public web-edition CV (English + Greek) as PDFs.

Usage:  python3 build_cv.py [output_dir]
Needs:  playwright (Chromium) and network access to Google Fonts.
Content lives in cv_data.py; edit it there and rebuild.
"""
import sys, pathlib
from playwright.sync_api import sync_playwright
from cv_data import CV

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE
FILES = {"en": "Nikos-Kalogerinis-CV-EN.pdf", "el": "Nikos-Kalogerinis-CV-GR.pdf"}
ACCENTS = ["var(--sun)", "var(--bloom)", "var(--mint)", "var(--cobalt)", "var(--sun)"]

CSS = """
:root { --cobalt:#2438E8; --sun:#FFC926; --bloom:#FF3D8B; --mint:#3DDC97; --ink:#14123A; --paper:#fff; --muted:#4a4870; }
@page { size: A4; margin: 14mm 15mm 17mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: "Commissioner", system-ui, sans-serif; color: var(--ink); font-size: 9.3pt; line-height: 1.42; }
.head {
  position: relative; overflow: hidden;
  background: var(--cobalt); color: var(--paper);
  border-radius: 7mm 7mm 7mm 1.5mm;
  padding: 9mm 10mm 8mm;
  margin-bottom: 7mm;
}
.head::before {
  content: ""; position: absolute; width: 62mm; height: 62mm; right: -16mm; top: -24mm; border-radius: 50%;
  background: radial-gradient(circle at 38% 36%, #FFFBE6 0%, #FFE680 18%, var(--sun) 45%, #FFA51F 80%, #FF8A1F 100%);
  box-shadow: 0 0 14mm 5mm rgba(255,214,90,.45);
}
.head h1 { position: relative; margin: 0; font-size: 27pt; font-weight: 900; letter-spacing: -.02em; line-height: 1; }
.head .role { position: relative; margin-top: 2.5mm; font-size: 11.5pt; font-weight: 500; }
.head .links { position: relative; margin-top: 4mm; display: flex; flex-wrap: wrap; gap: 2mm; }
.head .links span { background: var(--ink); color: var(--paper); border-radius: 99px; padding: .6mm 3.2mm; font-size: 8.5pt; font-weight: 700; }
h2 {
  display: flex; align-items: center; gap: 2.5mm;
  margin: 6mm 0 3mm; font-size: 13.5pt; font-weight: 900; letter-spacing: -.01em;
  break-after: avoid;
}
h2::before { content: ""; width: 7mm; height: 3.2mm; border-radius: 99px; background: var(--accent); }
.entry { display: grid; grid-template-columns: 37mm 1fr; gap: 4mm; margin-bottom: 3.6mm; break-inside: avoid; }
.when { font-weight: 700; font-size: 8.6pt; color: var(--cobalt); padding-top: .4mm; }
.org { font-weight: 700; font-size: 10.2pt; }
.pos { color: var(--muted); font-weight: 500; font-size: 8.8pt; margin-bottom: .6mm; }
.desc { margin: 0; }
ul { margin: 1mm 0 0; padding-left: 4mm; }
li { margin: .5mm 0; }
li::marker { color: var(--bloom); }
.extra { display: grid; grid-template-columns: 1fr 1fr; gap: 2.5mm 6mm; }
.extra div { break-inside: avoid; }
.extra b { display: block; font-size: 9.6pt; }
"""

FOOTER = """<div style="width:100%;font-family:sans-serif;font-size:7.5px;color:#6b6990;padding:0 15mm;display:flex;justify-content:space-between">
<span>{footer}</span><span>{page} <span class="pageNumber"></span> {of} <span class="totalPages"></span></span></div>"""


def build_html(d):
    out = [f'<!DOCTYPE html><html lang="{d["lang"]}"><head><meta charset="utf-8"><title>{d["title"]}</title>',
           '<link href="https://fonts.googleapis.com/css2?family=Commissioner:wght@400;500;700;900&display=swap" rel="stylesheet">',
           f'<style>{CSS}</style></head><body>',
           f'<header class="head"><h1>{d["name"]}</h1><div class="role">{d["role"]} · {d["place"]}</div>',
           '<div class="links">' + "".join(f"<span>{l}</span>" for l in d["links"]) + "</div></header>"]
    out.append(f'<section style="--accent:{ACCENTS[0]}"><h2>{d["extra_title"]}</h2><div class="extra">')
    out += [f"<div><b>{k}</b>{v}</div>" for k, v in d["extra"]]
    out.append("</div></section>")
    for i, (title, entries) in enumerate(d["sections"]):
        out.append(f'<section style="--accent:{ACCENTS[i + 1]}"><h2>{title}</h2>')
        for when, org, pos, desc, bullets in entries:
            out.append(f'<div class="entry"><div class="when">{when}</div><div><div class="org">{org}</div>'
                       f'<div class="pos">{pos}</div><p class="desc">{desc}</p>')
            if bullets:
                out.append("<ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>")
            out.append("</div></div>")
        out.append("</section>")
    out.append("</body></html>")
    return "".join(out)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for lang, d in CV.items():
            page = browser.new_page()
            page.set_content(build_html(d), wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            page.pdf(path=str(OUT / FILES[lang]), format="A4", print_background=True, prefer_css_page_size=True,
                     display_header_footer=True, header_template="<span></span>",
                     footer_template=FOOTER.format(**d))
            print("wrote", OUT / FILES[lang])
        browser.close()


if __name__ == "__main__":
    main()
