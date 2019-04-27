# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 17:45:10 2019

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
            resistance_wick=rev_data[i,2]
            
            
        
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
            sl_price=round(sl_price,2)
        elif rev==2:
            sl_price=wick+sl
            sl_price=round(sl_price,2)
    else:
        sl=sl*.0001
        if rev==1:
            sl_price=wick-sl
            sl_price=round(sl_price,4)
        elif rev==2:
            sl_price=wick+sl  
            sl_price=round(sl_price,4)
    return sl_price
    
def takeprofit_calc(pair,current_price,tp,rev):
    tp_price=0
    if 'JPY' in pair:
        tp=tp*.01
        if rev==1:
            tp_price=current_price+tp
            tp_price=round(tp_price,2)
        elif rev==2:
            tp_price=current_price-tp
            tp_price=round(tp_price,2)
    else:
        tp=tp*.0001
        if rev==1:
            tp_price=current_price+tp
            tp_price=round(tp_price,4)
        elif rev==2:
            tp_price=current_price-tp  
            tp_price=round(tp_price,4)
    return tp_price

def jpy_trade(sl,tp,pair,current_price,wick,rev):
    bal,marg,trades=account_value()
    if rev==1:
        units=str(int(units_calc(bal,.014,sl))) 
    elif rev==2:
        units=str(-1*(int(units_calc(bal,.014,sl)))) 
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
    print()
    print(bal)
    print()        
        
    print('current price: ',current_price)
    print()
    print()
    print()
    print(order)
    print()
    print()
    print()
    r=orders.OrderCreate(accountID,data=order)
    api.request(r)
    print(r.response)
    

    
def majors_trade(sl,tp,pair,current_price,wick,rev):
    bal,marg,trades=account_value()
    
    if rev==1:
        units=str(int(units_calc(bal,.014,sl))) 
    elif rev==2:
        units=str(-1*(int(units_calc(bal,.014,sl))))
    
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
    print()
    print(bal)
    print()         
    print('current price: ',current_price)
    print()
    print()
    print(order)
    print()
    print()
    print()
    r=orders.OrderCreate(accountID,data=order)
    api.request(r)
    print(r.response)    
    
    
    

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
    print(r.response)
    
    
pairs_dict={}    
closest_rev_dict={}
for pair in all_pairs:
    pairs_dict[pair]=past_data(pair,350,40)
    hr_start=start_of_hour(pair)
    closest_rev_dict[pair]=pair_reversal_func(pairs_dict[pair],hr_start)   
while True:
    
    if datetime.datetime.now().minute==0 and datetime.datetime.now().second>30:
    
        pairs_dict={}
        closest_rev_dict={}
        for pair in all_pairs:
            pairs_dict[pair]=past_data(pair,350,40)
            hr_start=start_of_hour(pair)
            closest_rev_dict[pair]=pair_reversal_func(pairs_dict[pair],hr_start)



    for pair in all_pairs:
        
        print(pair)
        print(account_value()[2])
        if account_value()[2]==0:
            bid=check_price(pair)[0]
            ask=check_price(pair)[1]
            spread=np.abs(ask-bid)

            if 'JPY' in pair and bid<=closest_rev_dict[pair][0] and ask>=closest_rev_dict[pair][2] and spread<=.03:
                print('Wants to take support trade on: ',pair)
                jpy_trade(7,20,pair,ask,closest_rev_dict[pair][2],1)

            elif 'JPY' in pair and ask>=closest_rev_dict[pair][1] and bid<=closest_rev_dict[pair][3] and spread<=.03:
                print('Wants to take resistance trade on: ',pair)
                jpy_trade(7,20,pair,bid,closest_rev_dict[pair][3],2)
                
            

            elif bid<=closest_rev_dict[pair][0] and ask>=closest_rev_dict[pair][2] and spread<=.0003:
                print('Wants to take support trade on: ',pair)
                majors_trade(7,20,pair,ask,closest_rev_dict[pair][2],1)


            elif ask>=closest_rev_dict[pair][1] and bid<=closest_rev_dict[pair][3] and spread<=.0003:
                print('Wants to take resistance trade on: ',pair)
                majors_trade(7,20,pair,ask,closest_rev_dict[pair][3],2)
        else:
            continue