import streamlit as st
from src.snowf_data_loader import Snowf
import pandas as pd
import plotly.express as px
from sklearn import preprocessing

#================================================================================================================#
#-LOAD DATA------------------------------------------------------------------------------------------------------#
#================================================================================================================#
@st.cache_data(ttl=3600)
def get_team_stats():
    return trad_team_stat.merge(
        teams
        , left_on = 'TEAM_ID'
        , right_on = 'ID'
    ). merge(
        team_stat_extended
        , on = ['TEAM_ID', 'YEAR']
    )
snow                = Snowf()
teams               = snow.get_data_teams()
team_stat_extended  = snow.get_data_team_stat_ext()
trad_team_stat      = snow.get_data_team_stat()
games               = snow.get_data_games()
team_roster         = snow.get_data_team_roster()
team_stat           = get_team_stats()

#================================================================================================================#
#-UI SELECTION---------------------------------------------------------------------------------------------------#
#================================================================================================================#
year_list           = set(team_stat[team_stat['YEAR']>=2023]['YEAR'])
team_list           = set(sorted(team_stat['TEAM_NAME']))

with st.sidebar:
    st.title('Team Stat')

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

if year_select == None:
    year_select = max(team_stat['YEAR'])

if team_select == None:
    team_select = 'Lakers'

#================================================================================================================#
#-LOGO & TOPLINE STATS-------------------------------------------------------------------------------------------#
#================================================================================================================#

@st.cache_data(ttl=3600)
def team_logo_url(team):
    return team_stat[team_stat['TEAM_NAME']==team]['LOGO_URL'].iloc[0]

@st.cache_data(ttl=3600)
def team_topline_stats(team, year):
    df                  = team_stat[(team_stat['TEAM_NAME']==team) & (team_stat['YEAR']>=year)].copy()
    df['WL']            = df[['WINS', 'LOSSES']].astype(str).agg('-'.join, axis=1)
    df['NET_RATING']    = df['OFF_RATING'] - df['DEF_RATING']
    df                  = df[['WL','CURRENT_STREAK', 'LAST_10_GAMES', 'NET_RATING', 'CONF_RANK']]
    df.columns          = ['WL', 'STRK', 'L10', 'NET', 'CONF_RNK']
    return df.iloc[0].to_dict()

with st.container(height=150, border=False):
    logo, topline_stats     = st.columns([2,8], vertical_alignment='center')
    with logo:
        url                 = team_logo_url(team_select)
        st.image(f'{url}', width=150)

    with topline_stats:
            topline_stats   = team_topline_stats(team_select, year_select)
            cols            = st.columns(len(topline_stats))
            idx             = 0
            
            for k, val in topline_stats.items():
                with cols[idx]:
                    st.subheader(k)
                    st.text(val)
                idx += 1

#================================================================================================================#
#-RADAR & SCATTER CHARTS-----------------------------------------------------------------------------------------#
#================================================================================================================#
@st.cache_data(ttl=3600)
def get_radar_stats(team, year):
    cols                = ['TEAM_NAME', 'YEAR', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'REB_PG','STL_PG', 'AST_PG', 'BLK_PG']
    df                  = team_stat.loc[:, cols].copy()

    x                   = df.loc[:, cols[2:]].values
    min_max_scaler      = preprocessing.MinMaxScaler()
    x_scaled            = min_max_scaler.fit_transform(x)
    df[cols[2:]]        = x_scaled

    res                 = df[(df['TEAM_NAME'] == team) & (df['YEAR'] == year)]
    val                 = res.iloc[0][2:].tolist()
    res                 = pd.DataFrame(dict(theta = cols[2:], r = val))

    return res


radar_col, scatter_col = st.columns([4,6], vertical_alignment='center')
with radar_col:
    st.markdown("<h3 style='text-align: center; color: grey;'>Team Advanced Stats</h3>", unsafe_allow_html=True)
    radar_stats = get_radar_stats(team_select, year_select)
    fig         = px.line_polar(radar_stats, r='r', theta='theta', line_close=True, range_r=[0,1])
    # fill shaded area
    fig.update_traces(fill='toself')
    # hide radial axis labels
    fig.update_layout(polar = dict(radialaxis = dict(showticklabels = False)))
    st.plotly_chart(fig, theme=None)

with scatter_col:
    st.markdown("<h3 style='text-align: center; color: grey;'>Offensive vs Defensive Ratings</h3>", unsafe_allow_html=True)
    df                                              = team_stat[team_stat['YEAR'] == year_select].copy()
    df['COLOR']                                     = "#0000FF" 
    df['SIZE']                                      = 10
    df.loc[df['TEAM_NAME'] == team_select, 'COLOR'] = "#FF0000"
    df.loc[df['TEAM_NAME'] == team_select, 'SIZE']  = 50
    df                                              = df.loc[:, ['TEAM_NAME','OFF_RATING', 'DEF_RATING', 'COLOR', 'SIZE']]

    fig                                             = px.scatter(
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
#-ROSTER & GAMES PLAYED------------------------------------------------------------------------------------------#
#================================================================================================================#

@st.cache_data()
def _get_team_id(team):
    df = team_stat.loc[:,['TEAM_NAME', 'TEAM_ID']].drop_duplicates()
    return df[df['TEAM_NAME'] == team]['TEAM_ID'].iloc[0]

roster, games_col   = st.columns([2,8])
selected_team_id    = _get_team_id(team_select)
with roster:
    with st.container(height=700):
        st.markdown("<h3 style='color: grey;'>Roster</h3>", unsafe_allow_html=True)
        current_roster  = team_roster[(team_roster['TEAMID']==selected_team_id) & (team_roster['SEASON'] == year_select)]\
                            .sort_values('PLAYER')\
                            .reset_index(drop = True)
        st.table(current_roster[['PLAYER', 'POSITION']])

with games_col:
    with st.container(height=700):
        st.markdown("<h3 style='color: grey;'>Games</h3>", unsafe_allow_html=True)
        season_games            = games.loc[(games['TEAM_ID'] == selected_team_id) & (games['YEAR']==year_select)].sort_values('GAME_DATE', ascending=False).reset_index(drop=True)
        season_games['MATCHUP'] = [x[4:] for x in season_games['MATCHUP']]
        season_games.rename(columns={'PLUS_MINUS':'+-', 'GAME_DATE':'DATE'}, inplace=True)
        st.table(season_games.loc[:, [
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
        ]])