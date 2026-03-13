from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal, TypeAlias


ThemeName: TypeAlias = Literal["executive", "newsroom", "midnight"]


@dataclass(slots=True)
class BaseGraphicSpec:
    graphic_type: str
    title: str
    subtitle: str | None = None
    theme: ThemeName = "executive"

    def model_dump(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class MetricCard:
    label: str
    value: str
    delta: str | None = None
    note: str | None = None
    accent: str | None = None


@dataclass(slots=True)
class KPIBoardSpec(BaseGraphicSpec):
    cards: list[MetricCard] | None = None

    def __post_init__(self) -> None:
        self.graphic_type = "kpi_board"
        if not self.cards or len(self.cards) < 2:
            raise ValueError("KPI board requires at least 2 cards")


@dataclass(slots=True)
class FunnelStage:
    label: str
    value: int
    note: str | None = None
    accent: str | None = None


@dataclass(slots=True)
class FunnelSpec(BaseGraphicSpec):
    stages: list[FunnelStage] | None = None

    def __post_init__(self) -> None:
        self.graphic_type = "funnel"
        if not self.stages or len(self.stages) < 3:
            raise ValueError("Funnel requires at least 3 stages")


@dataclass(slots=True)
class TimelineMilestone:
    period: str
    label: str
    detail: str
    status: Literal["done", "active", "next"] = "next"


@dataclass(slots=True)
class TimelineSpec(BaseGraphicSpec):
    milestones: list[TimelineMilestone] | None = None

    def __post_init__(self) -> None:
        self.graphic_type = "timeline"
        if not self.milestones or len(self.milestones) < 3:
            raise ValueError("Timeline requires at least 3 milestones")


@dataclass(slots=True)
class QuadrantPoint:
    label: str
    x: float
    y: float
    size: int = 1
    note: str | None = None
    accent: str | None = None


@dataclass(slots=True)
class QuadrantSpec(BaseGraphicSpec):
    x_label: str = ""
    y_label: str = ""
    top_left_label: str = ""
    top_right_label: str = ""
    bottom_left_label: str = ""
    bottom_right_label: str = ""
    points: list[QuadrantPoint] | None = None

    def __post_init__(self) -> None:
        self.graphic_type = "quadrant"
        if not self.points or len(self.points) < 2:
            raise ValueError("Quadrant requires at least 2 points")


@dataclass(slots=True)
class MaturityStage:
    level: str
    label: str
    detail: str
    score: int


@dataclass(slots=True)
class MaturityLadderSpec(BaseGraphicSpec):
    stages: list[MaturityStage] | None = None

    def __post_init__(self) -> None:
        self.graphic_type = "maturity_ladder"
        if not self.stages or len(self.stages) < 3:
            raise ValueError("Maturity ladder requires at least 3 stages")


@dataclass(slots=True)
class ScorecardColumn:
    key: str
    label: str


@dataclass(slots=True)
class ScorecardRow:
    criterion: str
    scores: dict[str, int]
    note: str | None = None


@dataclass(slots=True)
class ScorecardSpec(BaseGraphicSpec):
    columns: list[ScorecardColumn] | None = None
    rows: list[ScorecardRow] | None = None
    scale_max: int = 5

    def __post_init__(self) -> None:
        self.graphic_type = "scorecard"
        if not self.columns or len(self.columns) < 2:
            raise ValueError("Scorecard requires at least 2 columns")
        if not self.rows or len(self.rows) < 2:
            raise ValueError("Scorecard requires at least 2 rows")


@dataclass(slots=True)
class PyramidLayer:
    label: str
    detail: str
    accent: str | None = None


@dataclass(slots=True)
class PyramidSpec(BaseGraphicSpec):
    layers: list[PyramidLayer] | None = None

    def __post_init__(self) -> None:
        self.graphic_type = "pyramid"
        if not self.layers or len(self.layers) < 3:
            raise ValueError("Pyramid requires at least 3 layers")


GraphicSpec = (
    KPIBoardSpec
    | FunnelSpec
    | TimelineSpec
    | QuadrantSpec
    | MaturityLadderSpec
    | ScorecardSpec
    | PyramidSpec
)
