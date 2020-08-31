# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 11:15:11 2020

@author: jxnny
"""
#df['driverRef'][(df.year==2012)  & (df.circuitRef=="catalunya")].unique()
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from Sample_Race import sample_race as sr
from Sample_Race import sample_file as sf
from scipy.optimize import curve_fit
import itertools
import lmfit
#def functions
def tyre_flags(tyres):
    f_soft=[]
    f_supersoft=[]
    f_ultrasoft=[]
    f_medium=[]
    f_hard=[]
    for tyre in tyres:
        if tyre =='Soft':
            f_soft.append(1)
        else:
            f_soft.append(0)
        if tyre =='Super soft':
            f_supersoft.append(1)
        else:
            f_supersoft.append(0)
        if tyre =='Ultra soft':
            f_ultrasoft.append(1)
        else:
            f_ultrasoft.append(0)
        if tyre =='Medium':
            f_medium.append(1)
        else:
            f_medium.append(0)
        if tyre =='Hard':
            f_hard.append(1)
        else:
            f_hard.append(0)
    return f_soft,f_supersoft,f_ultrasoft,f_medium,f_hard

def tyre_model(stintlap,lap,f_soft,f_supersoft,f_ultrasoft,f_medium,f_hard,F,Ts,Ts2,Tsb,Tss,Tss2,Tssb,Tus,Tus2,Tusb,Tm,Tm2,Tmb,Th,Th2,Thb,t_base,max_lap):
# include flag vairable for the tyre choice   
    #f_soft,f_supersoft,f_ultrasoft,f_medium,f_hard=tyre_flags(tyre)
    #functions for different tyre choices
    tsoft=(Ts*stintlap+Ts2*(stintlap**2)+Tsb)*f_soft
    tsupersoft=(Tss*stintlap+Tss2*(stintlap**2)+Tssb)*f_supersoft
    tultrasoft=(Tus*stintlap+Tus2*(stintlap**2)+Tusb)*f_ultrasoft
    tmedium=(Tm*stintlap+Tm2*(stintlap**2)+Tmb)*f_medium
    thard=(Th*stintlap+Th2*(stintlap**2)+Thb)*f_hard
    tfuel=(F*(max_lap-lap))
    return (t_base+tfuel+tsoft+tsupersoft+tultrasoft+tmedium+thard)


def model_data(dataframe,report=False):
    
    f_soft,f_supersoft,f_ultrasoft,f_medium,f_hard=tyre_flags(dataframe['tyre'])
    max_lap=max(dataframe['lap']) 
    quickest=min(dataframe['time'])
    fmodel=lmfit.Model(tyre_model,independent_vars=['stintlap','lap','f_soft','f_supersoft','f_ultrasoft','f_medium','f_hard'])
    
    #make params in model and set max_lap param to be max lap in dataset
    params = fmodel.make_params(F=0.02,Ts=0.0,Ts2=0,Tsb=0,Tss=0,Tss2=0,Tssb=0,Tus=0,Tus2=0,Tusb=0,Tm=0.03,Tm2=0,Tmb=0,Th=0,Th2=0,Thb=0,t_base=quickest,max_lap=max_lap)
    params['max_lap'].vary=False
    params['t_base'].max=quickest+2
    params['t_base'].min=quickest-5
    
    #setting some vars to be min of zero becaue physics
    params['F'].min=0
    params['Ts'].min=-1
    params['Tss'].min=-1
    params['Tus'].min=-1
    params['Tm'].min=-1
    params['Th'].min=-1
    
    #need to make softest tyre vary=false!!! otherwise the errors will fail
    most_used=dataframe.tyre.mode().values[0]
    if most_used=="Soft":
        params['Tsb'].vary=False
    if most_used=="Super soft":
        params['Tssb'].vary=False
    if most_used=="Ultra soft":
        params['Tusb'].vary=False
    if most_used=="Medium":
        params['Tmb'].vary=False
    if most_used=="Hard":
        params['Thb'].vary=False

    
    params.add('dtsdl',0.1,vary=True,min=0)
    params.add('dtssdl',0.1,vary=True,min=0)
    params.add('dtusdl',0.1,vary=True,min=0)
    params.add('dtmdl',0.1,vary=True,min=0)
    params.add('dthdl',0.1,vary=True,min=0)
    params['Ts2'].expr='dtsdl /2'
    params['Tss2'].expr='dtssdl/2'
    params['Tus2'].expr='dtusdl /2'
    params['Tm2'].expr='dtmdl /2'
    params['Th2'].expr='dthdl/2'
    #for loop that determins if tyre is not used
    tyres_used=dataframe.tyre.unique()
    possible_tyres=['Soft','Super soft','Ultra soft','Medium','Hard']
    redundant=[tyre for tyre in possible_tyres if tyre not in tyres_used]
    
    if 'Soft' in redundant:
        params['Ts'].vary = False
        params['Ts2'].vary = False
        params['Tsb'].vary = False
        params['Ts2'].set(expr='')
        params['dtsdl'].vary = False
    if 'Super soft' in redundant:
        params['Tss'].vary = False
        params['Tss2'].vary = False
        params['Tss2'].set(expr='')
        params['Tssb'].vary = False
        params['dtssdl'].vary = False
    if 'Ultra soft' in redundant:
        params['Tus'].vary = False
        params['Tus2'].vary = False
        params['Tus2'].set(expr='')
        params['Tusb'].vary = False
        params['dtusdl'].vary = False
    if 'Medium' in redundant:
        params['Tm'].vary = False
        params['Tm2'].vary = False
        params['Tm2'].set(expr='')
        params['Tmb'].vary = False
        params['dtmdl'].vary = False
    if 'Hard' in redundant:
        params['Th'].vary = False
        params['Th2'].vary = False
        params['Th2'].set(expr='')
        params['Thb'].vary = False
        params['dthdl'].vary = False
    
    times=dataframe['time'].to_numpy()
    stintlaps=dataframe['stint lap'].to_numpy()
    laps=dataframe['lap'].to_numpy()
    fit=fmodel.fit(times,params, stintlap=stintlaps,lap=laps,f_soft=f_soft,f_supersoft=f_supersoft,f_ultrasoft=f_ultrasoft,f_medium=f_medium,f_hard=f_hard,method='least_squares')
    
    param=[]
    param_value=[]
    param_stderr=[]
    for key in fit.params:
        param.append(key)
        param_value.append(fit.params[key].value)
        param_stderr.append(fit.params[key].stderr)
    paramdf=pd.DataFrame(data=np.array(param_value).reshape(-1,len(param_value)),columns=param)
    param_stderrdf=pd.DataFrame(data=np.array(param_stderr).reshape(-1,len(param_stderr)),columns=param)
    if report==True:
        print(fit.fit_report())
    return paramdf,param_stderrdf
#%% data
expdir='C:/Users/jxnny/OneDrive/Documents/school/Leeds/Dissertation/experiments/'
expfile='catalunya_2012_will_merc'
csvtag='.csv'
datainall,dataoutall=sf(expdir+expfile+csvtag)
#%% ## getting parameters for each driver

##group data by driver
datain_d_groups=datainall.groupby('Driver')

#empty df for parameters
parameter_df = pd.DataFrame()
parameter_stderr_df=pd.DataFrame()
adjusted_data=pd.DataFrame()
#loop through all drivers in group object, save driver, race, year ,parameter data
#minus the bias for each driver from their lap times save to new df
for driver, driver_data in datain_d_groups:
    try:
        Driver=driver
        year=driver_data.iloc[0].year
        race=driver_data.iloc[0].race
        driver_param,driver_param_stderr=model_data(driver_data)
        driver_param=driver_param.assign(Driver=Driver,year=year,race=race)
        driver_param_stderr=driver_param_stderr.assign(Driver=Driver,year=year,race=race)
        #driver_adjusted=driver_data.assign(time=driver_data.time-driver_param.iloc[0].t_base)
        driver_adjusted=driver_data.assign(time=driver_data.time-driver_data.time.mean())
        parameter_df=parameter_df.append(driver_param, ignore_index = True)
        parameter_stderr_df=parameter_stderr_df.append(driver_param_stderr, ignore_index = True)
        adjusted_data=adjusted_data.append(driver_adjusted,ignore_index=True)
    except:
        pass

parameter_df.to_csv(expdir+'parameters_{}.csv'.format(expfile),index=False)
#%% plot things 
fig,ax = plt.subplots()
for k,d in adjusted_data.groupby(['Driver']):
    ax.scatter(d['stint lap'], d['time'], label='data with {} driver'.format(k) )
    fig.legend()
#%% get parameters for whole dataset 

driver_all_param,driver_all_param_stderr=model_data(adjusted_data,report=True)  
driver_all_param.to_csv(expdir+'parameters_{}.csv'.format(expfile),mode='a',index=False)
driver_all_param_stderr.to_csv(expdir+'parameters_{}.csv'.format(expfile),mode='a',index=False)