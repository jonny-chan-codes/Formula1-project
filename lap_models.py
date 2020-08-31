# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 16:46:59 2020

@author: jxnny
"""

def fuel_model(lap,stintlap,tyre,model_params,max_lap):
    F,t_base=model_params
    return(F*(max_lap-lap)+t_base)

def simple_tyre_model(lap,stintlap,tyre,model_params,max_lap):
    F,T,T2,t_base=model_params
    return(F*(max_lap-lap) +T*stintlap +T2*(stintlap**2) +t_base)

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

def tyre_model(lap,stintlap,tyre,model_params,max_lap):
    F,Ts,Ts2,Tsb,Tss,Tss2,Tssb,Tus,Tus2,Tusb,Tm,Tm2,Tmb,Th,Th2,Thb,t_base=model_params
# include flag vairable for the tyre choice   
    f_soft,f_supersoft,f_ultrasoft,f_medium,f_hard=tyre_flags(tyre)
    tsoft=(Ts*stintlap+Ts2*(stintlap**2)+Tsb)*f_soft
    tsupersoft=(Tss*stintlap+Tss2*(stintlap**2)+Tssb)*f_supersoft
    tultrasoft=(Tus*stintlap+Tus2*(stintlap**2)+Tusb)*f_ultrasoft
    tmedium=(Tm*stintlap+Tm2*(stintlap**2)+Tmb)*f_medium
    thard=(Th*stintlap+Th2*(stintlap**2)+Thb)*f_hard
    tfuel=(F*(max_lap-lap))
    return (t_base+tfuel+tsoft+tsupersoft+tultrasoft+tmedium+thard)

