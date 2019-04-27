# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 15:59:35 2019

@author: u698198
"""

import pandas as pd
import numpy as np

pairs=['USD_JPY','AUD_JPY','CAD_JPY','CHF_JPY','EUR_JPY','GBP_JPY','NZD_JPY',
      'AUD_USD','EUR_USD','GBP_USD','NZD_USD','USD_CAD','USD_CHF','AUD_CAD',
       'AUD_CHF','AUD_NZD','CAD_CHF','EUR_AUD','EUR_CAD','EUR_CHF','EUR_GBP',
       'EUR_NZD','GBP_AUD','GBP_CAD','GBP_CHF','GBP_NZD','NZD_CAD','NZD_CHF']
pairs_dict={}
for pair in pairs:
    pairs_dict[pair]=pd.read_csv('C://Users/U698198/Documents/'+pair+".csv")
pairs_dict['USD_JPY'].head()


results_dict={}
total_trades=0
total_te=0
for pair in pairs:    
    
    
    UJ_np=pairs_dict[pair].values
    reversal=[]
    def reversal_creation(num_candles,np_forex_data):
        for i in range(np_forex_data.shape[0]):
            if i<num_candles:
                reversal.append(0)
            elif np.nanmin(np_forex_data[i-num_candles:i+num_candles,4])==np_forex_data[i,4]:

                reversal.append(1)

            elif np.nanmax(np_forex_data[i-num_candles:i+num_candles,4])==np_forex_data[i,4]:
                reversal.append(2)
            else:
                reversal.append(0)
    reversal_creation(25,UJ_np)
    pairs_dict[pair]['reversal']=reversal
    pairs_dict[pair]=pairs_dict[pair][(pairs_dict[pair][['Volume']]!=0).all(axis=1)]
    UJ_np=pairs_dict[pair].values

    pairs_dict[pair].head()
    def Support(data,i,j,sl,tp,result_array):
        #is candle i-j a support?
        #is candle i's open above support?
        #is candle i's low below support?
        if data[i-j,8]==1 and ((data[i-j,4]>=data[i,3]) and (data[i-j,4]<=data[i,1])):
            for h in range (1,15):
                if (np.nanmin(data[i:i+h,3])<=(data[i-j,3]-sl)) and ((1 not in result_array[i-3:i,1]) and (2 not in result_array[i-3:i,1])):
                    result_array[i,0]=2
                    result_array[i,1]=(data[i-j,3]-sl)-data[i-j,4]

                    break

                elif ((np.nanmax(data[i:i+h,2])-data[i-j,4])>=tp) and ((1 not in result_array[i-3:i,1]) and (2 not in result_array[i-3:i,1])):
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
        if data[i-j,8]==1 and ((data[i-j,3]>=data[i,3]) and (data[i-j,4]<=data[i,1])):
            for h in range (1,15):
                if (np.nanmin(data[i:i+h,3])<=(data[i-j,3]-sl)) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
                    result_array[i,0]=2
                    result_array[i,1]=(data[i-j,3]-sl)-data[i-j,3]

                    break

                elif ((np.nanmax(data[i:i+h,2])-data[i-j,3])>=tp) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
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
        if data[i-j,8]==2 and (data[i-j,4]>=data[i,1]) and (data[i-j,4]<=data[i,2]):
            for h in range (1,15):
                if (np.nanmax(data[i:i+h,2])>=(data[i-j,2]+sl)) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
                    result_array[i,0]=2
                    result_array[i,1]=data[i-j,4]-(data[i-j,2]+sl)

                    break

                elif ((data[i-j,4]-np.nanmin(data[i:i+h,3]))>=tp) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
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
        if data[i-j,8]==2 and (data[i-j,4]>=data[i,1]) and (data[i-j,2]<=data[i,2]):
            for h in range (1,15):
                if (np.nanmax(data[i:i+h,2])>=(data[i-j,2]+sl)) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
                    result_array[i,0]=2
                    result_array[i,1]=data[i-j,2]-(data[i-j,2]+sl)

                    break

                elif ((data[i-j,2]-np.nanmin(data[i:i+h,3]))>=tp) and ((1 not in result_array[i-3:i,0]) and (2 not in result_array[i-3:i,0])):
                    result_array[i,0]=1
                    result_array[i,1]=tp
                       #(np.nanmax(np_final[i:i+h,1])-np_final[i-j,3])
                    break

                else:
                    continue
                    
                    
                    
    def Run_hr(forex):

        data=forex
        result_array=np.zeros(shape=(data.shape[0],2))
        for i in range(data.shape[0]):
            for j in range (1,30):
                #ResistanceatWick(data,i,j,.001,.002,result_array)#0.12 0.21 TE=1.279% for 2% risk
                #SupportatWick(data,i,j,.001,.002,result_array) #0.11 0.22 TE=1.45% for 2% risk
                #SturnedR(data,i,j,0,result_array)
                if "JPY" in pair:
                    Support(data,i,j,.07,.2,result_array) 
                    Resistance(data,i,j,.07,.2,result_array) 
                else:
                    Support(data,i,j,.0007,.002,result_array) 
                    Resistance(data,i,j,.0007,.002,result_array) 
        return result_array

    aidan=Run_hr(UJ_np)


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
    trades_taken=a[0]+a[1]
    total_trades=total_trades+trades_taken
    print('Trades Taken:',trades_taken)
    print()
    
    
    winrate=(a[0]/(a[0]+a[1]))*100
    print('winrate=',winrate)
    R_R=a[3]/-a[4]
    print('R:R',R_R)
    print()
    max_risk=.013
    print('max risk: ',max_risk)
    TE=((a[0]/(a[0]+a[1]))*max_risk*a[3]/-a[4])-((1-(a[0]/(a[0]+a[1])))*max_risk)
    total_te=total_te+TE
    max_risk=max_risk*100
    
    print('Trade Expectancy:',TE)
    print()
    import math
    class color:
       PURPLE = '\033[95m'
       CYAN = '\033[96m'
       DARKCYAN = '\033[36m'
       BLUE = '\033[94m'
       GREEN = '\033[92m'
       YELLOW = '\033[93m'
       RED = '\033[91m'
       BOLD = '\033[1m'
       UNDERLINE = '\033[4m'
       END = '\033[0m'
    Balance='${:,.2f}'.format(2000*(math.pow(1+TE,a[0]+a[1])))
    print(color.BOLD+color.RED+'${:,.2f}'.format(2000*(math.pow(1+TE,a[0]+a[1])))+color.END)
    TE=TE*100

    sr=pd.Series([trades_taken,str(round(winrate,2))+'%',R_R,str(round(max_risk,2))+'%',str(round(TE,2))+'%',Balance])
    results_dict[pair]=sr
d=pd.DataFrame(results_dict)
d=d.T
d.columns=['Trades_Taken','Win_Rate','RewardtoRisk','Max_allowed_Risk','Trade_Expectancy','Final_Balance']
print(d)
