"""
Graph-based schema — shared by:
  system_context, high_level_architecture, request_flow,
  module_structure, data_flow, deployment, decision_flow, verification_flow
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

NodeType = Literal[
    "frontend", "api", "service", "ai_service", "database",
    "queue", "cache", "storage", "auth", "external_api",
    "worker", "module", "lambda", "app_service", "vm",
    "function", "repo", "pipeline", "user", "s3", "rds", "redis",
    # decision/workflow types
    "decision", "process", "start", "end", "gate",
    # data flow types
    "data_source", "transform", "output",
]

EdgeType = Literal[
    "http", "internal_http", "grpc", "stream",
    "reads", "writes", "publishes", "consumes",
    "deploys_to", "authenticates_via", "triggers",
    "stores_in", "calls", "depends_on",
    # decision/workflow edge types
    "yes", "no", "condition", "next", "fallback",
    # data flow edge types
    "transforms", "produces", "feeds",
]

DiagramType = Literal[
    "system_context",
    "system_architecture",
    "request_flow",
    "data_flow",
    "module_structure",
    "deployment",
    "decision_flow",
    "verification_flow",
    "cloud_resource",
]

Direction = Literal["LR", "TB", "RL", "BT"]


class GraphNode(BaseModel):
    id: str
    label: str
    type: NodeType
    group: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    from_id: str = Field(alias="from")
    to_id: str = Field(alias="to")
    label: Optional[str] = None
    type: EdgeType

    model_config = {"populate_by_name": True}


class GraphGroup(BaseModel):
    id: str
    label: str


class CanonicalGraph(BaseModel):
    title: str
    diagram_type: DiagramType = "system_architecture"
    direction: Direction = "LR"
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    groups: List[GraphGroup] = Field(default_factory=list)
    source_refs: List[str] = Field(default_factory=list)


class DiagramSpec(BaseModel):
    diagram_type: DiagramType
    title: str
    direction: Direction = "LR"
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    groups: List[GraphGroup] = Field(default_factory=list)
    legend: bool = False
    notes: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_refs(self) -> "DiagramSpec":
        node_ids = {n.id for n in self.nodes}
        for edge in self.edges:
            if edge.from_id not in node_ids:
                raise ValueError(f"Edge from_id '{edge.from_id}' not in nodes")
            if edge.to_id not in node_ids:
                raise ValueError(f"Edge to_id '{edge.to_id}' not in nodes")
        for group in self.groups:
            members = [n for n in self.nodes if n.group == group.id]
            if not members:
                raise ValueError(f"Group '{group.id}' has no members")
        return self
