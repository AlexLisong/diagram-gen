"""
Sequence diagram schema — independent from graph schema.
Designed for PlantUML sequence diagram rendering.
"""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

StepStyle = Literal["solid", "dashed", "dotted"]

ParticipantType = Literal[
    "actor", "participant", "boundary", "control",
    "entity", "database", "queue", "collections",
]


class Participant(BaseModel):
    id: str
    label: str
    type: ParticipantType = "participant"


class SequenceStep(BaseModel):
    from_id: str = Field(alias="from")
    to_id: str = Field(alias="to")
    message: str
    style: StepStyle = "solid"
    activate: bool = False
    deactivate: bool = False
    note: Optional[str] = None
    is_return: bool = False

    model_config = {"populate_by_name": True}


class SequenceGroup(BaseModel):
    """Wraps steps in alt/loop/opt/par blocks."""
    type: Literal["alt", "loop", "opt", "par", "break", "critical"] = "alt"
    label: str = ""
    steps: List[SequenceStep] = Field(default_factory=list)
    else_label: Optional[str] = None
    else_steps: List[SequenceStep] = Field(default_factory=list)


class SequenceSpec(BaseModel):
    diagram_type: Literal["sequence"] = "sequence"
    title: str
    participants: List[Participant]
    steps: List[SequenceStep | SequenceGroup]
    notes: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_participant_refs(self) -> "SequenceSpec":
        pids = {p.id for p in self.participants}
        for step in self.steps:
            if isinstance(step, SequenceStep):
                if step.from_id not in pids:
                    raise ValueError(f"Step from_id '{step.from_id}' not in participants")
                if step.to_id not in pids:
                    raise ValueError(f"Step to_id '{step.to_id}' not in participants")
        return self
