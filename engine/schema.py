"""The single event format every part of the engine speaks."""
from dataclasses import dataclass, asdict
from typing import Literal
from typing import get_args   # put this at the top, with the other imports

Kind = Literal["pass", "carry", "shot", "goal", "tackle", "interception",
               "pressure", "foul", "card", "sub", "turnover"]


@dataclass
class MatchEvent:
    t: float                         # seconds since kick-off
    period: int                      # 1 or 2
    team: str                        # "home" or "away"
    player: str
    kind: Kind
    x: float                         # 0-100, attacking right
    y: float                         # 0-100, bottom = 0
    end_x: float | None = None
    end_y: float | None = None
    success: bool = True
    pressure: int = 1                # 1 none ... 5 very high (SkillCorner-style)
    difficulty: int | None = None    # 1 very easy ... 5 very hard (passes)
    xg: float | None = None          # shots and goals
    speed_kmh: float | None = None   # shot ball speed

    def __post_init__(self):          # runs automatically after creation: catch bad data early
        if not (0 <= self.x <= 100 and 0 <= self.y <= 100):
            raise ValueError(f"position off the pitch: ({self.x}, {self.y})")
        if not 1 <= self.pressure <= 5:
            raise ValueError(f"pressure must be 1-5, got {self.pressure}")
        if self.kind not in get_args(Kind):
            raise ValueError(f"unknown kind: {self.kind}")
        if self.difficulty is not None and not 1 <= self.difficulty <= 5:
            raise ValueError(f"difficulty must be 1-5 or None, got {self.difficulty}")

    def to_dict(self) -> dict:
        return asdict(self)            # handy for JSON, pandas, and later the agents
