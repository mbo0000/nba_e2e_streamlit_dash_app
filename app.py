import streamlit as st

conn = st.connection("snowflake")
df = conn.query("SELECT * FROM TEAMS;", ttl="10m")

for row in df.itertuples():
    st.write(f"{row.FULL_NAME} has a :{row.ABBREVIATION}:")