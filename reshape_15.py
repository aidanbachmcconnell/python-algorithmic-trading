# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 18:53:57 2019

@author: Aidan
"""

import pandas as pd
import numpy as np

df=pd.read_csv('C:/Users/Aidan/Documents/FOREX Trading/USD_JPY_min.csv',parse_dates=['Local time'],index_col='Local time')
df['Local time']=df.iloc[:,0][0:-9]
print(df.head())

