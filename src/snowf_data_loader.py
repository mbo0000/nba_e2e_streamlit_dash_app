import streamlit as st

class Snowf:

    def __init__(_self):
        _self.conn = None
    
    @st.cache_resource
    def _get_snowf_conn(_self):
        return st.connection("snowflake")

    @st.cache_data(ttl=3600)
    def query_data(_self, query):
        return _self.conn.query(query)

    @st.cache_data(ttl=3600)
    def get_all_source_data(_self, source):
        table_dfs  = {}
        _self.conn = _self._get_snowf_conn()
    
        for db, val in source.items():
            schema = list(val.keys())[0]
            for table in val[schema]:
                query             = f'select * from {db}.{schema}.{table};'
                table_dfs[table]  = _self.query_data(query)

        return table_dfs