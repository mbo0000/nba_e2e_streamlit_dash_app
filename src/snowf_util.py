import streamlit as st

_conn = st.connection("snowflake")
_tables = ['PLAYER_GAME_STAT','GAMES','TEAM_YOY_STAT','TEAMS','TEAM_ROSTER', 'PLAYER_CUM_STAT']

@st.cache_data(ttl=3600)
def get_all_tables_data():
    table_dict              = {}

    for table in _tables:
        df                  = _conn.query(f'select * from {table};')
        table_dict[table]   = df

    return table_dict

NBA_DATA = get_all_tables_data()