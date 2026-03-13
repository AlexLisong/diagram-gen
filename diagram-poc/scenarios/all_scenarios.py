"""
All 10 diagram type scenarios — using real Content OS / Tapp / Lighthouse examples.
"""

# ── 1. System Context ───────────────────────────────────────────────

SYSTEM_CONTEXT = {
    "diagram_type": "system_context",
    "title": "Content OS — System Context",
    "direction": "LR",
    "nodes": [
        {"id": "creator", "label": "Content Creator", "type": "user", "group": "actors"},
        {"id": "system", "label": "Content OS", "type": "service", "group": "core"},
        {"id": "repos", "label": "Git Repos", "type": "storage", "group": "inputs"},
        {"id": "cloud", "label": "Cloud Infra", "type": "external_api", "group": "inputs"},
        {"id": "slides", "label": "Slide Deck", "type": "output", "group": "outputs"},
        {"id": "script", "label": "Teleprompter", "type": "output", "group": "outputs"},
        {"id": "diagrams", "label": "Diagrams", "type": "output", "group": "outputs"},
    ],
    "edges": [
        {"from": "creator", "to": "system", "label": "Requests", "type": "http"},
        {"from": "repos", "to": "system", "label": "Source", "type": "reads"},
        {"from": "cloud", "to": "system", "label": "Infra Data", "type": "reads"},
        {"from": "system", "to": "slides", "label": "Generate", "type": "produces"},
        {"from": "system", "to": "script", "label": "Generate", "type": "produces"},
        {"from": "system", "to": "diagrams", "label": "Generate", "type": "produces"},
    ],
    "groups": [
        {"id": "actors", "label": "Actors"},
        {"id": "core", "label": "System"},
        {"id": "inputs", "label": "Inputs"},
        {"id": "outputs", "label": "Outputs"},
    ],
}

# ── 2. High-Level Architecture ──────────────────────────────────────

HIGH_LEVEL_ARCHITECTURE = {
    "diagram_type": "system_architecture",
    "title": "Content OS — Architecture",
    "direction": "LR",
    "nodes": [
        {"id": "ingestion", "label": "Repo Ingestion", "type": "service", "group": "pipeline"},
        {"id": "graph_builder", "label": "Graph Builder", "type": "ai_service", "group": "pipeline"},
        {"id": "planner", "label": "Content Planner", "type": "ai_service", "group": "pipeline"},
        {"id": "slides", "label": "Slide Generator", "type": "service", "group": "generators"},
        {"id": "script", "label": "Script Writer", "type": "ai_service", "group": "generators"},
        {"id": "diagrams", "label": "Diagram Engine", "type": "service", "group": "generators"},
        {"id": "verifier", "label": "Verifier", "type": "gate", "group": "quality"},
        {"id": "exporter", "label": "Exporter", "type": "service", "group": "quality"},
    ],
    "edges": [
        {"from": "ingestion", "to": "graph_builder", "label": "Raw Data", "type": "feeds"},
        {"from": "graph_builder", "to": "planner", "label": "Graph", "type": "feeds"},
        {"from": "planner", "to": "slides", "label": "Outline", "type": "calls"},
        {"from": "planner", "to": "script", "label": "Outline", "type": "calls"},
        {"from": "planner", "to": "diagrams", "label": "Specs", "type": "calls"},
        {"from": "slides", "to": "verifier", "label": "Draft", "type": "next"},
        {"from": "script", "to": "verifier", "label": "Draft", "type": "next"},
        {"from": "diagrams", "to": "verifier", "label": "Images", "type": "next"},
        {"from": "verifier", "to": "exporter", "label": "Approved", "type": "next"},
    ],
    "groups": [
        {"id": "pipeline", "label": "Ingestion Pipeline"},
        {"id": "generators", "label": "Content Generators"},
        {"id": "quality", "label": "Quality Gate"},
    ],
}

# ── 3. Request Flow ─────────────────────────────────────────────────

REQUEST_FLOW = {
    "diagram_type": "request_flow",
    "title": "AI Copilot Chat Request Flow",
    "direction": "LR",
    "nodes": [
        {"id": "react", "label": "React UI", "type": "frontend"},
        {"id": "copilot", "label": "CopilotKit", "type": "frontend"},
        {"id": "csharp", "label": "C# Gateway", "type": "api"},
        {"id": "python", "label": "Python Agent", "type": "ai_service"},
        {"id": "openai", "label": "OpenAI GPT-4", "type": "external_api"},
    ],
    "edges": [
        {"from": "react", "to": "copilot", "label": "Action", "type": "calls"},
        {"from": "copilot", "to": "csharp", "label": "POST /chat", "type": "http"},
        {"from": "csharp", "to": "python", "label": "Forward", "type": "internal_http"},
        {"from": "python", "to": "openai", "label": "LLM Call", "type": "http"},
        {"from": "python", "to": "csharp", "label": "MetaEvents", "type": "stream"},
        {"from": "csharp", "to": "react", "label": "SSE", "type": "stream"},
    ],
}

# ── 4. Sequence Diagram ────────────────────────────────────────────

SEQUENCE_AI_STREAMING = {
    "diagram_type": "sequence",
    "title": "AI Streaming Sequence — MetaEvent Flow",
    "participants": [
        {"id": "user", "label": "User", "type": "actor"},
        {"id": "fe", "label": "React Frontend", "type": "participant"},
        {"id": "api", "label": "C-Sharp Backend", "type": "participant"},
        {"id": "agent", "label": "Python Agent", "type": "participant"},
        {"id": "llm", "label": "OpenAI", "type": "database"},
    ],
    "steps": [
        {"from": "user", "to": "fe", "message": "Ask copilot question"},
        {"from": "fe", "to": "api", "message": "POST /api/copilot/chat", "activate": True},
        {"from": "api", "to": "agent", "message": "Forward request", "activate": True},
        {"from": "agent", "to": "llm", "message": "Chat completion", "activate": True},
        {"from": "llm", "to": "agent", "message": "Stream tokens", "style": "dashed", "is_return": True, "deactivate": True},
        {"from": "agent", "to": "api", "message": "MetaEvent: tool_result", "style": "dashed", "note": "Build MetaEvents from tool outputs"},
        {"from": "agent", "to": "api", "message": "MetaEvent: layout_card", "style": "dashed", "deactivate": True},
        {"from": "api", "to": "fe", "message": "SSE: CUSTOM event", "style": "dashed", "deactivate": True},
        {"from": "fe", "to": "user", "message": "Render AI response", "style": "dashed", "note": "Intercept and render cards"},
    ],
}

# ── 5. Data Flow ────────────────────────────────────────────────────

DATA_FLOW = {
    "diagram_type": "data_flow",
    "title": "Content OS — Data Pipeline",
    "direction": "TB",
    "nodes": [
        {"id": "repos", "label": "Git Repos", "type": "data_source", "group": "sources"},
        {"id": "docs", "label": "Docs / README", "type": "data_source", "group": "sources"},
        {"id": "cloud", "label": "Cloud Snapshot", "type": "data_source", "group": "sources"},
        {"id": "parser", "label": "Code Parser", "type": "transform", "group": "processing"},
        {"id": "normalizer", "label": "Entity Normalizer", "type": "transform", "group": "processing"},
        {"id": "graph_db", "label": "Project Graph", "type": "database", "group": "storage"},
        {"id": "slide_out", "label": "Slides", "type": "output", "group": "outputs"},
        {"id": "script_out", "label": "Script", "type": "output", "group": "outputs"},
        {"id": "diagram_out", "label": "Diagrams", "type": "output", "group": "outputs"},
    ],
    "edges": [
        {"from": "repos", "to": "parser", "label": "Files", "type": "feeds"},
        {"from": "docs", "to": "parser", "label": "Text", "type": "feeds"},
        {"from": "cloud", "to": "normalizer", "label": "Resources", "type": "feeds"},
        {"from": "parser", "to": "normalizer", "label": "Raw Entities", "type": "transforms"},
        {"from": "normalizer", "to": "graph_db", "label": "Canonical", "type": "writes"},
        {"from": "graph_db", "to": "slide_out", "label": "Outline", "type": "produces"},
        {"from": "graph_db", "to": "script_out", "label": "Talking Points", "type": "produces"},
        {"from": "graph_db", "to": "diagram_out", "label": "DiagramSpec", "type": "produces"},
    ],
    "groups": [
        {"id": "sources", "label": "Input Sources"},
        {"id": "processing", "label": "Processing"},
        {"id": "storage", "label": "Storage"},
        {"id": "outputs", "label": "Generated Assets"},
    ],
}

# ── 6. Module Structure ─────────────────────────────────────────────

MODULE_STRUCTURE = {
    "diagram_type": "module_structure",
    "title": "Content OS — Module Structure",
    "direction": "TB",
    "nodes": [
        {"id": "schemas", "label": "schemas/", "type": "module", "group": "core"},
        {"id": "extractors", "label": "extractors/", "type": "module", "group": "core"},
        {"id": "renderers", "label": "renderers/", "type": "module", "group": "core"},
        {"id": "exporters", "label": "exporters/", "type": "module", "group": "core"},
        {"id": "planners", "label": "planners/", "type": "module", "group": "orchestration"},
        {"id": "validators", "label": "validators/", "type": "module", "group": "orchestration"},
        {"id": "pipeline", "label": "pipeline.py", "type": "module", "group": "orchestration"},
        {"id": "scenarios", "label": "scenarios/", "type": "module", "group": "tests"},
    ],
    "edges": [
        {"from": "pipeline", "to": "extractors", "label": "uses", "type": "depends_on"},
        {"from": "pipeline", "to": "planners", "label": "uses", "type": "depends_on"},
        {"from": "pipeline", "to": "validators", "label": "uses", "type": "depends_on"},
        {"from": "pipeline", "to": "renderers", "label": "uses", "type": "depends_on"},
        {"from": "pipeline", "to": "exporters", "label": "uses", "type": "depends_on"},
        {"from": "extractors", "to": "schemas", "label": "imports", "type": "depends_on"},
        {"from": "renderers", "to": "schemas", "label": "imports", "type": "depends_on"},
        {"from": "scenarios", "to": "pipeline", "label": "tests", "type": "calls"},
    ],
    "groups": [
        {"id": "core", "label": "Core Libraries"},
        {"id": "orchestration", "label": "Orchestration"},
        {"id": "tests", "label": "Test Scenarios"},
    ],
}

# ── 7. Deployment Diagram ───────────────────────────────────────────

DEPLOYMENT = {
    "diagram_type": "deployment",
    "title": "Tapp — Azure Deployment",
    "direction": "TB",
    "nodes": [
        {"id": "vercel", "label": "Vercel", "type": "app_service", "group": "frontend"},
        {"id": "react_app", "label": "React SPA", "type": "frontend", "group": "frontend"},
        {"id": "app_svc", "label": "App Service", "type": "app_service", "group": "azure"},
        {"id": "dotnet", "label": ".NET API", "type": "api", "group": "azure"},
        {"id": "vm", "label": "Linux VM", "type": "vm", "group": "azure"},
        {"id": "python_svc", "label": "FastAPI Agent", "type": "ai_service", "group": "azure"},
        {"id": "sql", "label": "Azure SQL", "type": "database", "group": "data"},
        {"id": "redis", "label": "Azure Redis", "type": "redis", "group": "data"},
        {"id": "blob", "label": "Blob Storage", "type": "s3", "group": "data"},
    ],
    "edges": [
        {"from": "vercel", "to": "react_app", "label": "hosts", "type": "deploys_to"},
        {"from": "react_app", "to": "dotnet", "label": "REST", "type": "http"},
        {"from": "app_svc", "to": "dotnet", "label": "runs", "type": "deploys_to"},
        {"from": "vm", "to": "python_svc", "label": "runs", "type": "deploys_to"},
        {"from": "dotnet", "to": "python_svc", "label": "HTTP", "type": "internal_http"},
        {"from": "dotnet", "to": "sql", "label": "SQL", "type": "reads"},
        {"from": "dotnet", "to": "redis", "label": "Cache", "type": "reads"},
        {"from": "dotnet", "to": "blob", "label": "Files", "type": "stores_in"},
    ],
    "groups": [
        {"id": "frontend", "label": "Frontend - Vercel"},
        {"id": "azure", "label": "Azure Compute"},
        {"id": "data", "label": "Azure Data"},
    ],
}

# ── 8. Decision Flow ────────────────────────────────────────────────

DECISION_FLOW = {
    "diagram_type": "decision_flow",
    "title": "Content Generation — Decision Flow",
    "direction": "TB",
    "nodes": [
        {"id": "start", "label": "Start", "type": "start"},
        {"id": "has_repo", "label": "Repo available?", "type": "decision"},
        {"id": "scan_repo", "label": "Scan Repo", "type": "process"},
        {"id": "manual_input", "label": "Manual Input", "type": "process"},
        {"id": "has_docs", "label": "Docs complete?", "type": "decision"},
        {"id": "enrich", "label": "Enrich with LLM", "type": "process"},
        {"id": "build_graph", "label": "Build Graph", "type": "process"},
        {"id": "quality_ok", "label": "Quality gate?", "type": "gate"},
        {"id": "generate", "label": "Generate Assets", "type": "process"},
        {"id": "review", "label": "Human Review", "type": "process"},
        {"id": "done", "label": "Export", "type": "end"},
    ],
    "edges": [
        {"from": "start", "to": "has_repo", "type": "next"},
        {"from": "has_repo", "to": "scan_repo", "label": "Yes", "type": "yes"},
        {"from": "has_repo", "to": "manual_input", "label": "No", "type": "no"},
        {"from": "scan_repo", "to": "has_docs", "type": "next"},
        {"from": "manual_input", "to": "has_docs", "type": "next"},
        {"from": "has_docs", "to": "build_graph", "label": "Yes", "type": "yes"},
        {"from": "has_docs", "to": "enrich", "label": "No", "type": "no"},
        {"from": "enrich", "to": "build_graph", "type": "next"},
        {"from": "build_graph", "to": "quality_ok", "type": "next"},
        {"from": "quality_ok", "to": "generate", "label": "Pass", "type": "yes"},
        {"from": "quality_ok", "to": "review", "label": "Fail", "type": "no"},
        {"from": "review", "to": "build_graph", "label": "Retry", "type": "fallback"},
        {"from": "generate", "to": "done", "type": "next"},
    ],
}

# ── 9. Verification Flow ───────────────────────────────────────────

VERIFICATION_FLOW = {
    "diagram_type": "verification_flow",
    "title": "Content Verification Pipeline",
    "direction": "LR",
    "nodes": [
        {"id": "repo_src", "label": "Repo Source", "type": "data_source", "group": "evidence"},
        {"id": "doc_src", "label": "Doc Source", "type": "data_source", "group": "evidence"},
        {"id": "cloud_src", "label": "Cloud Source", "type": "data_source", "group": "evidence"},
        {"id": "extractor", "label": "Evidence Extractor", "type": "ai_service", "group": "verify"},
        {"id": "claims", "label": "Claim Builder", "type": "service", "group": "verify"},
        {"id": "verifier", "label": "Fact Verifier", "type": "gate", "group": "verify"},
        {"id": "approved", "label": "Approved Output", "type": "output", "group": "output"},
        {"id": "flagged", "label": "Flagged for Review", "type": "output", "group": "output"},
    ],
    "edges": [
        {"from": "repo_src", "to": "extractor", "label": "Code", "type": "feeds"},
        {"from": "doc_src", "to": "extractor", "label": "Docs", "type": "feeds"},
        {"from": "cloud_src", "to": "extractor", "label": "Infra", "type": "feeds"},
        {"from": "extractor", "to": "claims", "label": "Facts", "type": "transforms"},
        {"from": "claims", "to": "verifier", "label": "Claims", "type": "next"},
        {"from": "verifier", "to": "approved", "label": "Verified", "type": "yes"},
        {"from": "verifier", "to": "flagged", "label": "Unverified", "type": "no"},
    ],
    "groups": [
        {"id": "evidence", "label": "Evidence Sources"},
        {"id": "verify", "label": "Verification Pipeline"},
        {"id": "output", "label": "Results"},
    ],
}

# ── 10. Before / After ─────────────────────────────────────────────

BEFORE_AFTER = {
    "diagram_type": "before_after",
    "title": "Manual vs AI-Assisted Video Prep",
    "left": {
        "title": "Before (Manual)",
        "items": [
            "Read entire repo manually (2-4 hours)",
            "Write slide deck from scratch (3-5 hours)",
            "Draw diagrams in Figma/PPT (1-2 hours)",
            "Write script manually (2-3 hours)",
            "No fact-checking against source",
            "Inconsistent quality across videos",
        ],
    },
    "right": {
        "title": "After (Content OS)",
        "items": [
            "Auto-ingest repo + cloud (minutes)",
            "Auto-generate slide outline + draft",
            "Auto-generate verified diagrams",
            "Auto-generate teleprompter script",
            "Every claim traced to source code",
            "Consistent structure + quality",
        ],
    },
    "improvement_notes": [
        "10x faster prep time: 8-14 hours → under 1 hour",
        "Every diagram is deterministic and editable",
        "Every claim is source-verified, not hallucinated",
        "System scales to any repo, not just ones you know well",
    ],
}
