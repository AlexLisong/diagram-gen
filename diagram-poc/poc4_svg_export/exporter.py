"""
POC 4: Mermaid → SVG/PNG export.
Two strategies:
  A) mermaid-cli (mmdc) — Node.js tool, headless browser
  B) mermaid.ink API — HTTP-based, no install needed

This POC tests both paths.
"""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, "..")


def export_via_mmdc(mermaid_str: str, output_path: str, fmt: str = "svg") -> bool:
    """
    Export using mermaid-cli (mmdc).
    Requires: npm install -g @mermaid-js/mermaid-cli
    """
    if not shutil.which("mmdc"):
        print("⚠ mmdc not found. Install with: npm install -g @mermaid-js/mermaid-cli")
        return False

    tmp_input = Path(output_path).with_suffix(".mmd")
    tmp_input.write_text(mermaid_str)

    try:
        result = subprocess.run(
            ["mmdc", "-i", str(tmp_input), "-o", output_path, "-e", fmt, "-q"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            print(f"✓ Exported to {output_path}")
            return True
        else:
            print(f"✗ mmdc error: {result.stderr}")
            return False
    finally:
        tmp_input.unlink(missing_ok=True)


def get_mermaid_ink_url(mermaid_str: str, fmt: str = "svg") -> str:
    """
    Generate a mermaid.ink URL for rendering.
    This is a free public service — good for POC, not for production.
    """
    encoded = base64.urlsafe_b64encode(mermaid_str.encode()).decode()
    return f"https://mermaid.ink/{fmt}/{encoded}"


def export_to_html_preview(mermaid_str: str, output_path: str) -> None:
    """
    Generate a standalone HTML file with Mermaid JS for browser preview.
    No external tools needed.
    """
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Diagram Preview</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
  <style>
    body {{ font-family: system-ui; padding: 2rem; background: #f5f5f5; }}
    .mermaid {{ background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    h1 {{ color: #333; font-size: 1.2rem; }}
  </style>
</head>
<body>
  <h1>Diagram Preview</h1>
  <div class="mermaid">
{mermaid_str}
  </div>
  <script>mermaid.initialize({{ startOnLoad: true, theme: 'default' }});</script>
</body>
</html>"""
    Path(output_path).write_text(html)
    print(f"✓ HTML preview written to {output_path}")


# ── Demo ────────────────────────────────────────────────────────────

SAMPLE_MERMAID = """flowchart LR
  subgraph client[Client Layer]
    user(User)
    frontend(React Frontend)
  end

  subgraph backend[Backend Layer]
    api[C# Backend]
    ai[Python AI Service]
  end

  subgraph data[Data Layer]
    db[(SQL Server)]
    redis[(Redis Cache)]
  end

  user -->|Browser| frontend
  frontend -->|REST API| api
  api -->|AI Request| ai
  ai -.->|SSE Stream| frontend
  api -->|SQL| db
  api -->|Cache| redis
"""


if __name__ == "__main__":
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)

    # Strategy A: mmdc
    print("=== Strategy A: mermaid-cli (mmdc) ===")
    export_via_mmdc(SAMPLE_MERMAID, str(out_dir / "diagram.svg"), "svg")
    export_via_mmdc(SAMPLE_MERMAID, str(out_dir / "diagram.png"), "png")

    # Strategy B: mermaid.ink URL
    print("\n=== Strategy B: mermaid.ink URL ===")
    url = get_mermaid_ink_url(SAMPLE_MERMAID)
    print(f"SVG URL: {url[:100]}...")

    # Strategy C: HTML preview (always works)
    print("\n=== Strategy C: HTML preview ===")
    export_to_html_preview(SAMPLE_MERMAID, str(out_dir / "preview.html"))
