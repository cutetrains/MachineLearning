import pandas as pd
import numpy as np
import time
from datetime import datetime
from datetime import timedelta
import quandl
from datetime import date
import datetime as dt
import os
from os.path import expanduser
from dotenv import load_dotenv
#import secrets
useQuandl = True

def addYears(d, years):
    try:
#Return same day of the current year        
        return d.replace(year = d.year + years)
    except ValueError:
#If not same day, it will return other, i.e.  February 29 to March 1 etc.        
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))


# Function to insert row in the dataframe
def Insert_row(row_number, df, row_value):
    start_upper = 0
    end_upper = row_number
    start_lower = row_number
    end_lower = df.shape[0]
    upper_half = [*range(start_upper, end_upper, 1)]
    lower_half = [*range(start_lower, end_lower, 1)]
    lower_half = [x.__add__(1) for x in lower_half]
    index_ = upper_half + lower_half
    df.index = index_
    df.loc[row_number] = row_value
    df = df.sort_index()
    return df

#Quandl has a repository for oil records that is updated
if(useQuandl == True):
    load_dotenv(expanduser("~")+'\.env')
    quandl.ApiConfig.api_key = os.getenv('api_key_quandl')
    today = date.today()
    print("Today's date:", today)
    # Importing our data
    X_raw = quandl.get("FRED/DCOILBRENTEU", start_date="1987-05-20", end_date=today)
    X_raw.reset_index(inplace=True)
    X_raw = X_raw.rename(columns={'Value': 'Price'})
else:
    X_raw = pd.read_csv("C:\\Users\\gusta\\Dropbox\\Ekonomi\\Oil\\brent-daily_csv.csv",index_col=False)

firstDateS = str(X_raw.at[0, 'Date'])[0:10]
firstDateDT = datetime.strptime(str(firstDateS), '%Y-%m-%d')

numOfRows = X_raw.shape[0]
endDateDT = datetime.strptime(str(X_raw.at[numOfRows-1, 'Date'])[0:10], '%Y-%m-%d')
X_raw['TradeDay'] = 1
print(f'Fetched data from {firstDateDT} to {endDateDT}')
print(X_raw)

# Add dates for non-trading days.
# These will be ignored when generating training data
# Extend the length condition when inserting holiday rows
listComplete = False
position = 0
currentDateDT = firstDateDT
while listComplete == False:
    #Check if this datetime matches the date on the current row
    currentRowDT = datetime.strptime(str(X_raw.at[position, 'Date'])[0:10], '%Y-%m-%d')
    if(currentDateDT == currentRowDT):
        position = position + 1
        currentDateDT += timedelta(days=1)
    else:
        # A row is inserted
        if(currentRowDT > currentDateDT):
            previousOilPrice = X_raw.at[position-1,'Price']
            X_raw =  Insert_row(position, X_raw, [datetime.strftime(currentDateDT,'%Y-%m-%d'),previousOilPrice, 0])
        else:
            print("UNEXPECTED!!! Current row points to earlier date than current date")
    if(currentRowDT == endDateDT):
        listComplete = True
        print("Complete")

X_raw['Date'] = pd.to_datetime(X_raw['Date']).dt.date
X_raw.to_csv('C:\\Users\\gusta\\Dropbox\\Ekonomi\\Oil\\1_Brent_Daily_RawData.csv')

