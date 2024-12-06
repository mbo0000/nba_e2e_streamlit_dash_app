import streamlit as st

st.set_page_config(
    page_icon="🏀",
    layout="wide"
)

pg = st.navigation([
        # st.Page("src/pages/league_standing.py")
        st.Page("src/pages/team_season_stat.py")
    ])
pg.run()