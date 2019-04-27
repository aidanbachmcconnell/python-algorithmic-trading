# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 10:20:08 2019

@author: u698198
"""

import pandas as pd
import numpy as np
cc='GBP_JPY_1'
x=pd.read_csv('C://Users/U698198/Documents/'+cc+'.csv')
haha=x.values
Delta=[]
Magnitude=[]
for i in range(haha.shape[0]):
    Delta.append(haha[i,4]-haha[i,1])
    Magnitude.append(haha[i,2]-haha[i,3])
x['Delta']=Delta
x['Magnitude']=Magnitude
print(x.head())
y=x
y.columns=['Local_Time','Open','High','Low','Close','Volume','Delta','Magnitude']
lt=y['Local_Time']
lt.str.replace(" GMT-0600","")
pd_date_time=lt.str.replace(' GMT-0600','')
y['Local_Time']=pd_date_time

pd_forex_data=y

time_int=pd_date_time.str.slice(11,13)
a=time_int.values
b=a.astype('int64')
hours=b


pd_forex_data['hours']=hours
np_forex_data=pd_forex_data.values
pd_forex_data.head()

upper_wick=[]
lower_wick=[]

for i in range(np_forex_data.shape[0]):
    if np_forex_data[i,6]<=0:
        upper_wick.append(np_forex_data[i,2]-np_forex_data[i,1])
        lower_wick.append(np_forex_data[i,4]-np_forex_data[i,3])
        
        
    else:
        upper_wick.append(np_forex_data[i,2]-np_forex_data[i,4])
        lower_wick.append(np_forex_data[i,1]-np_forex_data[i,3])
        
pd_forex_data['upper_wick']=upper_wick
pd_forex_data['lower_wick']=lower_wick
np_forex_data=pd_forex_data.values
previous_upper=[]
previous_lower=[]
for i in range(np_forex_data.shape[0]):
    if i==0:
        previous_upper.append(0)
        previous_lower.append(0)
    else:
        previous_upper.append(np_forex_data[i-1,9])
        previous_lower.append(np_forex_data[i-1,10])

pd_forex_data['previous_upper']=previous_upper
pd_forex_data['previous_lower']=previous_lower

np_forex_data=pd_forex_data.values
np_forex_data=pd_forex_data.drop(['upper_wick','lower_wick'], axis=1).values    

reversal=[]
def reversal_creation(num_candles):
    for i in range(np_forex_data.shape[0]):
        if i<7:
            reversal.append(0)
        elif np.nanmin(np_forex_data[i-num_candles:i+num_candles,4])==np_forex_data[i,4]:

            reversal.append(1)

        elif np.nanmax(np_forex_data[i-num_candles:i+num_candles,4])==np_forex_data[i,4]:
            reversal.append(2)
        else:
            reversal.append(0)
    
        
            
reversal_creation(7)            
pd_forex_data['reversal']=reversal
np_updated=pd_forex_data.values
print(np_updated.shape)
drop_zeros=pd_forex_data[(pd_forex_data[['Volume']]!=0).all(axis=1)]
np_updated=drop_zeros.values   
print(np_updated.shape)

previous_volume=[]
last_hr=[]
last_4=[]
last_8=[]
last_16=[]

for i in range(np_updated.shape[0]):
    previous_volume.append(np_updated[i-1,5])
    last_hr.append(np_updated[i-1,6])
    last_4.append(np_updated[i-1,4]-np_updated[i-4,1])
    last_8.append(np_updated[i-1,4]-np_updated[i-8,1])
    last_16.append(np_updated[i-1,4]-np_updated[i-16,1])

drop_zeros.insert(14,'previous_volume',previous_volume)
drop_zeros.insert(15,'last_hr',last_hr)  
drop_zeros.insert(16,'last_4',last_4)
drop_zeros.insert(17,'last_8',last_8)
drop_zeros.insert(18,'last_16',last_16)

print(drop_zeros.shape)

np_updated=drop_zeros.values


np_final=drop_zeros.iloc[:,[1,2,3,4,8,11,12,13,14,15,16,17,18]].values

dz=drop_zeros.iloc[:,[1,2,3,4,8,11,12,13,14,15,16,17,18]]
print(np_final.shape)
print(dz.head())
