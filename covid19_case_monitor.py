#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
'''
Program to monitor COVID-19 "Confirmed", "Discharged" & "Active" Case Histories,

Required Files:
  ./Cases_Confirmed.txt    it store --> case no.  ,  dd/mm/yyyy
  ./Cases_Discharged.txt   it store --> dd/mm/yyyy,  case nos.
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.animation as animation
import numpy as np
import math
from datetime import datetime, timedelta
from pathlib import Path
from operator import methodcaller

__author__    = "Samuel Chia and Julian Chia"
__copyright__ = "Copyright Feb 2020"
__email__     = "julianchiayh@gmail.com"


def round_up_to_even(f):
    return math.ceil(f / 2.) * 2


def read_data( source ):
    '''Function to read in data from .txt file, "source" must be a pathlib.Path object.'''
    with source.open() as f:
      lines = f.readlines()
    return lines


def strip_split( string, chars=None, sep='\t', maxsplit=-1):
    a = string.strip( chars )
    if sep in a:
        return a.split( sep, maxsplit )
    else:
        return a.split( None, maxsplit )
    

def reformat_confirmed_case_data( indata, source ):
    # Convert "indata" to "outdata", a dictionary {case number : yyyy-mm-dd}.
    indata = list( filter(lambda x: x != '\n' , indata) )  #remove empty line(s)
    indata= [ strip_split(i) for i in indata[1:] ]         #get [ [case no., yyyy-mm-dd], [...], ... ]
    outdata = {}
    for line in indata:
        try:
            date = datetime.strptime(line[1],"%d/%m/%Y").strftime('%Y-%m-%d')
        except IndexError:
            print( f'\n    WARNING!!! Missing date in file "{source}" at line {line}. This data is excluded.\n' )
        else:
            outdata[line[0]] = date
    return outdata


def reformat_discharged_case_data( indata, source ):
    # Convert "indata" to "outdata"; a dictionary {yyyy-mm-dd : case numbers}.
    # Get "case_list"; a list of all discharged cases.
    indata = list( filter(lambda x: x != '\n' , indata) )  #remove empty line(s)
    indata= [ strip_split(i) for i in indata[1:] ]         #get [ [case no., yyyy-mm-dd], [...], ... ]
    outdata={}
    case_list=[]
    for line in indata:
        try:
            date = datetime.strptime(line[0], "%d/%m/%Y").strftime('%Y-%m-%d')
        except ValueError as exc:
            if "does not match format" in str(exc):
                print( f'\n    WARNING!!! Missing date in file "{source}" at line {line}. This data is excluded.\n' )
                pass
        else:
            if len(line) == 2:
                cases = strip_split( line[1], sep=',') #cases = line[1].split(',')
                outdata[date] = cases
                case_list.extend( cases )
            else:
                print( f'\n    WARNING!!! Missing case number in file "{source}" at line {line}. This data is excluded.\n' )
                
    return outdata, case_list


def get_time_axis( data1, data2 ):
    '''
    Get the time-axis to create the stem plot.
    It is will have a regulized time interval of 1 day.

    "data" - a dictornary that stores the required date info as it's values.
    '''
    all_dates = set(data1.values()).union( set(data2.keys()) )
    dstart = datetime.strptime( min( all_dates ), "%Y-%m-%d")
    dend = datetime.strptime( max( all_dates ), "%Y-%m-%d") + timedelta(days=1)
    delta = timedelta(days=1)
    time_axis_md = mdates.drange( dstart, dend, delta )
    time_axis_py = mdates.num2date( time_axis_md, tz=None )
    return time_axis_py


def get_confirmed_cases( time_axis, data ):
    # Collate data's y-axis for each date, i.e. history
    history={}
    dates = list(data.values())
    for i in time_axis:
        cases=[]
        for case, date in data.items():
            if i.strftime('%Y-%m-%d') == date:
                cases.append(case)
        #print( i, cases)
        history[i.strftime('%b-%d')] = cases 
    #print( f'\nhistory = {history}')
    return history


def get_discharged_cases( time_axis, data ):
    dhistory={ i.strftime('%b-%d'):[] for i in time_axis }
    for date, case in list(data.items()):
        date = datetime.strptime(date, "%Y-%m-%d").strftime('%b-%d')
        dhistory[date] = case
    return dhistory


##################
#### GET DATA ####
##################
source1 = Path('./Cases_Confirmed.txt')
confirmed_data = read_data( source1 )

source2 = Path('./Cases_Discharged.txt')
discharged_data = read_data( source2 )

######################
#### PROCESS DATA ####
######################
confirmed_data = reformat_confirmed_case_data( confirmed_data, source1 )

discharged_data, discharged_case_num = reformat_discharged_case_data( discharged_data, source2 )

time_axis = get_time_axis( confirmed_data, discharged_data )
                                                          
ccase_history = get_confirmed_cases( time_axis, confirmed_data )
max_daily_confirmed_cases = round_up_to_even( max( [len(i) for i in ccase_history.values()] ) )

dcase_history  = get_discharged_cases( time_axis, discharged_data )
max_daily_discharged_cases = -max( [len(i) for i in dcase_history.values()] )

######################
#### PRESENT DATA ####
######################
# Create figure and plot a stem plot with the date
fig, ax = plt.subplots(figsize= (12,6.1), constrained_layout=True)
ax.set(title="Singapore COVID-19 Cases in Year 2020 (with Case No)." )
ax.title.set_fontweight('bold')
for spine in ["top", "right"]:  # remove top and right spines
    ax.spines[spine].set_visible(False)

# format x-axis and y-axis
ax.get_xaxis().set_label_text(label='Days', fontweight='bold')
ax.get_yaxis().set_label_text(label='No. of Cases', fontweight='bold')
ax.set_ylim( [ max_daily_discharged_cases - 1, max_daily_confirmed_cases + 1 ] )
ax.yaxis.set_major_locator( ticker.MultipleLocator(2) )
ax.yaxis.set_minor_locator( ticker.MultipleLocator(1) )

# format ticks and grid
plt.setp( ax.get_xticklabels(), rotation=50, ha='right' )
ax.grid( linestyle=':',)

# Stem Plot values
clabels=list( ccase_history.values() )  # For annotation 
cyy = [ len(i) for i in clabels ]       # y-axis
cxx = list( ccase_history.keys() )      # x-axis

dlabels=list( dcase_history.values() ) # For annotation 
dyy = [ -len(i) for i in dlabels ]     # y-axis
dxx = list( dcase_history.keys() )     # x-axis

# Initialise stem plot parameters
cyyo = [ 0 for i in cyy ]
dyyo = [ 0 for i in dyy ]
clabelso = [ [] for i in clabels ]
dlabelso = [ [] for i in dlabels ]

# Draw Confirmed cases stem plot
cmarkerline, cstemline, cbaseline = ax.stem(
    cxx, cyyo, linefmt="-", basefmt="k-", label='Confirmed Cases', use_line_collection=True)
plt.setp(cmarkerline, marker="None" )
plt.setp(cstemline, color="#0000FF", alpha=1.0)

# Draw Discharged cases stem plot
dmarkerline, dstemline, dbaseline = ax.stem(
    dxx, dyyo, linefmt="-", basefmt="k-", label='Discharged Cases', use_line_collection=True)
plt.setp(dmarkerline, marker="None" )
plt.setp(dstemline, color="#00FF00" )

# Draw Legend
plt.legend( loc='upper left' )

# Draw Authors
textstr = 'Created by Samuel Chia & Julian Chia, February 2020.'
props = dict( boxstyle='round', facecolor='wheat', edgecolor='wheat', alpha=0.5)
author = ax.text( 0.05, 0.045, textstr, transform=ax.transAxes, fontsize=10,
                  va='center', ha='left', bbox=props )

# Draw Summary above Authors
sbody = f'Confirmed:      \nDischarged: \nActive:'
sbprops = dict( boxstyle='sawtooth,pad=0.5', fc='#FF6F61', ec='#FF6F61', alpha=0.8)
summary_body= ax.text( 0.052, 0.2, sbody, transform=ax.transAxes,
                       fontsize=12, weight='bold', color='white',
                       va='center', ha='left', bbox=sbprops )

######################
#### ANIMATE DATA ####
######################
def get_stemplot_values_for_frame( frame, source ):
    final = []
    for i, x in enumerate(source):
        if i <= frame:
            final.append(x)
        else:
            if type(x) is list:
                final.append([])
            else:
                final.append(0)
    return final


def get_annotation_values_for_frame( frame, source ):
    final = []
    for i, x in enumerate(source):
        if i <= frame:
            final.append(x)
    return final
     

def update(frame, timeline, cyy, dyy, clabels, dlabels, ann_list, stem_list, summary_body):
    print( f'\nProcess Frame:{frame}')
    #Remove previous frame stem plot lines and annotations
    for i in stem_list:
        for j in i:
            j.remove()
    stem_list[:] = []
    for i in ann_list:
        i.remove()
    ann_list[:] = []

    #Get current frame stem plot lines and annotations values
    cy = get_stemplot_values_for_frame( frame, cyy )
    dy = get_stemplot_values_for_frame( frame, dyy )
    clabs = get_annotation_values_for_frame( frame, clabels )
    dlabs = get_annotation_values_for_frame( frame, dlabels )

    #Get current frame confirmed case numbers
    ccase_nums = []
    for i in clabs:
        if i != []:
            for j in i:
                ccase_nums.append(int(j))

    #Get current frame discharge case numbers
    dcase_nums = []
    for i in dlabs:
        if i != []:
            for j in i:
                dcase_nums.append(int(j))

    # Net number of Active Confirmed cases
    netcase = len(ccase_nums) - len(dcase_nums)
    
    # Color variables & Annotation box properties
    color_c1 = "#0000FF"
    color_c2 = "#80ced6"
    color_d  = "#00FF00"
    color_cd = "#00FF00"
    bbox_cprops  = dict( boxstyle='round,pad=0.2', fc='#80ced6', alpha=1.0, ec=color_c1 )
    bbox_dprops  = dict( boxstyle='circle,pad=0.2', fc=color_d, alpha=0.0, ec=color_d )
    bbox_cdprops = dict( boxstyle='circle,pad=0.2', fc=color_cd, alpha=1.0, ec=color_cd )

    # Draw Confirmed cases stem plot
    cmarkerline, cstemline, cbaseline = ax.stem(
        timeline, cy, linefmt="-", basefmt="k-", label='Confirmed Cases',
        use_line_collection=True )
    plt.setp( cmarkerline, marker="None" )
    plt.setp( cstemline, color=color_c1, alpha=1.0)

    # Draw Discharged cases stem plot
    dmarkerline, dstemline, dbaseline = ax.stem(
        timeline, dy, linefmt="-", basefmt="k-", label='Discharged Cases',
        use_line_collection=True )
    plt.setp( dmarkerline, marker="None" )
    plt.setp( dstemline, color=color_d )
    stem_list.append( (cmarkerline, cstemline, cbaseline, dmarkerline, dstemline, dbaseline) )

    # Annotate Confirmed Cases    
    for i, cases in enumerate(clabs):
        count=1
        for case in cases:
            if int(case) in dcase_nums:
                # Confirmed and Discharged cases
                ann = ax.annotate(
                    f'{case}', xy=(timeline[i], count), xycoords='data',
                    rotation=0, ha='center', va='center', bbox=bbox_cdprops )
            else:
                # Confirmed cases
                ann = ax.annotate(
                    f'{case}', xy=(timeline[i], count), xycoords='data',
                    rotation=0, ha='center', va='center', bbox=bbox_cprops )
            ann_list.append(ann)
            count += 1

    # Annotate Discharged Cases
    for i, cases in enumerate(dlabs):
        count=1
        for case in cases:
            ann_d = ax.annotate(
                f'{case}', xy=(timeline[i], -count), xytext=(-2, 0), xycoords='data',
                textcoords='offset points', color=color_d, rotation=0,
                ha='right', va='center', bbox=bbox_dprops )
            ann_list.append(ann_d)
            count += 1

    # Update Summary
    sbody = f'Confirmed:   {len(ccase_nums)}\nDischarged:  {len(dcase_nums)}\nActive:          {netcase} '
    summary_body.set_text(sbody)


ann_list = []
stem_list = []
a = max(time_axis)
filename = f'covid19_{str(a.year)}_{str(a.month)}_{str(a.day)}.gif'
ani = animation.FuncAnimation(
    fig, update, fargs=(cxx, cyy, dyy, clabels, dlabels, ann_list, stem_list, summary_body),
    frames=range(0, len(cxx), 1), interval=1000, repeat=False, repeat_delay=10000,
    )
ani.save( filename, dpi=80, writer='imagemagick' )
print( f'\nCreated {Path.cwd()}/{filename}.')
plt.show()


