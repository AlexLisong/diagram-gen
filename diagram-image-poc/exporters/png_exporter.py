from __future__ import annotations

from io import BytesIO

try:
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Pillow is required for PNG generation. Use a Python environment with Pillow installed."
    ) from exc

from schemas.graph_schema import GraphDiagramSpec
from exporters.svg_exporter import (
    COLORS,
    PAGE_PADDING,
    _arrow_head,
    _edge_points,
    _edge_style,
    _group_label,
    _node_fill,
    layout_diagram,
)


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("Helvetica.ttc", size)
    except OSError:
        return ImageFont.load_default()


def _draw_dashed_line(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str,
    width: int,
    dash_pattern: str,
) -> None:
    on, off = [int(part) for part in dash_pattern.split()]
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    distance = max((dx * dx + dy * dy) ** 0.5, 1.0)
    step_x = dx / distance
    step_y = dy / distance
    cursor = 0.0
    while cursor < distance:
        seg_start = cursor
        seg_end = min(cursor + on, distance)
        draw.line(
            (
                start[0] + step_x * seg_start,
                start[1] + step_y * seg_start,
                start[0] + step_x * seg_end,
                start[1] + step_y * seg_end,
            ),
            fill=color,
            width=width,
        )
        cursor += on + off


def png_bytes(spec: GraphDiagramSpec) -> bytes:
    layout = layout_diagram(spec)
    image = Image.new("RGB", (layout.width, layout.height), COLORS["page"])
    draw = ImageDraw.Draw(image)
    title_font = _font(28)
    group_font = _font(16)
    label_font = _font(15)
    meta_font = _font(11)
    note_font = _font(11)

    draw.text((PAGE_PADDING, 12), spec.title, fill=COLORS["title"], font=title_font)

    for group_id, box in layout.group_boxes.items():
        draw.rounded_rectangle(
            (box.x, box.y, box.x + box.width, box.y + box.height),
            radius=16,
            fill=COLORS["group_fill"],
            outline=COLORS["group_stroke"],
            width=2,
        )
        draw.text((box.x + 16, box.y + 8), _group_label(group_id, spec.groups), fill=COLORS["text"], font=group_font)

    for edge in spec.edges:
        start, end = _edge_points(spec, layout.node_boxes, edge)
        style = _edge_style(edge.type)
        if style["dash"]:
            _draw_dashed_line(draw, start, end, COLORS["edge"], int(style["width"]), style["dash"])
        else:
            draw.line((start, end), fill=COLORS["edge"], width=int(style["width"]))
        left, right = _arrow_head(end, start)
        draw.polygon([end, left, right], fill=COLORS["edge"])
        if edge.label:
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2 - 14
            draw.text((mid_x - len(edge.label) * 3, mid_y), edge.label, fill=COLORS["note"], font=meta_font)

    for node in spec.nodes:
        box = layout.node_boxes[node.id]
        draw.rounded_rectangle(
            (box.x, box.y, box.x + box.width, box.y + box.height),
            radius=14,
            fill=_node_fill(node.type),
            outline=COLORS["node_stroke"],
            width=2,
        )
        draw.text((box.x + 14, box.y + 12), node.label, fill=COLORS["text"], font=label_font)
        draw.text((box.x + 14, box.y + 38), node.type.replace("_", " "), fill=COLORS["note"], font=meta_font)

    if spec.notes:
        start_y = layout.height - 18 - max(0, len(spec.notes) - 1) * 14
        for index, note in enumerate(spec.notes):
            draw.text((PAGE_PADDING, start_y + index * 14), note, fill=COLORS["note"], font=note_font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def write_png(spec: GraphDiagramSpec, output_path: str) -> None:
    with open(output_path, "wb") as handle:
        handle.write(png_bytes(spec))
