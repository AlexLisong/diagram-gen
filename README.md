# Diagram Generation POCs

This repo contains two main POCs plus one notable special case.

## Quick Take

- `diagram-image-poc`: better image quality
- `diagram-poc`: more diversity (`多样性`) in outputs and experiments
- `diagram-insight-poc`: presentation-focused insight graphics for deck use
- `diagram-poc/output_styled/10_before_after`: special case, because it uses a custom before/after comparison presentation instead of the standard graph flow

## Projects

### `diagram-image-poc`

Use this when image quality is the priority.

Key characteristics:

- stronger final visual quality
- SVG-first pipeline
- cleaner export path for high-quality assets
- good fit when the output needs to look polished

Main entry points:

- `diagram-image-poc/run_pocs.py`
- `diagram-image-poc/run_style_variants.py`

Outputs go to:

- `diagram-image-poc/outputs/`

### `diagram-poc`

Use this when diversity and experimentation are the priority.

Key characteristics:

- more output variety
- more theme/style exploration across diagram types
- includes multiple rendering approaches across Mermaid, PlantUML, and HTML
- useful as the broader exploration sandbox

Main entry points:

- `diagram-poc/generate_all.py`
- `diagram-poc/generate_styled.py`

Outputs go to:

- `diagram-poc/output/`
- `diagram-poc/output_styled/`

### `diagram-insight-poc`

Use this when the slide needs presentation graphics rather than system diagrams.

Key characteristics:

- focused on slide-ready insight visuals
- explores more chart and infographic shapes used in decks
- useful for business storytelling, prioritization, KPI framing, and comparisons
- outputs clean SVG plus HTML previews

Main entry point:

- `diagram-insight-poc/run_pocs.py`

Outputs go to:

- `diagram-insight-poc/outputs/`

## Special Case: `10_before_after`

The last POC, `10_before_after`, is special.

Location:

- `diagram-poc/output_styled/10_before_after/`

Why it stands out:

- it is a before/after comparison card, not a standard node-edge diagram
- it uses a dedicated HTML presentation path
- it is treated differently from the other graph-based outputs

Related files:

- `diagram-poc/scenarios/all_scenarios.py`
- `diagram-poc/generate_styled.py`
- `diagram-poc/renderers/comparison_renderer.py`

## Practical Guidance

- choose `diagram-image-poc` when you want the best-looking exported image
- choose `diagram-poc` when you want more variety and broader POC exploration
- choose `diagram-insight-poc` when you want PPT-style charts and insight graphics
- keep `10_before_after` in mind as a separate pattern that may deserve its own handling in future work
