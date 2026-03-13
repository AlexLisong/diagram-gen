from __future__ import annotations

from pathlib import Path

from schemas.graph_schema import GraphDiagramSpec, GraphEdge, GraphGroup, GraphNode

IGNORE_DIRS = {
    ".git",
    ".next",
    "node_modules",
    ".turbo",
    ".idea",
    ".vscode",
    "__pycache__",
    ".venv",
    "outputs",
}

GROUP_MAP = {
    "schemas": "design",
    "extractors": "ingestion",
    "planners": "planning",
    "renderers": "rendering",
    "exporters": "delivery",
    "tests": "quality",
}

TYPE_MAP = {
    "schemas": "document",
    "extractors": "service",
    "planners": "ai_service",
    "renderers": "frontend",
    "exporters": "output",
    "tests": "verifier",
}

EDGE_RULES = [
    ("extractors", "schemas", "shape spec", "depends_on"),
    ("planners", "schemas", "build spec", "depends_on"),
    ("planners", "extractors", "source scan", "calls"),
    ("renderers", "schemas", "render spec", "depends_on"),
    ("exporters", "renderers", "emit assets", "calls"),
]


def extract_repo_module_diagram(repo_path: str) -> GraphDiagramSpec:
    root = Path(repo_path)
    if not root.exists():
        raise FileNotFoundError(f"Missing repo path: {repo_path}")

    top_dirs = [
        child.name
        for child in sorted(root.iterdir())
        if child.is_dir() and child.name not in IGNORE_DIRS
    ]

    preferred = ["schemas", "extractors", "planners", "renderers", "exporters", "tests"]
    selected = [name for name in preferred if name in top_dirs]
    if not selected:
        selected = top_dirs[:6]

    groups = [
        GraphGroup(id="design", label="Schemas"),
        GraphGroup(id="ingestion", label="Extractors"),
        GraphGroup(id="planning", label="Planners"),
        GraphGroup(id="rendering", label="Renderers"),
        GraphGroup(id="delivery", label="Exporters"),
        GraphGroup(id="quality", label="Quality"),
    ]

    nodes = [
        GraphNode(
            id=name,
            label=name,
            type=TYPE_MAP.get(name, "module"),
            group=GROUP_MAP.get(name, "design"),
            metadata={"path": str(root / name)},
        )
        for name in selected
    ]

    node_ids = {node.id for node in nodes}
    edges = [
        GraphEdge(**{"from": source, "to": target, "label": label, "type": edge_type})
        for source, target, label, edge_type in EDGE_RULES
        if source in node_ids and target in node_ids
    ]

    active_groups = [group for group in groups if any(node.group == group.id for node in nodes)]
    return GraphDiagramSpec(
        diagram_type="module_structure",
        title=f"{root.name} Module Structure",
        direction="LR",
        groups=active_groups,
        nodes=nodes,
        edges=edges,
        notes=[
            "Rule-based extraction from top-level directories.",
            "This is a module map, not a raw file tree dump.",
        ],
        source_refs=[str(root)],
    )
