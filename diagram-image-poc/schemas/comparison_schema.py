from __future__ import annotations

from pydantic import BaseModel, Field


class ComparisonColumn(BaseModel):
    title: str
    items: list[str]


class ComparisonDiagramSpec(BaseModel):
    diagram_type: str = "before_after"
    title: str
    left: ComparisonColumn
    right: ComparisonColumn
    notes: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
