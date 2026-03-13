from __future__ import annotations

from schemas.sequence_schema import SequenceDiagramSpec, SequenceParticipant, SequenceStep


def _participant_line(participant: SequenceParticipant) -> str:
    if participant.type == "actor":
        return f'actor "{participant.label}" as {participant.id}'
    if participant.type == "database":
        return f'database "{participant.label}" as {participant.id}'
    return f'participant "{participant.label}" as {participant.id}'


def _arrow(step: SequenceStep) -> str:
    if step.kind == "async":
        return "->>"
    if step.kind == "response":
        return "-->"
    if step.kind == "stream":
        return "-->>"
    if step.style == "dashed":
        return "-->"
    return "->"


def plantuml_string(spec: SequenceDiagramSpec) -> str:
    lines = [
        "@startuml",
        "skinparam Shadowing false",
        "skinparam DefaultFontName Helvetica",
        f"title {spec.title}",
    ]

    for participant in spec.participants:
        lines.append(_participant_line(participant))

    for step in spec.steps:
        lines.append(f'{step.from_id} {_arrow(step)} {step.to_id}: {step.message}')

    for note in spec.notes:
        lines.append(f"note over {spec.participants[0].id}: {note}")

    lines.append("@enduml")
    return "\n".join(lines) + "\n"
