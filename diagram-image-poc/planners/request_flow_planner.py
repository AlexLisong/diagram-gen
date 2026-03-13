from __future__ import annotations

from schemas.graph_schema import GraphDiagramSpec, GraphEdge, GraphGroup, GraphNode


def build_request_flow() -> GraphDiagramSpec:
    return GraphDiagramSpec(
        diagram_type="request_flow",
        title="Repo to Slides Request Flow",
        direction="TB",
        groups=[GraphGroup(id="flow", label="Primary Path")],
        nodes=[
            GraphNode(id="select_repo", label="Select Repo", type="user", group="flow"),
            GraphNode(id="outline", label="Generate Outline", type="ai_service", group="flow"),
            GraphNode(id="slides", label="Generate Slides", type="service", group="flow"),
            GraphNode(id="script", label="Generate Script", type="service", group="flow"),
            GraphNode(id="review", label="Review Output", type="verifier", group="flow"),
            GraphNode(id="export", label="Export Deck", type="output", group="flow"),
        ],
        edges=[
            GraphEdge(**{"from": "select_repo", "to": "outline", "label": "brief", "type": "http"}),
            GraphEdge(**{"from": "outline", "to": "slides", "label": "outline", "type": "calls"}),
            GraphEdge(**{"from": "outline", "to": "script", "label": "story beats", "type": "calls"}),
            GraphEdge(**{"from": "slides", "to": "review", "label": "draft slides", "type": "publishes"}),
            GraphEdge(**{"from": "script", "to": "review", "label": "draft script", "type": "publishes"}),
            GraphEdge(**{"from": "review", "to": "export", "label": "approved", "type": "approves"}),
        ],
        notes=[
            "Main path only. Async or retry branches belong in sequence or decision diagrams.",
        ],
        source_refs=["synthetic:repo_to_slides_flow"],
    )
