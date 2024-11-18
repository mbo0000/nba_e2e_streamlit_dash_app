import streamlit as st

pg = st.navigation([
        st.Page("src/pages/league_standing.py")
        , st.Page("src/pages/team_season_stat.py")
    ])
pg.run()