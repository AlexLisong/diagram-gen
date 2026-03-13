from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

ParticipantType = Literal["actor", "frontend", "service", "database", "external"]
StepStyle = Literal["solid", "dashed"]
StepKind = Literal["request", "response", "stream", "async"]


class SequenceParticipant(BaseModel):
    id: str
    label: str
    type: ParticipantType = "service"


class SequenceStep(BaseModel):
    from_id: str = Field(alias="from")
    to_id: str = Field(alias="to")
    message: str
    style: StepStyle = "solid"
    kind: StepKind = "request"

    model_config = {"populate_by_name": True}


class SequenceDiagramSpec(BaseModel):
    diagram_type: Literal["sequence"] = "sequence"
    title: str
    participants: list[SequenceParticipant]
    steps: list[SequenceStep]
    notes: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_spec(self) -> "SequenceDiagramSpec":
        participant_ids = [participant.id for participant in self.participants]
        if len(participant_ids) != len(set(participant_ids)):
            raise ValueError("Participant ids must be unique")
        if len(participant_ids) > 7:
            raise ValueError("POC sequence diagrams support at most 7 participants")

        known_ids = set(participant_ids)
        for step in self.steps:
            if step.from_id not in known_ids:
                raise ValueError(f"Unknown step source: {step.from_id}")
            if step.to_id not in known_ids:
                raise ValueError(f"Unknown step target: {step.to_id}")
            if len(step.message) > 48:
                raise ValueError(f"Sequence message too long: {step.message}")

        return self
