from __future__ import annotations

from schemas.graph_schema import GraphDiagramSpec, GraphEdge, GraphGroup, GraphNode


def build_data_flow() -> GraphDiagramSpec:
    return GraphDiagramSpec(
        diagram_type="data_flow",
        title="Content OS Data Flow",
        direction="LR",
        groups=[
            GraphGroup(id="sources", label="Sources"),
            GraphGroup(id="processing", label="Processing"),
            GraphGroup(id="artifacts", label="Artifacts"),
        ],
        nodes=[
            GraphNode(id="repo", label="Raw Repo Data", type="repo", group="sources"),
            GraphNode(id="docs", label="Raw Docs", type="document", group="sources"),
            GraphNode(id="cloud", label="Cloud Snapshot", type="cloud", group="sources"),
            GraphNode(id="normalize", label="Normalized Graph", type="service", group="processing"),
            GraphNode(id="diagram_specs", label="Diagram Specs", type="document", group="processing"),
            GraphNode(id="slides", label="Slides", type="output", group="artifacts"),
            GraphNode(id="script", label="Script", type="output", group="artifacts"),
            GraphNode(id="summary", label="Evidence Summary", type="output", group="artifacts"),
        ],
        edges=[
            GraphEdge(**{"from": "repo", "to": "normalize", "label": "extract", "type": "reads"}),
            GraphEdge(**{"from": "docs", "to": "normalize", "label": "extract", "type": "reads"}),
            GraphEdge(**{"from": "cloud", "to": "normalize", "label": "extract", "type": "reads"}),
            GraphEdge(**{"from": "normalize", "to": "diagram_specs", "label": "canonicalize", "type": "writes"}),
            GraphEdge(**{"from": "diagram_specs", "to": "slides", "label": "render", "type": "writes"}),
            GraphEdge(**{"from": "diagram_specs", "to": "script", "label": "narrate", "type": "writes"}),
            GraphEdge(**{"from": "normalize", "to": "summary", "label": "evidence", "type": "writes"}),
        ],
        notes=[
            "This view is about data stages, not service boundaries.",
        ],
        source_refs=["synthetic:content_os_data_flow"],
    )
