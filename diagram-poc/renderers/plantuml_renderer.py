"""
PlantUML renderer for sequence diagrams.
Converts SequenceSpec → PlantUML string.
"""

from __future__ import annotations

from schemas.sequence_schema import (
    Participant,
    SequenceGroup,
    SequenceSpec,
    SequenceStep,
)

ARROW_STYLES: dict[str, str] = {
    "solid": "->",
    "dashed": "-->",
    "dotted": "..>",
}

RETURN_ARROW_STYLES: dict[str, str] = {
    "solid": "<--",
    "dashed": "<--",
    "dotted": "<..",
}

PARTICIPANT_KEYWORDS: dict[str, str] = {
    "actor": "actor",
    "participant": "participant",
    "boundary": "boundary",
    "control": "control",
    "entity": "entity",
    "database": "database",
    "queue": "queue",
    "collections": "collections",
}


def _render_participant(p: Participant) -> str:
    keyword = PARTICIPANT_KEYWORDS.get(p.type, "participant")
    return f'{keyword} "{p.label}" as {p.id}'


def _render_step(step: SequenceStep) -> list[str]:
    lines: list[str] = []
    if step.is_return:
        arrow = RETURN_ARROW_STYLES.get(step.style, "<--")
        lines.append(f"{step.to_id} {arrow} {step.from_id}: {step.message}")
    else:
        arrow = ARROW_STYLES.get(step.style, "->")
        lines.append(f"{step.from_id} {arrow} {step.to_id}: {step.message}")
    if step.activate:
        lines.append(f"activate {step.to_id}")
    if step.note:
        lines.append(f'note right of {step.to_id}: {step.note}')
    if step.deactivate:
        lines.append(f"deactivate {step.to_id}")
    return lines


def _render_group(group: SequenceGroup) -> list[str]:
    lines: list[str] = []
    lines.append(f"{group.type} {group.label}")
    for step in group.steps:
        lines.extend(f"  {l}" for l in _render_step(step))
    if group.else_label and group.else_steps:
        lines.append(f"else {group.else_label}")
        for step in group.else_steps:
            lines.extend(f"  {l}" for l in _render_step(step))
    lines.append("end")
    return lines


def render_plantuml_sequence(spec: SequenceSpec) -> str:
    """Convert a SequenceSpec into a PlantUML sequence diagram string."""
    lines: list[str] = []
    lines.append("@startuml")
    lines.append(f"title {spec.title}")
    lines.append("")

    # Participants
    for p in spec.participants:
        lines.append(_render_participant(p))
    lines.append("")

    # Steps
    for step in spec.steps:
        if isinstance(step, SequenceGroup):
            lines.extend(_render_group(step))
        else:
            lines.extend(_render_step(step))
    lines.append("")

    # Notes
    for note in spec.notes:
        lines.append(f"note across: {note}")

    lines.append("@enduml")
    return "\n".join(lines)
