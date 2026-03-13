"""
Unified image exporter.
  Mermaid → SVG/PNG  (via mmdc)
  PlantUML → SVG/PNG (via plantuml jar or picoweb)
  HTML → PNG         (via puppeteer/playwright)
"""

from __future__ import annotations

import base64
import shutil
import subprocess
from pathlib import Path


def export_mermaid_png(mermaid_str: str, output_path: str) -> bool:
    """Export Mermaid string to PNG via mmdc."""
    if not shutil.which("mmdc"):
        print("  [skip] mmdc not found")
        return False

    out = Path(output_path)
    tmp = out.with_name(out.stem + "_tmp.mmd")
    tmp.write_text(mermaid_str)
    try:
        r = subprocess.run(
            ["mmdc", "-i", str(tmp), "-o", str(out), "-e", "png", "-q",
             "-b", "white", "-w", "1200"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0:
            print(f"  [mmdc error] {r.stderr.strip()}")
        return r.returncode == 0
    finally:
        tmp.unlink(missing_ok=True)


def export_mermaid_svg(mermaid_str: str, output_path: str) -> bool:
    """Export Mermaid string to SVG via mmdc."""
    if not shutil.which("mmdc"):
        return False

    out = Path(output_path)
    tmp = out.with_name(out.stem + "_tmp.mmd")
    tmp.write_text(mermaid_str)
    try:
        r = subprocess.run(
            ["mmdc", "-i", str(tmp), "-o", str(out), "-e", "svg", "-q"],
            capture_output=True, text=True, timeout=30,
        )
        return r.returncode == 0
    finally:
        tmp.unlink(missing_ok=True)


def export_plantuml_png(puml_str: str, output_path: str) -> bool:
    """
    Export PlantUML string to PNG.
    Tries: 1) plantuml CLI  2) plantuml picoweb  3) write .puml only
    """
    out = Path(output_path)
    puml_path = out.with_suffix(".puml")
    puml_path.write_text(puml_str)

    # Try plantuml jar
    if shutil.which("plantuml"):
        r = subprocess.run(
            ["plantuml", "-tpng", str(puml_path)],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0:
            generated = puml_path.with_suffix(".png")
            if generated.exists() and generated != out:
                generated.rename(out)
            return True

    # Try java -jar plantuml.jar
    jar_path = Path.home() / "plantuml.jar"
    if jar_path.exists() and shutil.which("java"):
        r = subprocess.run(
            ["java", "-jar", str(jar_path), "-tpng", str(puml_path)],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode == 0:
            generated = puml_path.with_suffix(".png")
            if generated.exists() and generated != out:
                generated.rename(out)
            return True

    print(f"  [skip] plantuml not found, wrote {puml_path}")
    return False


def export_html_to_png(html_str: str, output_path: str) -> bool:
    """
    Export HTML to PNG via puppeteer/playwright.
    Falls back to writing HTML only.
    """
    out = Path(output_path)
    html_path = out.with_suffix(".html")
    html_path.write_text(html_str)

    if shutil.which("node"):
        # Find puppeteer from mmdc's dependencies or global
        script = f"""
let puppeteer;
try {{ puppeteer = require('puppeteer'); }} catch {{
  const {{ execSync }} = require('child_process');
  const mmdc_path = execSync('which mmdc').toString().trim();
  const base = require('path').resolve(mmdc_path, '../../lib/node_modules/@mermaid-js/mermaid-cli/node_modules/puppeteer');
  puppeteer = require(base);
}}
(async () => {{
  const browser = await puppeteer.launch({{headless: 'new'}});
  const page = await browser.newPage();
  await page.setViewport({{width: 1000, height: 700}});
  await page.goto('file://{html_path.absolute()}');
  await page.screenshot({{path: '{out.absolute()}', fullPage: true}});
  await browser.close();
}})();
"""
        script_path = out.with_suffix(".cjs")
        script_path.write_text(script)
        try:
            r = subprocess.run(
                ["node", str(script_path)],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode == 0 and out.exists():
                return True
        finally:
            script_path.unlink(missing_ok=True)

    print(f"  [skip] puppeteer not found, wrote {html_path}")
    return False
