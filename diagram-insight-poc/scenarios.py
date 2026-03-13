from __future__ import annotations

from models import (
    FunnelSpec,
    FunnelStage,
    GraphicSpec,
    KPIBoardSpec,
    MaturityLadderSpec,
    MaturityStage,
    MetricCard,
    PyramidLayer,
    PyramidSpec,
    QuadrantPoint,
    QuadrantSpec,
    ScorecardColumn,
    ScorecardRow,
    ScorecardSpec,
    TimelineMilestone,
    TimelineSpec,
)


def build_kpi_board() -> KPIBoardSpec:
    return KPIBoardSpec(
        graphic_type="kpi_board",
        title="AI Support Copilot - Executive Snapshot",
        subtitle="A deck-ready KPI board for an opening business slide",
        theme="executive",
        cards=[
            MetricCard(label="Auto-resolved tickets", value="42%", delta="+11 pts", note="Quarter over quarter"),
            MetricCard(label="Median response time", value="2.8m", delta="-37%", note="First human reply"),
            MetricCard(label="Agent assist usage", value="68%", delta="+19 pts", note="Support team adoption"),
            MetricCard(label="CSAT uplift", value="+9", delta="4.6/5", note="Pilot cohort average"),
        ],
    )


def build_funnel() -> FunnelSpec:
    return FunnelSpec(
        graphic_type="funnel",
        title="Presentation Funnel - Repo to Approved Slide",
        subtitle="Useful when the slide needs to show drop-off or narrowing focus",
        theme="newsroom",
        stages=[
            FunnelStage(label="Source material", value=120, note="Repos, docs, tickets"),
            FunnelStage(label="Candidate insights", value=56, note="After extraction and grouping"),
            FunnelStage(label="Slide-worthy ideas", value=24, note="Ranked by importance"),
            FunnelStage(label="Approved messages", value=9, note="Passed review"),
            FunnelStage(label="Final presentation beats", value=4, note="Shown to stakeholders"),
        ],
    )


def build_timeline() -> TimelineSpec:
    return TimelineSpec(
        graphic_type="timeline",
        title="Insight Graphics Rollout Timeline",
        subtitle="A roadmap graphic for deck planning and delivery sequencing",
        theme="executive",
        milestones=[
            TimelineMilestone(period="Week 1", label="Primitive set", detail="KPI, funnel, quadrant, timeline", status="done"),
            TimelineMilestone(period="Week 2", label="Deck themes", detail="Executive, newsroom, midnight", status="done"),
            TimelineMilestone(period="Week 3", label="Story graphics", detail="Pyramid, maturity ladder, scorecard", status="active"),
            TimelineMilestone(period="Week 4", label="Slide integration", detail="Export package for deck workflows", status="next"),
            TimelineMilestone(period="Week 5", label="Narrative automation", detail="Pair graphics with talking points", status="next"),
        ],
    )


def build_quadrant() -> QuadrantSpec:
    return QuadrantSpec(
        graphic_type="quadrant",
        title="Presentation Graphics Priority Map",
        subtitle="A 2x2 slide for prioritizing which visuals matter most",
        theme="midnight",
        x_label="Execution Effort",
        y_label="Audience Impact",
        top_left_label="Fast wins",
        top_right_label="Strategic bets",
        bottom_left_label="Low leverage",
        bottom_right_label="Expensive distractions",
        points=[
            QuadrantPoint(label="KPI board", x=28, y=83, size=4, note="Opens the deck cleanly"),
            QuadrantPoint(label="Quadrant map", x=35, y=72, size=3, note="Good for prioritization slides"),
            QuadrantPoint(label="Scorecard", x=52, y=68, size=3, note="Useful in comparisons"),
            QuadrantPoint(label="Annotated screenshots", x=66, y=78, size=5, note="High value, more manual polish"),
            QuadrantPoint(label="Pyramid narrative", x=31, y=58, size=2, note="Good for strategy decks"),
            QuadrantPoint(label="Radial infographic", x=74, y=42, size=2, note="More style than substance"),
        ],
    )


def build_maturity_ladder() -> MaturityLadderSpec:
    return MaturityLadderSpec(
        graphic_type="maturity_ladder",
        title="Manual to Agentic Presentation Maturity",
        subtitle="A transformation graphic for change-over-time storytelling",
        theme="executive",
        stages=[
            MaturityStage(level="L1", label="Manual", detail="Analyst assembles raw slide content by hand", score=1),
            MaturityStage(level="L2", label="Assisted", detail="LLM drafts text and simple diagrams", score=2),
            MaturityStage(level="L3", label="Repeatable", detail="Reusable templates and canonical specs", score=3),
            MaturityStage(level="L4", label="Adaptive", detail="Graphics chosen from presentation intent", score=4),
            MaturityStage(level="L5", label="Agentic", detail="Slide stories generated with evidence and visuals", score=5),
        ],
    )


def build_scorecard() -> ScorecardSpec:
    return ScorecardSpec(
        graphic_type="scorecard",
        title="POC Comparison Scorecard",
        subtitle="A presentation slide to compare the three tracks in this repo",
        theme="newsroom",
        columns=[
            ScorecardColumn(key="diagram_poc", label="diagram-poc"),
            ScorecardColumn(key="image_poc", label="diagram-image-poc"),
            ScorecardColumn(key="insight_poc", label="diagram-insight-poc"),
        ],
        rows=[
            ScorecardRow(criterion="Image quality", scores={"diagram_poc": 3, "image_poc": 5, "insight_poc": 4}, note="SVG-first quality still leads"),
            ScorecardRow(criterion="Visual diversity", scores={"diagram_poc": 5, "image_poc": 4, "insight_poc": 5}, note="Insight graphics broaden deck shapes"),
            ScorecardRow(criterion="Technical diagrams", scores={"diagram_poc": 5, "image_poc": 4, "insight_poc": 2}, note="Still strongest in the original POCs"),
            ScorecardRow(criterion="Presentation readiness", scores={"diagram_poc": 3, "image_poc": 4, "insight_poc": 5}, note="Designed for slide storytelling"),
        ],
    )


def build_pyramid() -> PyramidSpec:
    return PyramidSpec(
        graphic_type="pyramid",
        title="Presentation Story Pyramid",
        subtitle="A message hierarchy graphic for strategy and executive storytelling",
        theme="executive",
        layers=[
            PyramidLayer(label="Recommendation", detail="What we should do next"),
            PyramidLayer(label="Insight", detail="What the evidence means"),
            PyramidLayer(label="Evidence", detail="What the system, metrics, and examples show"),
            PyramidLayer(label="Source Material", detail="Repos, docs, tickets, and observations"),
        ],
    )


def all_specs() -> dict[str, GraphicSpec]:
    return {
        "executive_kpi_board": build_kpi_board(),
        "repo_to_slide_funnel": build_funnel(),
        "rollout_timeline": build_timeline(),
        "graphics_priority_quadrant": build_quadrant(),
        "agentic_maturity_ladder": build_maturity_ladder(),
        "poc_scorecard": build_scorecard(),
        "story_pyramid": build_pyramid(),
    }
