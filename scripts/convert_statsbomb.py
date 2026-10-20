"""Learning tool: map real StatsBomb rows onto MatchEvent. Not used by the product."""
import sys
from pathlib import Path
import pandas as pd
from engine.schema import MatchEvent
from engine.coords import from_statsbomb
from dataclasses import replace

KIND = {"Pass": "pass", "Carry": "carry", "Shot": "shot", "Duel": "tackle",
        "Interception": "interception", "Pressure": "pressure",
        "Foul Committed": "foul", "Dispossessed": "turnover", "Miscontrol": "turnover"}


def is_point(v) -> bool:
    return isinstance(v, list) and len(v) >= 2


def convert(ev: pd.DataFrame, home: str) -> list[MatchEvent]:
    out, skipped = [], 0
    for r in ev.to_dict("records"):            # each row becomes a plain dict
        kind = KIND.get(r["type"])
        if kind is None or not is_point(r.get("location")):
            skipped += 1
            continue
        x, y = from_statsbomb(*r["location"][:2])  # * unpacks [x, y] into two arguments
        end = r.get("pass_end_location") if is_point(r.get("pass_end_location")) else r.get("carry_end_location")
        ex, ey = from_statsbomb(*end[:2]) if is_point(end) else (None, None)
        if kind == "shot" and r.get("shot_outcome") == "Goal":
            kind = "goal"
        failed = pd.notna(r.get("pass_outcome")) if kind == "pass" else False
        out.append(MatchEvent(
            t=r["minute"] * 60 + r["second"], period=int(r["period"]),
            team="home" if r["team"] == home else "away",
            player=str(r["player"]), kind=kind, x=x, y=y, end_x=ex, end_y=ey,
            success=not failed,
            pressure=4 if r.get("under_pressure") == True else 1,
            xg=r.get("shot_statsbomb_xg") if kind in ("shot", "goal") else None,
        ))
        if pd.notna(r.get("foul_committed_card")):
            out.append(replace(out[-1], kind="card"))
    print(f"converted {len(out)}, skipped {skipped} (receipts, starting XI, etc.)")
    return out


if __name__ == "__main__":
    match_id = int(sys.argv[1])                    # the number you type after the command
    path = Path("data/raw") / f"{match_id}.pkl"
    if not path.exists():
        available = sorted(p.stem for p in Path("data/raw").glob("*.pkl") if p.stem.isdigit())
        sys.exit(f"No cached match {match_id}. Try one of: {', '.join(available[:5])}")
    ev = pd.read_pickle(path)
    matches = pd.read_pickle("data/raw/matches.pkl")
    home = matches.loc[matches.match_id == match_id, "home_team"].iloc[0]
    events = convert(ev, home)
    from collections import Counter
    print(Counter(e.kind for e in events))          # how many of each kind
    for e in events:
        if e.kind == "card":
            print(f"{e.t // 60:.0f}'  {e.player}")  # minute and player