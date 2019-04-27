# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 10:18:18 2019

@author: u698198
"""

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

def stoploss_calc(pair,wick,sl):
    sl_price=0
    return sl_price
    
def takeprofit_calc(pair,current_price,tp):
    tp_price=0
    return tp_price

def jpy_trade(sl,tp,pair,current_price):
    bal,marg,trades=account_value()
    units=units_calc(bal,.01,sl)
    stoploss=stoploss_calc(pair,wick,sl)
    takeprofit=takeprofit_calc(pair,current_price,tp)
    
    order={"order": {
        "type": "MARKET",
        "units": units,
        "instrument": pair,
        "timeInForce": "FOK",
        "takeProfitOnFill": {
            "timeInForce": "GTC",
            "price": stoploss
        },
        "stopLossOnFill": {
            "timeInForce": "GTC",
            "price": takeprofit
    }
  }
}
    

    
def majors_trade(sl,tp,pair):
    bal,marg,trades=account_value()
    units=units_calc(bal,.01,sl)
    stoploss=stoploss_calc(pair,wick,sl)
    takeprofit=takeprofit_calc(pair,current_price,tp)
    
    order={"order": {
        "type": "MARKET",
        "units": units,
        "instrument": pair,
        "timeInForce": "FOK",
        "takeProfitOnFill": {
            "timeInForce": "GTC",
            "price": stoploss
        },
        "stopLossOnFill": {
            "timeInForce": "GTC",
            "price": takeprofit
    }
  }
}
    
    
    
    
def cross_trade(sl,tp,pair):
    bal,marg,trades=account_value()
    units=units_calc(bal,.01,sl)
    stoploss=stoploss_calc(pair,wick,sl)
    takeprofit=takeprofit_calc(pair,current_price,tp)
    
    
    order={"order": {
        "type": "MARKET",
        "units": units,
        "instrument": pair,
        "timeInForce": "FOK",
        "takeProfitOnFill": {
            "timeInForce": "GTC",
            "price": stoploss
        },
        "stopLossOnFill": {
            "timeInForce": "GTC",
            "price": takeprofit
    }
  }
}