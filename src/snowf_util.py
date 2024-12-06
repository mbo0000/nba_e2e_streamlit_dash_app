import streamlit as st

_CONN = st.connection("snowflake")
_SOURCE = {
    'clean' : {
        'nba': ['PLAYER_GAME_STAT','GAMES','TEAM_YOY_STAT','TEAMS','TEAM_ROSTER']
    }
    , 'analytics' : {
        'nba' : ['PLAYER_CUM_STAT', 'TEAM_STAT_EXTENDED']
    }
}

@st.cache_data(ttl=3600)
def _get_all_tables_data():
    table_dfs              = {}

    for db, val in _SOURCE.items():
        schema = list(val.keys())[0]
        
        for table in val[schema]:
            query             = f'select * from {db}.{schema}.{table};'
            table_dfs[table]  = _CONN.query(query)

    return table_dfs

NBA_DATA = _get_all_tables_data()