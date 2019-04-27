# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 12:32:44 2019

@author: u698198
"""

import pandas as pd
import numpy as np
from collections import OrderedDict

#Specify what pair you want to import
pair='USD_JPY_MIN'
#Change the directory to your own
x=pd.read_csv("C://Users/U698198/Documents/"+pair+".csv",index_col=0,parse_dates=True)


#Resample Minute data into 15 minute data
df15 = (x.resample('15Min')
               .agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}))

df1h = (x.resample('1H')
               .agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'}))

np_data=df15.values
EMA=[]
#Function for creating exponential moving averages
def EMA_CALC(data,period):
    for i in range(data.shape[0]):
        if i==0:
            EMA.append(data[0,0])
        elif i <period:
            previous_ema=data[0:i,3].mean()
            EMA.append((data[i,3]-previous_ema)*(2/(period+1))+previous_ema)
        else:
            EMA.append((data[i,3]-EMA[i-1])*(2/(period+1))+EMA[i-1])

EMA_CALC(np_data,14)
df15['ema_14']=EMA
EMA=[]
EMA_CALC(np_data,50)
df15['ema_50']=EMA


np_arr=df15.values


#Function for calculating when the emas cross=>shift in momentum
def cross(data):
    iscross=[]
    for i in range(data.shape[0]):
        if i==0:
            iscross.append(0)
        elif np_arr[i-1,4]<np_arr[i-1,5] and np_arr[i,4]>np_arr[i,5]:
            iscross.append(1)
        elif np_arr[i-1,4]>np_arr[i-1,5] and np_arr[i,4]<np_arr[i,5]:
            iscross.append(2)
        else:
            iscross.append(0)
    return iscross
df15['cross']=cross(np_arr)
np15=df15.values