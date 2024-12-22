import streamlit as st
from src.snowf_data_loader import Snowf
import pandas as pd
import plotly.express as px
from sklearn import preprocessing


#================================================================================================================#
#-LOAD DATA------------------------------------------------------------------------------------------------------#
#================================================================================================================#
_SOURCE = {
        'clean' : {
            'nba': [
                'TEAMS'
                ,'GAMES'
                ,'TEAM_YOY_STAT'
                ,'TEAM_ROSTER'
            ]
        }
        , 'analytics' : {
            'nba' : [
                'TEAM_STAT_EXTENDED'
                , 'PLAYER_CUM_STAT'
            ]
        }
    }

snow                = Snowf()
source_data         = snow.get_all_source_data(_SOURCE)
teams               = source_data['TEAMS']
team_stat_extended  = source_data['TEAM_STAT_EXTENDED']
trad_team_stat      = source_data['TEAM_YOY_STAT']
games               = source_data['GAMES']
team_roster         = source_data['TEAM_ROSTER']
player_cum_stat     = source_data['PLAYER_CUM_STAT']
team_stat           = trad_team_stat.merge(
                        teams
                        , left_on = 'TEAM_ID'
                        , right_on = 'ID'
                    ). merge(
                        team_stat_extended
                        , on = ['TEAM_ID', 'YEAR']
                    )
selected_team_id    = None

#================================================================================================================#
#-HELPER FUNCS---------------------------------------------------------------------------------------------------#
#================================================================================================================#

@st.cache_data
def get_team_logo(team_id):
    return team_stat[team_stat['TEAM_ID']==team_id]['LOGO_URL'].iloc[0]

@st.cache_data
def get_team_id(team):
    df = team_stat.loc[:,['TEAM_NAME', 'TEAM_ID']].drop_duplicates()
    return df[df['TEAM_NAME'] == team]['TEAM_ID'].iloc[0]

@st.cache_data(ttl=3600)
def get_stat_by_team(df, team_id):
    return df[(df['TEAM_ID']==team_id)]

@st.cache_data(ttl=3600)
def get_stat_by_year(df,year):
    return df[df['YEAR'] == year]

@st.cache_data(ttl=3600)
def team_topline_stats(team_id, year):
    df                  = get_stat_by_team(team_stat, team_id).copy()
    df                  = get_stat_by_year(df, year)
    df['WL']            = df[['WINS', 'LOSSES']].astype(str).agg('-'.join, axis=1)
    df['NET_RATING']    = df['OFF_RATING'] - df['DEF_RATING']
    df                  = df[['WL','CURRENT_STREAK', 'LAST_10_GAMES', 'NET_RATING', 'CONF_RANK']]
    df.columns          = ['WL', 'STRK', 'L10', 'NET', 'CONF_RNK']
    return df.iloc[0].to_dict()

@st.cache_data(ttl=3600)
def get_radar_stats(team_id, year):
    cols                = ['TEAM_ID', 'YEAR', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'REB_PG','STL_PG', 'AST_PG', 'BLK_PG']
    df                  = team_stat[cols].copy()

    x                   = df.loc[:, cols[2:]].values
    min_max_scaler      = preprocessing.MinMaxScaler()
    x_scaled            = min_max_scaler.fit_transform(x)
    df[cols[2:]]        = x_scaled

    res                 = get_stat_by_team(df, team_id)
    res                 = get_stat_by_year(res, year)
    val                 = res.iloc[0][2:].tolist()
    res                 = pd.DataFrame(dict(theta = cols[2:], r = val))

    return res

#================================================================================================================#
#-UI SELECTION---------------------------------------------------------------------------------------------------#
#================================================================================================================#
year_list           = sorted(set(year for year in team_stat['YEAR'] if year >= 2024))
team_list           = set(sorted(team_stat['TEAM_NAME']))

with st.sidebar:
    st.title('Team Stat')
    st.markdown('For more info, visit [Github repo](https://github.com/mbo0000/nba_e2e_data_pipeline)')
    st.divider()

    year_select         = st.selectbox(
                                'Select Season Year'
                                , year_list
                                , index         = None
                                , placeholder   = '2024'
                            )

    team_select        = st.selectbox(
                                'Select Team Name'
                                , team_list
                                , index         = None
                                , placeholder   = 'Lakers'
                            )

# set default values on load
if year_select == None:
    year_select         = 2024

if team_select == None:
    team_select         = 'Lakers'

selected_team_id    = get_team_id(team_select)

#================================================================================================================#
#-LOGO & SEASON TOPLINE------------------------------------------------------------------------------------------#
#================================================================================================================#

with st.container(height=150, border=False):
    logo, topline_stats     = st.columns([2,8], vertical_alignment='center')
    with logo:
        url                 = get_team_logo(selected_team_id)
        st.image(f'{url}', width=150)

    with topline_stats:
            topline_stats   = team_topline_stats(selected_team_id, year_select)
            cols            = st.columns(len(topline_stats))
            idx             = 0
            
            for k, val in topline_stats.items():
                with cols[idx]:
                    st.subheader(k)
                    st.text(val)
                idx += 1
st.divider()

#================================================================================================================#
#-TRADITIONAL STATS----------------------------------------------------------------------------------------------#
#================================================================================================================#

with st.container(height=150, border=False):
    _, col = st.columns([0.5,9.5], vertical_alignment='center')

    trad_stats      =  get_stat_by_team(team_stat, selected_team_id)[[
                            'YEAR'
                            , 'WIN_PCT'
                            , 'FG_PCT'
                            , 'FG3_PCT'
                            , 'FT_PCT'
                            , 'REB_PG'
                            , 'STL_PG'
                            , 'AST_PG'
                            , 'BLK_PG'
                        ]].copy()
    curr_year_stats = get_stat_by_year(trad_stats, year_select).astype(float)
    prev_year_stats = get_stat_by_year(trad_stats, year_select-1).fillna(0).astype(float)
    labels          = curr_year_stats.columns[1:]

    with col:
        for idx, col in enumerate(st.columns(len(labels))):
            label = labels[idx]
            value = round(curr_year_stats[label].iloc[0],2)
            delta = round(curr_year_stats[label].iloc[0] - prev_year_stats[label].iloc[0],2)
            col.metric(label = label, value = value, delta = delta)

st.divider()
#================================================================================================================#
#-RADAR & SCATTER CHARTS-----------------------------------------------------------------------------------------#
#================================================================================================================#

radar_col, scatter_col = st.columns([4,6], vertical_alignment='center')
with radar_col:
    st.markdown("<h3 style='text-align: center; color: grey;'>Team Advanced Stats</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>Normalized traditional stats team vs league</p>", unsafe_allow_html=True)

    radar_stats = get_radar_stats(selected_team_id, year_select)
    fig         = px.line_polar(radar_stats, r='r', theta='theta', line_close=True, range_r=[0,1])

    # fill shaded area
    fig.update_traces(fill='toself')
    # hide radial axis labels
    fig.update_layout(polar = dict(radialaxis = dict(showticklabels = False)))

    st.plotly_chart(fig, theme=None)

with scatter_col:
    st.markdown("<h3 style='text-align: center; color: grey;'>Season Offensive vs Defensive Ratings</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: grey;'>Season averages of offensive and defensive ratings for all games played</p>", unsafe_allow_html=True)
    
    df                                                      = get_stat_by_year(team_stat, year_select).copy()
    df['COLOR']                                             = "#0000FF" 
    df['SIZE']                                              = 10
    df.loc[df['TEAM_ID'] == selected_team_id, 'COLOR']      = "#FF0000"
    df.loc[df['TEAM_ID'] == selected_team_id, 'SIZE']       = 50
    df                                                      = df[['TEAM_ID', 'TEAM_NAME','OFF_RATING', 'DEF_RATING', 'COLOR', 'SIZE']]

    fig                                                     = px.scatter(
                                                                df
                                                                , x         = "OFF_RATING"
                                                                , y         = "DEF_RATING"
                                                                , color     = "COLOR"
                                                                , size      = 'SIZE'
                                                                , hover_data= ['TEAM_NAME']
                                                            )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, theme=None)


#================================================================================================================#
#-GAMES STATS----------------------------------------------------------------------------------------------------#
#================================================================================================================#

team_games                  = get_stat_by_team(games, selected_team_id)
season_games                = get_stat_by_year(team_games, year_select)\
                                .sort_values('GAME_DATE', ascending=False)\
                                .reset_index(drop=True)
season_games['MATCHUP']     = [x[4:] for x in season_games['MATCHUP']]
season_games.rename(columns={'PLUS_MINUS':'+-', 'GAME_DATE':'DATE'}, inplace=True)

st.markdown("<h3 style='color: grey;'>Games Stats</h3>", unsafe_allow_html=True)
with st.container(height=500, border=False):
    st.dataframe(season_games[[
            'DATE'
            , 'MATCHUP'
            , 'SEASON_TYPE'
            , 'WL'
            , 'PTS'
            , 'FGA'
            , 'FGM'
            , 'FG_PCT'
            , 'FG3A'
            , 'FG3M'
            , 'FG3_PCT'
            , 'FTA'
            , 'FTM'
            , 'FT_PCT'
            , 'REB'
            , 'STL'
            , 'BLK'
            , 'TOV'
            , '+-'
        ]]
        , height=500
        , hide_index=True
        , use_container_width=True
    )


#================================================================================================================#
#-PLAYERS STATS--------------------------------------------------------------------------------------------------#
#================================================================================================================#
st.markdown("<h3 style='color: grey;'>Players Season Stats</h3>", unsafe_allow_html=True)

team_roster.rename(columns = {'TEAMID' : 'TEAM_ID', 'SEASON' : 'YEAR'}, inplace = True)
selected_team_roster        = get_stat_by_team(team_roster, selected_team_id)
curr_year_roster            = get_stat_by_year(selected_team_roster, year_select)[['TEAM_ID', 'PLAYER']]
df_merged                   = player_cum_stat.merge(curr_year_roster, on = 'PLAYER').copy()
player_year_stat            = get_stat_by_year(df_merged, year_select)
player_team_stat            = get_stat_by_team(player_year_stat, selected_team_id)[[
                                    'PLAYER'
                                    , 'GAME_PLAYED'
                                    , 'AVG_MIN_PLAYED'
                                    , 'POINT_PG'
                                    , 'FIELD_GOAL_PERCENTAGE'
                                    , 'THREE_POINT_PERCENTAGE'
                                    , 'FREE_THROW_PERCENTAGE'
                                    , 'ASSIST_PG'
                                    , 'REBOUND_PG'
                                    , 'BLOCK_PER_GAME'
                                    , 'STEAL_PER_GAME'
                                ]].drop_duplicates()

labels                      = ['PLAYER', 'GP', 'AVG_MIN', 'PTS', 'FG_PCT', '3P_PCT', 'FT_PCT', 'AST_PCT', 'REB_PG', 'BLK_PG', 'STL_PG']
player_team_stat.columns    = labels

with st.container(height=500, border=False):
    st.dataframe(player_team_stat, height=500, hide_index=True, use_container_width=True)