# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 22:59:54 2020

@author: jxnny
"""

import pandas as pd
import os
import numpy as np 
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from scipy.optimize import curve_fit

#os.chdir(wdir)


datadir='C:/Users/jxnny/OneDrive/Documents/school/Leeds/Dissertation/data'
laptime_df=pd.read_csv(datadir+'/kaggle_laptimes_cleaned.csv')
pitdf=pd.read_csv(datadir+'/kaggle_pitstops_cleaned.csv')


def polynomial(lap,a,b,c):
    return a*lap**2+b*lap+c

def predict_outlier(data,contamination):
    #function that returns a list of whether it thinks a point is an outlier, works using the isolation forest algorithm 
    clf = IsolationForest(n_estimators=100 , max_samples='auto', random_state = 1, contamination= contamination)
    clf.fit(data)
    out_score=clf.score_samples(data)
    preds = clf.predict(data)
    outlier=[]
    for point in range(len(preds)):
        if clf.score_samples(data)[point]<-0.56 :
            dpoint='outlier'
        else:
            dpoint='inlier'
        outlier.append(dpoint)
    return outlier, out_score

def predict_outlier_cedric(data):
    outlier_detected=False
    pabc,pcov=curve_fit(polynomial, data['stint lap'], data['time'],p0=[0.1,0,90])
    model_pred=polynomial(data['stint lap'],pabc[0],pabc[1],pabc[2])
    stdev=data['time'].std()
    outlier=[]
    outlier2=[]
    for point in range(len(data)):
         if data['time'].iloc[point]>model_pred.iloc[point]+1.96*stdev or data['stint lap'].iloc[point]==1:
             dpoint='outlier'
             outlier2.append(data.iloc[point]['stint lap'])
             outlier_detected=True
         else :
             dpoint='inlier'
         outlier.append(dpoint)
         
    if outlier_detected==False:
            return outlier2
    else:
        data['out']=outlier
        return outlier2+predict_outlier_cedric(data[data['out']=='inlier'])

def predict_outlier_cedric2(data):
    outlierlaps=predict_outlier_cedric(data)
    outlier=[]
    for point in range(len(data)):
        if data['stint lap'].iloc[point] in outlierlaps:
            point='outlier'
        else:
            point='inlier'
        outlier.append(point)
    return outlier

    
#this one cleans using whatever algorithm predict_outlier function uses 
def sample_race(driver,circuit,year,clean=True,tyres=True,out='isolation'):
    sample_laptimes=laptime_df[['lap','time']][(laptime_df.year==year) & (laptime_df.driverRef==str(driver)) & (laptime_df.circuitRef==str(circuit))]
    pits=pitdf[(pitdf.year==year) & (pitdf.driverRef==str(driver)) & (pitdf.circuitRef==str(circuit))]
    stint=[]
    tyre=[]
    stintlap=[]
    lapofstint=0
    sample_laptimes=sample_laptimes.sort_values(by=['lap'])
    strategy=[]
    strategy.append(tuple(pits['lap'].values))
    strategy.append(tuple(pits.iloc[0,7:].dropna().values))
    for lap in sample_laptimes['lap']:
        stintnum=1
        lapofstint+=1
        for stoplap in pits['lap']:
            if lap > stoplap:
                stintnum+=1
        #reset stint lap if stint restarts         
        if lap in pits['lap'].values+1:
            lapofstint=1
        stint.append(stintnum)
        stintlap.append(lapofstint)
        if tyres==True:
            tyreused=pits.iloc[0,6+stintnum]
            tyre.append(tyreused)
    sample_laptimes['stint lap']=stintlap
    sample_laptimes['stint']=stint 
    if tyres==True:    
        sample_laptimes['tyre']=tyre
    if clean==True:
        grouped = sample_laptimes.groupby('stint')
        outlier1=[]
        outlier_scores1=[]
        for stint, group in grouped:
            #here I find outliers depending on what algorithm I want to use 
            #set expected contamination to be 2 outliers per stint 
            if out == 'isolation':
                dummy=predict_outlier(group[['stint lap','time']],contamination=0.0)
                outlier1.append(dummy[0])
                outlier_scores1.append(dummy[1])
            elif out == 'cedric':
                outlier1.append(predict_outlier_cedric2(group[['stint lap','time']]))
            outlier2 = [item for sublist in outlier1 for item in sublist]
            outlier2=np.asarray(outlier2)
            outlier_scores2=[item for sublist in outlier_scores1 for item in sublist]
            outlier_scores2=np.asarray(outlier_scores2)

        sample_laptimes['outliers']=outlier2
        sample_laptimes['outlier score']=outlier_scores2
        group_outlier=sample_laptimes.groupby('outliers')
        inliers=group_outlier.get_group('inlier')
        inliers=inliers.assign(Driver=driver,race=circuit,year=year)
        outliers=group_outlier.get_group('outlier')
        outliers=outliers.assign(Driver=driver,race=circuit,year=year)
        return inliers, outliers,strategy

    return sample_laptimes,[],strategy




#reads file, calls sample_race for each of the rows in that file and then puts it all together (assumes tyres and clean =true)
def sample_file(csvfile):
    sample_me=pd.read_csv(csvfile)
    drivers=sample_me['driver']
    races=sample_me['race']
    year=sample_me['year']
    inliers=pd.DataFrame()
    outliers=pd.DataFrame()
    for i in range(len(drivers)):
        print(drivers[i])
        ins,outs,strat=sample_race(drivers[i],races[i], year[i])
        ins=ins.assign(Driver=drivers[i],race=races[i],year=year[i])
        outs=outs.assign(Driver=drivers[i],race=races[i],year=year[i])
        inliers=inliers.append(ins,ignore_index=True)
        outliers=outliers.append(outs,ignore_index=True)
   
    return inliers, outliers


#----------------testing----------------------------------------------------
driver='hamilton'  
circuit='spa'
year=2015
tyre_data=True
clean_data=True


sample=sample_race(driver,circuit,year,clean=clean_data,tyres=tyre_data)
# sample_stint = sample[sample['stint']==3]
# test2=predict_outlier_cedric2(sample_stint[['stint lap','time']])

# # #different ways to plot it 
# plt.style.use('ggplot')
# title='{}, {}, {}'.format(driver,circuit,year)
# #%%
# plt.plot(testtimes_inlier['lap'],testtimes_inlier['time'],'.')
# plt.title(title)
# plt.ylabel('time(s)')
# plt.show()

