import pandas as pd
import numpy as np
import time
from math import sqrt
from datetime import datetime
from datetime import timedelta
import logging
import os
from os.path import expanduser
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

# The script retrieves some historic records.
backDates = [1, 7, 30, 90, 365, 365*3+1]

# The future oil price for some dates. This will reduce the size of the data set
# This will be the y (result)
forwardDates = [1, 7, 30, 90]

# Moving Average window sizes
maDates = [3, 9, 30, 100]

rollingMaxRange = 365
rollingMinRange = 365

if(max(maDates)> max(backDates)):
    logging.error(f'Date mismatch! max({maDates}) is larger than max({backDates})')
if(max([rollingMaxRange, rollingMinRange]) > max(backDates)):
    logging.error(f'Date mismatch! rolling max/min range is larger than max({backDates})')

print(f'Use {backDates} days ago to predict {forwardDates} days ahead')

Xraw = pd.read_csv(os.sep.join((expanduser("~"),'1_Brent_Daily_RawData.csv')), index_col=[0])
print(Xraw)

# Week-ends and other non-trading days has already been added to this set.
# The indices correspond to the days since the first record. 
earliest = max(backDates)
latest = Xraw.shape[0]-max(forwardDates)

print(f"Generate training data between {Xraw.at[earliest,'Date']} and {Xraw.at[latest,'Date']}")
for d in backDates:
    Xraw[f'Back{d}'] = Xraw['Price'].shift(0) / Xraw['Price'].shift(d) - 1

for d in forwardDates:
    Xraw[f'Fwd{d}'] = Xraw['Price'].shift(-d) / Xraw['Price'].shift(0) - 1

latestValue = 0
    
for i in range(latest-1, earliest, -1):
    if ( (Xraw.loc[i, 'TradeDay']== 0 ) and (Xraw.loc[i+1, 'TradeDay']== 1 )):
        latestValue = Xraw.loc[i, 'Fwd1']
        Xraw.loc[i, 'Fwd1'] = 0
    if ( (Xraw.loc[i, 'TradeDay']== 1 ) and (Xraw.loc[i+1, 'TradeDay']== 0 )):
        Xraw.loc[i, 'Fwd1'] = latestValue

print(f"Sum both the amount of negative back dates and the accumulated loss over those dates. ")
for i in range(earliest, latest):
    sumNegative = 0
    sumBackDatesPct = 0
    for d in backDates:
        thisV = Xraw.at[i, f'Back{d}']
        sumBackDatesPct = sumBackDatesPct + thisV
        if(thisV < 0):
            sumNegative = sumNegative + 1
    Xraw.loc[i, 'Negative Backdates'] = sumNegative
    Xraw.loc[i, 'Sum for Backdates'] = sumBackDatesPct

print(f'Calculating moving averages for {maDates}')
for i in maDates:
    Xraw[f'MA{i}'] = Xraw['Price'].rolling(window=i).mean()
    Xraw[f'MAd{i}'] = Xraw[f'MA{i}']/Xraw['Price']

print("Calculating quota and rolling MAX and MIN for one year")
Xraw['MIN365'] = Xraw['Price'].rolling(365).min()
Xraw['MAX365'] = Xraw['Price'].rolling(365).max()
Xraw['QTA1Y'] = (Xraw['Price'] - Xraw['MIN365']) / (Xraw['MAX365']-Xraw['MIN365'])
    
print(f'Delete empty records and keep only trading days')
Xraw=Xraw.dropna()
Xraw = Xraw.drop(Xraw[Xraw.TradeDay == 0 ].index)
print(Xraw)#print (df)

Xraw.to_csv(os.sep.join((expanduser("~"),'2_Brent_Daily_Training_Data.csv')))
