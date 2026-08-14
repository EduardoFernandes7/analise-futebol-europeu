import datetime as dt
import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))

from analysis.metrics import (
    finished_matches,
    goals_summary_table,
    home_advantage_table,
    overperformance_table,
    team_results,
    title_race_gap_table,
    load_data,
)

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"

st.set_page_config(page_title="Futebol Europeu — Análise", page_icon="⚽", layout="wide")

matches, standings = load_data(PROCESSED_DIR)
played = finished_matches(matches)

st.title("⚽ Análise das 5 Grandes Ligas Europeias")
st.caption(
    f"Premier League, La Liga, Bundesliga, Serie A e Ligue 1 — temporada {matches['season'].iloc[0]}/"
    f"{str(matches['season'].iloc[0] + 1)[-2:]}. Fonte: football-data.org."
)

league_options = ["Todas as ligas"] + sorted(matches["league_name"].unique())
selected_league = st.sidebar.selectbox("Liga", league_options)

league_matches = played if selected_league == "Todas as ligas" else played[played["league_name"] == selected_league]
league_standings = standings if selected_league == "Todas as ligas" else standings[standings["league_name"] == selected_league]

tab_overview, tab_standings, tab_team = st.tabs(["Visão geral", "Classificação", "Time"])

with tab_overview:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Vantagem de jogar em casa")
        fig = px.bar(
            home_advantage_table(matches if selected_league == "Todas as ligas" else league_matches),
            x="league_name",
            y=["vitoria_mandante_pct", "empate_pct", "vitoria_visitante_pct"],
            barmode="stack",
            labels={"league_name": "Liga", "value": "% das partidas", "variable": "Resultado"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Média de gols por partida")
        fig = px.bar(
            goals_summary_table(matches if selected_league == "Todas as ligas" else league_matches),
            x="league_name",
            y="media_gols_por_partida",
            labels={"league_name": "Liga", "media_gols_por_partida": "Gols/partida"},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Disputa pelo título (diferença de pontos entre 1º e 2º)")
    st.dataframe(title_race_gap_table(standings), use_container_width=True, hide_index=True)

    st.subheader("Times que superaram ou decepcionaram o saldo de gols")
    st.caption("Posição esperada = ranking pelo saldo de gols. Diferença positiva = terminou acima do esperado.")
    st.dataframe(
        overperformance_table(standings).head(10),
        use_container_width=True,
        hide_index=True,
    )

with tab_standings:
    st.subheader(f"Classificação — {selected_league}")
    st.dataframe(
        league_standings.sort_values(["league_name", "position"]).drop(columns=["season"]),
        use_container_width=True,
        hide_index=True,
    )

with tab_team:
    teams = sorted(league_standings["team"].unique())
    selected_team = st.selectbox("Time", teams)

    if selected_team:
        results = team_results(matches, selected_team)
        wins = (results["resultado"] == "V").sum()
        draws = (results["resultado"] == "E").sum()
        losses = (results["resultado"] == "D").sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Vitórias", wins)
        col2.metric("Empates", draws)
        col3.metric("Derrotas", losses)

        st.dataframe(results, use_container_width=True, hide_index=True)

last_update = dt.datetime.fromtimestamp((PROCESSED_DIR / "matches.parquet").stat().st_mtime)
st.sidebar.caption(f"Dados atualizados em {last_update:%d/%m/%Y}")
