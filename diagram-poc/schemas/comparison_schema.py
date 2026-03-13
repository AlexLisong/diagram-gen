"""
Comparison / Before-After schema — independent from graph schema.
Rendered as HTML template, not Mermaid/PlantUML.
"""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ComparisonSide(BaseModel):
    title: str
    items: List[str]
    icon: Optional[str] = None  # emoji or icon name
    color: str = "#666"


class ComparisonSpec(BaseModel):
    diagram_type: Literal["before_after", "comparison"] = "before_after"
    title: str
    left: ComparisonSide
    right: ComparisonSide
    improvement_notes: List[str] = Field(default_factory=list)
