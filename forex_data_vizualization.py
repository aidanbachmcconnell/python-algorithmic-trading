# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 10:54:58 2019

@author: u698198
"""

import numpy as np
import pandas as pd
import requests.packages.urllib3
import matplotlib.pyplot as plt
import seaborn
pair='USD_JPY'
d=pd.read_csv('C://Users/U698198/Documents/'+pair+'.csv')
d['Close'].plot(figsize=(40,20))
plt.title('DATA',fontsize=150)
plt.xlabel('Hours in dataset',fontsize=100)
plt.ylabel('Price',fontsize=100)
plt.xticks(fontsize=30)
plt.yticks(fontsize=30)
plt.show()