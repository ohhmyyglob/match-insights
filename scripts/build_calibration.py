"""Summarise the cached real matches into engine/calibration.json (numbers only)."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

RAW = Path("data/raw")
OUT = Path("engine/calibration.json")


def team_stats(g: pd.DataFrame) -> dict:
    """One team's numbers for one match."""
    p, s = g[g.type == "Pass"], g[g.type == "Shot"]
    return {
        "passes": len(p),
        "pass_completion": float(p.pass_outcome.isna().mean()),
        "shots": len(s),
        "goals": int((s.shot_outcome == "Goal").sum()),
        "pressures": int((g.type == "Pressure").sum()),
        "tackles": int((g.type == "Duel").sum()),
        "fouls": int((g.type == "Foul Committed").sum()),
    }


def main():
    files = [f for f in RAW.glob("*.pkl") if f.stem.isdigit()]   # skip matches.pkl
    rows, goal_minutes, pass_lengths = [], [], []
    for f in files:
        ev = pd.read_pickle(f)
        rows += [team_stats(g) for _, g in ev.groupby("team")]
        goals = ev[(ev.type == "Shot") & (ev.shot_outcome == "Goal")]
        goal_minutes += goals.minute.tolist()
        pass_lengths += ev.loc[ev.type == "Pass", "pass_length"].dropna().tolist()

    df = pd.DataFrame(rows)
    cal = {
        "source": f"Aggregates from {len(files)} StatsBomb Open Data matches (PL 2015/16)",
        "per_team_per_match": {
            col: {"mean": round(df[col].mean(), 3), "std": round(df[col].std(), 3)}
            for col in df.columns
        },
        "pass_length_pct": dict(zip(["p10", "p25", "p50", "p75", "p90"],
            np.percentile(pass_lengths, [10, 25, 50, 75, 90]).round(1).tolist())),
        "goals_per_15min": np.histogram(goal_minutes, bins=range(0, 106, 15))[0].tolist(),
    }
    OUT.write_text(json.dumps(cal, indent=2))
    print(f"Saved {OUT} from {len(files)} matches")


if __name__ == "__main__":
    main()