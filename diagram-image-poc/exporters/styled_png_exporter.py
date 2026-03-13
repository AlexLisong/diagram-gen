from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

try:
    from PIL import Image, ImageColor, ImageDraw, ImageFont
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Pillow is required for PNG generation. Use a Python environment with Pillow installed."
    ) from exc

from schemas.graph_schema import GraphDiagramSpec
from exporters.svg_exporter import (
    Box,
    _arrow_head,
    _edge_points,
    _edge_style,
    _group_label,
    layout_diagram,
)


@dataclass(frozen=True)
class StyleTheme:
    name: str
    title_font: str
    body_font: str
    bg_top: str
    bg_bottom: str
    title: str
    text: str
    meta: str
    edge: str
    edge_label_fill: str
    edge_label_text: str
    group_fill: str
    group_stroke: str
    group_header_fill: str
    node_stroke: str
    shadow: str
    glow: str
    min_width: int
    min_height: int
    node_fill: dict[str, str]
    show_grid: bool = False
    grid_color: str = "#000000"
    title_scale: float = 1.0
    shadow_offset_y: int = 10
    node_radius: int = 16
    group_radius: int = 20
    hero_panel_fill: str | None = None
    hero_panel_stroke: str | None = None
    hero_kicker_fill: str | None = None
    hero_kicker_text: str | None = None
    hero_badge_fill: str | None = None
    hero_badge_text: str | None = None
    focus_outline: str | None = None
    focus_glow: str | None = None
    focus_label_fill: str | None = None
    focus_label_text: str | None = None


THEMES = {
    "studio": StyleTheme(
        name="studio",
        title_font="/System/Library/Fonts/Avenir Next.ttc",
        body_font="/System/Library/Fonts/Avenir.ttc",
        bg_top="#f8efe2",
        bg_bottom="#efe4d2",
        title="#142033",
        text="#1d2939",
        meta="#526072",
        edge="#57657a",
        edge_label_fill="#fff8ee",
        edge_label_text="#243447",
        group_fill="#f3e7d6",
        group_stroke="#c4a98a",
        group_header_fill="#ead5be",
        node_stroke="#243447",
        shadow="#7f5f4633",
        glow="#f4d6b655",
        min_width=1600,
        min_height=900,
        node_fill={
            "frontend": "#ffd7b0",
            "api": "#c9dcf6",
            "service": "#d6ecd0",
            "ai_service": "#b7dcd1",
            "database": "#d9d2f5",
            "storage": "#fff1bf",
            "external_api": "#f7c8cf",
            "module": "#d7e8f2",
            "user": "#f8e0a8",
            "repo": "#d7d7d7",
            "document": "#f6e8c2",
            "cloud": "#d5e7ff",
            "decision": "#fff1c7",
            "verifier": "#d6e8cf",
            "output": "#f9e1c8",
            "worker": "#f0d4c6",
        },
        title_scale=1.0,
        shadow_offset_y=10,
        node_radius=16,
        group_radius=20,
    ),
    "blueprint": StyleTheme(
        name="blueprint",
        title_font="/System/Library/Fonts/Menlo.ttc",
        body_font="/System/Library/Fonts/Menlo.ttc",
        bg_top="#081423",
        bg_bottom="#102540",
        title="#dff6ff",
        text="#d8eff8",
        meta="#89bfd1",
        edge="#7ae7ff",
        edge_label_fill="#10324c",
        edge_label_text="#dff6ff",
        group_fill="#0d2237",
        group_stroke="#4bb7d9",
        group_header_fill="#12324d",
        node_stroke="#8defff",
        shadow="#02060e99",
        glow="#2fd1ff44",
        min_width=1600,
        min_height=900,
        node_fill={
            "frontend": "#153654",
            "api": "#173f63",
            "service": "#12354a",
            "ai_service": "#0d4958",
            "database": "#19335a",
            "storage": "#27455e",
            "external_api": "#4a2944",
            "module": "#1b3550",
            "user": "#3c4520",
            "repo": "#2d3642",
            "document": "#3d4d29",
            "cloud": "#173456",
            "decision": "#5a4818",
            "verifier": "#1d4f44",
            "output": "#4b341e",
            "worker": "#4a2f29",
        },
        show_grid=True,
        grid_color="#1f4d69",
        title_scale=0.92,
        shadow_offset_y=8,
        node_radius=14,
        group_radius=16,
    ),
    "broadcast": StyleTheme(
        name="broadcast",
        title_font="/System/Library/Fonts/Avenir Next Condensed.ttc",
        body_font="/System/Library/Fonts/HelveticaNeue.ttc",
        bg_top="#17181c",
        bg_bottom="#0e1014",
        title="#fff3e8",
        text="#f6eee5",
        meta="#d1beb0",
        edge="#ff8b5e",
        edge_label_fill="#261a15",
        edge_label_text="#fff3e8",
        group_fill="#1a1d23",
        group_stroke="#ff8b5e",
        group_header_fill="#291f1a",
        node_stroke="#ffd7c2",
        shadow="#00000088",
        glow="#ff7b3b44",
        min_width=1600,
        min_height=900,
        node_fill={
            "frontend": "#7c3d22",
            "api": "#91512d",
            "service": "#4a5f41",
            "ai_service": "#205b61",
            "database": "#473c74",
            "storage": "#66521c",
            "external_api": "#6a2940",
            "module": "#385063",
            "user": "#7d6421",
            "repo": "#4d4f56",
            "document": "#6b5931",
            "cloud": "#27446b",
            "decision": "#8a4d16",
            "verifier": "#2f654f",
            "output": "#7e3f27",
            "worker": "#6e3328",
        },
        title_scale=1.06,
        shadow_offset_y=12,
        node_radius=16,
        group_radius=18,
    ),
    "glass_sunset": StyleTheme(
        name="glass_sunset",
        title_font="/System/Library/Fonts/SFGeorgianRounded.ttf",
        body_font="/System/Library/Fonts/HelveticaNeue.ttc",
        bg_top="#f6d8c8",
        bg_bottom="#e8eff8",
        title="#1e2a3a",
        text="#203041",
        meta="#546171",
        edge="#5d6f88",
        edge_label_fill="#ffffffcc",
        edge_label_text="#243447",
        group_fill="#ffffff66",
        group_stroke="#ffffffaa",
        group_header_fill="#ffffff88",
        node_stroke="#ffffffdd",
        shadow="#5c6a7a22",
        glow="#ffffff66",
        min_width=1600,
        min_height=900,
        node_fill={
            "frontend": "#ffd8ccbb",
            "api": "#d8e9ffbb",
            "service": "#dff6e3bb",
            "ai_service": "#cfeef0bb",
            "database": "#e4ddffbb",
            "storage": "#fff3cabb",
            "external_api": "#ffd5debb",
            "module": "#deebf4bb",
            "user": "#ffe7bdbb",
            "repo": "#edededbb",
            "document": "#f8edcbbb",
            "cloud": "#dceaffbb",
            "decision": "#fff1cdbb",
            "verifier": "#dcf0d7bb",
            "output": "#ffe4d3bb",
            "worker": "#f2d8cebb",
        },
        title_scale=1.0,
        shadow_offset_y=6,
        node_radius=22,
        group_radius=28,
    ),
    "terminal_lime": StyleTheme(
        name="terminal_lime",
        title_font="/System/Library/Fonts/Menlo.ttc",
        body_font="/System/Library/Fonts/Menlo.ttc",
        bg_top="#08110a",
        bg_bottom="#030805",
        title="#d7ffd7",
        text="#bff7c0",
        meta="#76b976",
        edge="#6cff7d",
        edge_label_fill="#0c170dcc",
        edge_label_text="#d7ffd7",
        group_fill="#09140a",
        group_stroke="#4cdb67",
        group_header_fill="#0d1c0f",
        node_stroke="#85ff99",
        shadow="#000000aa",
        glow="#1aff6640",
        min_width=1600,
        min_height=900,
        node_fill={
            "frontend": "#0e2414",
            "api": "#102815",
            "service": "#0e2313",
            "ai_service": "#12301f",
            "database": "#132118",
            "storage": "#233019",
            "external_api": "#2a1c14",
            "module": "#132317",
            "user": "#243119",
            "repo": "#1b211c",
            "document": "#28331f",
            "cloud": "#13241b",
            "decision": "#372d10",
            "verifier": "#143024",
            "output": "#2c1d14",
            "worker": "#281714",
        },
        show_grid=True,
        grid_color="#123119",
        title_scale=0.9,
        shadow_offset_y=4,
        node_radius=10,
        group_radius=12,
    ),
    "editorial_poster": StyleTheme(
        name="editorial_poster",
        title_font="/System/Library/Fonts/Palatino.ttc",
        body_font="/System/Library/Fonts/HelveticaNeue.ttc",
        bg_top="#f8f5ee",
        bg_bottom="#efe7d9",
        title="#132238",
        text="#1d2a38",
        meta="#5a6673",
        edge="#d04a2f",
        edge_label_fill="#fff8ef",
        edge_label_text="#223142",
        group_fill="#fffaf1",
        group_stroke="#d04a2f",
        group_header_fill="#f2e3d0",
        node_stroke="#1f2f45",
        shadow="#cab8a033",
        glow="#ffd3b855",
        min_width=1600,
        min_height=900,
        node_fill={
            "frontend": "#ffd9b8",
            "api": "#d1e0ff",
            "service": "#dcefd6",
            "ai_service": "#cbe6ea",
            "database": "#ddd6fb",
            "storage": "#fff2c8",
            "external_api": "#ffd5d5",
            "module": "#ddeaf5",
            "user": "#ffe8b1",
            "repo": "#e0dfdd",
            "document": "#f9efca",
            "cloud": "#d9ebff",
            "decision": "#fff1cf",
            "verifier": "#d9ebd7",
            "output": "#ffe5d5",
            "worker": "#f3d6c5",
        },
        title_scale=1.12,
        shadow_offset_y=5,
        node_radius=8,
        group_radius=10,
    ),
    "broadcast_hero": StyleTheme(
        name="broadcast_hero",
        title_font="/System/Library/Fonts/Avenir Next Condensed.ttc",
        body_font="/System/Library/Fonts/HelveticaNeue.ttc",
        bg_top="#12141a",
        bg_bottom="#090b0f",
        title="#fff5ed",
        text="#fff0e7",
        meta="#d6c1b4",
        edge="#ff7e45",
        edge_label_fill="#2b1812ee",
        edge_label_text="#fff5ed",
        group_fill="#161a21",
        group_stroke="#ff7e45",
        group_header_fill="#241a16",
        node_stroke="#ffe0cc",
        shadow="#00000099",
        glow="#ff7e4544",
        min_width=1600,
        min_height=900,
        node_fill={
            "frontend": "#874124",
            "api": "#a95c2f",
            "service": "#4a6444",
            "ai_service": "#1e6b74",
            "database": "#4e4380",
            "storage": "#6b5720",
            "external_api": "#7a3047",
            "module": "#3b566c",
            "user": "#896f22",
            "repo": "#545760",
            "document": "#756234",
            "cloud": "#2b4e78",
            "decision": "#955016",
            "verifier": "#2f7056",
            "output": "#8e4829",
            "worker": "#75372b",
        },
        title_scale=1.18,
        shadow_offset_y=14,
        node_radius=16,
        group_radius=18,
        hero_panel_fill="#0f131acc",
        hero_panel_stroke="#ff7e45",
        hero_kicker_fill="#ff7e45",
        hero_kicker_text="#140c08",
        hero_badge_fill="#fff5ed",
        hero_badge_text="#1e232d",
        focus_outline="#ffb38b",
        focus_glow="#ff7e4570",
        focus_label_fill="#ff7e45",
        focus_label_text="#140c08",
    ),
    "editorial_hero": StyleTheme(
        name="editorial_hero",
        title_font="/System/Library/Fonts/Palatino.ttc",
        body_font="/System/Library/Fonts/HelveticaNeue.ttc",
        bg_top="#faf7f0",
        bg_bottom="#efe7da",
        title="#132238",
        text="#223142",
        meta="#5d6875",
        edge="#d1462c",
        edge_label_fill="#fffaf2ee",
        edge_label_text="#223142",
        group_fill="#fffdf7",
        group_stroke="#d1462c",
        group_header_fill="#f2e2cf",
        node_stroke="#223142",
        shadow="#8c745833",
        glow="#ffd2b055",
        min_width=1600,
        min_height=900,
        node_fill={
            "frontend": "#ffd9bc",
            "api": "#d6e5ff",
            "service": "#deefd8",
            "ai_service": "#d1eaf0",
            "database": "#e1dafb",
            "storage": "#fff1ca",
            "external_api": "#ffd8d8",
            "module": "#e0ebf5",
            "user": "#ffe9b8",
            "repo": "#e4e1dc",
            "document": "#faf0cb",
            "cloud": "#deedff",
            "decision": "#fff2d3",
            "verifier": "#dcebdb",
            "output": "#ffe7d8",
            "worker": "#f2dacb",
        },
        title_scale=1.22,
        shadow_offset_y=6,
        node_radius=10,
        group_radius=12,
        hero_panel_fill="#fffaf3cc",
        hero_panel_stroke="#d1462c",
        hero_kicker_fill="#132238",
        hero_kicker_text="#fffaf3",
        hero_badge_fill="#d1462c",
        hero_badge_text="#fffaf3",
        focus_outline="#d1462c",
        focus_glow="#ffd2b088",
        focus_label_fill="#132238",
        focus_label_text="#fffaf3",
    ),
}


def available_styles() -> list[str]:
    return sorted(THEMES)


def _font(path: str, size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def _hex_to_rgba(value: str) -> tuple[int, int, int, int]:
    rgba = ImageColor.getcolor(value, "RGBA")
    return rgba


def _node_fill(theme: StyleTheme, node_type: str) -> str:
    return theme.node_fill.get(node_type, "#dce7ef")


def _draw_vertical_gradient(image: Image.Image, top: str, bottom: str) -> None:
    draw = ImageDraw.Draw(image)
    top_rgb = ImageColor.getcolor(top, "RGB")
    bottom_rgb = ImageColor.getcolor(bottom, "RGB")
    width, height = image.size
    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = tuple(
            int(top_rgb[i] + (bottom_rgb[i] - top_rgb[i]) * ratio)
            for i in range(3)
        )
        draw.line((0, y, width, y), fill=color)


def _draw_grid(draw: ImageDraw.ImageDraw, size: tuple[int, int], color: str, spacing: int = 48) -> None:
    width, height = size
    rgba = _hex_to_rgba(color)
    for x in range(0, width, spacing):
        draw.line((x, 0, x, height), fill=rgba, width=1)
    for y in range(0, height, spacing):
        draw.line((0, y, width, y), fill=rgba, width=1)


def _scaled_box(box: Box, scale: float, offset_x: int, offset_y: int) -> tuple[int, int, int, int]:
    left = int(box.x * scale + offset_x)
    top = int(box.y * scale + offset_y)
    right = int((box.x + box.width) * scale + offset_x)
    bottom = int((box.y + box.height) * scale + offset_y)
    return left, top, right, bottom


def _rounded_shadow(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    radius: int,
    fill: str,
    offset: tuple[int, int] = (0, 10),
) -> None:
    ox, oy = offset
    shadow_rect = (rect[0] + ox, rect[1] + oy, rect[2] + ox, rect[3] + oy)
    draw.rounded_rectangle(shadow_rect, radius=radius, fill=_hex_to_rgba(fill))


def _edge_label(
    draw: ImageDraw.ImageDraw,
    center: tuple[float, float],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
    text_fill: str,
) -> None:
    if not text:
        return
    bbox = draw.textbbox((0, 0), text, font=font)
    pad_x = 10
    pad_y = 6
    rect = (
        int(center[0] - (bbox[2] - bbox[0]) / 2 - pad_x),
        int(center[1] - (bbox[3] - bbox[1]) / 2 - pad_y),
        int(center[0] + (bbox[2] - bbox[0]) / 2 + pad_x),
        int(center[1] + (bbox[3] - bbox[1]) / 2 + pad_y),
    )
    draw.rounded_rectangle(rect, radius=12, fill=_hex_to_rgba(fill))
    draw.text(
        (rect[0] + pad_x, rect[1] + pad_y - 1),
        text,
        fill=text_fill,
        font=font,
    )


def _draw_pill(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
    text_fill: str,
    pad_x: int = 14,
    pad_y: int = 8,
) -> tuple[int, int, int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    rect = (
        x,
        y,
        x + (bbox[2] - bbox[0]) + pad_x * 2,
        y + (bbox[3] - bbox[1]) + pad_y * 2,
    )
    draw.rounded_rectangle(rect, radius=999, fill=_hex_to_rgba(fill))
    draw.text((x + pad_x, y + pad_y - 1), text, fill=text_fill, font=font)
    return rect


def _diagram_label(spec: GraphDiagramSpec) -> str:
    return spec.diagram_type.replace("_", " ").upper()


def _pick_focus_node(spec: GraphDiagramSpec) -> str | None:
    if not spec.nodes:
        return None
    degree: dict[str, int] = {node.id: 0 for node in spec.nodes}
    for edge in spec.edges:
        degree[edge.from_id] += 1
        degree[edge.to_id] += 1
    priority = {
        "ai_service": 50,
        "verifier": 40,
        "api": 35,
        "decision": 30,
        "service": 25,
        "output": 15,
    }
    ranked = sorted(
        spec.nodes,
        key=lambda node: (priority.get(node.type, 0) + degree.get(node.id, 0), len(node.label)),
        reverse=True,
    )
    return ranked[0].id if ranked else None


def styled_png_bytes(spec: GraphDiagramSpec, style: str = "studio") -> bytes:
    theme = THEMES[style]
    base_layout = layout_diagram(spec)
    scale = min(
        theme.min_width / max(base_layout.width, 1),
        theme.min_height / max(base_layout.height, 1),
    )
    scale = max(scale, 1.0)
    canvas_width = max(theme.min_width, int(base_layout.width * scale))
    canvas_height = max(theme.min_height, int(base_layout.height * scale))
    offset_x = int((canvas_width - base_layout.width * scale) / 2)
    offset_y = int((canvas_height - base_layout.height * scale) / 2)

    image = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    _draw_vertical_gradient(image, theme.bg_top, theme.bg_bottom)
    draw = ImageDraw.Draw(image, "RGBA")

    if theme.show_grid:
        _draw_grid(draw, image.size, theme.grid_color)

    glow_color = _hex_to_rgba(theme.glow)
    draw.ellipse((-120, -80, int(canvas_width * 0.38), int(canvas_height * 0.42)), fill=glow_color)
    draw.ellipse((int(canvas_width * 0.68), int(canvas_height * 0.55), canvas_width + 80, canvas_height + 60), fill=glow_color)

    title_font = _font(theme.title_font, int(42 * theme.title_scale * scale / 1.55))
    group_font = _font(theme.body_font, int(19 * scale / 1.55))
    label_font = _font(theme.body_font, int(20 * scale / 1.55))
    meta_font = _font(theme.body_font, int(12 * scale / 1.55))
    note_font = _font(theme.body_font, int(14 * scale / 1.55))
    edge_label_font = _font(theme.body_font, int(13 * scale / 1.55))
    kicker_font = _font(theme.body_font, int(15 * scale / 1.55))
    badge_font = _font(theme.body_font, int(14 * scale / 1.55))

    title_x = int(44 * scale + offset_x)
    title_y = int(18 * scale + offset_y)
    if theme.hero_panel_fill and theme.hero_panel_stroke and theme.hero_kicker_fill and theme.hero_kicker_text:
        panel_x = title_x - 10
        panel_y = title_y - 6
        panel_w = int(canvas_width * 0.42)
        panel_h = int(118 * scale / 1.55)
        draw.rounded_rectangle(
            (panel_x, panel_y, panel_x + panel_w, panel_y + panel_h),
            radius=24,
            fill=_hex_to_rgba(theme.hero_panel_fill),
            outline=theme.hero_panel_stroke,
            width=max(2, int(scale)),
        )
        pill_rect = _draw_pill(
            draw,
            panel_x + 18,
            panel_y + 16,
            _diagram_label(spec),
            kicker_font,
            theme.hero_kicker_fill,
            theme.hero_kicker_text,
        )
        draw.text((panel_x + 18, pill_rect[3] + 12), spec.title, fill=theme.title, font=title_font)
    else:
        draw.text((title_x, title_y), spec.title, fill=theme.title, font=title_font)

    if theme.hero_badge_fill and theme.hero_badge_text:
        badge_text = "YOUTUBE FRAME"
        badge_box = draw.textbbox((0, 0), badge_text, font=badge_font)
        badge_x = canvas_width - (badge_box[2] - badge_box[0]) - 44
        badge_y = 36
        _draw_pill(draw, badge_x, badge_y, badge_text, badge_font, theme.hero_badge_fill, theme.hero_badge_text, pad_x=16, pad_y=8)

    focus_node_id = _pick_focus_node(spec) if theme.focus_outline and theme.focus_glow else None
    for group_id, box in base_layout.group_boxes.items():
        rect = _scaled_box(box, scale, offset_x, offset_y)
        radius = int(theme.group_radius * scale / 1.55)
        _rounded_shadow(draw, rect, radius=radius, fill=theme.shadow)
        draw.rounded_rectangle(rect, radius=radius, fill=_hex_to_rgba(theme.group_fill), outline=theme.group_stroke, width=max(2, int(scale)))
        header_height = max(32, int(36 * scale / 1.55))
        header_rect = (rect[0], rect[1], rect[2], rect[1] + header_height)
        draw.rounded_rectangle(header_rect, radius=radius, fill=_hex_to_rgba(theme.group_header_fill))
        draw.text(
            (rect[0] + max(16, int(16 * scale / 1.55)), rect[1] + max(8, int(8 * scale / 1.55))),
            _group_label(group_id, spec.groups),
            fill=theme.text,
            font=group_font,
        )

    for edge in spec.edges:
        start, end = _edge_points(spec, base_layout.node_boxes, edge)
        start_scaled = (
            int(start[0] * scale + offset_x),
            int(start[1] * scale + offset_y),
        )
        end_scaled = (
            int(end[0] * scale + offset_x),
            int(end[1] * scale + offset_y),
        )
        style_meta = _edge_style(edge.type)
        width = max(2, int(style_meta["width"] * scale / 1.4))
        if style_meta["dash"]:
            on, off = [max(2, int(int(part) * scale / 1.4)) for part in style_meta["dash"].split()]
            dx = end_scaled[0] - start_scaled[0]
            dy = end_scaled[1] - start_scaled[1]
            distance = max((dx * dx + dy * dy) ** 0.5, 1.0)
            step_x = dx / distance
            step_y = dy / distance
            cursor = 0.0
            while cursor < distance:
                seg_start = cursor
                seg_end = min(cursor + on, distance)
                draw.line(
                    (
                        start_scaled[0] + step_x * seg_start,
                        start_scaled[1] + step_y * seg_start,
                        start_scaled[0] + step_x * seg_end,
                        start_scaled[1] + step_y * seg_end,
                    ),
                    fill=theme.edge,
                    width=width,
                )
                cursor += on + off
        else:
            draw.line((start_scaled, end_scaled), fill=theme.edge, width=width)

        left, right = _arrow_head(end_scaled, start_scaled, size=max(10, int(10 * scale / 1.45)))
        draw.polygon([end_scaled, left, right], fill=theme.edge)
        if edge.label:
            center = ((start_scaled[0] + end_scaled[0]) / 2, (start_scaled[1] + end_scaled[1]) / 2 - max(12, int(10 * scale / 1.55)))
            _edge_label(draw, center, edge.label, edge_label_font, theme.edge_label_fill, theme.edge_label_text)

    for node in spec.nodes:
        rect = _scaled_box(base_layout.node_boxes[node.id], scale, offset_x, offset_y)
        radius = int(theme.node_radius * scale / 1.55)
        _rounded_shadow(
            draw,
            rect,
            radius=radius,
            fill=theme.shadow,
            offset=(0, max(4, int(theme.shadow_offset_y * scale / 1.8))),
        )
        draw.rounded_rectangle(
            rect,
            radius=radius,
            fill=_hex_to_rgba(_node_fill(theme, node.type)),
            outline=theme.node_stroke,
            width=max(2, int(scale)),
        )
        if node.id == focus_node_id and theme.focus_glow and theme.focus_outline:
            glow_rect = (rect[0] - 10, rect[1] - 10, rect[2] + 10, rect[3] + 10)
            draw.rounded_rectangle(glow_rect, radius=radius + 10, outline=_hex_to_rgba(theme.focus_glow), width=max(8, int(scale * 3)))
            draw.rounded_rectangle(glow_rect, radius=radius + 10, outline=theme.focus_outline, width=max(2, int(scale)))
        title_pos = (
            rect[0] + max(16, int(16 * scale / 1.55)),
            rect[1] + max(14, int(14 * scale / 1.55)),
        )
        meta_pos = (
            rect[0] + max(16, int(16 * scale / 1.55)),
            rect[1] + max(48, int(48 * scale / 1.55)),
        )
        draw.text(title_pos, node.label, fill=theme.text, font=label_font)
        draw.text(meta_pos, node.type.replace("_", " "), fill=theme.meta, font=meta_font)
        if node.id == focus_node_id and theme.focus_label_fill and theme.focus_label_text:
            _draw_pill(
                draw,
                rect[0] + 10,
                rect[1] - max(32, int(28 * scale / 1.55)),
                "Focus",
                kicker_font,
                theme.focus_label_fill,
                theme.focus_label_text,
                pad_x=12,
                pad_y=6,
            )

    if spec.notes:
        note_text = "  •  ".join(spec.notes)
        note_y = canvas_height - max(42, int(36 * scale / 1.55))
        draw.text((title_x, note_y), note_text, fill=theme.meta, font=note_font)

    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="PNG", quality=95)
    return buffer.getvalue()


def write_styled_png(spec: GraphDiagramSpec, output_path: str, style: str = "studio") -> None:
    with open(output_path, "wb") as handle:
        handle.write(styled_png_bytes(spec, style=style))


def write_style_contact_sheet(
    title: str,
    style_paths: dict[str, str],
    output_path: str,
    columns: int = 3,
) -> None:
    card_width = 480
    card_height = 270
    title_height = 86
    gutter = 24
    padding = 28
    label_height = 34
    styles = sorted(style_paths.items())
    rows = (len(styles) + columns - 1) // columns
    width = padding * 2 + columns * card_width + (columns - 1) * gutter
    height = padding * 2 + title_height + rows * (card_height + label_height) + max(0, rows - 1) * gutter

    canvas = Image.new("RGB", (width, height), "#0e1116")
    draw = ImageDraw.Draw(canvas)
    title_font = _font("/System/Library/Fonts/Avenir Next.ttc", 34)
    label_font = _font("/System/Library/Fonts/Menlo.ttc", 18)
    meta_font = _font("/System/Library/Fonts/HelveticaNeue.ttc", 15)

    draw.text((padding, padding), title, fill="#f5f7fa", font=title_font)
    draw.text((padding, padding + 44), "Style exploration board", fill="#92a0b1", font=meta_font)

    for index, (style_name, path) in enumerate(styles):
        row = index // columns
        col = index % columns
        x = padding + col * (card_width + gutter)
        y = padding + title_height + row * (card_height + label_height + gutter)
        with Image.open(path) as source:
            thumb = source.convert("RGB")
            thumb.thumbnail((card_width, card_height))
            thumb_x = x + (card_width - thumb.width) // 2
            thumb_y = y + (card_height - thumb.height) // 2
            draw.rounded_rectangle(
                (x - 2, y - 2, x + card_width + 2, y + card_height + 2),
                radius=18,
                outline="#283140",
                width=2,
                fill="#151a22",
            )
            canvas.paste(thumb, (thumb_x, thumb_y))
        draw.text((x + 8, y + card_height + 8), style_name, fill="#e8edf2", font=label_font)

    canvas.save(output_path, format="PNG", quality=95)
