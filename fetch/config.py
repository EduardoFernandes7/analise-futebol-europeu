import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "https://api.football-data.org/v4"
API_KEY = os.environ["FOOTBALL_DATA_API_KEY"]

# Top 5 ligas europeias, temporada 2025/26 (a mais recente já concluída)
SEASON = 2025

LEAGUES = {
    "PL": "Premier League",
    "PD": "La Liga",
    "BL1": "Bundesliga",
    "SA": "Serie A",
    "FL1": "Ligue 1",
}

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
