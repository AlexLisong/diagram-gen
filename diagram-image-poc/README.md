# Diagram Image POC

This prototype now follows the POC path you outlined:

- inputs get normalized into canonical diagram specs
- specs render into Mermaid, PlantUML, or HTML comparison assets
- graph specs export deterministic `SVG` as the primary high-quality artifact
- `PNG` remains a derived preview/export format and should not replace the `SVG` flow

Current canonical schemas:

- `schemas/graph_schema.py`
- `schemas/sequence_schema.py`
- `schemas/comparison_schema.py`

Current extract / plan / render flow:

- `extractors/repo_extractor.py`
- `planners/*.py`
- `renderers/mermaid_renderer.py`
- `renderers/plantuml_renderer.py`
- `renderers/ppt_comparison_renderer.py`
- `exporters/svg_exporter.py`
- `exporters/png_exporter.py`

SVG output is the canonical graph rendering path for this project:

- keep the full SVG generation flow end-to-end
- treat SVG as the source of truth for visual quality
- use PNG for convenience previews, thumbnails, or compatibility exports
- do not simplify the pipeline by dropping SVG in favor of PNG-only output

Implemented POC diagram types:

- `system_context`
- `high_level_architecture`
- `request_flow`
- `module_structure`
- `decision_flow`
- `verification_flow`
- `sequence`
- `before_after`

Run:

```bash
cd /Users/song/bon-git/diagram-image-poc
python3 run_pocs.py
```

Style exploration runs separately and does not replace the baseline POC outputs or the core SVG pipeline:

```bash
python3 run_style_variants.py
```

If the default `python3` does not have `Pillow`, use:

```bash
/opt/homebrew/Caskroom/miniforge/base/bin/python3 run_pocs.py
```

Artifacts written to `outputs/`:

- graph specs: `.json`, `.mmd`, `.svg`, `.png`
- preferred HQ artifact for graph diagrams: `.svg`
- raster preview/export artifact: `.png`
- sequence specs: `.json`, `.puml`
- comparison specs: `.json`, `.html`
- run summary: `summary.json`
- style exploration: `style_variants/*.png` plus contact sheets

Current style exploration presets:

- `studio`
- `blueprint`
- `broadcast`
- `glass_sunset`
- `terminal_lime`
- `editorial_poster`
- `broadcast_hero`
- `editorial_hero`

Sample scenarios included:

1. Content OS system context
2. Content OS high-level architecture
3. Repo-to-slides request flow
4. Repo-backed module structure for this POC repo
5. Decision flow for missing docs / cloud snapshot / review
6. Verification and evidence flow
7. Streaming sequence
8. Manual vs agentic before/after

What this POC proves right now:

1. One constrained graph schema can drive multiple diagram types.
2. Sequence and comparison need separate specs instead of forcing everything into one graph model.
3. Mermaid and PlantUML DSL can be generated deterministically from canonical specs.
4. Repo structure can be extracted into an abstracted module diagram instead of dumping a file tree.
5. The SVG generation flow produces high-quality diagram assets while PNG remains available for immediate previews.

Not implemented yet:

- real cloud snapshot extraction
- docs parsing
- automatic diagram type selection
- direct PPT insertion
- Mermaid or PlantUML CLI image rendering
