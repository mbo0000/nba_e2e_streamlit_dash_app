import streamlit as st

_SOURCE = {
        'clean' : {
            'nba': ['PLAYER_GAME_STAT','GAMES','TEAM_YOY_STAT','TEAMS','TEAM_ROSTER']
        }
        , 'analytics' : {
            'nba' : ['PLAYER_CUM_STAT', 'TEAM_STAT_EXTENDED']
        }
    }

class Snowf:
    def __init__(self):
        pass

    @st.cache_resource
    def _get_snowf_conn(_self):
        return st.connection("snowflake")

    @st.cache_data(ttl=3600)
    def _get_all_tables_data(_self):
        table_dfs   = {}
        conn        = _self._get_snowf_conn()

        for db, val in _SOURCE.items():
            schema = list(val.keys())[0]

            for table in val[schema]:
                query             = f'select * from {db}.{schema}.{table};'
                table_dfs[table]  = conn.query(query)

        return table_dfs

    def get_data_teams(self):
        return self._get_all_tables_data()['TEAMS']

    def get_data_games(self):
        return self._get_all_tables_data()['GAMES']

    def get_data_team_stat(self):
        return self._get_all_tables_data()['TEAM_YOY_STAT']

    def get_data_team_roster(self):
        return self._get_all_tables_data()['TEAM_ROSTER']

    def get_data_team_stat_ext(self):
        return self._get_all_tables_data()['TEAM_STAT_EXTENDED']