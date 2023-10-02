# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 16:12:02 2023

@author: nicho
"""
import pandas as pd
import nfl_data_py as nfl
from global_variables import years, save_loc

## Variables
valid_pos =  ['QB', 'RB', 'WR', 'TE'] ## Only look at data for the QB, RB, WR, TE positions

## download the data set with weekly data - # nfl.import_weekly_data(years, columns, downcast) 
weekly_df = nfl.import_weekly_data(years)

cols_to_drop = ['headshot_url']
col_rename_dict = {'recent_team' : 'team'}

weekly_df = weekly_df.drop(columns= cols_to_drop)
weekly_df = weekly_df.rename(columns=col_rename_dict)

weekly_df = weekly_df[weekly_df['position_group'].isin(valid_pos)]

## NEED TO FIGURE OUT HOW TO ADD RETURN YARDS - USE Play-By-Play DF?
weekly_df['return_yards_placeholder'] = 0

## Load play_by_play_data
pbp_df = pd.read_csv(f'{save_loc}pbp_filtered.csv')

## Used pbp_df to get runs / passes greater than 40 yards
def create_play_bonus_df(pbp_df, league_bonus_dict, league_name):
    '''Create a dataframe with bonus points for for yard plays'''
    #league_bonus_dict = td_palooza_bonus
        
    ## Selected columns
    cols_play_len = ['possession_team', 'week', 'play_type_nfl','touchdown','yards_gained','passer', 'passing_yards','receiver', 'receiving_yards', 'rusher','rushing_yards']    
    
    len_bonus_plays_df = pbp_df[(pbp_df['play_type_nfl'].isin(['RUSH', 'PASS'])) & (pbp_df['yards_gained'] >= league_bonus_dict['play_yd_bonus_len'])][cols_play_len]
    
    player_list = []
    team_list = []
    week_list = []
    bonus_point_list = []
    
    for idx, row in len_bonus_plays_df.iterrows():
        if row['play_type_nfl'] == 'RUSH':
            rush_bonus_points = league_bonus_dict['yd_rush_bonus']
            if row['touchdown'] == 1:
                rush_bonus_points += league_bonus_dict['yd_rush_td_bonus']
            player_list.append(row['rusher'])
            team_list.append(row['possession_team'])
            week_list.append(row['week'])
            bonus_point_list.append(rush_bonus_points) 
        elif row['play_type_nfl'] == 'PASS':
            pass_bonus_points = league_bonus_dict['yd_pass_bonus']
            rec_bonus_points = league_bonus_dict['yd_rec_bonus']
            if row['touchdown'] == 1:
                pass_bonus_points += league_bonus_dict['yd_pass_td_bonus']
                rec_bonus_points += league_bonus_dict['yd_rec_td_bonus']
            player_list.extend([row['passer'], row['receiver']])
            team_list.extend([row['possession_team'], row['possession_team']])
            week_list.extend([row['week'], row['week']])
            bonus_point_list.extend([pass_bonus_points, rec_bonus_points])
            
    play_bonus_df = pd.DataFrame({
        'player_name': player_list,
        'team' : team_list,
        'week' : week_list,
        f"{league_name}_play_bonus_fan_pts" : bonus_point_list})       
    return play_bonus_df




def get_league_fantasy_points(weekly_df, pbp_df, league_scoring_dict, league_bonus_dict, league_name):

    ## Creating columns for pre-bonus fantasy points and total yard bonus fantasy points
    pre_bonus_fan_pts_list = []
    total_yard_bonus_fan_pts_list =[]
    
    ## Calculate fantasy points before single play bonuses
    for idx, row in weekly_df.iterrows():
        
        ## Passing total yard bonuses
        if row['passing_yards'] >= 500:
            total_pass_yard_bonus = (league_bonus_dict['pass_500_bonus'] + 
                                     league_bonus_dict['pass_400_bonus'] +
                                     league_bonus_dict['pass_300_bonus'])
        elif row['passing_yards'] >= 400:
            total_pass_yard_bonus = (league_bonus_dict['pass_400_bonus'] + 
                                     league_bonus_dict['pass_300_bonus'])
        elif row['passing_yards'] >= 300:
            total_pass_yard_bonus = league_bonus_dict['pass_300_bonus']
        else:
            total_pass_yard_bonus = 0
       
        ## Rushing total yard bonuses     
        if row['rushing_yards'] >= 200:
            total_rush_yard_bonus = (league_bonus_dict['rush_200_bonus'] + 
                                     league_bonus_dict['rush_150_bonus'] +
                                     league_bonus_dict['rush_100_bonus'])
        elif row['rushing_yards'] >= 150:
            total_rush_yard_bonus = (league_bonus_dict['rush_150_bonus'] + 
                                     league_bonus_dict['rush_100_bonus'])
        elif row['rushing_yards'] >= 100:
            total_rush_yard_bonus = league_bonus_dict['rush_100_bonus']
        else:
            total_rush_yard_bonus = 0
            
        ## Receiving total yard bonuses     
        if row['receiving_yards'] >= 200:
            total_rec_yard_bonus = (league_bonus_dict['rec_200_bonus'] + 
                                    league_bonus_dict['rec_150_bonus'] +
                                    league_bonus_dict['rec_100_bonus'])
        elif row['receiving_yards'] >= 150:
            total_rec_yard_bonus = (league_bonus_dict['rec_150_bonus'] + 
                                    league_bonus_dict['rec_100_bonus'])
        elif row['receiving_yards'] >= 100:
            total_rec_yard_bonus = league_bonus_dict['rec_100_bonus']
        else:
            total_rec_yard_bonus = 0
        
        ## Sum bonuses and assign to row
        #row[f"{league_name}_total_yard_bonus_fan_pts"] = total_pass_yard_bonus + total_rush_yard_bonus + total_rec_yard_bonus
        total_yard_bonus_fan_pts_list.append(total_pass_yard_bonus + total_rush_yard_bonus + total_rec_yard_bonus)
    
        ## Getting point totals            
        passing_fan_pts = (
            row['completions'] * league_scoring_dict['pass_completions_multiplier'] +
            row['passing_yards'] * league_scoring_dict['pass_yd_multiplier'] +
            row['passing_tds'] * league_scoring_dict['pass_td_multiplier'] +
            row['interceptions'] * league_scoring_dict['int_multiplier'] +
            row['sack_fumbles_lost'] * league_scoring_dict['fum_lost'] +
            row['passing_2pt_conversions'] * league_scoring_dict['two_pt_conv_multiplier']
            )
        
        rushing_fan_pts = (
            row['rushing_yards'] * league_scoring_dict['rush_yd_multiplier'] +
            row['rushing_tds'] * league_scoring_dict['rush_td_multiplier'] +
            row['rushing_fumbles_lost'] * league_scoring_dict['fum_lost'] +
            row['rushing_2pt_conversions'] * league_scoring_dict['two_pt_conv_multiplier'] # + total_rush_yard_bonus
            )
            
        receiving_fan_pts = (
            row['receptions'] * league_scoring_dict['rec_multiplier'] +
            row['receiving_yards'] * league_scoring_dict['rec_yd_multiplier'] +
            row['receiving_tds'] * league_scoring_dict['rec_td_multiplier'] +
            row['receiving_fumbles_lost'] * league_scoring_dict['fum_lost'] +
            row['receiving_2pt_conversions'] * league_scoring_dict['two_pt_conv_multiplier'] # + total_rec_yard_bonus
            )
        
        return_fan_pts = (
            row['return_yards_placeholder'] * league_scoring_dict['ret_yd_multiplier'] +
            row['special_teams_tds'] * league_scoring_dict['ret_td_multiplier']
            )
        
        ## Sum fantasy points to get total fantasy points pre-bonus
        #row[f"{league_name}_pre_bonus_fan_pts"] = passing_fan_pts + rushing_fan_pts + receiving_fan_pts + return_fan_pts
        pre_bonus_fan_pts_list.append(passing_fan_pts + rushing_fan_pts + receiving_fan_pts + return_fan_pts)
    
    weekly_df[f"{league_name}_pre_bonus_fan_pts"] = pre_bonus_fan_pts_list
    weekly_df[f"{league_name}_total_yard_bonus_fan_pts"] = total_yard_bonus_fan_pts_list
    
    ## Create df to get play based bonuses using create_play_bonus_df function
    play_bonus_df = create_play_bonus_df(pbp_df, league_bonus_dict, league_name)
    
    result_df = pd.merge(left=weekly_df,
                         right=play_bonus_df,
                         how='left',
                         on=['player_name','team', 'week'])
    
    result_df[f"{league_name}_play_bonus_fan_pts"] = result_df[f"{league_name}_play_bonus_fan_pts"] .fillna(0)
    
    result_df[f"{league_name}_total_fan_pts"] = result_df[f"{league_name}_pre_bonus_fan_pts"] + result_df[f"{league_name}_total_yard_bonus_fan_pts"] +result_df[f"{league_name}_play_bonus_fan_pts"]

    return result_df[['player_name','team', 'week', f"{league_name}_pre_bonus_fan_pts",
                      f"{league_name}_total_yard_bonus_fan_pts", f"{league_name}_play_bonus_fan_pts",
                      f"{league_name}_total_fan_pts"]] # weekly_fantasy_df_w_league_points




# test_play_bonus_df = create_play_bonus_df(pbp_df, td_palooza_bonuses, 'td_palooza')


from league_scoring import td_palooza_scoring, td_palooza_bonuses

td_palooza_points_df = get_league_fantasy_points(weekly_df,
                                                 pbp_df,
                                                 league_scoring_dict=td_palooza_scoring,
                                                 league_bonus_dict=td_palooza_bonuses,
                                                 league_name='td_palooza')
### JOIN ABOVE TO WEEKLY DF
weekly_w_td_palooza = pd.merge(left=weekly_df, 
                               right=td_palooza_points_df,
                               how='left',
                               on=['player_name','team', 'week'])

## Test
