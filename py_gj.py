# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 09:20:56 2019

@author: Aidan
"""
import pandas as pd
import numpy as np

x=pd.read_csv ('C://Users/Aidan/Documents/FOREX Trading/USD_JPY.csv')
df=x[~(x==0).any(axis=1)]
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

#loop through the forex data array and create reversal instance for every row in the dataset
#0 being no reversal, 1=support, 2=resistance
#compute this by determining if the current row is the max or min of the previous 7 rows or the next 7 rows


reversal=[]
def reversal_creation(num_candles):
    for i in range(np_forex_data.shape[0]):
        if i<num_candles:
            reversal.append(0)
        elif np.nanmin(np_forex_data[i-num_candles:i+num_candles,4])==np_forex_data[i,4]:

            reversal.append(1)

        elif np.nanmax(np_forex_data[i-num_candles:i+num_candles,4])==np_forex_data[i,4]:
            reversal.append(2)
        else:
            reversal.append(0)
    
        
            
reversal_creation(25)            
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
########################################################################
########################################################################
########################################################################
########################################################################
########################################################################
def SturnedR(data,i,j,sl,result_array):#only enter if price hits or goes above the line
    #is candle i-j a support?
    #is the mean of the previous 4 below the low of support?
    #is candle i's open below support?
    #is candle i's high above support?
    if data[i-j,7]==1 and (np.mean(data[i-5:i,3])<=data[i-j,2]) and (data[i,0]<=data[i-j,3]) and (data[i,1]>=data[i-j,3]):
        for h in range (1,15):
            #is the max of this candle through the next h candles above the supports high?
            #is there a not win or a loss within the last 3 candles?
            if (np.nanmax(data[i:i+h,1])>=(data[i-j,1]+sl)) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
                result_array[i,0]=2
                result_array[i,1]=data[i-j,2]-(data[i-j,1]+sl)

                break
            #is the the diff between support and the min of candle i to h greater than the diff between supports high +sl and the entry
            #is there not a win or a loss within the last 3 candles?
            elif ((data[i-j,2]-np.nanmin(data[i:i+h,2]))>=(data[i-j,1]+sl-data[i-j,2])) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
                result_array[i,0]=1
                result_array[i,1]=data[i-j,2]-np.nanmin(data[i:i+h,2])

                break

            else:
                continue
def Support(data,i,j,sl,tp,result_array):
    #is candle i-j a support?
    #is candle i's open above support?
    #is candle i's low below support?
    if data[i-j,7]==1 and ((data[i-j,3]>=data[i,2]) and (data[i-j,3]<=data[i,0])):
        for h in range (1,15):
            if (np.nanmin(data[i:i+h,2])<=(data[i-j,2]-sl)) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
                result_array[i,0]=2
                result_array[i,1]=(data[i-j,2]-sl)-data[i-j,3]

                break

            elif ((np.nanmax(data[i:i+h,1])-data[i-j,3])>=tp) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
                result_array[i,0]=1
                result_array[i,1]=tp
                   #(np.nanmax(np_final[i:i+h,1])-np_final[i-j,3])
                break

            else:
                continue
def SupportatWick(data,i,j,sl,tp,result_array):
    #is candle i-j a support?
    #is candle i's open above support?
    #is candle i's low below low of support?
    if data[i-j,7]==1 and ((data[i-j,2]>=data[i,2]) and (data[i-j,3]<=data[i,0])):
        for h in range (1,15):
            if (np.nanmin(data[i:i+h,2])<=(data[i-j,2]-sl)) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
                result_array[i,0]=2
                result_array[i,1]=(data[i-j,2]-sl)-data[i-j,2]

                break

            elif ((np.nanmax(data[i:i+h,1])-data[i-j,2])>=tp) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
                result_array[i,0]=1
                result_array[i,1]=tp
                   #(np.nanmax(np_final[i:i+h,1])-np_final[i-j,3])
                break

            else:
                continue
def Resistance(data,i,j,sl,tp,result_array):
    #is candle i-j a resistance?
    #is candle i's open below resistance?
    #is candle i's high above resistance?
    if data[i-j,7]==2 and (data[i-j,3]>=data[i,0]) and (data[i-j,3]<=data[i,1]):
        for h in range (1,15):
            if (np.nanmax(data[i:i+h,1])>=(data[i-j,1]+sl)) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
                result_array[i,0]=2
                result_array[i,1]=data[i-j,3]-(data[i-j,1]+sl)

                break

            elif ((data[i-j,3]-np.nanmin(data[i:i+h,2]))>=tp) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
                result_array[i,0]=1
                result_array[i,1]=tp
                   #(np.nanmax(np_final[i:i+h,1])-np_final[i-j,3])
                break

            else:
                continue
def ResistanceatWick(data,i,j,sl,tp,result_array):
    #is candle i-j a resistance?
    #is candle i's open below resistance?
    #is candle i's high above the high of resistance?
    if data[i-j,7]==2 and (data[i-j,3]>=data[i,0]) and (data[i-j,1]<=data[i,1]):
        for h in range (1,15):
            if (np.nanmax(data[i:i+h,1])>=(data[i-j,1]+sl)) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
                result_array[i,0]=2
                result_array[i,1]=data[i-j,1]-(data[i-j,1]+sl)

                break

            elif ((data[i-j,1]-np.nanmin(data[i:i+h,2]))>=tp) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
                result_array[i,0]=1
                result_array[i,1]=tp
                   #(np.nanmax(np_final[i:i+h,1])-np_final[i-j,3])
                break

            else:
                continue
def Run(forex):
    
    data=forex
    result_array=np.zeros(shape=(data.shape[0],2))
    for i in range(data.shape[0]):
        for j in range (1,30):
            ResistanceatWick(data,i,j,0.1,0.2,result_array)#0.12 0.21 TE=1.279% for 2% risk
            SupportatWick(data,i,j,0.1,0.2,result_array) #0.11 0.22 TE=1.45% for 2% risk
            #SturnedR(data,i,j,0,result_array)
            #Support(data,i,j,0.0005,0.0015,result_array) #0.05 0.2
            #Resistance(data,i,j,0.0005,0.0015,result_array)#0.04 0.2
           
    return result_array
aidan=Run(np_final)

def test(re):
    wins=0
    losses=0
    nothing=0
    win_am=0
    loss_am=0
    for k in range(re.shape[0]):
        if re[k,0]==1:
            wins=wins+1
            win_am=win_am+re[k,1]
        elif re[k,0]==2:
            losses=losses+1
            loss_am=loss_am+re[k,1]
        else:
            nothing=nothing+1
   
    FINAL={'wins':wins,'losses':losses,'nothing':nothing,'avg_win':win_am/wins,'avg_loss':loss_am/losses}
    return [wins,losses,nothing,win_am/wins,loss_am/losses]
a=test(aidan)

print(a)
print(a[0]+a[1]+a[2])
print('Trades Taken:',a[0]+a[1])
print('winrate=',a[0]/(a[0]+a[1]))
print('R:R',a[3]/-a[4])
print()
TE=((a[0]/(a[0]+a[1]))*.02*a[3]/-a[4])-((1-(a[0]/(a[0]+a[1])))*.02)
print('Trade Expectancy:',TE)
import math
print(2000*(math.pow(1+TE,a[0]+a[1])))
print(np_final.shape,aidan.shape)
  
