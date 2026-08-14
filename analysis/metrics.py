"""Funções de análise compartilhadas entre o notebook exploratório e o dashboard Streamlit."""

from pathlib import Path

import pandas as pd


def load_data(processed_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    matches = pd.read_parquet(processed_dir / "matches.parquet")
    standings = pd.read_parquet(processed_dir / "standings.parquet")
    return matches, standings


def finished_matches(matches: pd.DataFrame) -> pd.DataFrame:
    return matches[matches["status"] == "FINISHED"].copy()


def home_advantage_table(matches: pd.DataFrame) -> pd.DataFrame:
    played = finished_matches(matches)
    grouped = played.groupby("league_name")["winner"]
    return (
        grouped.value_counts(normalize=True)
        .unstack(fill_value=0)
        .rename(
            columns={
                "HOME_TEAM": "vitoria_mandante_pct",
                "AWAY_TEAM": "vitoria_visitante_pct",
                "DRAW": "empate_pct",
            }
        )
        .assign(partidas=grouped.size())
        .reset_index()
    )


def goals_summary_table(matches: pd.DataFrame) -> pd.DataFrame:
    played = finished_matches(matches)
    played["total_goals"] = played["home_goals"] + played["away_goals"]
    return (
        played.groupby("league_name")
        .agg(
            partidas=("total_goals", "size"),
            gols_totais=("total_goals", "sum"),
            media_gols_por_partida=("total_goals", "mean"),
        )
        .reset_index()
        .sort_values("media_gols_por_partida", ascending=False)
    )


def title_race_gap_table(standings: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for league_name, table in standings.groupby("league_name"):
        table = table.sort_values("position")
        leader, runner_up = table.iloc[0], table.iloc[1]
        rows.append(
            {
                "league_name": league_name,
                "lider": leader["team"],
                "pontos_lider": leader["points"],
                "vice": runner_up["team"],
                "pontos_vice": runner_up["points"],
                "diferenca_pontos": leader["points"] - runner_up["points"],
            }
        )
    return pd.DataFrame(rows).sort_values("diferenca_pontos")


def team_results(matches: pd.DataFrame, team: str) -> pd.DataFrame:
    played = finished_matches(matches)
    team_matches = played[(played["home_team"] == team) | (played["away_team"] == team)].copy()
    team_matches = team_matches.sort_values("utc_date")

    def _result(row: pd.Series) -> str:
        is_home = row["home_team"] == team
        goals_for = row["home_goals"] if is_home else row["away_goals"]
        goals_against = row["away_goals"] if is_home else row["home_goals"]
        if goals_for > goals_against:
            return "V"
        if goals_for < goals_against:
            return "D"
        return "E"

    team_matches["resultado"] = team_matches.apply(_result, axis=1)
    team_matches["mandante_ou_visitante"] = team_matches["home_team"].apply(
        lambda home_team: "casa" if home_team == team else "fora"
    )
    return team_matches[
        [
            "utc_date",
            "league_name",
            "matchday",
            "home_team",
            "away_team",
            "home_goals",
            "away_goals",
            "mandante_ou_visitante",
            "resultado",
        ]
    ]


def overperformance_table(standings: pd.DataFrame) -> pd.DataFrame:
    """Compara a posição real na tabela com a posição esperada pelo saldo de gols."""
    rows = []
    for league_name, table in standings.groupby("league_name"):
        table = table.copy()
        table["posicao_esperada"] = (
            table["goal_difference"].rank(ascending=False, method="min").astype(int)
        )
        table["diferenca_posicao"] = table["posicao_esperada"] - table["position"]
        rows.append(table)
    result = pd.concat(rows)
    return result[
        ["league_name", "team", "position", "posicao_esperada", "diferenca_posicao", "points", "goal_difference"]
    ].sort_values("diferenca_posicao", ascending=False)
