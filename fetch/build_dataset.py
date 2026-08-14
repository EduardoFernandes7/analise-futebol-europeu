import json

import pandas as pd

from fetch.config import LEAGUES, PROCESSED_DIR, RAW_DIR, SEASON
from fetch.football_data_api import get_matches, get_standings


def _matches_to_rows(league_code: str, league_name: str, payload: dict) -> list[dict]:
    rows = []
    for match in payload["matches"]:
        score = match["score"]["fullTime"]
        rows.append(
            {
                "league_code": league_code,
                "league_name": league_name,
                "season": SEASON,
                "matchday": match["matchday"],
                "stage": match["stage"],
                "utc_date": match["utcDate"],
                "status": match["status"],
                "home_team": match["homeTeam"]["name"],
                "away_team": match["awayTeam"]["name"],
                "home_goals": score["home"],
                "away_goals": score["away"],
                "winner": match["score"]["winner"],
            }
        )
    return rows


def _standings_to_rows(league_code: str, league_name: str, payload: dict) -> list[dict]:
    total_table = next(s for s in payload["standings"] if s["type"] == "TOTAL")["table"]
    rows = []
    for entry in total_table:
        rows.append(
            {
                "league_code": league_code,
                "league_name": league_name,
                "season": SEASON,
                "position": entry["position"],
                "team": entry["team"]["name"],
                "played_games": entry["playedGames"],
                "won": entry["won"],
                "draw": entry["draw"],
                "lost": entry["lost"],
                "points": entry["points"],
                "goals_for": entry["goalsFor"],
                "goals_against": entry["goalsAgainst"],
                "goal_difference": entry["goalDifference"],
            }
        )
    return rows


def build_dataset() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    all_matches: list[dict] = []
    all_standings: list[dict] = []

    for code, name in LEAGUES.items():
        print(f"Buscando {name} ({code})...")

        matches_payload = get_matches(code, SEASON)
        (RAW_DIR / f"{code}_matches.json").write_text(
            json.dumps(matches_payload, ensure_ascii=False), encoding="utf-8"
        )
        all_matches.extend(_matches_to_rows(code, name, matches_payload))

        standings_payload = get_standings(code, SEASON)
        (RAW_DIR / f"{code}_standings.json").write_text(
            json.dumps(standings_payload, ensure_ascii=False), encoding="utf-8"
        )
        all_standings.extend(_standings_to_rows(code, name, standings_payload))

    matches_df = pd.DataFrame(all_matches)
    matches_df["utc_date"] = pd.to_datetime(matches_df["utc_date"])
    matches_df.to_parquet(PROCESSED_DIR / "matches.parquet", index=False)

    standings_df = pd.DataFrame(all_standings)
    standings_df.to_parquet(PROCESSED_DIR / "standings.parquet", index=False)

    print(f"{len(matches_df)} partidas e {len(standings_df)} linhas de classificação salvas em {PROCESSED_DIR}")


if __name__ == "__main__":
    build_dataset()
