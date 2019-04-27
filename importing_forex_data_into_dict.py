# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 11:24:51 2019

@author: u698198
"""
import numpy as np
import pandas as pd
import requests.packages.urllib3
import matplotlib.pyplot as plt
import seaborn

#FOR THIS IMPORT TO WORK YOU NEED TO CONFIGURE READ_CSV TO YOUR OWN DIRECTORY
#TO GET DATA GO TO DUKASCOPY AND GO TO THEIR HISTORICAL DATA FEED
pairs=['USD_JPY','CAD_JPY','NZD_JPY',
      'AUD_USD','EUR_USD','NZD_USD','USD_CHF','AUD_CAD',
       'AUD_CHF','AUD_NZD','EUR_CHF','EUR_GBP',
       'GBP_CHF','NZD_CHF','USD_SGD','AUD_JPY',
       'USD_CAD',
       'NZD_CAD','CAD_CHF']
#'EUR_JPY''EUR_NZD','GBP_USD','EUR_AUD','EUR_CAD','GBP_AUD','GBP_CAD','GBP_NZD','CHF_JPY','GBP_JPY','GBP_USD',
pairs_dict={}
for pair in pairs:
    pairs_dict[pair]=pd.read_csv('C://Users/U698198/Documents/'+pair+".csv")
    print(pairs_dict[pair].head())