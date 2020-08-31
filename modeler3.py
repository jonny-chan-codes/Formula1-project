# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 12:43:54 2020

@author: jxnny
"""

import os
wdir='C:/Users/jxnny/OneDrive/Documents/school/Leeds/Dissertation'
os.chdir(wdir)
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from Sample_Race import sample_race as sr
from Sample_Race import sample_file as sf
from scipy.optimize import curve_fit
import itertools
import lmfit

#import modeler2
photodir='C:/Users/jxnny/OneDrive/Documents/school/Leeds/Dissertation/latex/'
#function that returns flag configs for whatever tyre choice, so i dont have to copy it for every model 
#its a pain, python doesnt like fitting using booleans, so need to make flags beforehand and pass them in as independant vairables 
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

#model components fuel penalty + tbase + tyre penalty
def fuel_component(lap,F,t_base,max_lap):
    return(F*(max_lap-lap)+t_base)

def tyre_component(stintlap,lap,f_soft,f_supersoft,f_ultrasoft,f_medium,f_hard,Ts,Ts2,Tsb,Tss,Tss2,Tssb,Tus,Tus2,Tusb,Tm,Tm2,Tmb,Th,Th2,Thb):
    tsoft=(Ts*stintlap+Ts2*(stintlap**2)+Tsb)*f_soft
    tsupersoft=(Tss*stintlap+Tss2*(stintlap**2)+Tssb)*f_supersoft
    tultrasoft=(Tus*stintlap+Tus2*(stintlap**2)+Tusb)*f_ultrasoft
    tmedium=(Tm*stintlap+Tm2*(stintlap**2)+Tmb)*f_medium
    thard=(Th*stintlap+Th2*(stintlap**2)+Thb)*f_hard


    return (tsoft+tsupersoft+tultrasoft+tmedium+thard)

#composite model by adding fuel component and tyre component 
compmodel=lmfit.Model(tyre_component,independent_vars=['stintlap','f_soft','f_supersoft','f_ultrasoft','f_medium','f_hard','lap'])+lmfit.Model(fuel_component,independent_vars=['lap'])
# print('parameter names: {}'.format(compmodel.param_names))
# print('independent variables: {}'.format(compmodel.independent_vars))

#data 
driver='vettel'
circuit='villeneuve'
year=2012
tyre_data=True
clean_data=True
savefig=False
#sample the database and get the times and outliers 
datain,dataout,used_strat=sr(driver,circuit,year,clean=clean_data,tyres=tyre_data)

#find some parameters for model 
max_lap=max(datain['lap']) 
quickest=min(datain['time'])
#tyreflags
f_soft,f_supersoft,f_ultrasoft,f_medium,f_hard=tyre_flags(datain['tyre'])
#initialise parameters

params = compmodel.make_params(F=0.02,Ts=0.0,Ts2=0,Tsb=0,Tss=0,Tss2=0,Tssb=0,Tus=0,Tus2=0,Tusb=0,Tm=0,Tm2=0,Tmb=0,Th=0,Th2=0,Thb=0,t_base=quickest,max_lap=max_lap)

most_used=datain.tyre.mode().values[0]
most_used=dataout[dataout['stint lap']==1].tyre.mode().values[0]
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

params.add('dtsdl',0.1,vary=True,min=0)
params.add('dtssdl',0.1,vary=True,min=0)
params.add('dtusdl',0.1,vary=True,min=0)
params.add('dtmdl',0.1,vary=True,min=0)
params.add('dthdl',0.1,vary=True,min=0)
#right now i dont have a justification for setting these minimums but otherwise my model/optimizer gives back unrealistic results 
params['Ts2'].expr='dtsdl /2'
params['Tss2'].expr='dtssdl/2'
params['Tus2'].expr='dtusdl /2'
params['Tm2'].expr='dtmdl /2'
params['Th2'].expr='dthdl/2'


#not all tyres will be used in a race so I need to be able to turn off fitting on the useless parameters
#list of tyres in the dataset
tyres_used=datain.tyre.unique()

possible_tyres=['Soft','Super soft','Ultra soft','Medium','Hard']
#for loop that determins if tyre is not used 
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


times=datain['time'].to_numpy()
stintlaps=datain['stint lap'].to_numpy()
laps=datain['lap'].to_numpy()


compfit=compmodel.fit(times,params, stintlap=stintlaps,lap=laps,f_soft=f_soft,f_supersoft=f_supersoft,f_ultrasoft=f_ultrasoft,f_medium=f_medium,f_hard=f_hard,method='least_squares')

param=[]
param_value=[]
for key in compfit.params:
    param.append(key)
    param_value.append(compfit.params[key].value)
paramdf=pd.DataFrame(data=np.array(param_value).reshape(-1,len(param_value)),columns=param)
#reoder paramlist
col=['F','Ts','Ts2','Tsb','Tss','Tss2','Tssb','Tus','Tus2','Tusb','Tm','Tm2','Tmb','Th','Th2','Thb','t_base']
paramdf=paramdf[col]
#happily it gives the same results as in modeler 2

comps = compfit.eval_components()
#%%
plt.style.use('ggplot')
title='{}, {}, {}'.format(driver.capitalize(),circuit.capitalize(),year)
#$$
fig,ax = plt.subplots()
    #for loop adds to the figure by looping over each stint 
for k,d in datain.groupby(['tyre']):
    ax.scatter(d['lap'], d['time'], label='{} tyre'.format(k))
ax.plot(datain.lap,comps['tyre_component']+comps['fuel_component'],'r--', label='model prediction')
fig.legend(loc='upper right', bbox_to_anchor=(0.95, 0.85))
plt.title(title+'\n Complete Model ')
plt.xlabel('Lap')
plt.ylabel('Lap-time(s)')
plt.show()



datain['fuel_component']=comps['fuel_component']
fig2,ax2 = plt.subplots()
for k,d in datain.groupby(['tyre']):
    ax2.scatter(d['lap'], d['time']-d['fuel_component'] ,label='{} tyre'.format(k))
plt.xlabel('Lap')
plt.ylabel('lap-time minus fuel component (s)')
ax2.plot(datain.lap,comps['tyre_component'],'r--',label='tyre penalty')
fig2.legend(loc='upper right', bbox_to_anchor=(0.95, 0.4))
plt.title(title+'\n Tyre Penalty Modelled')
plt.show()

fig3,ax3 = plt.subplots()
    #for loop adds to the figure by looping over each stint 
for k,d in datain.groupby(['tyre']):
    ax3.scatter(d['lap'], d['time'], label='{} tyre'.format(k))
ax3.plot(datain.lap,comps['fuel_component'],'r--', label='fuel penalty + base time')
fig3.legend(loc='upper right', bbox_to_anchor=(0.55, 0.35))
plt.title(title+'\n Fuel Penalty Modelled')
plt.xlabel('Lap')
plt.ylabel('Lap-time(s)')
plt.show()

if savefig==True:
    fig.savefig(photodir+title+'model.pdf')
    fig2.savefig(photodir+title+'tyre_model.pdf')
    fig3.savefig(photodir+title+'fuel_model.pdf')
