# import streamlit as st
# import src.snowf_util as snow

# st.title('League Standing & Leaderboard')
# st.sidebar.header("League Standing")

# # load data
# teams               = snow.NBA_DATA['TEAMS']
# team_stat_extended  = snow.NBA_DATA['TEAM_STAT_EXTENDED']
# team_stat           = snow.NBA_DATA['TEAM_YOY_STAT'].merge(
#                         teams
#                         , left_on = 'TEAM_ID'
#                         , right_on = 'ID'
#                     )
# team_stat           = team_stat.merge(team_stat_extended, on = ['TEAM_ID', 'YEAR'])\
#                         [['NICKNAME', 'WINS', 'LOSSES', 'WIN_PCT', 'YEAR', 'TEAM_CONFERENCE', 'CURRENT_STREAK', 'LAST_10_GAMES']]

# # season selection
# years               = set(team_stat[team_stat['YEAR']>=2023]['YEAR'])
# year_select         = st.selectbox(
#                         'Select Season Year'
#                         , years
#                         , index = None
#                         , placeholder = '2024'
#                     )

# if year_select == None:
#     year_select        = max(team_stat['YEAR'])


# # get team stat df
# @st.cache_data(ttl=3600)
# def get_team_standing_stats(conf, df, year):
#     standing = df[df['YEAR'] == year].sort_values('WIN_PCT', ascending=False)
#     return standing[standing['TEAM_CONFERENCE']==conf][['NICKNAME', 'WINS', 'LOSSES', 'WIN_PCT', 'LAST_10_GAMES', 'CURRENT_STREAK']]\
#             .rename(columns = {
#                 'NICKNAME'          : 'TEAM'
#                 , 'WINS'            : 'W'
#                 , 'LOSSES'          : 'L'
#                 , 'LAST_10_GAMES'   : 'L10'
#                 , 'CURRENT_STREAK'  : 'STK'
#             })

# conf            = ['East', 'West']
# for idx, col in enumerate(st.columns(2)):
#     with col:
#         st.header(conf[idx])
#         table      = get_team_standing_stats(conf[idx], team_stat, year_select).reset_index(drop = True)
#         st.table(table)


# # league stat leaderboard
# stats_dct = [
#             {'ppg': {
#                     'label'     : 'point_pg'
#                     , 'caption' : 'Points Per Game'
#                 }
#             }
#             , {'rbp': {
#                     'label'     : 'rebound_pg'
#                     , 'caption' : 'Rebounds Per Game'
#                 }
#             }
#             , {'apg': {
#                     'label'     : 'assist_pg'
#                     , 'caption' : 'Assists Per Game'
#                 }
#             }
#             , {'3pm': {
#                     'label'     : 'three_point_made'
#                     , 'caption' : '3 Points Made'
#                 }
#             }
#             , {'bpg': {
#                     'label'     : 'block_per_game'
#                     , 'caption' : 'Block Per Game'
#                 }
#             }
#             , {'spg': {
#                     'label'     : 'steal_per_game'
#                     , 'caption' : 'Steal Per Game'
#                 }
#             }
#         ]

# if len(stats_dct) % 2 != 0:
#     stats_dct.append({
#         None: None
#     })


# player_stat = snow.NBA_DATA['PLAYER_CUM_STAT']

# @st.cache_data(ttl=3600)
# def get_player_stat(label, key, df, year):
#     stat = df[df['YEAR'] == year]
#     return stat.sort_values([label, 'GAME_PLAYED'], ascending = [False, False])\
#                 .rename(columns = {label : key})\
#                 .reset_index(drop = True)\
#                 .head(5)[['PLAYER', 'TEAM', key ]]

# grid = [stats_dct[i:i+2] for i in range(0, len(stats_dct),2)]
# for row in grid:  
    
#     for idx, table in enumerate(st.columns(2)):
#         col             = row[idx]

#         with table:
#             val         = list(col.values())[0]
#             key         = list(col.keys())[0]
#             if not val: continue

#             caption     = val['caption']
#             label       = val['label'].upper()
#             stat_name   = key.upper()
#             df          = get_player_stat(label, stat_name, player_stat, year_select)

#             st.caption(caption)
#             st.table(df)