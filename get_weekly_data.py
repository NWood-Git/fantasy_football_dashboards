# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 17:09:08 2023

@author: nicho
"""
import pandas as pd
import nfl_data_py as nfl
from global_variables import years, save_loc

## Variables
valid_pos =  ['QB', 'RB', 'WR', 'TE'] ## Only look at data for the QB, RB, WR, TE positions

## download and clean the data set with weekly data - 
## nfl.import_weekly_data(years, columns, downcast) 
weekly_data_df = nfl.import_weekly_data(years)

cols_to_drop = ['headshot_url', 'fantasy_points','fantasy_points_ppr']
col_rename_dict = {'recent_team' : 'team'}

weekly_data_df = weekly_data_df.drop(columns= cols_to_drop)
weekly_data_df = weekly_data_df.rename(columns=col_rename_dict)

weekly_data_df = weekly_data_df[weekly_data_df['position_group'].isin(valid_pos)]

## NEED TO FIGURE OUT HOW TO ADD RETURN YARDS - USE Play-By-Play DF?
weekly_data_df['return_yards_placeholder'] = 0

## Add Key column 
weekly_data_df['key'] = weekly_data_df.apply(lambda row :  f"{row['player_name']}|{row['team']}|{row['position_group']}|{row['week']}", axis=1 )

weekly_data_df.to_csv(f'{save_loc}weekly_data_df.csv', index=False)
