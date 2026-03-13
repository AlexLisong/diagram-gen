from __future__ import annotations

import html
import math

from models import (
    FunnelSpec,
    GraphicSpec,
    KPIBoardSpec,
    MaturityLadderSpec,
    PyramidSpec,
    QuadrantSpec,
    ScorecardSpec,
    TimelineSpec,
)

WIDTH = 1600
HEIGHT = 900

THEMES = {
    "executive": {
        "bg": "#f4efe6",
        "panel": "#fffaf2",
        "text": "#1f2937",
        "muted": "#6b7280",
        "line": "#d6d3d1",
        "accent": "#c2410c",
        "accent_2": "#0f766e",
        "accent_3": "#1d4ed8",
        "accent_4": "#7c3aed",
    },
    "newsroom": {
        "bg": "#f7f7f5",
        "panel": "#ffffff",
        "text": "#111827",
        "muted": "#4b5563",
        "line": "#d1d5db",
        "accent": "#b91c1c",
        "accent_2": "#0f766e",
        "accent_3": "#2563eb",
        "accent_4": "#a16207",
    },
    "midnight": {
        "bg": "#081221",
        "panel": "#102033",
        "text": "#f8fafc",
        "muted": "#94a3b8",
        "line": "#243447",
        "accent": "#38bdf8",
        "accent_2": "#22c55e",
        "accent_3": "#f59e0b",
        "accent_4": "#a78bfa",
    },
}


def _esc(value: str) -> str:
    return html.escape(value, quote=True)


def _svg_text(x: float, y: float, text: str, size: int = 24, weight: int = 500, fill: str = "#111827", anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="Inter, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{_esc(text)}</text>'
    )


def _wrap_svg(content: str, theme: dict[str, str]) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Presentation insight graphic">
  <defs>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#0f172a" flood-opacity="0.10"/>
    </filter>
  </defs>
  <rect width="{WIDTH}" height="{HEIGHT}" fill="{theme['bg']}"/>
  {content}
</svg>"""


def _header(title: str, subtitle: str | None, theme: dict[str, str]) -> str:
    parts = [
        _svg_text(96, 96, title, size=42, weight=700, fill=theme["text"]),
    ]
    if subtitle:
        parts.append(_svg_text(96, 136, subtitle, size=18, weight=400, fill=theme["muted"]))
    parts.append(f'<line x1="96" y1="164" x2="1504" y2="164" stroke="{theme["line"]}" stroke-width="2"/>')
    return "".join(parts)


def _accent_cycle(theme: dict[str, str]) -> list[str]:
    return [theme["accent"], theme["accent_2"], theme["accent_3"], theme["accent_4"]]


def render_graphic(spec: GraphicSpec) -> str:
    theme = THEMES[spec.theme]
    content = _header(spec.title, spec.subtitle, theme)

    if isinstance(spec, KPIBoardSpec):
        content += _render_kpi_board(spec, theme)
    elif isinstance(spec, FunnelSpec):
        content += _render_funnel(spec, theme)
    elif isinstance(spec, TimelineSpec):
        content += _render_timeline(spec, theme)
    elif isinstance(spec, QuadrantSpec):
        content += _render_quadrant(spec, theme)
    elif isinstance(spec, MaturityLadderSpec):
        content += _render_maturity_ladder(spec, theme)
    elif isinstance(spec, ScorecardSpec):
        content += _render_scorecard(spec, theme)
    elif isinstance(spec, PyramidSpec):
        content += _render_pyramid(spec, theme)
    else:
        raise TypeError(f"Unsupported spec type: {type(spec)!r}")

    return _wrap_svg(content, theme)


def render_preview_html(spec: GraphicSpec, svg: str) -> str:
    theme = THEMES[spec.theme]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_esc(spec.title)}</title>
  <style>
    body {{
      margin: 0;
      background: {theme["bg"]};
      min-height: 100vh;
      display: grid;
      place-items: center;
      font-family: Inter, Arial, sans-serif;
    }}
    .frame {{
      width: min(96vw, 1600px);
      box-shadow: 0 24px 80px rgba(15, 23, 42, 0.16);
      border-radius: 20px;
      overflow: hidden;
    }}
    svg {{
      display: block;
      width: 100%;
      height: auto;
    }}
  </style>
</head>
<body>
  <div class="frame">{svg}</div>
</body>
</html>"""


def _render_kpi_board(spec: KPIBoardSpec, theme: dict[str, str]) -> str:
    parts: list[str] = []
    card_colors = _accent_cycle(theme)
    columns = min(4, len(spec.cards))
    rows = math.ceil(len(spec.cards) / columns)
    gap = 28
    board_x = 96
    board_y = 210
    board_w = WIDTH - (board_x * 2)
    board_h = HEIGHT - board_y - 80
    card_w = (board_w - gap * (columns - 1)) / columns
    card_h = (board_h - gap * (rows - 1)) / rows

    for index, card in enumerate(spec.cards):
        row = index // columns
        col = index % columns
        x = board_x + col * (card_w + gap)
        y = board_y + row * (card_h + gap)
        accent = card.accent or card_colors[index % len(card_colors)]
        parts.append(
            f'<rect x="{x}" y="{y}" rx="28" ry="28" width="{card_w}" height="{card_h}" fill="{theme["panel"]}" '
            f'stroke="{theme["line"]}" stroke-width="1.5" filter="url(#shadow)"/>'
        )
        parts.append(f'<rect x="{x + 24}" y="{y + 24}" rx="8" ry="8" width="72" height="8" fill="{accent}"/>')
        parts.append(_svg_text(x + 24, y + 72, card.label, size=20, weight=600, fill=theme["muted"]))
        parts.append(_svg_text(x + 24, y + 156, card.value, size=56, weight=700, fill=theme["text"]))
        if card.delta:
            parts.append(
                f'<rect x="{x + 24}" y="{y + 184}" rx="18" ry="18" width="120" height="38" fill="{accent}" fill-opacity="0.12"/>'
            )
            parts.append(_svg_text(x + 84, y + 210, card.delta, size=18, weight=700, fill=accent, anchor="middle"))
        if card.note:
            parts.append(_svg_text(x + 24, y + card_h - 26, card.note, size=18, weight=400, fill=theme["muted"]))
    return "".join(parts)


def _render_funnel(spec: FunnelSpec, theme: dict[str, str]) -> str:
    parts: list[str] = []
    colors = _accent_cycle(theme)
    top_width = 1040
    bottom_width = 520
    segment_h = 102
    center_x = WIDTH / 2
    start_y = 230
    max_value = spec.stages[0].value

    for index, stage in enumerate(spec.stages):
        y = start_y + index * (segment_h + 18)
        ratio_top = index / max(len(spec.stages) - 1, 1)
        ratio_bottom = (index + 1) / max(len(spec.stages), 1)
        width_top = top_width - (top_width - bottom_width) * ratio_top
        width_bottom = top_width - (top_width - bottom_width) * ratio_bottom
        points = [
            (center_x - width_top / 2, y),
            (center_x + width_top / 2, y),
            (center_x + width_bottom / 2, y + segment_h),
            (center_x - width_bottom / 2, y + segment_h),
        ]
        point_str = " ".join(f"{px},{py}" for px, py in points)
        accent = stage.accent or colors[index % len(colors)]
        opacity = 0.18 + (0.1 * index)
        parts.append(
            f'<polygon points="{point_str}" fill="{accent}" fill-opacity="{min(opacity, 0.42)}" '
            f'stroke="{accent}" stroke-width="2"/>'
        )
        parts.append(_svg_text(center_x - width_top / 2 + 34, y + 44, stage.label, size=26, weight=700, fill=theme["text"]))
        parts.append(_svg_text(center_x - width_top / 2 + 34, y + 76, stage.note or "", size=16, weight=400, fill=theme["muted"]))
        conversion = stage.value / max_value
        parts.append(_svg_text(center_x + width_top / 2 - 34, y + 50, f"{stage.value}", size=34, weight=700, fill=theme["text"], anchor="end"))
        parts.append(_svg_text(center_x + width_top / 2 - 34, y + 82, f"{conversion:.0%} of start", size=16, weight=500, fill=theme["muted"], anchor="end"))
    return "".join(parts)


def _render_timeline(spec: TimelineSpec, theme: dict[str, str]) -> str:
    parts: list[str] = []
    colors = _accent_cycle(theme)
    x0 = 150
    x1 = WIDTH - 150
    y = 510
    step = (x1 - x0) / max(len(spec.milestones) - 1, 1)
    parts.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{theme["line"]}" stroke-width="8" stroke-linecap="round"/>')

    status_color = {"done": theme["accent_2"], "active": theme["accent"], "next": theme["accent_3"]}
    for index, milestone in enumerate(spec.milestones):
        x = x0 + index * step
        card_y = 250 if index % 2 == 0 else 565
        line_y = 396 if index % 2 == 0 else 510
        accent = status_color[milestone.status]
        parts.append(f'<line x1="{x}" y1="{line_y}" x2="{x}" y2="{y}" stroke="{accent}" stroke-width="4"/>')
        parts.append(f'<circle cx="{x}" cy="{y}" r="18" fill="{theme["panel"]}" stroke="{accent}" stroke-width="6"/>')
        parts.append(
            f'<rect x="{x - 145}" y="{card_y}" rx="24" ry="24" width="290" height="124" fill="{theme["panel"]}" '
            f'stroke="{theme["line"]}" stroke-width="1.5" filter="url(#shadow)"/>'
        )
        parts.append(f'<rect x="{x - 145}" y="{card_y}" rx="24" ry="24" width="290" height="16" fill="{colors[index % len(colors)]}" fill-opacity="0.18"/>')
        parts.append(_svg_text(x - 118, card_y + 42, milestone.period, size=18, weight=700, fill=accent))
        parts.append(_svg_text(x - 118, card_y + 78, milestone.label, size=24, weight=700, fill=theme["text"]))
        parts.append(_svg_text(x - 118, card_y + 108, milestone.detail, size=16, weight=400, fill=theme["muted"]))
    return "".join(parts)


def _render_quadrant(spec: QuadrantSpec, theme: dict[str, str]) -> str:
    parts: list[str] = []
    colors = _accent_cycle(theme)
    chart_x = 180
    chart_y = 230
    chart_w = 1160
    chart_h = 540
    mid_x = chart_x + chart_w / 2
    mid_y = chart_y + chart_h / 2

    panel_opacity = 0.08 if spec.theme == "midnight" else 0.14
    parts.append(f'<rect x="{chart_x}" y="{chart_y}" width="{chart_w}" height="{chart_h}" rx="28" ry="28" fill="{theme["panel"]}" stroke="{theme["line"]}" stroke-width="1.5"/>')
    parts.append(f'<rect x="{chart_x}" y="{chart_y}" width="{chart_w / 2}" height="{chart_h / 2}" fill="{theme["accent_2"]}" fill-opacity="{panel_opacity}"/>')
    parts.append(f'<rect x="{mid_x}" y="{chart_y}" width="{chart_w / 2}" height="{chart_h / 2}" fill="{theme["accent"]}" fill-opacity="{panel_opacity}"/>')
    parts.append(f'<rect x="{chart_x}" y="{mid_y}" width="{chart_w / 2}" height="{chart_h / 2}" fill="{theme["accent_3"]}" fill-opacity="{panel_opacity}"/>')
    parts.append(f'<rect x="{mid_x}" y="{mid_y}" width="{chart_w / 2}" height="{chart_h / 2}" fill="{theme["accent_4"]}" fill-opacity="{panel_opacity}"/>')
    parts.append(f'<line x1="{mid_x}" y1="{chart_y}" x2="{mid_x}" y2="{chart_y + chart_h}" stroke="{theme["line"]}" stroke-width="3"/>')
    parts.append(f'<line x1="{chart_x}" y1="{mid_y}" x2="{chart_x + chart_w}" y2="{mid_y}" stroke="{theme["line"]}" stroke-width="3"/>')

    parts.append(_svg_text(chart_x + 24, chart_y + 38, spec.top_left_label, size=20, weight=700, fill=theme["muted"]))
    parts.append(_svg_text(chart_x + chart_w - 24, chart_y + 38, spec.top_right_label, size=20, weight=700, fill=theme["muted"], anchor="end"))
    parts.append(_svg_text(chart_x + 24, chart_y + chart_h - 20, spec.bottom_left_label, size=20, weight=700, fill=theme["muted"]))
    parts.append(_svg_text(chart_x + chart_w - 24, chart_y + chart_h - 20, spec.bottom_right_label, size=20, weight=700, fill=theme["muted"], anchor="end"))
    parts.append(_svg_text(chart_x + chart_w / 2, chart_y + chart_h + 54, spec.x_label, size=20, weight=600, fill=theme["muted"], anchor="middle"))
    parts.append(f'<g transform="translate({chart_x - 58},{chart_y + chart_h / 2}) rotate(-90)">{_svg_text(0, 0, spec.y_label, size=20, weight=600, fill=theme["muted"], anchor="middle")}</g>')

    for index, point in enumerate(spec.points):
        cx = chart_x + (point.x / 100.0) * chart_w
        cy = chart_y + chart_h - (point.y / 100.0) * chart_h
        radius = 14 + (point.size * 6)
        accent = point.accent or colors[index % len(colors)]
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{accent}" fill-opacity="0.85" stroke="{theme["panel"]}" stroke-width="3"/>')
        parts.append(_svg_text(cx, cy + 6, str(point.size), size=18, weight=700, fill=theme["panel"], anchor="middle"))
        parts.append(_svg_text(cx + radius + 10, cy - 2, point.label, size=17, weight=700, fill=theme["text"]))
        if point.note:
            parts.append(_svg_text(cx + radius + 10, cy + 22, point.note, size=14, weight=400, fill=theme["muted"]))
    return "".join(parts)


def _render_maturity_ladder(spec: MaturityLadderSpec, theme: dict[str, str]) -> str:
    parts: list[str] = []
    colors = _accent_cycle(theme)
    base_x = 150
    base_y = 760
    step_w = 230
    step_h = 92

    for index, stage in enumerate(spec.stages):
        x = base_x + index * (step_w - 10)
        height = step_h + index * 56
        y = base_y - height
        accent = colors[index % len(colors)]
        parts.append(
            f'<rect x="{x}" y="{y}" rx="24" ry="24" width="{step_w}" height="{height}" fill="{theme["panel"]}" '
            f'stroke="{theme["line"]}" stroke-width="1.5" filter="url(#shadow)"/>'
        )
        parts.append(f'<rect x="{x}" y="{y}" rx="24" ry="24" width="{step_w}" height="16" fill="{accent}" fill-opacity="0.22"/>')
        parts.append(_svg_text(x + 26, y + 50, stage.level, size=18, weight=700, fill=accent))
        parts.append(_svg_text(x + 26, y + 92, stage.label, size=28, weight=700, fill=theme["text"]))
        parts.append(_svg_text(x + 26, y + 128, stage.detail, size=16, weight=400, fill=theme["muted"]))
        parts.append(_svg_text(x + step_w - 28, y + 52, f"{stage.score}/5", size=20, weight=700, fill=theme["muted"], anchor="end"))
    return "".join(parts)


def _render_scorecard(spec: ScorecardSpec, theme: dict[str, str]) -> str:
    parts: list[str] = []
    table_x = 96
    table_y = 230
    table_w = WIDTH - 192
    header_h = 72
    row_h = 92
    criteria_w = 360
    note_w = 300
    value_w = (table_w - criteria_w - note_w) / len(spec.columns)
    colors = _accent_cycle(theme)

    parts.append(f'<rect x="{table_x}" y="{table_y}" width="{table_w}" height="{header_h + row_h * len(spec.rows)}" rx="28" ry="28" fill="{theme["panel"]}" stroke="{theme["line"]}" stroke-width="1.5"/>')
    parts.append(f'<rect x="{table_x}" y="{table_y}" width="{table_w}" height="{header_h}" rx="28" ry="28" fill="{theme["text"]}" fill-opacity="0.04"/>')
    parts.append(_svg_text(table_x + 24, table_y + 46, "Criterion", size=20, weight=700, fill=theme["muted"]))

    for index, column in enumerate(spec.columns):
        x = table_x + criteria_w + index * value_w
        parts.append(_svg_text(x + value_w / 2, table_y + 46, column.label, size=20, weight=700, fill=theme["muted"], anchor="middle"))
    parts.append(_svg_text(table_x + table_w - note_w / 2, table_y + 46, "Readout", size=20, weight=700, fill=theme["muted"], anchor="middle"))

    for row_index, row in enumerate(spec.rows):
        y = table_y + header_h + row_index * row_h
        parts.append(f'<line x1="{table_x}" y1="{y}" x2="{table_x + table_w}" y2="{y}" stroke="{theme["line"]}" stroke-width="1.5"/>')
        parts.append(_svg_text(table_x + 24, y + 54, row.criterion, size=22, weight=700, fill=theme["text"]))
        for col_index, column in enumerate(spec.columns):
            x = table_x + criteria_w + col_index * value_w
            score = row.scores[column.key]
            accent = colors[col_index % len(colors)]
            bar_w = max(32, (value_w - 48) * (score / spec.scale_max))
            parts.append(f'<rect x="{x + 24}" y="{y + 28}" width="{value_w - 48}" height="22" rx="11" ry="11" fill="{theme["line"]}" fill-opacity="0.45"/>')
            parts.append(f'<rect x="{x + 24}" y="{y + 28}" width="{bar_w}" height="22" rx="11" ry="11" fill="{accent}"/>')
            parts.append(_svg_text(x + value_w / 2, y + 76, f"{score}/{spec.scale_max}", size=16, weight=700, fill=theme["muted"], anchor="middle"))
        parts.append(_svg_text(table_x + table_w - note_w + 20, y + 54, row.note or "", size=16, weight=400, fill=theme["muted"]))
    return "".join(parts)


def _render_pyramid(spec: PyramidSpec, theme: dict[str, str]) -> str:
    parts: list[str] = []
    colors = _accent_cycle(theme)
    top_width = 300
    bottom_width = 1100
    center_x = WIDTH / 2
    start_y = 260
    total_h = 500
    layer_h = total_h / len(spec.layers)

    for index, layer in enumerate(spec.layers):
        ratio_top = index / len(spec.layers)
        ratio_bottom = (index + 1) / len(spec.layers)
        width_top = top_width + (bottom_width - top_width) * ratio_top
        width_bottom = top_width + (bottom_width - top_width) * ratio_bottom
        y = start_y + index * layer_h
        accent = layer.accent or colors[index % len(colors)]
        points = [
            (center_x - width_top / 2, y),
            (center_x + width_top / 2, y),
            (center_x + width_bottom / 2, y + layer_h - 12),
            (center_x - width_bottom / 2, y + layer_h - 12),
        ]
        point_str = " ".join(f"{px},{py}" for px, py in points)
        parts.append(f'<polygon points="{point_str}" fill="{accent}" fill-opacity="{0.14 + 0.08 * index}" stroke="{accent}" stroke-width="2"/>')
        parts.append(_svg_text(center_x, y + 48, layer.label, size=24, weight=700, fill=theme["text"], anchor="middle"))
        parts.append(_svg_text(center_x, y + 80, layer.detail, size=16, weight=400, fill=theme["muted"], anchor="middle"))
    return "".join(parts)
