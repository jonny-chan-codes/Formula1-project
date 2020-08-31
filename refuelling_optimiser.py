# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 11:37:04 2020

@author: jxnny
"""

import os
wdir='C:/Users/jxnny/OneDrive/Documents/school/Leeds/Dissertation'
os.chdir(wdir)
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import itertools 
import lap_models
import modeler2
import modeler3
from tqdm import tqdm
photodir='C:/Users/jxnny/OneDrive/Documents/school/Leeds/Dissertation/latex/'
datadir='C:/Users/jxnny/OneDrive/Documents/school/Leeds/Dissertation/data'
pittimes=pd.read_csv(datadir+'/pittimes.csv', index_col='circuitRef')

data=modeler3.datain.append(modeler3.dataout)
track=modeler3.circuit
N_laps=max(data['lap'])
N_stop=2
Max_stop=2
min_stop=2
savefig=False
Robust_stuff=False

#tyre_options=['Soft','Soft','Super soft','Super soft','Ultra soft','Ultra soft','Medium','Medium','Hard','Hard']
soft=0
super_soft=0
ultra_soft=0
medium=3
hard=3
first_stint='Medium'

#%%
model_params=modeler3.paramdf.iloc[0].values[0:17]
if Robust_stuff==True:
    param_data_dir='C:/Users/jxnny/OneDrive/Documents/school/Leeds/Dissertation/experiments/'
    param_datafile='parameters_catalunya_2012_will_merc'
    paramdf=pd.read_csv(param_data_dir+param_datafile+'.csv')
    bottas_param=paramdf[paramdf.Driver=='bottas'].iloc[:,0:17]
    multi_param=paramdf.iloc[3,0:17]
    param_stderr=paramdf.iloc[5,0:17]
    
    f=float(multi_param['F']) -5*float(param_stderr['F'])
    tm=float(multi_param['Tm']) +0*float(param_stderr['Tm'])
    tm2=float(multi_param['Tm2']) +0*float(param_stderr['Tm2'])
    tmb=float(multi_param['Tmb']) +0*float(param_stderr['Tmb'])
    th=float(multi_param['Th']) +0*float(param_stderr['Th'])
    th2=float(multi_param['Th2']) +0*float(param_stderr['Th2'])
    thb=float(multi_param['Thb']) +0*float(param_stderr['Thb'])
    t_base=float(bottas_param['t_base'])
    
    ts=0
    ts2=0
    tsb=0
    tss=0
    tss2=0
    tssb=0
    tus=0
    tus2=0
    tusb=0
    
    
    
    model_params=list((f,ts,ts2,tsb,tss,ts2,tsb,tus,tus2,tusb,tm,tm2,tmb,th,th2,thb,t_base))


def tyre_options_maker(soft=3,supersoft=3,ultrasoft=3,medium=3,hard=3):
    s = np.array(['Soft' for _ in range(soft)])
    ss = np.array(['Super soft' for _ in range(supersoft)])
    us = np.array(['Ultra soft' for _ in range(ultrasoft)])
    m = np.array(['Medium' for _ in range(medium)])
    h = np.array(['Hard' for _ in range(hard)])
    tyre_list = [y for x in [s,ss,us,m,h] for y in x] 
    return tyre_list

tyre_options=tyre_options_maker(soft=soft,supersoft=super_soft,ultrasoft=ultra_soft,medium=medium,hard=hard)
def list_options(N_lap,N_stop,tyre_options=tyre_options,**kwargs):
    first_stint=kwargs.get('first_stint',None)
    lap_list=np.linspace(1,N_lap,num=N_lap,dtype=int)
    #stint_list=np.linspace(1,N_stop+1,num=N_stop+1,dtype=int)
    
    stop_list=[i for i in itertools.combinations(lap_list,r=N_stop)]
    tyre_combos= [i for i in itertools.permutations(tyre_options,r=N_stop+1)]
    tyre_combos=set(tyre_combos)
    #code that gets rid of tyre combos with the same tyre in every stint, as thats not allowed
    #also if option of first stint is not none then it will get rid of all strategies where 
    #the first stint tyre is not first_stint. This is so if you got to q3 the strategy engineer can set the first tyre. 
    dummycombos=[]
    if first_stint==None:
        for combo in tyre_combos:
            if combo.count(combo[0])!=len(combo):
                dummycombos.append(combo)
    else:
        for combo in tyre_combos:
            if combo.count(combo[0])!=len(combo) and combo[0]==first_stint:
                dummycombos.append(combo)
    tyre_combos=dummycombos
    
    potential_strategies=[list(i) for i in itertools.product(stop_list,tyre_combos)] 
    print("{} potential strategies found".format(len(potential_strategies)))
    return (potential_strategies)

testlist=list_options(N_lap=N_laps, N_stop=N_stop,first_stint='Medium')
#%%
test_strat=[(15, 42), ('Medium', 'Medium', 'Hard')]


def tyre_flags(tyre):
    
    if tyre =='Soft':
        f_soft=1
    else:
        f_soft=0
    if tyre =='Super soft':
        f_supersoft=1
    else:
        f_supersoft=0
    if tyre =='Ultra soft':
        f_ultrasoft=1
    else:
        f_ultrasoft=0
    if tyre =='Medium':
        f_medium=1
    else:
        f_medium=0
    if tyre =='Hard':
        f_hard=1
    else:
        f_hard=0
    return f_soft,f_supersoft,f_ultrasoft,f_medium,f_hard

#%%
def pit_pen_calculator(strategy,max_lap=N_laps,track='catalunya'):
    pit_pen=0
    #starting laps and end laps 
    stint_starts=[]
    stint_starts.append(0)
    for stoplap in strategy[0]:
        stint_starts.append(stoplap)
    stint_ends=list(strategy[0])
    stint_ends.append(max_lap)
    refuel_time=pittimes.loc[track].values[2]
    av_pit=2.92
    base_time=pittimes.loc[track].values[0]-av_pit
    for i in range(1,len(stint_starts)):
        delta=stint_ends[i]-stint_starts[i]
        if delta*refuel_time>av_pit:
            pit_time=base_time+delta*refuel_time
            pit_pen+=pit_time
        else:
            pit_time=base_time+av_pit
            pit_pen+=pit_time
    return pit_pen

def stint_time_integrator(start,stop,params,tyre,max_lap):
    F,Ts,Ts2,Tsb,Tss,Tss2,Tssb,Tus,Tus2,Tusb,Tm,Tm2,Tmb,Th,Th2,Thb,t_base=params 
    f_soft,f_supersoft,f_ultrasoft,f_medium,f_hard=tyre_flags(tyre)
    delta=stop-start
    fuel=(F*max_lap*delta)-F*(0.5*delta*(start+stop+1))+t_base*(delta)
    soft=(((delta+1)*delta/2)*Ts+((2*delta+1)*(delta+1)*delta/6)*Ts2 +Tsb*delta)*f_soft
    supersoft=(((delta+1)*delta/2)*Tss+((2*delta+1)*(delta+1)*delta/6)*Tss2 +Tssb*delta)*f_supersoft
    ultrasoft=(((delta+1)*delta/2)*Tus+((2*delta+1)*(delta+1)*delta/6)*Tus2 +Tusb*delta)*f_ultrasoft
    medium=(((delta+1)*delta/2)*Tm+((2*delta+1)*(delta+1)*delta/6)*Tm2 +Tmb*delta)*f_medium
    hard=(((delta+1)*delta/2)*Th+((2*delta+1)*(delta+1)*delta/6)*Th2 +Thb*delta)*f_hard
    time=fuel+soft+supersoft+ultrasoft+medium+hard
    return time
#%%

def strategy_to_time(strategy,model_params,max_lap=N_laps):
    total_time=0
    nstop=len(strategy[0])
    tyres=strategy[1]
    #starting laps and end laps 
    stint_starts=[]
    stint_starts.append(0)
    for stoplap in strategy[0]:
        stint_starts.append(stoplap)
    stint_ends=list(strategy[0])
    stint_ends.append(max_lap)
    #integrate over each stint and add up the times
    for i in range(len(stint_starts)):
       add_time=stint_time_integrator(stint_starts[i], stint_ends[i], model_params, tyres[i], max_lap=N_laps)
       #print(add_time)
       total_time+=add_time
    #add up the pit stop penalties
    total_time+=nstop*pittimes.loc[modeler3.circuit].values[0]
    return total_time


def strategy_to_time2(strategy,model_params,max_lap=N_laps):
    total_time=0
    tyres=strategy[1]
    #starting laps and end laps 
    stint_starts=[]
    stint_starts.append(0)
    
    for stoplap in strategy[0]:
        stint_starts.append(stoplap)
    stint_ends=list(strategy[0])
    stint_ends.append(max_lap)
    #integrate over each stint and add up the times
    deltas=[stint_ends[i]-stint_starts[i] for i in range(len(stint_starts))]
    stint_starts2=[0 for i in range(len(stint_starts))]
    
    for i in range(len(stint_starts)):
       add_time=stint_time_integrator(stint_starts2[i], deltas[i], model_params, tyres[i], max_lap=deltas[i])
       #print(add_time)
       total_time+=add_time
    #add up the pit stop penalties
    total_time+=pit_pen_calculator(strategy,max_lap=max_lap,track=track)
    return total_time
test_strat=[(15, 42), ('Medium', 'Medium', 'Hard')]
print(strategy_to_time2(test_strat, model_params))
#%%
def strategy_to_laps(stops,tyres,N_lap):
    lap_df=pd.DataFrame()
    lap_list=np.linspace(1,N_lap,num=N_lap,dtype=int)
    stops=np.asarray(stops)
    stintlap=[]
    stintnumber=[]
    tyre=[]
    lapofstint=0
    for lap in lap_list:
        stintnum=1
        lapofstint+=1
        for stoplap in stops:
            if lap > stoplap:
                stintnum+=1                
        if lap in stops+1:
            lapofstint=1
        stintlap.append(lapofstint)
        stintnumber.append(stintnum)
        tyreused=tyres[stintnum-1]
        tyre.append(tyreused)    
    lap_df['lap']=lap_list
    lap_df['stintnumber']=stintnumber
    lap_df['stintlap']=stintlap
    lap_df['tyre']=tyre
    max_laps=[]
    stint_group=lap_df.groupby(['stintnumber'])
    for stint, stintdf in stint_group:
        msl=stintdf.stintlap.max()
        max_lapd=[msl for i in range(len(stintdf))]
        max_laps.extend(max_lapd)
   # stint_group=stint_group.assign(stint_max_lap=stint_group.stintlap.max())
    lap_df['stint_max_laps']=max_laps
    return lap_df


def laps_to_time(strategy,model,model_params,plot=False,**kwargs):
    label=kwargs.get('label','best strategy model')
    shape=kwargs.get('shape','o')
    nstop=len(strategy[strategy['stintlap']==1])-1
    total_time=0
    times=[]
    laps=strategy['lap']
    stintlaps=strategy['stintlap']
    tyres=strategy['tyre']
    for lap in range(len(laps)):
        time=model(laps[lap],stintlaps[lap],tyres[lap],model_params,len(strategy))
        total_time+=time
        times.append(time)  
    total_time+=nstop*pittimes.loc[modeler3.circuit].values[0] #median pit stop time
    if plot==True:
        plt.scatter(laps.values,times,marker=shape,label=label)
    mintime=min(times)
    return total_time,mintime


def laps_to_time2(strategy,model,model_params,strat,plot=False,**kwargs):
    label=kwargs.get('label','best strategy model')
    shape=kwargs.get('shape','o')
    size=kwargs.get('size',20)
    color=kwargs.get('color',None)
    total_time=0
    times=[]
    laps=strategy['lap']
    stintlaps=strategy['stintlap']
    max_laps=strategy['stint_max_laps']
    tyres=strategy['tyre']
    for lap in range(len(laps)):
        time=model(stintlaps[lap],stintlaps[lap],tyres[lap],model_params,max_laps[lap])
        total_time+=time
        times.append(time)  
    total_time+=pit_pen_calculator(strat,max_lap=N_laps,track=track) #median pit stop time
    if plot==True:
        if shape=='line':
            plt.plot(laps.values,times,label=label)
        elif color!=None:
            plt.scatter(laps.values,times,marker=shape,color=color,s=size,label=label)
        else:
            plt.scatter(laps.values,times,marker=shape,label=label)
    mintime=min(times)
    return total_time,mintime
#%%
    
def optimize_strategy(N_lap,min_stop,max_stop,model,model_params,tyre_options,**kwargs):
    first_stint=kwargs.get('first_stint',None)
    close_cut=kwargs.get('close_cut',30)
    best_time=1000000
    close_times=[]
    close_strategy=[]
    for n_stop in range(min_stop,max_stop+1):
        print('exploring {} stop strategy'.format(n_stop))
        strategy_list=list_options(N_lap=N_lap, N_stop=n_stop,first_stint=first_stint)
    
        for strategy in tqdm(strategy_list,position=0,leave=True):
            model_time=strategy_to_time2(strategy, model_params,N_lap)
            if model_time < best_time:
                best_time=model_time
                best_strategy=strategy
            elif model_time < best_time+close_cut:
                close_times.append(model_time)
                close_strategy.append(strategy)
    close_times=pd.DataFrame(list(zip(close_times, close_strategy)),columns=['time','strategy'])  
    close_times=close_times[close_times['time'] < best_time+close_cut]
    close_times=close_times.sort_values(by=['time'])
    #laps_to_time(strategy_to_laps(best_strategy[0], best_strategy[1], N_lap=N_lap), model, model_params,plot=True)         
    return best_strategy, best_time, close_times

#%%
best_strat, best_time, close_times=optimize_strategy(N_lap=N_laps, min_stop=min_stop,max_stop=Max_stop, model=lap_models.tyre_model, model_params=model_params, tyre_options=tyre_options, first_stint=first_stint,close_cut=10)
print("quickest_strategy {}".format(best_strat))
#%%
if Robust_stuff==False:
    fastest_lap=10000
    print("found {} close times, checking for fasterst lap".format(len(close_times)))
    for strat in close_times.strategy:
        totalt,sfastest_lap=laps_to_time2(strategy_to_laps(strat[0], strat[1], N_lap=N_laps),strat=strat, model=lap_models.tyre_model, model_params=model_params,plot=False)
        if sfastest_lap<fastest_lap:
            fastest_lap=sfastest_lap
            quick_lap_strat=strat
    
    print("quickest_lap_strategy {}, fast lap:{}".format(quick_lap_strat,fastest_lap))
#%%
best_nf=[(19, 29, 48), ('Medium', 'Hard', 'Medium', 'Medium')]
title2='{}, {}, {}'.format(modeler3.driver.capitalize(),modeler3.circuit.capitalize(),modeler3.year)
fig,ax = plt.subplots()
    #for loop adds to the figure by looping over each stint 
# for k,d in modeler3.datain.groupby(['tyre']):
#     ax.scatter(d['lap'], d['time'], label='lap times, tyre = {}'.format(k))
#laps_to_time2(strategy_to_laps(best_nf[0], best_nf[1], N_lap=N_laps),strat=best_strat, model=lap_models.tyre_model, model_params=model_params,plot=True,label="best strategy no refuelling",color='r',size=30 ,shape='x')
laps_to_time2(strategy_to_laps(best_strat[0], best_strat[1], N_lap=N_laps),strat=best_strat, model=lap_models.tyre_model, model_params=model_params,plot=True,color='yellowgreen' ,label="best strategy with refuelling")
if Robust_stuff==False:
    laps_to_time2(strategy_to_laps(quick_lap_strat[0], quick_lap_strat[1], N_lap=N_laps),strat=quick_lap_strat ,model=lap_models.tyre_model, model_params=model_params,plot=True,color='steelblue',label="strategy with quick lap")
title='Refuelling Strategies\n{}, {}, {}'.format(modeler3.driver.capitalize(),modeler3.circuit.capitalize(),modeler3.year)
plt.legend()
plt.xlabel('Lap')
plt.ylabel('Lap-time(s)')
plt.title(title)
plt.show()

fig2,ax2 = plt.subplots()
# for k,d in modeler3.datain.groupby(['tyre']):
#     ax2.scatter(d['lap'], d['time'], label='lap times, tyre = {}'.format(k))
laps_to_time(strategy_to_laps(best_strat[0], best_strat[1], N_lap=N_laps),strat=best_strat, model=lap_models.tyre_model, model_params=model_params,plot=True,color='r',size=30,shape='x',label="best strategy, without refuelling")
laps_to_time2(strategy_to_laps(best_strat[0], best_strat[1], N_lap=N_laps),strat=best_strat, model=lap_models.tyre_model, model_params=model_params,plot=True,color='yellowgreen' ,label="best strategy, with refuelling")    

title='With and Without Refuelling Comparison \n{}, {}, {}'.format(modeler3.driver.capitalize(),modeler3.circuit.capitalize(),modeler3.year)
plt.legend()
plt.xlabel('Lap')
plt.ylabel('Lap-time(s)')
plt.title(title)
#%%
# comparing optimal strategy to the actual performance 
#gonna have to change this if I have many drivers in my dataset
actual_race_time=modeler3.datain.time.sum()+modeler3.dataout.time.sum()
pred_time=strategy_to_time2(modeler3.used_strat , model_params=model_params,max_lap=N_laps)
if Robust_stuff==False:
   quick_lap_time=strategy_to_time2(quick_lap_strat , model_params=model_params,max_lap=N_laps)
   print('optimised strategy (refuelling) predicted time : {} \n actual race time: {} \n predicted time of actual strategy: {} \n time of strategy with quick lap (refuelling):{}'.format(best_time,actual_race_time,pred_time,quick_lap_time))
print(strategy_to_time2(best_nf , model_params=model_params,max_lap=N_laps))

if Robust_stuff==True :
    strat_star=[(18, 32, 49), ('Medium', 'Hard', 'Medium', 'Medium')]
    star_time=strategy_to_time2(strat_star, model_params=model_params,max_lap=N_laps)
    print('optimised strategy predicted time : {} \n actual race time: {} \n time if using strat_star: {}'.format(best_time,actual_race_time,star_time))
    print(star_time-best_time)
    
if savefig==True:
    fig.savefig(photodir+title2+'refuel strat max stop {}.pdf'.format(Max_stop))
    fig2.savefig(photodir+title2+'refuel comparison max stop {}.pdf'.format(Max_stop))
