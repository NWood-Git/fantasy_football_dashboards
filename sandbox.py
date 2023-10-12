# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 16:12:02 2023

@author: nicho
"""
import pandas as pd
import nfl_data_py as nfl
from global_variables import years, save_loc

## Load play_by_play_data
pbp_df = pd.read_csv(f'{save_loc}pbp_filtered.csv')
weekly_data_df = pd.read_csv(f'{save_loc}weekly_data_df.csv')

## Functions to create Weekly data / fantasy points for analysis

## Create data frame with data frame with the big play bonus points
## Used pbp_df to get runs / passes greater than 40 yards
def create_play_bonus_df(pbp_df, league_bonus_dict, league_name, league_col_prefix=False):
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
    
    if league_col_prefix is True:
        play_bonus_df = pd.DataFrame({
            'player_name': player_list,
            'team' : team_list,
            'week' : week_list,
            f"{league_name}_play_bonus_fan_pts" : bonus_point_list})
    else:
        play_bonus_df = pd.DataFrame({
            'player_name': player_list,
            'team' : team_list,
            'week' : week_list,
            'play_bonus_fan_pts' : bonus_point_list})
    
    return play_bonus_df


## Create data frame wuth fantasy points - this uses the above create_play_bonus_df function
## This calculates fantasy points and the total yard bonsuses

def get_league_fantasy_points(weekly_input_df, pbp_df, league_scoring_dict, league_bonus_dict,
                              league_name, league_col_prefix=False):

    weekly_df = weekly_input_df.copy()
    
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
        pre_bonus_fan_pts_list.append(passing_fan_pts + rushing_fan_pts + receiving_fan_pts + return_fan_pts)
    
    if league_col_prefix is True:
        weekly_df[f"{league_name}_pre_bonus_fan_pts"] = pre_bonus_fan_pts_list
        weekly_df[f"{league_name}_total_yard_bonus_fan_pts"] = total_yard_bonus_fan_pts_list
    else:
        weekly_df['pre_bonus_fan_pts'] = pre_bonus_fan_pts_list
        weekly_df['total_yard_bonus_fan_pts'] = total_yard_bonus_fan_pts_list
        
    
    ## Create df to get play based bonuses using create_play_bonus_df function
    play_bonus_df = create_play_bonus_df(pbp_df, league_bonus_dict, league_name, league_col_prefix)
    
    result_df = pd.merge(left=weekly_df,
                         right=play_bonus_df,
                         how='left',
                         on=['player_name','team', 'week'])
   
    if league_col_prefix is True:
        result_df[f"{league_name}_play_bonus_fan_pts"] = result_df[f"{league_name}_play_bonus_fan_pts"] .fillna(0)
        
        result_df[f"{league_name}_total_fan_pts"] = result_df[f"{league_name}_pre_bonus_fan_pts"] + result_df[f"{league_name}_total_yard_bonus_fan_pts"] +result_df[f"{league_name}_play_bonus_fan_pts"]
    
        output_df = result_df[['player_name','team', 'week', f"{league_name}_pre_bonus_fan_pts",
                               f"{league_name}_total_yard_bonus_fan_pts", f"{league_name}_play_bonus_fan_pts",
                               f"{league_name}_total_fan_pts"]] # weekly_fantasy_df_w_league_points
    else:
        result_df['play_bonus_fan_pts'] = result_df['play_bonus_fan_pts'] .fillna(0)
        
        result_df['total_fan_pts'] = result_df['pre_bonus_fan_pts'] + result_df['total_yard_bonus_fan_pts'] + result_df['play_bonus_fan_pts']
    
        output_df = result_df[['player_name','team', 'week','pre_bonus_fan_pts', 'total_yard_bonus_fan_pts',
                               'play_bonus_fan_pts', 'total_fan_pts']] # weekly_fantasy_df_w_league_points
    
    output_df = output_df.drop_duplicates( keep='first', ignore_index=True)    
    
    return output_df



## Will not use the function to merge the points df with the weekly_data_df. 
## Instead will combine in PowerBI

## Add the df with fantasy points (created by: get_league_fantasy_points) and merge with weekly data df
# def merge_weekly_df_w_league_points_df(weekly_df, league_points_df, league_name, save_loc=None, save_df=False):
#     output_df = pd.merge(left=weekly_df,
#                          right=league_points_df,
#                          how='left',
#                          on=['player_name','team', 'week'])
#     if save_df is True:
#         output_df.to_csv(f"{save_loc}{league_name}_df.csv")
    
#     return output_df
    


from league_scoring import td_palooza_scoring, td_palooza_bonuses

td_palooza_points_df = get_league_fantasy_points(weekly_data_df,
                                                 pbp_df,
                                                 league_scoring_dict=td_palooza_scoring,
                                                 league_bonus_dict=td_palooza_bonuses,
                                                 league_name='td_palooza',
                                                 league_col_prefix=False)


td_palooza_points_df.to_csv(f"{save_loc}td_palooza_df.csv", index=False)


# ### JOIN ABOVE TO WEEKLY DF
# weekly_w_td_palooza_2 = merge_weekly_df_w_league_points_df(weekly_data_df,
#                                                            td_palooza_points_df,
#                                                            league_name='td_palooza',
#                                                            save_loc=save_loc,
#                                                            save_df=True)


