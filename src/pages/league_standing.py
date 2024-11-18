import streamlit as st
import src.snowf_util as snow

st.title('League Standing & Leaderboard')
st.sidebar.header("League Standing")

teams           = snow.NBA_DATA['TEAMS']
team_stat       = snow.NBA_DATA['TEAM_YOY_STAT'].merge(
                    teams
                    , left_on = 'TEAM_ID'
                    , right_on = 'ID'
                )[['NICKNAME', 'WINS', 'LOSSES', 'WIN_PCT', 'YEAR', 'TEAM_CONFERENCE']]

year_options    = set(team_stat[team_stat['YEAR']>=2023]['YEAR'])
year            = st.selectbox(
                    'Select Season Year'
                    , year_options
                    , index = None
                    , placeholder = '2024'
                )

if year == None:
    year        = max(team_stat['YEAR'])

@st.cache_data(ttl=3600)
def get_team_standing_stats(conf, df, year):
    standing = df[df['YEAR'] == year].sort_values('WIN_PCT', ascending=False)
    return standing[standing['TEAM_CONFERENCE']==conf][['NICKNAME', 'WINS', 'LOSSES', 'WIN_PCT']].rename(columns = {'NICKNAME' : 'TEAM'})

conf            = ['East', 'West']
for idx, col in enumerate(st.columns(2)):
    with col:
        st.header(conf[idx])
        table      = get_team_standing_stats(conf[idx], team_stat, year)
        st.markdown(table.style.hide(axis="index").to_html(), unsafe_allow_html=True)



stats_dct = [
            {'ppg': {
                    'label'     : 'point_pg'
                    , 'caption' : 'Points Per Game'
                }
            }
            , {'rbp': {
                    'label'     : 'rebound_pg'
                    , 'caption' : 'Rebounds Per Game'
                }
            }
            , {'apg': {
                    'label'     : 'assist_pg'
                    , 'caption' : 'Assists Per Game'
                }
            }
            , {'3pm': {
                    'label'     : 'three_point_made'
                    , 'caption' : '3 Points Made'
                }
            }
            , {'bpg': {
                    'label'     : 'block_per_game'
                    , 'caption' : 'Block Per Game'
                }
            }
            , {'spg': {
                    'label'     : 'steal_per_game'
                    , 'caption' : 'Steal Per Game'
                }
            }
        ]

if len(stats_dct) % 2 != 0:
    stats_dct.append({
        None: None
    })


player_stat = snow.NBA_DATA['PLAYER_CUM_STAT']

@st.cache_data(ttl=3600)
def get_player_stat(label, df, year):
    stat = df[df['YEAR'] == year]
    return stat[['PLAYER', 'TEAM', label]]\
                            .sort_values(label, ascending = False)\
                            .rename(columns = {label : key.upper()})\
                            .reset_index(drop = True)\
                            .head(5)

grid = [stats_dct[i:i+2] for i in range(0, len(stats_dct),2)]
for row in grid:  
    
    for idx, table in enumerate(st.columns(2)):
        col             = row[idx]

        with table:
            val         = list(col.values())[0]
            key         = list(col.keys())[0]

            if not val: continue

            caption     = val['caption']
            label       = val['label'].upper()
            df          = get_player_stat(label, player_stat, year)

            st.caption(caption)
            st.table(df)