import numpy as np
import pandas as pd
import json
import requests
import streamlit as st
import streamlit_pandas as sp
st.set_page_config(layout="wide")

cols = ['now_cost','web_name','total_points','selected_by_percent','form','element_type', 'event_points',
        'points_per_game', 'status',
        'transfers_in', 'transfers_in_event', 'transfers_out',
         'minutes', 'goals_scored', 'assists', 
         'clean_sheets', 'goals_conceded', 'saves', 
         'ict_index', 'starts', ]


ignore =['form','points_per_game', 'status',
        'transfers_in', 'transfers_in_event', 'transfers_out',
         'minutes', 'goals_scored', 'assists', 
         'clean_sheets', 'goals_conceded', 'saves', 
         'ict_index', 'starts', ]

x = requests.get('https://fantasy.premierleague.com/api/leagues-classic/2250375/standings/')
players = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')

players = json.loads(players.text)['elements']
players = pd.DataFrame(players,columns=cols)
players['now_cost'] = players['now_cost']/10
players[['selected_by_percent','form','points_per_game','ict_index']] = players[['selected_by_percent','form','points_per_game','ict_index']].astype(float)
players = players.rename(columns={'web_name':'name'})
players = players.rename(columns={'now_cost':'cost'})
players = players.rename(columns={'element_type':'position'})
players['name'] = players['name'].str.lower()

position_map = {
    1: 'GK',
    2: 'DEF',
    3: 'MID',
    4: 'ATT'
}

# Convert PositionType numbers to corresponding position strings
players['position'] = players['position'].map(position_map)
create_data = {"position": "multiselect"}

y = json.loads(x.text)
standings = y['standings']['results']

df = pd.DataFrame(standings)
df = df[['player_name','entry_name','rank','total']]

all_widgets = sp.create_widgets(players,create_data=create_data,ignore_columns=ignore)
res = sp.filter_df(players, all_widgets)

st.header("Players")
st.write(res)

st.header("Standings")
st.write(df)


