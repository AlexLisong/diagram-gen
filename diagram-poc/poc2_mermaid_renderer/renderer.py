"""
POC 2: Deterministic Mermaid renderer.
Converts DiagramSpec → Mermaid string.
No LLM involved — pure template logic.
"""

from __future__ import annotations

import sys
sys.path.insert(0, "..")

from models import DiagramSpec, GraphEdge, GraphNode

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
    # default: rectangle
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
            # Ungrouped nodes at top level
            for node in nodes:
                lines.append(f"  {_node_shape(node)}")
            lines.append("")

    # Render edges
    for edge in spec.edges:
        lines.append(_edge_line(edge))

    return "\n".join(lines)


# ── Demo ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from models import GraphGroup

    spec = DiagramSpec(
        diagram_type="system_architecture",
        title="Tapp AI Copilot Architecture",
        direction="LR",
        nodes=[
            GraphNode(id="user", label="User", type="user", group="client"),
            GraphNode(id="frontend", label="React Frontend", type="frontend", group="client"),
            GraphNode(id="api", label="C# Backend", type="api", group="backend"),
            GraphNode(id="ai", label="Python AI Service", type="ai_service", group="backend"),
            GraphNode(id="db", label="SQL Server", type="database", group="data"),
            GraphNode(id="redis", label="Redis Cache", type="cache", group="data"),
        ],
        edges=[
            GraphEdge(**{"from": "user", "to": "frontend", "label": "Browser", "type": "http"}),
            GraphEdge(**{"from": "frontend", "to": "api", "label": "REST API", "type": "http"}),
            GraphEdge(**{"from": "api", "to": "ai", "label": "AI Request", "type": "internal_http"}),
            GraphEdge(**{"from": "ai", "to": "frontend", "label": "SSE Stream", "type": "stream"}),
            GraphEdge(**{"from": "api", "to": "db", "label": "SQL", "type": "reads"}),
            GraphEdge(**{"from": "api", "to": "redis", "label": "Cache", "type": "reads"}),
        ],
        groups=[
            GraphGroup(id="client", label="Client Layer"),
            GraphGroup(id="backend", label="Backend Layer"),
            GraphGroup(id="data", label="Data Layer"),
        ],
    )

    mermaid = render_mermaid(spec)
    print(mermaid)

    # Write to file
    with open("output.mmd", "w") as f:
        f.write(mermaid)
    print("\n✓ Written to output.mmd")
