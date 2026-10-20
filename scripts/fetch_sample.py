"""Download a reproducible sample of PL 2015/16 matches into data/raw/."""
from pathlib import Path
import warnings
from statsbombpy import sb

warnings.filterwarnings("ignore")
RAW = Path("data/raw")
N_MATCHES = 20
SEED = 7          # same seed = same 20 matches every time you run it


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    matches = sb.matches(competition_id=2, season_id=27)
    matches.to_pickle(RAW / "matches.pkl")
    sample = matches.sample(N_MATCHES, random_state=SEED)

    for i, m in enumerate(sample.itertuples(), start=1):
        path = RAW / f"{m.match_id}.pkl"
        if path.exists():
            print(f"[{i}/{N_MATCHES}] cached  {m.home_team} v {m.away_team}")
            continue
        sb.events(match_id=m.match_id).to_pickle(path)
        print(f"[{i}/{N_MATCHES}] fetched {m.home_team} v {m.away_team}")


if __name__ == "__main__":     # only runs when you execute the file, not when it's imported
    main()