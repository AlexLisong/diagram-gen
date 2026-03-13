"""
Deterministic Mermaid renderer.
Converts DiagramSpec → Mermaid flowchart string.
Supports all graph-based diagram types.
"""

from __future__ import annotations

from schemas.graph_schema import DiagramSpec, GraphEdge, GraphNode

# ── Edge style mapping ──────────────────────────────────────────────

EDGE_STYLES: dict[str, str] = {
    "http":               "-->",
    "internal_http":      "-->",
    "grpc":               "-->",
    "stream":             "-.->",
    "reads":              "-->",
    "writes":             "-->",
    "publishes":          "-..->",
    "consumes":           "-..->",
    "deploys_to":         "==>",
    "authenticates_via":  "-.->",
    "triggers":           "-->",
    "stores_in":          "-->",
    "calls":              "-->",
    "depends_on":         "-.->",
    # decision/workflow
    "yes":                "-->",
    "no":                 "-.->",
    "condition":          "-->",
    "next":               "-->",
    "fallback":           "-.->",
    # data flow
    "transforms":         "-->",
    "produces":           "-->",
    "feeds":              "-->",
}

# ── Node shape mapping ──────────────────────────────────────────────

NODE_SHAPES: dict[str, tuple[str, str]] = {
    "frontend":     ("(", ")"),
    "user":         ("(", ")"),
    "database":     ("[(", ")]"),
    "cache":        ("[(", ")]"),
    "redis":        ("[(", ")]"),
    "rds":          ("[(", ")]"),
    "queue":        ("[[", "]]"),
    "storage":      ("[(", ")]"),
    "s3":           ("[(", ")]"),
    "lambda":       ("{{", "}}"),
    "function":     ("{{", "}}"),
    "external_api": (">", "]"),
    # decision/workflow
    "decision":     ("{", "}"),
    "start":        ("([", "])"),
    "end":          ("([", "])"),
    "gate":         ("{", "}"),
    # data flow
    "data_source":  (">", "]"),
    "transform":    ("[[", "]]"),
    "output":       ("([", "])"),
}

DEFAULT_SHAPE = ("[", "]")


def _node_shape(node: GraphNode) -> str:
    left, right = NODE_SHAPES.get(node.type, DEFAULT_SHAPE)
    return f"{node.id}{left}{node.label}{right}"


def _edge_line(edge: GraphEdge) -> str:
    arrow = EDGE_STYLES.get(edge.type, "-->")
    if edge.label:
        return f"  {edge.from_id} {arrow}|{edge.label}| {edge.to_id}"
    return f"  {edge.from_id} {arrow} {edge.to_id}"


def render_mermaid(spec: DiagramSpec) -> str:
    """Convert a DiagramSpec into a Mermaid flowchart string."""
    lines: list[str] = []
    lines.append(f"flowchart {spec.direction}")
    lines.append("")

    # Group nodes by group id
    grouped: dict[str | None, list[GraphNode]] = {}
    for node in spec.nodes:
        grouped.setdefault(node.group, []).append(node)

    group_map = {g.id: g for g in spec.groups}

    # Render grouped nodes in subgraphs
    for gid, nodes in grouped.items():
        if gid and gid in group_map:
            label = group_map[gid].label
            lines.append(f"  subgraph {gid}[{label}]")
            for node in nodes:
                lines.append(f"    {_node_shape(node)}")
            lines.append("  end")
            lines.append("")
        else:
            for node in nodes:
                lines.append(f"  {_node_shape(node)}")
            lines.append("")

    # Render edges
    for edge in spec.edges:
        lines.append(_edge_line(edge))

    return "\n".join(lines)
