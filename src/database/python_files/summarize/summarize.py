#!/usr/bin/env python
# coding: utf-8

# # Import Libraries

# In[4]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import math
import sys

from datetime import datetime

on_server = int(sys.argv[1])
    
at_home = 'C:'

if(on_server==0):
        path_to_module = at_home + '/Users/Indy/Desktop/coding/Dementia_proj/src/database/python_files/'

elif(on_server==1):
        path_to_module = '/var/www/html/python/mysql_connect/python_files'

sys.path.append(path_to_module)
os.chdir(path_to_module)

# # Set data path

if(on_server==0):
        basepath = at_home + '/Users/Indy/Desktop/coding/Dementia_proj/'
else:
        basepath = '/var/www/html/python/mysql_connect/'

datapath = basepath + 'DDC_Data/'
mypath = basepath + 'DDC_Data/raw/'

from os import listdir, walk
from os.path import isfile, join

from summarize.activity_summary import get_df_summary_all, get_floor_start, get_ceil_finish
from load_data.load_dataset import calc_sec, calc_ts
from predict.preprocessing import convert_time_to_string

def get_duration_per_act(i, df_summary_all):
        from_actual = df_summary_all.loc[i, 'from actual']
        to_actual = df_summary_all.loc[i, 'to actual']
        total_i = df_summary_all.loc[i, 'total count']

        if(total_i!=0):
                print(i)
                print('from actual:', from_actual)
                print('to actual:', to_actual)
                print('total i:', total_i)
                if(from_actual!=None and to_actual!=None):
                        duration_actual = calc_sec(to_actual) - calc_sec(from_actual)
                else:
                        duration_actual = 0

                duration_per_act = duration_actual/total_i
                return convert_time_to_string(duration_per_act)
        
        return None

def get_summarized_data(df_all_p, all_patients):
        # # Load Predicted Data
        df_date = df_all_p.copy()
        df_date['date'] = df_date['timestamp'].apply(lambda x: x.strftime('%Y-%m-%d'))
        df_date['time'] = df_date['timestamp'].apply(lambda x: x.strftime('%H:%M:%S.%f'))

        cols = ['ID','date','time','x','y','z','HR','y_pred']
        df_date = df_date[cols]

        # # Summarize Data
        df_summary_all, df_act_period = get_df_summary_all(all_patients, df_date)
        if(df_summary_all.empty and df_act_period.empty):
                return df_summary_all, df_act_period

        cols = ['ID', 'date', 'from', 'to', 'y_pred']
        df_act_period = df_act_period[cols]
        df_act_period = df_act_period.reset_index(drop=True)

        df_summary_all = df_summary_all.reset_index(drop=True)
        df_summary_all.to_csv('df_summary.csv')
        df_act_period.to_csv('df_act_period.csv')

        # get actual time (from, until)
        actual_from_all = []
        for i in range(len(df_summary_all)):
                keep_start = -1

                for j in range(len(df_act_period)):
                        floor_start = get_floor_start(df_act_period.loc[j, 'from'])

                        if(df_act_period.loc[j, 'date']==df_summary_all.loc[i, 'date'] and
                        df_act_period.loc[j, 'ID']==df_summary_all.loc[i, 'ID']):

                                if(floor_start>keep_start and floor_start==calc_sec(df_summary_all.loc[i, 'from'])):

                                        actual_from_all.append(df_act_period.loc[j, 'from'])
                                        keep_start = calc_sec(df_act_period.loc[j, 'from'])

                                elif(floor_start<=keep_start):
                                        actual_from_all.append(datetime.strptime('00:00:00', '%H:%M:%S'))
                                        break

        actual_to_all = []
        for i in range(len(df_summary_all)-1, -1, -1):
                keep_finish = calc_sec(df_summary_all.loc[i, 'to'])

                for j in range(len(df_act_period)-1, -1, -1):

                        ceil_finish = get_ceil_finish(df_act_period.loc[j, 'to'])


                        if(df_act_period.loc[j, 'date']==df_summary_all.loc[i, 'date'] and
                        df_act_period.loc[j, 'ID']==df_summary_all.loc[i, 'ID']):

                                if(keep_finish==ceil_finish):

                                        actual_to_all.append(df_act_period.loc[j, 'to'])
                                        break
                                else:
                                        actual_to_all.append(datetime.strptime('00:00:00', '%H:%M:%S'))

        df_summary_all['from actual'] = pd.Series(actual_from_all)
        df_summary_all['to actual'] = pd.Series(actual_to_all[::-1])

        # duration_per_act = [get_duration_per_act(i, df_summary_all) for i in range(len(df_summary_all))]
        # df_summary_all['duration per action'] = pd.Series(duration_per_act)

        df_summary_all['duration per action'] = pd.Series([None for i in range(df_summary_all.shape[0])])

        return df_summary_all, df_act_period
