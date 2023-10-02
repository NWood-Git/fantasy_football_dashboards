# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 20:36:49 2023

@author: nicho
"""
import pandas as pd
import nfl_data_py as nfl
from global_variables import years, save_loc

pbp = nfl.import_pbp_data(years, downcast=True, cache=False, alt_path=None)

pbp_cols = ['home_team','away_team','week','play_type_nfl','play_type','yards_gained','field_goal_result','kick_distance',
 'extra_point_result','two_point_conv_result','td_team','td_player_name','interception','safety','fumble_lost',
 'own_kickoff_recovery_td','sack','touchdown','pass_touchdown', 'rush_touchdown', 'return_touchdown',
 'fumble','complete_pass','lateral_recovery','passer','passing_yards',
 'receiver','receiving_yards','rusher','rushing_yards','punt_returner_player_name',
 'kickoff_returner_player_name','kicker_player_name','return_team','return_yards','special_teams_play','st_play_type',
 'away_score','home_score','total_line','success','pass','rush','special','possession_team', 'desc']
## 'play_type' - 'play_type_nfl' is more informative

pbp_filtered = pbp[pbp_cols]

## Create Dataframe to see unique values for each field

# Initialize an empty list to store the column names and unique values
column_names = []
unique_values = []

# Iterate through each column in the DataFrame
for column in pbp_filtered.columns:
    # Append the column name to the list of column names
    column_names.append(column)
    
    # Get the unique values from the column and convert them to a list
    unique_values_list = pbp_filtered[column].unique().tolist()
    
    # Append the list of unique values to the list of unique values
    unique_values.append(unique_values_list)

# Create a new DataFrame using the lists of column names and unique values
pbp_col_info_df = pd.DataFrame({'Column_Name': column_names, 'Unique_Values': unique_values})

## Save - pbp_col_info_df
# pbp_col_info_df.to_csv("pbp_col_info.csv")

## Filter out rows with undesirable values in the any specific columns

## Remove rows where play_type_nfl is not helpful for desired analysis:
play_type_nfl_values_to_filter_out = ['GAME_START',  'PENALTY', 'TIMEOUT', 'END_QUARTER', 'UNSPECIFIED', 'END_GAME']

pbp_filtered = pbp_filtered[~pbp_filtered['play_type_nfl'].isin(play_type_nfl_values_to_filter_out)]

## Fix name Abrev so it is First Inital. Last Name
## Split after first period to avoid issues with A. St. Brown but fix Breece Hall from Bre. Hall to B. Hall and Michael Carter from Mi. Carter to M. Carter)
pbp_filtered['rusher'] = pbp_filtered['rusher'].apply(lambda x: x if pd.isna(x) is True else f"{x.split('.',1)[0][0]}.{x.split('.',1)[1]}")
pbp_filtered['receiver'] = pbp_filtered['receiver'].apply(lambda x: x if pd.isna(x) is True else f"{x.split('.',1)[0][0]}.{x.split('.',1)[1]}")
pbp_filtered['passer'] = pbp_filtered['passer'].apply(lambda x: x if pd.isna(x) is True else f"{x.split('.',1)[0][0]}.{x.split('.',1)[1]}")


## Save pbp_filtered file:
pbp_filtered.to_csv(f"{save_loc}pbp_filtered.csv", index=False)
