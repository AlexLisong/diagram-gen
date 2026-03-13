from __future__ import annotations

from schemas.sequence_schema import SequenceDiagramSpec, SequenceParticipant, SequenceStep


def build_sequence_diagram() -> SequenceDiagramSpec:
    return SequenceDiagramSpec(
        title="Repo to Slides Streaming Sequence",
        participants=[
            SequenceParticipant(id="user", label="Creator", type="actor"),
            SequenceParticipant(id="ui", label="Frontend", type="frontend"),
            SequenceParticipant(id="api", label="Gateway API", type="service"),
            SequenceParticipant(id="agent", label="Planner Agent", type="service"),
            SequenceParticipant(id="renderer", label="Diagram Renderer", type="service"),
        ],
        steps=[
            SequenceStep(**{"from": "user", "to": "ui", "message": "Select repo"}),
            SequenceStep(**{"from": "ui", "to": "api", "message": "POST /projects/{repo}"}),
            SequenceStep(**{"from": "api", "to": "agent", "message": "Build outline"}),
            SequenceStep(**{"from": "agent", "to": "renderer", "message": "Render graph DSL", "kind": "async"}),
            SequenceStep(**{"from": "renderer", "to": "agent", "message": "Mermaid assets", "kind": "response"}),
            SequenceStep(**{"from": "agent", "to": "api", "message": "Stream status", "kind": "stream"}),
            SequenceStep(**{"from": "api", "to": "ui", "message": "SSE updates", "kind": "stream"}),
        ],
        notes=[
            "Sequence POC stays under 5 participants to avoid unreadable output.",
        ],
        source_refs=["synthetic:streaming_sequence"],
    )
