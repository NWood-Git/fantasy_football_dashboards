# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 17:11:07 2023

@author: nicho
"""

## TD Palooza
td_palooza_scoring = {
    'pass_completions_multiplier' : 0,
    'pass_yd_multiplier' : 0.05,
    'pass_td_multiplier' : 6,
    'int_multiplier' : -2,
    'rush_yd_multiplier' : 0.10,
    'rush_td_multiplier' : 6,
    'rec_multiplier' : 0,
    'rec_yd_multiplier' : 0.10,
    'rec_td_multiplier' : 6,
    'ret_yd_multiplier' : 0.10,
    'ret_td_multiplier' : 6,
    'two_pt_conv_multiplier' : 2,
    'fum_lost' :  -2,
    'fg_0_19' : 3,
    'fg_20_29' : 3,
    'fg_30_29' : 3,
    'fg_40_49': 4,
    'fg_50+' : 5,
    'PAT_made_multiplier' : 1}

td_palooza_dst_scoring = {
    'sack' : 1,
    'interception' : 2,
    'forced_fumble' : 0,
    'fumble_recovery' : 2,
    'defensive_td' : 6,
    'safety' : 2,
    'block_kick' : 2,
    '0_pts_allowed' : 10,
    '1_6_pts_allowed' : 7,
    '7_13_pts_allowed' : 4,
    '14_20_pts_allowed' : 1,
    '21_27_pts_allowed' : 0,
    '28_34_pts_allowed' : -1,
    '35+_pts_allowed' : -4,
    'PAT_returned' : 2,    
    'return_td' : 6
    }

td_palooza_bonuses = {
    'play_yd_bonus_len' : 40,
    'pass_300_bonus' : 5,
    'pass_400_bonus' : 7,
    'pass_500_bonus' : 10,
    'yd_pass_bonus' : 2,
    'yd_pass_td_bonus' : 2, 
    'rush_100_bonus' : 5,
    'rush_150_bonus' : 7,
    'rush_200_bonus' : 10,
    'yd_rush_bonus' : 2,
    'yd_rush_td_bonus' : 2,
    'rec_100_bonus' : 5,
    'rec_150_bonus' : 7,
    'rec_200_bonus' : 10,
    'yd_rec_bonus' : 2,
    'yd_rec_td_bonus' : 2}
