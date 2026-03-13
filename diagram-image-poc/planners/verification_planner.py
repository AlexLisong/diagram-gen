from __future__ import annotations

from schemas.graph_schema import GraphDiagramSpec, GraphEdge, GraphGroup, GraphNode


def build_verification_flow() -> GraphDiagramSpec:
    return GraphDiagramSpec(
        diagram_type="verification_flow",
        title="Verification and Evidence Flow",
        direction="LR",
        groups=[
            GraphGroup(id="sources", label="Sources"),
            GraphGroup(id="verification", label="Verification"),
            GraphGroup(id="outputs", label="Outputs"),
        ],
        nodes=[
            GraphNode(id="repo", label="Repo", type="repo", group="sources"),
            GraphNode(id="docs", label="Docs", type="document", group="sources"),
            GraphNode(id="cloud", label="Cloud", type="cloud", group="sources"),
            GraphNode(id="extract", label="Evidence Extraction", type="service", group="verification"),
            GraphNode(id="claims", label="Claim Builder", type="service", group="verification"),
            GraphNode(id="verify", label="Verifier", type="verifier", group="verification"),
            GraphNode(id="review", label="Human Review", type="user", group="verification"),
            GraphNode(id="approved", label="Approved Output", type="output", group="outputs"),
        ],
        edges=[
            GraphEdge(**{"from": "repo", "to": "extract", "label": "facts", "type": "reads"}),
            GraphEdge(**{"from": "docs", "to": "extract", "label": "facts", "type": "reads"}),
            GraphEdge(**{"from": "cloud", "to": "extract", "label": "facts", "type": "reads"}),
            GraphEdge(**{"from": "extract", "to": "claims", "label": "evidence", "type": "writes"}),
            GraphEdge(**{"from": "claims", "to": "verify", "label": "claims", "type": "calls"}),
            GraphEdge(**{"from": "verify", "to": "review", "label": "low confidence", "type": "branches"}),
            GraphEdge(**{"from": "verify", "to": "approved", "label": "pass", "type": "approves"}),
            GraphEdge(**{"from": "review", "to": "approved", "label": "approved", "type": "approves"}),
        ],
        notes=[
            "This POC makes the anti-hallucination path explicit rather than implicit.",
        ],
        source_refs=["synthetic:verification_flow"],
    )
