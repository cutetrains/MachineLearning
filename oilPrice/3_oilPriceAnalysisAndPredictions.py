import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
import re
import os
from os.path import expanduser
from dotenv import load_dotenv

inData = pd.read_csv(os.sep.join((expanduser("~"),'2_Brent_Daily_Training_Data.csv')), index_col=[0])
print(list(inData))

print(f'Correlation calculation for some features:')
backDates  = []
fwdDates = []
maDates = []
for i in list(inData):
    if "Back" in i[0:4]:
        backDates.append(i)
    if "Fwd" in i[0:3]:
        fwdDates.append(i)
    if "MAd" in i[0:3]:
        maDates.append(i)

#TODO: Merge output to one big string and print at end? On the other hand, the
    #  output may serve as a progress indicator.

print(f'Find correlation between {backDates}  and {fwdDates}:')
print("\t\t", end = "")
print('\t'.join(fwdDates))

for i in backDates: #Back date correlation 
    print("{:13}".format(i), end = "")
    for j in fwdDates:
        print("{:8.4f}".format(inData[i].corr(inData[j])), end = "")
    print("")

print("{:13}".format('Price'), end = "") # Price correlation
for j in fwdDates:
    print("{:8.4f}".format(inData['Price'].corr(inData[j])), end = "")
print("")

print("{:13}".format('NBackD'), end = "") # Negative Back Dates
for j in fwdDates:
    print("{:8.4f}".format(inData['Negative Backdates'].corr(inData[j])), end = "")
print("")

print("{:13}".format('SBackD'), end = "") # Sum of Back Dates
for j in fwdDates:
    print("{:8.4f}".format(inData['Sum for Backdates'].corr(inData[j])), end = "")
print("")

print("{:13}".format('QTA1Y'), end = "") # Sum of Quota one year
for j in fwdDates:
    print("{:8.4f}".format(inData['QTA1Y'].corr(inData[j])), end = "")
print("")

for i in maDates: 
    print("{:13}".format(i), end = "")
    for j in fwdDates:
        print("{:8.4f}".format(inData[i].corr(inData[j])), end = "")
    print("")

# Now, divide the data into training data, test data and cross-verification data
# 1990-05-21 -> 2022-01-01 corresponds to 8000 samples.
# One year corresponds to 250 samples
# TR   qTE qTR     qCV   qTR
# The worst case scenario is five sets of data with four quarantine periods.
# q = 3Y -> Data is 20 years (12 Y Training, 4 Y Test, 4 Y Cross verification)
# q = 1Y -> Data is 28 years (16 Y Training, 6 Y Test, 6 Y Cross verification)
length = inData.shape[0]
quarantineLength = 250
mlDataSize = length - quarantineLength * 4
print(f'Total data set is {length} samples. \nQuarantine length is {quarantineLength} samples.')
print(f'The ML data size is {mlDataSize} samples')
trainingLength = int( mlDataSize * 0.6) #TODO: Constants in the start of the script
testLength = int( mlDataSize * 0.2)
crossVerificationLength = int( mlDataSize * 0.2)
print(f'Training: {trainingLength} samples')
print(f'Test: {testLength} samples')
print(f'Cross Verification: {crossVerificationLength} samples')
# Select a random sample to be test data and another random sample to
# be cross verification.
#print(length)
