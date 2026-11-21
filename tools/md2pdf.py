#!/usr/bin/env python3
"""Markdown -> PDF via python-markdown + headless Chrome.

Handles CJK, tables, fenced code, box-drawing, and relative images.

    tools/md2pdf.py REPORT.zh.md
    tools/md2pdf.py REPORT.md -o out.pdf

Requires: python3-markdown and Google Chrome or Chromium on PATH.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

import markdown

CSS = """
@page { size: A4; margin: 18mm 16mm; }
body {
  font-family: "Noto Sans CJK SC","Noto Serif CJK SC","Noto Sans",sans-serif;
  font-size: 11pt; line-height: 1.55; color: #1b1b1b; max-width: 100%;
}
h1 { font-size: 20pt; } h2 { font-size: 15pt; margin-top: 1.4em; border-bottom: 1px solid #ddd; padding-bottom: .2em; }
h3 { font-size: 12.5pt; }
code { font-family: "DejaVu Sans Mono","Noto Sans Mono CJK SC","Noto Sans CJK SC",monospace;
       font-size: 9.5pt; background: #f3f3f3; padding: .1em .3em; border-radius: 3px; }
pre { background: #f6f8fa; padding: 10px 12px; border-radius: 6px; overflow: visible;
      white-space: pre-wrap; word-break: break-word; page-break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 9pt; line-height: 1.4; }
table { border-collapse: collapse; width: 100%; font-size: 10pt; page-break-inside: avoid; }
th, td { border: 1px solid #ccc; padding: 5px 8px; text-align: left; vertical-align: top; }
th { background: #f0f0f0; }
img { max-width: 100%; }
a { color: #0b57d0; text-decoration: none; }
"""


def find_chrome():
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        p = shutil.which(name)
        if p:
            return p
    sys.exit("error: Google Chrome / Chromium not found on PATH")


def render(md_path, out_path):
    md_path = os.path.abspath(md_path)
    base = os.path.dirname(md_path)
    with open(md_path, encoding="utf-8") as f:
        body = markdown.markdown(
            f.read(),
            extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
        )
    html = (
        '<!doctype html><html><head><meta charset="utf-8">'
        f'<base href="file://{base}/">'
        f"<style>{CSS}</style></head><body>{body}</body></html>"
    )
    chrome = find_chrome()
    with tempfile.TemporaryDirectory() as tmp:
        html_path = os.path.join(tmp, "doc.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        cmd = [
            chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--allow-file-access-from-files", "--no-pdf-header-footer",
            "--virtual-time-budget=15000",
            f"--print-to-pdf={os.path.abspath(out_path)}",
            f"file://{html_path}",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(out_path):
            sys.exit(f"chrome failed ({r.returncode}):\n{r.stderr}")
    print(f"wrote {out_path}")


def main():
    ap = argparse.ArgumentParser(description="Markdown -> PDF")
    ap.add_argument("input", help="input .md")
    ap.add_argument("-o", "--output", help="output .pdf (default: input with .pdf)")
    a = ap.parse_args()
    out = a.output or os.path.splitext(a.input)[0] + ".pdf"
    render(a.input, out)


if __name__ == "__main__":
    main()
