from __future__ import annotations

from html import escape

from schemas.comparison_schema import ComparisonDiagramSpec


def _render_items(items: list[str]) -> str:
    rendered = "\n".join(f"<li>{escape(item)}</li>" for item in items)
    return f"<ul>{rendered}</ul>"


def comparison_html(spec: ComparisonDiagramSpec) -> str:
    notes = "".join(f"<p>{escape(note)}</p>" for note in spec.notes)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(spec.title)}</title>
  <style>
    :root {{
      --bg: #f7f1e6;
      --panel: rgba(255, 255, 255, 0.72);
      --ink: #1f2937;
      --muted: #5b6470;
      --before: #c96b4a;
      --after: #2f7d57;
      --stroke: rgba(31, 41, 55, 0.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Helvetica, Arial, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, #f6d9b7, transparent 26%),
        radial-gradient(circle at bottom right, #d8ead8, transparent 28%),
        var(--bg);
    }}
    main {{
      min-height: 100vh;
      padding: 56px;
      display: grid;
      gap: 28px;
      align-content: center;
    }}
    h1 {{
      margin: 0;
      font-size: 40px;
    }}
    .columns {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 24px;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--stroke);
      border-radius: 24px;
      padding: 28px;
      box-shadow: 0 16px 40px rgba(31, 41, 55, 0.08);
      backdrop-filter: blur(14px);
    }}
    .eyebrow {{
      margin: 0 0 16px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-size: 12px;
      color: var(--muted);
    }}
    .before h2 {{ color: var(--before); }}
    .after h2 {{ color: var(--after); }}
    h2 {{
      margin: 0 0 16px;
      font-size: 30px;
    }}
    ul {{
      margin: 0;
      padding-left: 22px;
      display: grid;
      gap: 12px;
      font-size: 22px;
      line-height: 1.35;
    }}
    .notes {{
      color: var(--muted);
      font-size: 16px;
      display: grid;
      gap: 8px;
    }}
    @media (max-width: 900px) {{
      main {{ padding: 28px; }}
      .columns {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 32px; }}
      ul {{ font-size: 18px; }}
    }}
  </style>
</head>
<body>
  <main>
    <section>
      <p class="eyebrow">Before / After</p>
      <h1>{escape(spec.title)}</h1>
    </section>
    <section class="columns">
      <article class="panel before">
        <p class="eyebrow">Before</p>
        <h2>{escape(spec.left.title)}</h2>
        {_render_items(spec.left.items)}
      </article>
      <article class="panel after">
        <p class="eyebrow">After</p>
        <h2>{escape(spec.right.title)}</h2>
        {_render_items(spec.right.items)}
      </article>
    </section>
    <section class="notes">{notes}</section>
  </main>
</body>
</html>
"""
