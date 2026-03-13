# Diagram Insight POC

This POC focuses on presentation graphics rather than system diagrams.

The goal is to generate the kinds of visuals that show up in slides:

- KPI boards
- funnels
- timelines
- 2x2 quadrants
- maturity ladders
- scorecards
- narrative pyramids

## Positioning

- `diagram-poc`: broader diagram experimentation
- `diagram-image-poc`: stronger image quality for diagram outputs
- `diagram-insight-poc`: presentation-first insight graphics for decks

This project is useful when a slide needs a clear point of view, not just a technical topology.

## Why This Exists

In presentations, we often need graphics such as:

- executive metrics snapshots
- prioritization maps
- transformation journeys
- comparison scorecards
- story hierarchy graphics
- business funnel visuals

Those are not well served by only using architecture diagrams, sequence diagrams, or node-edge graphs.

## Implemented POC Graphic Types

- `kpi_board`
- `funnel`
- `timeline`
- `quadrant`
- `maturity_ladder`
- `scorecard`
- `pyramid`

## Run

```bash
cd /Users/song/bon-git/diagram-gen/diagram-insight-poc
python3 run_pocs.py
```

Artifacts go to `outputs/`:

- canonical spec: `.json`
- primary graphic artifact: `.svg`
- preview wrapper: `.html`
- run summary: `summary.json`

## Sample Scenarios

1. Executive KPI board
2. Presentation feature priority quadrant
3. Demo funnel
4. Rollout timeline
5. Manual-to-agentic maturity ladder
6. POC comparison scorecard
7. Presentation story pyramid

## Next Useful Extensions

- radial scorecards
- heatmaps
- waterfall charts
- stakeholder maps
- swimlane roadmap graphics
- callout slides with annotated screenshots
