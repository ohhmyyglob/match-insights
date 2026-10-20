"""Generate a synthetic match from calibration.json. v0: right totals, naive positions."""
import json
from pathlib import Path
import numpy as np
from engine.schema import MatchEvent

CAL = json.loads(Path("engine/calibration.json").read_text())
STATS = CAL["per_team_per_match"]
SQUADS = {"home": ["Adeyemi", "Kova", "Lindqvist", "Mbeki", "Osei"],     # invented names only
          "away": ["Brandt", "Duarte", "Fofana", "Halvorsen", "Ruiz"]}


def clamp(v: float) -> float:
    return float(min(100, max(0, v)))


def generate(seed: int = 42, script: list[dict] | None = None) -> list[MatchEvent]:
    rng = np.random.default_rng(seed)         # same seed = identical match: perfect for demos

# How busy is this match? Draw both teams' pass counts from the real averages.
    total_passes = sum(
        max(1, rng.normal(STATS["passes"]["mean"], STATS["passes"]["std"])) for _ in range(2)
    )
    avg_gap = 90 * 60 / total_passes          # average seconds between passes
    completion = STATS["pass_completion"]["mean"]

    events = []
    t, period = 0.0, 1
    side, x, y = "home", 50.0, 50.0           # home kicks off from the centre spot

    while t < 90 * 60:
        t += rng.exponential(avg_gap)         # random gaps: mostly short, a few long

        if period == 1 and t >= 45 * 60:      # half time: away kicks off
            period, side, x, y = 2, "away", 50.0, 50.0

        end_x = clamp(x + rng.normal(6, 10))  # usually forward, sometimes back
        end_y = clamp(y + rng.normal(0, 12))  # some sideways movement
        near_goal = max(0.0, (x - 60) / 40)                          # new
        success = bool(rng.random() < completion - 0.3 * near_goal)  # changed

        events.append(MatchEvent(
            t=float(t), period=period, team=side,
            player=str(rng.choice(SQUADS[side])), kind="pass",
            x=x, y=y, end_x=end_x, end_y=end_y,
            success=success, pressure=int(rng.integers(1, 6)),
        ))

        if success:                           # same team, ball moves on
            x, y = end_x, end_y
        else:                                 # turnover: other team, flipped view
            side = "away" if side == "home" else "home"
            x, y = 100 - end_x, 100 - end_y

    for beat in script or []:
        events.append(MatchEvent(**beat))
    return sorted(events, key=lambda e: e.t)

    def draw(stat: str) -> int:               # a believable count, never negative
        return max(0, round(rng.normal(STATS[stat]["mean"], STATS[stat]["std"])))

    events = []
    for side in ("home", "away"):
        for _ in range(draw("passes")):
            t = float(rng.uniform(0, 90 * 60))
            x, y = rng.uniform(5, 95), rng.uniform(5, 95)
            events.append(MatchEvent(
                t=t, period=1 if t < 45 * 60 else 2, team=side,
                player=str(rng.choice(SQUADS[side])), kind="pass",
                x=clamp(x), y=clamp(y),
                end_x=clamp(x + rng.normal(8, 10)), end_y=clamp(y + rng.normal(0, 12)),
                success=bool(rng.random() < STATS["pass_completion"]["mean"]),
                pressure=int(rng.integers(1, 6)),     # 1 to 5 (the 6 is excluded)
            ))
    for beat in script or []:                    # scripted story moments: YOU choose the drama
        events.append(MatchEvent(**beat))         # ** unpacks a dict into keyword arguments
    return sorted(events, key=lambda e: e.t)


if __name__ == "__main__":
    match = generate(script=[
        dict(t=78*60, period=2, team="away", player="Kova", kind="goal",
             x=88, y=52, xg=0.31, speed_kmh=96),
    ])
    out = Path("data/synthetic/match_seed42.json")
    out.write_text(json.dumps([e.to_dict() for e in match], indent=1))
    print(f"{len(match)} events -> {out}")