"""
POC: Styled diagram generation — different themes per diagram type for YouTube.

Generates the same 10 diagrams with distinct visual styles:
  - dark/neon for architecture & deployment (tech-heavy, impressive)
  - forest for data/verification flows (organic, pipeline feel)
  - warm for decision flows (approachable, workflow)
  - neutral for module structure (clean, engineering)
  - custom HTML for sequence & comparison (maximum control)
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from schemas.graph_schema import DiagramSpec
from schemas.sequence_schema import SequenceSpec, SequenceStep, Participant
from schemas.comparison_schema import ComparisonSpec
from renderers.mermaid_renderer import render_mermaid
from renderers.plantuml_renderer import render_plantuml_sequence
from renderers.comparison_renderer import render_comparison_html

from scenarios.all_scenarios import (
    SYSTEM_CONTEXT, HIGH_LEVEL_ARCHITECTURE, REQUEST_FLOW,
    SEQUENCE_AI_STREAMING, DATA_FLOW, MODULE_STRUCTURE,
    DEPLOYMENT, DECISION_FLOW, VERIFICATION_FLOW, BEFORE_AFTER,
)

THEMES_DIR = Path(__file__).parent / "themes"
OUTPUT_DIR = Path(__file__).parent / "output_styled"

# ── Theme assignment per diagram ────────────────────────────────────

STYLE_MAP: dict[str, dict] = {
    "01_system_context":     {"theme": "neon",    "css": "youtube-dark.css",  "bg": "#0f172a", "width": 1920},
    "02_architecture":       {"theme": "dark",    "css": "youtube-dark.css",  "bg": "#1e1e2e", "width": 1920},
    "03_request_flow":       {"theme": "neon",    "css": "youtube-dark.css",  "bg": "#0f172a", "width": 1920},
    "05_data_flow":          {"theme": "forest",  "css": "youtube-light.css", "bg": "white",   "width": 1920},
    "06_module_structure":   {"theme": "neutral", "css": "youtube-light.css", "bg": "white",   "width": 1920},
    "07_deployment":         {"theme": "dark",    "css": "youtube-dark.css",  "bg": "#1e1e2e", "width": 1920},
    "08_decision_flow":      {"theme": "warm",    "css": "youtube-light.css", "bg": "#fffbeb", "width": 1200},
    "09_verification_flow":  {"theme": "forest",  "css": "youtube-light.css", "bg": "white",   "width": 1920},
}


def export_themed_mermaid(mermaid_str: str, name: str, style: dict) -> bool:
    """Export Mermaid with a specific theme config and CSS."""
    out_dir = OUTPUT_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)

    mmd_path = out_dir / "diagram.mmd"
    png_path = out_dir / "diagram.png"
    mmd_path.write_text(mermaid_str)

    theme_config = THEMES_DIR / f"{style['theme']}.json"
    css_file = THEMES_DIR / style["css"]

    cmd = [
        "mmdc", "-i", str(mmd_path), "-o", str(png_path),
        "-e", "png", "-q",
        "-b", style.get("bg", "white"),
        "-w", str(style.get("width", 1200)),
        "-s", "2",  # 2x scale for high-res
    ]
    if theme_config.exists():
        cmd.extend(["-c", str(theme_config)])
    if css_file.exists():
        cmd.extend(["-C", str(css_file)])

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        print(f"  [error] {r.stderr.strip()[:200]}")
        return False
    return True


def generate_styled_sequence(data: dict) -> bool:
    """Generate a high-quality HTML-based sequence diagram."""
    out_dir = OUTPUT_DIR / "04_sequence"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Use PlantUML if available (better sequence diagrams)
    steps = []
    for s in data.get("steps", []):
        steps.append(SequenceStep(**s))

    spec = SequenceSpec(
        title=data["title"],
        participants=[Participant(**p) for p in data["participants"]],
        steps=steps,
    )

    puml = render_plantuml_sequence(spec)
    (out_dir / "diagram.puml").write_text(puml)

    # Try PlantUML with dark theme
    if shutil.which("plantuml"):
        # Create a themed version
        themed_puml = puml.replace(
            "@startuml",
            "@startuml\n!theme cyborg-outline\nskinparam backgroundColor #0f172a\n"
            "skinparam defaultFontColor #e2e8f0\n"
            "skinparam sequenceArrowColor #22d3ee\n"
            "skinparam sequenceLifeLineBorderColor #6366f1\n"
            "skinparam sequenceParticipantBorderColor #14b8a6\n"
            "skinparam sequenceParticipantBackgroundColor #1e293b\n"
            "skinparam noteBorderColor #6366f1\n"
            "skinparam noteBackgroundColor #1e293b\n"
            "skinparam sequenceBoxBorderColor #334155\n"
            "skinparam defaultFontName Inter\n"
            "skinparam defaultFontSize 14\n"
        )
        themed_path = out_dir / "diagram_dark.puml"
        themed_path.write_text(themed_puml)

        r = subprocess.run(
            ["plantuml", "-tpng", "-SdefaultFontSize=14", str(themed_path)],
            capture_output=True, text=True, timeout=30,
        )
        generated = themed_path.with_suffix(".png")
        if r.returncode == 0 and generated.exists():
            target = out_dir / "diagram.png"
            if generated != target:
                generated.rename(target)
            return True

    # Fallback: Mermaid sequence with dark theme
    from generate_all import _sequence_to_mermaid
    mermaid_seq = _sequence_to_mermaid(spec)
    return export_themed_mermaid(mermaid_seq, "04_sequence",
                                 {"theme": "dark", "css": "youtube-dark.css", "bg": "#1e1e2e", "width": 1200})


def generate_styled_comparison(data: dict) -> bool:
    """Generate a YouTube-quality dark comparison card."""
    out_dir = OUTPUT_DIR / "10_before_after"
    out_dir.mkdir(parents=True, exist_ok=True)

    spec = ComparisonSpec(**data)

    left_items = "\n".join(f'        <li>{item}</li>' for item in spec.left.items)
    right_items = "\n".join(f'        <li>{item}</li>' for item in spec.right.items)
    notes_list = "\n".join(f'        <li>{n}</li>' for n in spec.improvement_notes)

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Inter', system-ui, sans-serif; background: #0f172a; padding: 3rem; color: #e2e8f0; }}
    .container {{ max-width: 960px; margin: 0 auto; }}
    h1 {{ text-align: center; font-size: 2rem; font-weight: 800; margin-bottom: 2.5rem;
          background: linear-gradient(135deg, #22d3ee, #6366f1);
          -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .comparison {{ display: grid; grid-template-columns: 1fr 60px 1fr; gap: 0; align-items: stretch; }}
    .side {{ padding: 2rem; border-radius: 16px; backdrop-filter: blur(10px); }}
    .side h2 {{ font-size: 1.3rem; font-weight: 700; margin-bottom: 1.2rem; padding-bottom: 0.6rem; }}
    .side ul {{ list-style: none; }}
    .side li {{ padding: 0.7rem 0; font-size: 1rem; border-bottom: 1px solid rgba(255,255,255,0.06); }}
    .side li::before {{ display: inline-block; width: 1.8rem; font-weight: 700; }}
    .left {{ background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); }}
    .left h2 {{ color: #f87171; border-bottom: 2px solid #ef4444; }}
    .left li::before {{ content: "✗ "; color: #f87171; }}
    .right {{ background: rgba(34, 197, 94, 0.08); border: 1px solid rgba(34, 197, 94, 0.2); }}
    .right h2 {{ color: #4ade80; border-bottom: 2px solid #22c55e; }}
    .right li::before {{ content: "✓ "; color: #4ade80; }}
    .arrow {{ display: flex; align-items: center; justify-content: center; font-size: 2.5rem; color: #6366f1; }}
    .notes {{ margin-top: 2.5rem; padding: 1.8rem; border-radius: 16px;
              background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2);
              border-left: 4px solid #6366f1; }}
    .notes h3 {{ color: #a5b4fc; font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem; }}
    .notes ul {{ list-style: none; }}
    .notes li {{ font-size: 0.95rem; padding: 0.4rem 0; color: #94a3b8; }}
    .notes li::before {{ content: "→ "; color: #6366f1; font-weight: 700; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>{spec.title}</h1>
    <div class="comparison">
      <div class="side left">
        <h2>{spec.left.title}</h2>
        <ul>
{left_items}
        </ul>
      </div>
      <div class="arrow">→</div>
      <div class="side right">
        <h2>{spec.right.title}</h2>
        <ul>
{right_items}
        </ul>
      </div>
    </div>
    <div class="notes">
      <h3>Key Improvements</h3>
      <ul>
{notes_list}
      </ul>
    </div>
  </div>
</body>
</html>"""

    html_path = out_dir / "diagram.html"
    html_path.write_text(html)

    # Render to PNG via puppeteer
    png_path = out_dir / "diagram.png"
    script = f"""
let puppeteer;
try {{ puppeteer = require('puppeteer'); }} catch {{
  const {{ execSync }} = require('child_process');
  const p = execSync('which mmdc').toString().trim();
  const base = require('path').resolve(p, '../../lib/node_modules/@mermaid-js/mermaid-cli/node_modules/puppeteer');
  puppeteer = require(base);
}}
(async () => {{
  const browser = await puppeteer.launch({{headless: 'new'}});
  const page = await browser.newPage();
  await page.setViewport({{width: 1000, height: 800, deviceScaleFactor: 2}});
  await page.goto('file://{html_path.absolute()}');
  await page.screenshot({{path: '{png_path.absolute()}', fullPage: true}});
  await browser.close();
}})();
"""
    script_path = out_dir / "_render.cjs"
    script_path.write_text(script)
    try:
        r = subprocess.run(["node", str(script_path)], capture_output=True, text=True, timeout=30)
        return r.returncode == 0 and png_path.exists()
    finally:
        script_path.unlink(missing_ok=True)


def main() -> None:
    if not shutil.which("mmdc"):
        print("mmdc not found")
        return

    results: list[tuple[str, bool]] = []

    # Graph-based diagrams with themed styles
    GRAPH_SCENARIOS = {
        "01_system_context": SYSTEM_CONTEXT,
        "02_architecture": HIGH_LEVEL_ARCHITECTURE,
        "03_request_flow": REQUEST_FLOW,
        "05_data_flow": DATA_FLOW,
        "06_module_structure": MODULE_STRUCTURE,
        "07_deployment": DEPLOYMENT,
        "08_decision_flow": DECISION_FLOW,
        "09_verification_flow": VERIFICATION_FLOW,
    }

    for name, data in GRAPH_SCENARIOS.items():
        style = STYLE_MAP[name]
        spec = DiagramSpec(**data)
        mermaid = render_mermaid(spec)
        ok = export_themed_mermaid(mermaid, name, style)
        icon = "✓" if ok else "✗"
        theme_label = f"{style['theme']}+{style['css'].split('.')[0]}"
        print(f"  {icon} {name:30s} [{theme_label:25s}] {spec.title}")
        results.append((name, ok))

    # Sequence diagram
    ok = generate_styled_sequence(SEQUENCE_AI_STREAMING)
    print(f"  {'✓' if ok else '✗'} {'04_sequence':30s} {'[plantuml-dark]':27s} {SEQUENCE_AI_STREAMING['title']}")
    results.append(("04_sequence", ok))

    # Before/After comparison
    ok = generate_styled_comparison(BEFORE_AFTER)
    print(f"  {'✓' if ok else '✗'} {'10_before_after':30s} {'[html-dark-glassmorphism]':27s} {BEFORE_AFTER['title']}")
    results.append(("10_before_after", ok))

    # Summary
    passed = sum(1 for _, ok in results if ok)
    print(f"\n  {passed}/{len(results)} styled diagrams generated → {OUTPUT_DIR.absolute()}")


if __name__ == "__main__":
    main()
