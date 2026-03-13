from __future__ import annotations

from schemas.graph_schema import GraphDiagramSpec, GraphEdge, GraphGroup, GraphNode


def build_decision_flow() -> GraphDiagramSpec:
    return GraphDiagramSpec(
        diagram_type="decision_flow",
        title="Content OS Decision Flow",
        direction="TB",
        groups=[
            GraphGroup(id="checks", label="Checks"),
            GraphGroup(id="actions", label="Actions"),
        ],
        nodes=[
            GraphNode(id="docs_ready", label="Docs complete?", type="decision", group="checks"),
            GraphNode(id="cloud_ready", label="Cloud snapshot ready?", type="decision", group="checks"),
            GraphNode(id="draft", label="Generate draft", type="ai_service", group="actions"),
            GraphNode(id="human_review", label="Human review needed?", type="decision", group="checks"),
            GraphNode(id="request_input", label="Request more input", type="output", group="actions"),
            GraphNode(id="publish", label="Publish deck", type="output", group="actions"),
        ],
        edges=[
            GraphEdge(**{"from": "docs_ready", "to": "cloud_ready", "label": "yes", "type": "branches"}),
            GraphEdge(**{"from": "docs_ready", "to": "request_input", "label": "no", "type": "branches"}),
            GraphEdge(**{"from": "cloud_ready", "to": "draft", "label": "yes", "type": "branches"}),
            GraphEdge(**{"from": "cloud_ready", "to": "request_input", "label": "no", "type": "branches"}),
            GraphEdge(**{"from": "draft", "to": "human_review", "label": "confidence < 0.9", "type": "branches"}),
            GraphEdge(**{"from": "human_review", "to": "publish", "label": "no", "type": "branches"}),
            GraphEdge(**{"from": "human_review", "to": "request_input", "label": "yes", "type": "branches"}),
        ],
        notes=[
            "Decision diagrams stay useful only when branches remain shallow and legible.",
        ],
        source_refs=["synthetic:decision_flow"],
    )
