import numpy as np
import pandas as pd
import json
import requests
import streamlit as st
import sys
import os

# Add the package directory to sys.path
sys.path.append(os.path.abspath('streamlit_pandas-0.0.9'))

# Now you can import modules from the package
import streamlit_pandas as sp
st.set_page_config(layout="wide")

def highlight_owned(row):
    color = 'background-color: grey' if row['Owned'] else ''
    return [color] * len(row)

cols = ['id','now_cost','web_name','total_points','selected_by_percent','form','element_type', 'event_points',
        'points_per_game', 'status',
        'transfers_in', 'transfers_in_event', 'transfers_out',
         'minutes', 'goals_scored', 'assists', 
         'clean_sheets', 'goals_conceded', 'saves', 
         'ict_index', 'starts', ]


ignore =['id','form','points_per_game', 'status',
        'transfers_in', 'transfers_in_event', 'transfers_out',
         'minutes', 'goals_scored', 'assists', 
         'clean_sheets', 'goals_conceded', 'saves', 
         'ict_index', 'starts','event_points','selected_by_percent' ]

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
create_data = {"position": "multiselect",'Owned':'multiselect'}

y = json.loads(x.text)
standings = y['standings']['results']

df = pd.DataFrame(standings)
df = df[['player_name','entry_name','rank','total']]


mercenaire = []
for connard in standings:
    picks = requests.get('https://fantasy.premierleague.com/api/entry/{}/event/5/picks/'.format(connard['entry']))
    picks = json.loads(picks.text)['picks']
    for i in picks:
        mercenaire.append([connard['entry_name'],i['element']])

players_owned = pd.DataFrame(mercenaire,columns=("owner",'id'))

df_merged = pd.merge(players, players_owned, on='id', how='left', indicator=True)
df_merged['Owned'] = df_merged['_merge'] == 'both'

# Drop the '_merge' column as it's no longer needed
df_merged.drop(columns=['_merge'], inplace=True)

column_to_move = 'owner'
new_column_order = [column_to_move] + [col for col in df_merged.columns if col != column_to_move]

# Reorder the DataFrame
df_merged = df_merged[new_column_order]

#styled_df = df_merged.style.apply(highlight_owned, axis=1)

all_widgets = sp.create_widgets(df_merged,create_data=create_data,ignore_columns=ignore)
res = sp.filter_df(df_merged, all_widgets)

st.header("Players")
st.write(res)

st.header("Standings")
st.write(df)


