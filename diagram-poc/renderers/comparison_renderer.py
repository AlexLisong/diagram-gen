"""
HTML renderer for before/after and comparison diagrams.
Outputs a standalone HTML file or an SVG-compatible layout.
"""

from __future__ import annotations

from schemas.comparison_schema import ComparisonSpec


def render_comparison_html(spec: ComparisonSpec) -> str:
    """Convert ComparisonSpec into a standalone HTML comparison card."""
    left_items = "\n".join(
        f'        <li>{item}</li>' for item in spec.left.items
    )
    right_items = "\n".join(
        f'        <li>{item}</li>' for item in spec.right.items
    )
    notes_html = ""
    if spec.improvement_notes:
        notes_list = "\n".join(
            f'      <li>{n}</li>' for n in spec.improvement_notes
        )
        notes_html = f"""
    <div class="notes">
      <h3>Key Improvements</h3>
      <ul>
{notes_list}
      </ul>
    </div>"""

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{spec.title}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f0f2f5; padding: 2rem; }}
    .container {{ max-width: 960px; margin: 0 auto; }}
    h1 {{ text-align: center; color: #1a1a2e; font-size: 1.6rem; margin-bottom: 2rem; }}
    .comparison {{ display: grid; grid-template-columns: 1fr 60px 1fr; gap: 0; align-items: stretch; }}
    .side {{ padding: 2rem; border-radius: 12px; }}
    .side h2 {{ font-size: 1.2rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid; }}
    .side ul {{ list-style: none; }}
    .side li {{ padding: 0.6rem 0; font-size: 0.95rem; border-bottom: 1px solid rgba(0,0,0,0.06); }}
    .side li::before {{ display: inline-block; width: 1.5rem; }}
    .left {{ background: #fff0f0; }}
    .left h2 {{ color: #c0392b; border-color: #e74c3c; }}
    .left li::before {{ content: "✗ "; color: #e74c3c; }}
    .right {{ background: #f0fff4; }}
    .right h2 {{ color: #27ae60; border-color: #2ecc71; }}
    .right li::before {{ content: "✓ "; color: #2ecc71; }}
    .arrow {{ display: flex; align-items: center; justify-content: center; font-size: 2rem; color: #7f8c8d; }}
    .notes {{ margin-top: 2rem; padding: 1.5rem; background: #fff; border-radius: 12px;
              border-left: 4px solid #3498db; }}
    .notes h3 {{ color: #2c3e50; font-size: 1rem; margin-bottom: 0.8rem; }}
    .notes li {{ font-size: 0.9rem; padding: 0.3rem 0; color: #555; }}
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
    </div>{notes_html}
  </div>
</body>
</html>"""
