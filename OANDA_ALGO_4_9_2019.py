# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 19:14:06 2019

@author: Aidan
"""

import oandapyV20
from oandapyV20 import API
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades 
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.transactions as trans
import oandapyV20.endpoints.instruments as instruments
import pandas as pd

import json

from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints.pricing import PricingStream
import numpy as np
import datetime


accountID='101-001-10831130-001'
access_token='45cc721fe40759fb0b76d015456ba8b8-27c86888ddbab88249c3914ba1ff2a01'

api = API(access_token)

jpy_pairs=['USD_JPY','EUR_JPY','AUD_JPY','CAD_JPY','CHF_JPY']
major_pairs=['GBP_USD','USD_CAD','USD_CHF','EUR_USD','AUD_USD','NZD_USD']
cross_pairs=['AUD_CAD','AUD_CHF','AUD_NZD','CAD_CHF','EUR_AUD','EUR_CAD','EUR_CHF','NZD_CAD','NZD_CHF']
all_pairs=['USD_JPY','EUR_JPY','AUD_JPY','CAD_JPY','CHF_JPY','GBP_USD','USD_CAD','USD_CHF','EUR_USD','AUD_USD','NZD_USD','AUD_CAD','AUD_CHF','AUD_NZD','CAD_CHF','EUR_AUD','EUR_CAD','EUR_CHF','NZD_CAD','NZD_CHF']


def past_data(pair,cnt,far_back):
    
    params = {
          "count": cnt,
          "granularity": "H1"}
    
    r = instruments.InstrumentsCandles(instrument=pair,
                                   params=params)
    a=api.request(r)
    
    
    Date_Time=[]
    O=[]
    H=[]
    L=[]
    C=[]
    Volume=[]
    C_minus_O=[]
    H_minus_L=[]
    for i in range(cnt):
        
        if (float(a['candles'][i]['volume']))!=0:
            Date_Time.append(a['candles'][i]['time'])
            O.append(float(a['candles'][i]['mid']['o']))
            H.append(float(a['candles'][i]['mid']['h']))
            L.append(float(a['candles'][i]['mid']['l']))
            C.append(float(a['candles'][i]['mid']['c']))
            Volume.append(float(a['candles'][i]['volume']))
            C_minus_O.append(float(a['candles'][i]['mid']['c'])-float(a['candles'][i]['mid']['o']))
            H_minus_L.append(float(a['candles'][i]['mid']['h'])-float(a['candles'][i]['mid']['l']))
   

    past_dict={'Date_Time':Date_Time,'Open':O,'High':H,'Low':L,'Close':C,'Volume':Volume,'C_O':C_minus_O,'H_L':H_minus_L}
    df=pd.DataFrame(past_dict)
    df=df.tail(far_back)
    
    
    return df
x=past_data(jpy_pairs[3],300,150)
x.tail()


def start_of_hour(pair):
    params={"count":1,"granularity":"H1"}
    r = instruments.InstrumentsCandles(instrument=pair,params=params)
    a=api.request(r)
    hr_start=float(a['candles'][-1]['mid']['o'])
    
    return hr_start



def reversal_creation(num_candles,np_data,_list):
    for i in range(np_data.shape[0]):
        if i<num_candles:
            _list.append(0)
        elif np.nanmin(np_data[i-num_candles:i+num_candles,4])==np_data[i,4]:
            _list.append(1)
        elif np.nanmax(np_data[i-num_candles:i+num_candles,4])==np_data[i,4]:
            _list.append(2)
        else:
            _list.append(0)
    return _list




def closest_reversal(rev_data,hour_val):
    support_diff=1000
    resistance_diff=1000
    support=0
    resistance=0
    support_wick=0
    resistance_wick=0
    
    for i in range(rev_data.shape[0]):
        if rev_data[i,8]==1 and (hour_val>=rev_data[i,4]) and (support_diff>=(hour_val-rev_data[i,4])):
            support_diff=hour_val-rev_data[i,4]
            support=rev_data[i,4]
            support_wick=rev_data[i,3]
            
        
        elif rev_data[i,8]==2 and (hour_val<=rev_data[i,4]) and(resistance_diff>=(rev_data[i,4]-hour_val)):
            resistance_diff=rev_data[i,4]
            resistance=rev_data[i,4]
            resistance=rev_data[i,2]
            
            
        
        else:
            continue
     
    return support,resistance,support_wick,resistance_wick

def check_price(pair):
    bid_ask=[]
    params={"instruments":pair}
            
    r = pricing.PricingInfo(accountID=accountID, params=params)
    a=api.request(r)
    
    bid=float(a['prices'][0]['bids'][0]['price'])
    ask=float(a['prices'][0]['asks'][0]['price'])
    avg=(bid+ask)/2
    
    bid_ask.append(bid)
    bid_ask.append(ask)
    bid_ask.append(avg)
    
    
    
    return bid_ask
def pair_reversal_func(data,hour):
    pand_df=data
    reversal=[]
    num_p=pand_df.values
    reversal_creation(25,num_p,reversal)
    pand_df['reversal']=reversal
    num_p=pand_df.values
    s,r,s_w,r_w=closest_reversal(num_p,hour)
    
    return s,r,s_w,r_w

def account_value():
        
    api = oandapyV20.API(access_token=access_token)
    r = accounts.AccountDetails(accountID)
    acc_details=api.request(r)
    
    balance=float(acc_details['account']['balance'])
    margin_available=float(acc_details['account']['marginAvailable'])
    open_trades=float(acc_details['account']['openTradeCount'])
    
    return balance,margin_available,open_trades


def units_calc(trading_account,max_risk,sl):
    units=(max_risk*trading_account/sl)*10000
    
    return units

def stoploss_calc(pair,wick,sl,rev):
    sl_price=0
    if 'JPY' in pair:
        sl=sl*.01
        if rev==1:
            sl_price=wick-sl
        elif rev==2:
            sl_price=wick+sl
    else:
        sl=sl*.0001
        if rev==1:
            sl_price=wick-sl
        elif rev==2:
            sl_price=wick+sl    
    return sl_price
    
def takeprofit_calc(pair,current_price,tp,rev):
    tp_price=0
    if 'JPY' in pair:
        tp=tp*.01
        if rev==1:
            tp_price=current_price+tp
        elif rev==2:
            tp_price=current_price-tp
    else:
        tp=tp*.0001
        if rev==1:
            tp_price=current_price+tp
        elif rev==2:
            tp_price=current_price-tp  
    return tp_price

def jpy_trade(sl,tp,pair,current_price,wick,rev):
    bal,marg,trades=account_value()
    units=str(int(units_calc(bal,.01,sl)))
    stoploss=str(stoploss_calc(pair,wick,sl,rev))
    takeprofit=str(takeprofit_calc(pair,current_price,tp,rev))
    
    order={"order": 
        {
        "type": "MARKET",
        "units": units,
        "instrument": pair,
        "timeInForce": "FOK",
        "takeProfitOnFill": {
            "timeInForce": "GTC",
            "price": takeprofit
        },
        "stopLossOnFill": {
            "timeInForce": "GTC",
            "price": stoploss}
        }
        }
    r=orders.OrderCreate(accountID,data=order)
    api.request(r)
    

    
def majors_trade(sl,tp,pair,current_price,wick,rev):
    bal,marg,trades=account_value()
    units=str(int(units_calc(bal,.01,sl)))
    stoploss=str(stoploss_calc(pair,wick,sl,rev))
    takeprofit=str(takeprofit_calc(pair,current_price,tp,rev))
    
    order={"order": 
        {
        "type": "MARKET",
        "units": units,
        "instrument": pair,
        "timeInForce": "FOK",
        "takeProfitOnFill": {
            "timeInForce": "GTC",
            "price": takeprofit
        },
        "stopLossOnFill": {
            "timeInForce": "GTC",
            "price": stoploss}
        }
        }
    r=orders.OrderCreate(accountID,data=order)
    api.request(r)    
    
    
    

def cross_trade(sl,tp,pair,current_price,wick,rev):
    bal,marg,trades=account_value()
    units=str(int(units_calc(bal,.01,sl)))
    stoploss=str(stoploss_calc(pair,wick,sl,rev))
    takeprofit=str(takeprofit_calc(pair,current_price,tp,rev))
    
    order={"order": 
        {
        "type": "MARKET",
        "units": units,
        "instrument": pair,
        "timeInForce": "FOK",
        "takeProfitOnFill": {
            "timeInForce": "GTC",
            "price": takeprofit
        },
        "stopLossOnFill": {
            "timeInForce": "GTC",
            "price": stoploss}
        }
        }
    r=orders.OrderCreate(accountID,data=order)
    api.request(r)
    
    
while True:


    if datetime.datetime.now().minute==0:
        for pair in jpy_pairs:
            if pair =='USD_JPY' and (past_data(pair,350,35).iloc[-1,0][0:13] !=USD_JPY_PAST.iloc[-1,0][0:13]):
                USD_JPY_PAST=past_data(pair,350,35)
                USD_JPY_HR=start_of_hour(pair)

                usd_jpy_s,usd_jpy_r,usd_jpy_s_w,usd_jpy_r_w=pair_reversal_func(USD_JPY_PAST,USD_JPY_HR)

            elif pair =='EUR_JPY' and (past_data(pair,350,35).iloc[-1,0][0:13] !=EUR_JPY_PAST.iloc[-1,0][0:13]):              
                EUR_JPY_PAST=past_data(pair,350,35)
                EUR_JPY_HR=start_of_hour(pair)

                eur_jpy_s,eur_jpy_r,eur_jpy_s_w,eur_jpy_r_w=pair_reversal_func(EUR_JPY_PAST,EUR_JPY_HR)

            elif pair=='AUD_JPY' and (past_data(pair,350,35).iloc[-1,0][0:13] !=AUD_JPY_PAST.iloc[-1,0][0:13]):
                AUD_JPY_PAST=past_data(pair,350,35)
                AUD_JPY_HR=start_of_hour(pair)

                aud_jpy_s,aud_jpy_r,aud_jpy_s_w,aud_jpy_r_w=pair_reversal_func(AUD_JPY_PAST,AUD_JPY_HR)

            elif pair=='CAD_JPY' and (past_data(pair,350,35).iloc[-1,0][0:13] !=CAD_JPY_PAST.iloc[-1,0][0:13]):
                CAD_JPY_PAST=past_data(pair,350,35)
                CAD_JPY_HR=start_of_hour(pair)

                cad_jpy_s,cad_jpy_r,cad_jpy_s_w,cad_jpy_r_w=pair_reversal_func(CAD_JPY_PAST,CAD_JPY_HR)


            elif pair=='CHF_JPY' and (past_data(pair,350,35).iloc[-1,0][0:13] !=CHF_JPY_PAST.iloc[-1,0][0:13]):
                CHF_JPY_PAST=past_data(pair,350,35)
                CHF_JPY_HR=start_of_hour(pair)

                chf_jpy_s,chf_jpy_r,chf_jpy_s_w,chf_jpy_r_w=pair_reversal_func(CHF_JPY_PAST,CHF_JPY_HR)

            else:
                continue

        jpy_dict={'USD_JPY':[usd_jpy_s,usd_jpy_r,usd_jpy_s_w,usd_jpy_r_w],
                  'EUR_JPY':[eur_jpy_s,eur_jpy_r,eur_jpy_s_w,eur_jpy_r_w],
                  'AUD_JPY':[aud_jpy_s,aud_jpy_r,aud_jpy_s_w,aud_jpy_r_w],
                  'CAD_JPY':[cad_jpy_s,cad_jpy_r,cad_jpy_s_w,cad_jpy_r_w],
                  'CHF_JPY':[chf_jpy_s,chf_jpy_r,chf_jpy_s_w,chf_jpy_r_w]}

        for pair in major_pairs:
            if pair=='GBP_USD' and (past_data(pair,350,35).iloc[-1,0][0:13] !=GBP_USD_PAST.iloc[-1,0][0:13]):
                GBP_USD_PAST=past_data(pair,350,35)
                GBP_USD_HR=start_of_hour(pair) 

                gbp_usd_s,gbp_usd_r,gbp_usd_s_w,gbp_usd_r_w=pair_reversal_func(GBP_USD_PAST,GBP_USD_HR)


            elif pair=='USD_CAD' and (past_data(pair,350,35).iloc[-1,0][0:13] !=USD_CAD_PAST.iloc[-1,0][0:13]):
                USD_CAD_PAST=past_data(pair,350,35)            
                USD_CAD_HR=start_of_hour(pair) 

                usd_cad_s,usd_cad_r,usd_cad_s_w,usd_cad_r_w=pair_reversal_func(USD_CAD_PAST,USD_CAD_HR)

            elif pair=='USD_CHF' and (past_data(pair,350,35).iloc[-1,0][0:13] !=USD_CHF_PAST.iloc[-1,0][0:13]):
                USD_CHF_PAST=past_data(pair,350,35)            
                USD_CHF_HR=start_of_hour(pair) 

                usd_chf_s,usd_chf_r,usd_chf_s_w,usd_chf_r_w=pair_reversal_func(USD_CHF_PAST,USD_CHF_HR)


            elif pair=='EUR_USD'and (past_data(pair,350,35).iloc[-1,0][0:13] !=EUR_USD_PAST.iloc[-1,0][0:13]):
                EUR_USD_PAST=past_data(pair,350,35)
                EUR_USD_HR=start_of_hour(pair) 

                eur_usd_s,eur_usd_r,eur_usd_s_w,eur_usd_r_w=pair_reversal_func(EUR_USD_PAST,EUR_USD_HR)

            elif pair=='AUD_USD' and (past_data(pair,350,35).iloc[-1,0][0:13] !=AUD_USD_PAST.iloc[-1,0][0:13]):
                AUD_USD_PAST=past_data(pair,350,35)
                GBP_USD_HR=start_of_hour(pair) 

                aud_usd_s,aud_usd_r,aud_usd_s_w,aud_usd_r_w=pair_reversal_func(AUD_USD_PAST,AUD_USD_HR)

            elif pair=='NZD_USD' and (past_data(pair,350,35).iloc[-1,0][0:13] !=NZD_USD_PAST.iloc[-1,0][0:13]):
                NZD_USD_PAST=past_data(pair,350,35)
                GBP_USD_HR=start_of_hour(pair) 

                nzd_usd_s,nzd_usd_r,nzd_usd_s_w,nzd_usd_r_w=pair_reversal_func(NZD_USD_PAST,NZD_USD_HR)

            else:
                continue

        major_dict={'GBP_USD':[gbp_usd_s,gbp_usd_r],
                    'USD_CAD':[usd_cad_s,usd_cad_r],
                    'USD_CHF':[usd_chf_s,usd_chf_r],
                    'EUR_USD':[eur_usd_s,eur_usd_r],
                    'AUD_USD':[aud_usd_s,aud_usd_r],
                    'NZD_USD':[nzd_usd_s,nzd_usd_r]}

        for pair in cross_pairs:
            if pair =='AUD_CAD' and (past_data(pair,350,35).iloc[-1,0][0:13] !=AUD_CAD_PAST.iloc[-1,0][0:13]):
                AUD_CAD_PAST=past_data(pair,350,35)
                AUD_CAD_HR=start_of_hour(pair) 

                aud_cad_s,aud_cad_r,aud_cad_s_w,aud_cad_r_w=pair_reversal_func(AUD_CAD_PAST,AUD_CAD_HR)



            elif pair=='AUD_CHF' and (past_data(pair,350,35).iloc[-1,0][0:13] !=AUD_CHF_PAST.iloc[-1,0][0:13]):
                AUD_CHF_PAST=past_data(pair,350,35)
                AUD_CHF_HR=start_of_hour(pair) 

                aud_chf_s,aud_chf_r,aud_chf_s_w,aud_chf_r_w=pair_reversal_func(AUD_CHF_PAST,AUD_CHF_HR)


            elif pair=='AUD_NZD' and (past_data(pair,350,35).iloc[-1,0][0:13] !=AUD_NZD_PAST.iloc[-1,0][0:13]):
                AUD_NZD_PAST=past_data(pair,350,35)
                AUD_NZD_HR=start_of_hour(pair) 

                aud_nzd_s,aud_nzd_r,aud_nzd_s_w,aud_nzd_r_w=pair_reversal_func(AUD_NZD_PAST,AUD_NZD_HR)


            elif pair=='CAD_CHF' and (past_data(pair,350,35).iloc[-1,0][0:13] !=CAD_CHF_PAST.iloc[-1,0][0:13]):
                CAD_CHF_PAST=past_data(pair,350,35)
                CAD_CHF_HR=start_of_hour(pair) 

                cad_chf_s,cad_chf_r,cad_chf_s_w,cad_chf_r_w=pair_reversal_func(CAD_CHF_PAST,CAD_CHF_HR)


            elif pair=='EUR_AUD' and (past_data(pair,350,35).iloc[-1,0][0:13] !=EUR_AUD_PAST.iloc[-1,0][0:13]):
                EUR_AUD_PAST=past_data(pair,350,35)
                EUR_AUD_HR=start_of_hour(pair) 

                eur_aud_s,eur_aud_r,eur_aud_s_w,eur_aud_r_w=pair_reversal_func(EUR_AUD_PAST,EUR_AUD_HR)


            elif pair=='EUR_CAD' and (past_data(pair,350,35).iloc[-1,0][0:13] !=EUR_CAD_PAST.iloc[-1,0][0:13]):
                EUR_CAD_PAST=past_data(pair,350,35)
                EUR_CAD_HR=start_of_hour(pair) 

                eur_cad_s,eur_cad_r,eur_cad_s_w,eur_cad_r_w=pair_reversal_func(EUR_CAD_PAST,EUR_CAD_HR)


            elif pair=='EUR_CHF' and (past_data(pair,350,35).iloc[-1,0][0:13] !=EUR_CHF_PAST.iloc[-1,0][0:13]):
                EUR_CHF_PAST=past_data(pair,350,35)
                EUR_CHF_HR=start_of_hour(pair) 

                eur_chf_s,eur_chf_r,eur_chf_s_w,eur_chf_r_w=pair_reversal_func(EUR_CHF_PAST,EUR_CHF_HR)


            elif pair=='NZD_CAD' and (past_data(pair,350,35).iloc[-1,0][0:13] !=NZD_CAD_PAST.iloc[-1,0][0:13]):
                NZD_CAD_PAST=past_data(pair,350,35)
                NZD_CAD_HR=start_of_hour(pair) 

                nzd_cad_s,nzd_cad_r,nzd_cad_s_w,nzd_cad_r_w=pair_reversal_func(NZD_CAD_PAST,NZD_CAD_HR)


            elif pair=='NZD_CHF' and (past_data(pair,350,35).iloc[-1,0][0:13] !=NZD_CHF_PAST.iloc[-1,0][0:13]):
                NZD_CHF_PAST=past_data(pair,350,35)
                NZD_CAD_HR=start_of_hour(pair) 

                nzd_cad_s,nzd_cad_r,nzd_cad_s_w,nzd_cad_r_w=pair_reversal_func(NZD_CAD_PAST,NZD_CAD_HR)
            else:
                continue

        cross_dict={'AUD_CAD':[aud_cad_s,aud_cad_r,aud_cad_s_w,aud_cad_r_w],
                    'AUD_CHF':[aud_chf_s,aud_chf_r,aud_chf_s_w,aud_chf_r_w],
                    'AUD_NZD':[aud_nzd_s,aud_nzd_r,aud_nzd_s_w,aud_nzd_r_w],
                    'CAD_CHF':[cad_chf_s,cad_chf_r,cad_chf_s_w,cad_chf_r_w],
                    'EUR_AUD':[eur_aud_s,eur_aud_r,eur_aud_s_w,eur_aud_r_w],
                    'EUR_CAD':[eur_cad_s,eur_cad_r,eur_cad_s_w,eur_cad_r_w],
                    'EUR_CHF':[eur_chf_s,eur_chf_r,eur_chf_s_w,eur_chf_r_w],
                    'NZD_CAD':[nzd_cad_s,nzd_cad_r,nzd_cad_s_w,nzd_cad_r_w],
                    'NZD_CHF':[nzd_chf_s,nzd_chf_r,nzd_chf_s_w,nzd_chf_r_w]}






    while account_value()[2]==0:


        for pair in jpy_pairs:
            bid=check_price(pair)[0]
            ask=check_price(pair)[1]
            spread=np.abs(ask-bid)

            if spread>=.03:
                continue

            elif bid<=jpy_dict[pair][0] and ask>=jpy_dict[pair][2]:
                rev=1
                jpy_trade(12,30,pair,ask,jpy_dict[pair][2],1)


            elif ask>=jpy_dict[pair][1] and bid<=jpy_dict[pair][3]:
                rev=2
                jpy_trade(12,30,pair,bid,jpy_dict[pair][3],2)


        for pair in major_pairs:
            bid=check_price(pair)[0]
            ask=check_price(pair)[1]
            spread=np.abs(ask-bid)

            if spread>=.0003:
                continue

            if bid<=major_dict[pair][0] and ask>=major_dict[pair][2]:
                rev=1
                majors_trade(12,30,pair,ask,major_dict[pair][2],1)


            elif ask>=major_dict[pair][1] and bid<=major_dict[pair][3]:
                rev=2
                majors_trade(12,30,pair,bid,major_dict[pair][3],2)    


        for pair in cross_pairs:
            bid=check_price(pair)[0]
            ask=check_price(pair)[1]
            spread=np.abs(ask-bid)

            if spread>=.0003:
                continue

            if bid<=cross_dict[pair][0] and ask>=cross_dict[pair][2]:
                rev=1
                majors_trade(12,30,pair,ask,cross_dict[pair][2],1)


            elif ask>=major_dict[pair][1] and bid<=major_dict[pair][3]:
                rev=2
                majors_trade(12,30,pair,bid,cross_dict[pair][3],2)



                