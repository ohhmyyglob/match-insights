# Synthetic Match Insights Engine
Explains the game beyond the stats from synthetic, football-realistic events.

## Run it
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m engine.generator

## Data
All match data in this repo is synthetic. The generator is calibrated on aggregate
statistics (averages and distributions only) derived from StatsBomb Open Data.