from __future__ import annotations

from html import escape
from math import atan2, cos, sin

from schemas.graph_schema import GraphDiagramSpec, GraphEdge, GraphGroup, GraphNode

CARD_WIDTH = 190
CARD_HEIGHT = 68
GROUP_GAP = 72
NODE_GAP = 26
PAGE_PADDING = 44
HEADER_HEIGHT = 78
FOOTER_HEIGHT = 30

COLORS = {
    "page": "#f5f1ea",
    "title": "#1f2937",
    "group_fill": "#e9dfd0",
    "group_stroke": "#b9a487",
    "edge": "#6b7280",
    "note": "#5b6470",
    "text": "#1f2937",
    "node_stroke": "#243447",
}

NODE_FILL = {
    "frontend": "#f8d6b5",
    "api": "#c9dcf6",
    "service": "#d5ecd2",
    "ai_service": "#bddfd6",
    "database": "#d9d2f5",
    "cache": "#ead1dc",
    "storage": "#fff0bf",
    "external_api": "#f7c7ce",
    "module": "#d7e8f2",
    "user": "#fde6b8",
    "repo": "#d8d8d8",
    "document": "#f6e8c3",
    "cloud": "#d5e7ff",
    "decision": "#fff2cc",
    "verifier": "#d9ead3",
    "output": "#fce5cd",
}

EDGE_STYLE = {
    "stream": {"dash": "8 6", "width": 2},
    "depends_on": {"dash": "4 4", "width": 2},
    "publishes": {"dash": "2 6", "width": 2},
    "consumes": {"dash": "2 6", "width": 2},
    "branches": {"dash": "6 6", "width": 2},
    "default": {"dash": "", "width": 2},
}


class Box:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def cx(self) -> int:
        return self.x + self.width // 2

    @property
    def cy(self) -> int:
        return self.y + self.height // 2


class Layout:
    def __init__(self, width: int, height: int, node_boxes: dict[str, Box], group_boxes: dict[str, Box]) -> None:
        self.width = width
        self.height = height
        self.node_boxes = node_boxes
        self.group_boxes = group_boxes


def _group_order(spec: GraphDiagramSpec) -> list[str]:
    explicit = [group.id for group in spec.groups]
    extras = sorted({node.group for node in spec.nodes if node.group and node.group not in explicit})
    if extras:
        return explicit + extras
    if explicit:
        return explicit
    return ["ungrouped"]


def _group_members(spec: GraphDiagramSpec, group_id: str) -> list[GraphNode]:
    if group_id == "ungrouped":
        return [node for node in spec.nodes if not node.group]
    return [node for node in spec.nodes if node.group == group_id]


def layout_diagram(spec: GraphDiagramSpec) -> Layout:
    group_ids = _group_order(spec)
    node_boxes: dict[str, Box] = {}
    group_boxes: dict[str, Box] = {}
    cursor_x = PAGE_PADDING
    cursor_y = PAGE_PADDING + HEADER_HEIGHT
    max_x = 0
    max_y = 0

    for group_id in group_ids:
        nodes = _group_members(spec, group_id)
        if not nodes:
            continue

        if spec.direction == "LR":
            group_x = cursor_x
            group_y = PAGE_PADDING + HEADER_HEIGHT
            inner_y = group_y + 38
            for index, node in enumerate(nodes):
                y = inner_y + index * (CARD_HEIGHT + NODE_GAP)
                node_boxes[node.id] = Box(group_x + 18, y, CARD_WIDTH, CARD_HEIGHT)
            group_height = 38 + len(nodes) * CARD_HEIGHT + max(0, len(nodes) - 1) * NODE_GAP + 20
            group_width = CARD_WIDTH + 36
            group_boxes[group_id] = Box(group_x, group_y, group_width, group_height)
            cursor_x += group_width + GROUP_GAP
            max_x = max(max_x, group_x + group_width)
            max_y = max(max_y, group_y + group_height)
        else:
            group_x = PAGE_PADDING
            group_y = cursor_y
            inner_x = group_x + 18
            for index, node in enumerate(nodes):
                x = inner_x + index * (CARD_WIDTH + NODE_GAP)
                node_boxes[node.id] = Box(x, group_y + 38, CARD_WIDTH, CARD_HEIGHT)
            group_width = 36 + len(nodes) * CARD_WIDTH + max(0, len(nodes) - 1) * NODE_GAP
            group_height = CARD_HEIGHT + 58
            group_boxes[group_id] = Box(group_x, group_y, group_width, group_height)
            cursor_y += group_height + GROUP_GAP
            max_x = max(max_x, group_x + group_width)
            max_y = max(max_y, group_y + group_height)

    width = max(max_x + PAGE_PADDING, 720)
    height = max(max_y + FOOTER_HEIGHT, 420)
    return Layout(width=width, height=height, node_boxes=node_boxes, group_boxes=group_boxes)


def _group_label(group_id: str, groups: list[GraphGroup]) -> str:
    for group in groups:
        if group.id == group_id:
            return group.label
    if group_id == "ungrouped":
        return "Ungrouped"
    return group_id.replace("_", " ").title()


def _node_fill(node_type: str) -> str:
    return NODE_FILL.get(node_type, "#dce7ef")


def _edge_points(spec: GraphDiagramSpec, boxes: dict[str, Box], edge: GraphEdge) -> tuple[tuple[int, int], tuple[int, int]]:
    source = boxes[edge.from_id]
    target = boxes[edge.to_id]
    if spec.direction == "LR":
        if source.cx <= target.cx:
            return (source.x + source.width, source.cy), (target.x, target.cy)
        return (source.x, source.cy), (target.x + target.width, target.cy)
    if source.cy <= target.cy:
        return (source.cx, source.y + source.height), (target.cx, target.y)
    return (source.cx, source.y), (target.cx, target.y + target.height)


def _edge_style(edge_type: str) -> dict[str, object]:
    return EDGE_STYLE.get(edge_type, EDGE_STYLE["default"])


def _arrow_head(end: tuple[int, int], start: tuple[int, int], size: int = 9) -> tuple[tuple[float, float], tuple[float, float]]:
    angle = atan2(end[1] - start[1], end[0] - start[0])
    left = (end[0] - size * cos(angle - 0.45), end[1] - size * sin(angle - 0.45))
    right = (end[0] - size * cos(angle + 0.45), end[1] - size * sin(angle + 0.45))
    return left, right


def svg_string(spec: GraphDiagramSpec) -> str:
    layout = layout_diagram(spec)
    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{layout.width}" height="{layout.height}" viewBox="0 0 {layout.width} {layout.height}">',
        f'  <rect width="{layout.width}" height="{layout.height}" fill="{COLORS["page"]}" />',
        f'  <text x="{PAGE_PADDING}" y="38" font-size="28" font-family="Helvetica, Arial, sans-serif" fill="{COLORS["title"]}" font-weight="700">{escape(spec.title)}</text>',
    ]

    for group_id, box in layout.group_boxes.items():
        lines.append(
            f'  <rect x="{box.x}" y="{box.y}" width="{box.width}" height="{box.height}" rx="16" fill="{COLORS["group_fill"]}" stroke="{COLORS["group_stroke"]}" stroke-width="2" />'
        )
        lines.append(
            f'  <text x="{box.x + 16}" y="{box.y + 24}" font-size="16" font-family="Helvetica, Arial, sans-serif" fill="{COLORS["text"]}" font-weight="600">{escape(_group_label(group_id, spec.groups))}</text>'
        )

    for edge in spec.edges:
        start, end = _edge_points(spec, layout.node_boxes, edge)
        style = _edge_style(edge.type)
        dash = style["dash"]
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        lines.append(
            f'  <line x1="{start[0]}" y1="{start[1]}" x2="{end[0]}" y2="{end[1]}" stroke="{COLORS["edge"]}" stroke-width="{style["width"]}"{dash_attr} />'
        )
        left, right = _arrow_head(end, start)
        lines.append(
            f'  <polygon points="{end[0]},{end[1]} {left[0]:.2f},{left[1]:.2f} {right[0]:.2f},{right[1]:.2f}" fill="{COLORS["edge"]}" />'
        )
        if edge.label:
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2 - 8
            lines.append(
                f'  <text x="{mid_x:.1f}" y="{mid_y:.1f}" text-anchor="middle" font-size="12" font-family="Helvetica, Arial, sans-serif" fill="{COLORS["note"]}">{escape(edge.label)}</text>'
            )

    for node in spec.nodes:
        box = layout.node_boxes[node.id]
        lines.append(
            f'  <rect x="{box.x}" y="{box.y}" width="{box.width}" height="{box.height}" rx="14" fill="{_node_fill(node.type)}" stroke="{COLORS["node_stroke"]}" stroke-width="2" />'
        )
        lines.append(
            f'  <text x="{box.x + 14}" y="{box.y + 26}" font-size="15" font-family="Helvetica, Arial, sans-serif" fill="{COLORS["text"]}" font-weight="700">{escape(node.label)}</text>'
        )
        lines.append(
            f'  <text x="{box.x + 14}" y="{box.y + 48}" font-size="11" font-family="Helvetica, Arial, sans-serif" fill="{COLORS["note"]}">{escape(node.type.replace("_", " "))}</text>'
        )

    if spec.notes:
        start_y = layout.height - 14 - max(0, len(spec.notes) - 1) * 14
        for index, note in enumerate(spec.notes):
            lines.append(
                f'  <text x="{PAGE_PADDING}" y="{start_y + index * 14}" font-size="11" font-family="Helvetica, Arial, sans-serif" fill="{COLORS["note"]}">{escape(note)}</text>'
            )

    lines.append("</svg>")
    return "\n".join(lines)


def write_svg(spec: GraphDiagramSpec, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(svg_string(spec))
