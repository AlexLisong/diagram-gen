from __future__ import annotations

from schemas.graph_schema import GraphDiagramSpec, GraphEdge, GraphNode

NODE_CLASSES = {
    "user": "user",
    "frontend": "frontend",
    "api": "api",
    "service": "service",
    "ai_service": "ai",
    "database": "database",
    "storage": "storage",
    "external_api": "external",
    "module": "module",
    "repo": "repo",
    "document": "document",
    "cloud": "cloud",
    "decision": "decision",
    "verifier": "verifier",
    "output": "output",
}


def _node_shape(node: GraphNode) -> str:
    label = node.label.replace('"', "'")
    if node.type == "user":
        return f"{node.id}([{label}])"
    if node.type in {"database", "storage"}:
        return f"{node.id}[({label})]"
    if node.type == "decision":
        return f"{node.id}{{{label}}}"
    if node.type == "output":
        return f"{node.id}[/{label}/]"
    return f"{node.id}[{label}]"


def _edge_arrow(edge: GraphEdge) -> str:
    if edge.type in {"stream", "publishes", "consumes", "branches"}:
        return "-.->"
    return "-->"


def _edge_line(edge: GraphEdge) -> str:
    label = edge.label.replace('"', '\\"')
    arrow = _edge_arrow(edge)
    if label:
        return f"{edge.from_id} {arrow}|{label}| {edge.to_id}"
    return f"{edge.from_id} {arrow} {edge.to_id}"


def mermaid_string(spec: GraphDiagramSpec) -> str:
    lines: list[str] = [
        "---",
        f"title: {spec.title}",
        "---",
        f"flowchart {spec.direction}",
    ]

    grouped_node_ids: set[str] = set()
    for group in spec.groups:
        members = [node for node in spec.nodes if node.group == group.id]
        if not members:
            continue
        lines.append(f'  subgraph {group.id}["{group.label}"]')
        for node in members:
            grouped_node_ids.add(node.id)
            lines.append(f"    {_node_shape(node)}")
        lines.append("  end")

    for node in spec.nodes:
        if node.id not in grouped_node_ids:
            lines.append(f"  {_node_shape(node)}")

    for edge in spec.edges:
        lines.append(f"  {_edge_line(edge)}")

    used_classes: set[str] = set()
    for node in spec.nodes:
        class_name = NODE_CLASSES.get(node.type, "default")
        used_classes.add(class_name)
        lines.append(f"  class {node.id} {class_name}")

    style_lines = {
        "user": "fill:#fde6b8,stroke:#8a6d3b,color:#1f2937",
        "frontend": "fill:#f8d6b5,stroke:#8a5a2b,color:#1f2937",
        "api": "fill:#c9dcf6,stroke:#355c8a,color:#1f2937",
        "service": "fill:#d5ecd2,stroke:#48724b,color:#1f2937",
        "ai": "fill:#bddfd6,stroke:#2d6a68,color:#1f2937",
        "database": "fill:#d9d2f5,stroke:#5d4f8f,color:#1f2937",
        "storage": "fill:#fff0bf,stroke:#927127,color:#1f2937",
        "external": "fill:#f7c7ce,stroke:#9c4050,color:#1f2937",
        "module": "fill:#d7e8f2,stroke:#47667a,color:#1f2937",
        "repo": "fill:#d8d8d8,stroke:#5a5a5a,color:#1f2937",
        "document": "fill:#f6e8c3,stroke:#8a7750,color:#1f2937",
        "cloud": "fill:#d5e7ff,stroke:#4067a8,color:#1f2937",
        "decision": "fill:#fff2cc,stroke:#9c7a00,color:#1f2937",
        "verifier": "fill:#d9ead3,stroke:#4f7d43,color:#1f2937",
        "output": "fill:#fce5cd,stroke:#9b5f1b,color:#1f2937",
        "default": "fill:#e5e7eb,stroke:#6b7280,color:#1f2937",
    }
    for class_name in sorted(used_classes):
        lines.append(f"  classDef {class_name} {style_lines[class_name]}")

    if spec.notes:
        lines.append("  %% Notes")
        for note in spec.notes:
            lines.append(f"  %% {note}")

    return "\n".join(lines) + "\n"
