# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 19:55:03 2020

@author: jxnny
"""

import pandas as pd
import os
import re

#%% make data dictionary containing all the kaggle files
wdir='C:/Users/jxnny/OneDrive/Documents/school/Leeds/Dissertation/data'
os.chdir(wdir)


files = []
for dirname, _, filenames in os.walk("."):
    for filename in filenames:
        files.append(str(os.path.join(dirname, filename)))
files

names = [re.findall('\w*.csv', x)[0].split('.')[0] for x in files]

data_dict = {}

for i, file in enumerate(files):
    name = names[i]
    data_dict[name] = pd.read_csv(file, encoding = 'latin-1')
data_dict['tyres'] = pd.read_csv('tyres.csv',encoding='utf8')

# drop some df feilds to prepare for joins
data_dict['drivers'].drop(columns = ['number', 'code', 'url','code','dob','nationality'], inplace = True)
data_dict['circuits'].drop(columns = ['name', 'location', 'url','alt','country','lat','lng'], inplace = True)
data_dict['races'].drop(columns = ['round', 'name', 'url','date','time'], inplace = True)

data_dict['tyres'][['forename','surname']]=data_dict['tyres'].name.str.split(" ",1,expand=True)
data_dict['tyres']=data_dict['tyres'].drop(columns=['name'])
data_dict['tyres']=data_dict['tyres'].merge(data_dict['drivers'],  how='left', on=['forename', 'surname'])

#get rid of (number) in tyre dataframe!!
data_dict['tyres']=data_dict['tyres'].replace(to_replace ='(\s\(\d+\))', value = '', regex = True)

#new dataframe of laptime 

df = data_dict['lapTimes'].copy()
df = df.merge(data_dict['races'], how = 'left')
df = df.merge(data_dict['circuits'], how = 'left')
df = df.merge(data_dict['drivers'], how = 'left')
df.drop(columns=['raceId','driverId','circuitId','forename','surname','time'],inplace=True)

pitdf=data_dict['pitStops'].copy()
pitdf=pitdf.merge(data_dict['races'], how = 'left')
pitdf = pitdf.merge(data_dict['circuits'], how = 'left')
pitdf = pitdf.merge(data_dict['drivers'], how = 'left')
pitdf=pitdf.merge(data_dict['tyres'], how = 'left')

pitdf.drop(columns=['raceId','driverId','circuitId','forename','surname','time'],inplace=True)
#make new field for seconds
df['time']=df['milliseconds']/1000
df=df.drop(columns='milliseconds')
#reorder df
orderme=['year','circuitRef','driverRef','lap','time','position']
df=df[orderme]
#df.to_csv('kaggle_laptimes_cleaned.csv',index=False)
#pitdf.to_csv('kaggle_pitstops_cleaned.csv',index=False)
#%%
pittimes=(pitdf.groupby(['circuitRef']).milliseconds.median()/1000)\
    .rename("Seconds")

#pittimes.to_csv('pittimes.csv')
