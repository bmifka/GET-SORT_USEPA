#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""----------------------------------------------------------------------------
This program analyzes the US-EPA air quality or meteo scalar files in
combination with Wind speed and direction files downloaded using the get_EPA_files
script. The result of analysis is the list of stations and instruments with
mutual Wind and specified Variable data (e.g. PM10) available for each year
in a defined period. This is useful for determining the period in which the
time series of wind and scalar data is available at the station of interest.
The list is stored in the output file (e.g. Analyze_EPA_Files.csv).


The user defines the: 1) start and end year
                  	  2) path to directory with files
                  	  3) variable prefixes in file names (i.e.for PM10_1991.csv,
                                                  	prefix is 'PM10')
              	      4) output file name
    
The program finds and makes a list of all stations and instruments
(identified with POC number) and stores the list in output csv file.

Usage:
Download US EPA files using get_EPA_files and edit SET OPTIONS:
   
#******************************************************************************
#                          SET OPTIONS: 
#******************************************************************************
#--input
year_s            = 1991            
year_e            = 1995            
files_dir         = 'EPA_FILES/'         
fname_prefixW     = 'WIND'  
fname_prefixV     = 'PM10'            
# Specify the file path
outFile_path      = 'Analyze_EPA_Files.csv' 
   
 
******************************************************************************* 
*                       HOW TO INTERPRET output file
*******************************************************************************
The Columns are:
    Station Identifiers   : State Code,County Code, Site Number
    Instrument Identifiers: POCW (for Wind) and POC+variable prefix for Variable 
                            (e.g. POCPM10)
    Station Coordinates   : Lat and Lon
    Station & County Name : Station Name and County Name
    Available Data Columns: 0 if not available, year if available       


Created on Wed May 22 22:00:20 2024

@author: boris mifka (boris.mifka@phy.uniri.hr)
"""
import os
import pandas as pd
import numpy as np


#--this clears the console if IDE is used
def clear_console():
    # Check if the operating system is Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # Check if the operating system is Unix/Linux/Mac
    elif os.name == 'posix':
        _ = os.system('clear')
clear_console()

#******************************************************************************
#                          SET OPTIONS: 
#******************************************************************************
#--input
year_s            = 1991            
year_e            = 1995            
files_dir         = 'EPA_FILES/'         
fname_prefixW     = 'WIND'  
fname_prefixV     = 'PM10'            
# Specify the file path
outFile_path = 'Analyze_EPA_Files.csv'


#******************************************************************************
#                         DO NOT EDIT THIS PART...
#******************************************************************************
years=np.arange(year_s, year_e + 1)
NoYears = len(years)
STATION_LST=[]
STATION_ARRAY=np.empty((0,5),dtype=int)
META_LST=[]
META_ARRAY=np.empty((0,4),dtype=int)

#---trazenje POCova
#POC_WS = []
#POC_PM = []

#--main loop iterating trought the files
for k in range(len(years)):
    file_path = os.path.join(files_dir, f'{fname_prefixW}_{years[k]}.csv')
    #--read important columns for Wind
    WINDin    = pd.read_csv(file_path)
    WND       = WINDin["Sample Measurement"]
    WND_POC   = WINDin["POC"]
    WND_datep = WINDin["Date GMT"]
    WND_timep = WINDin["Time GMT"]
    WND_date  = WND_datep.to_numpy()
    WND_time  = WND_timep.to_numpy()
    ID_1      = WINDin["State Code"]
    ID_2      = WINDin["County Code"]
    ID_3      = WINDin["Site Num"]
    ID_W      = WINDin["Parameter Name"]
    
    #--index the rows with Wind Speed
    ID_WBS     = np.array(ID_W == 'Wind Speed - Resultant')
    #ID_WBD     = np.array(ID_W == 'Wind Direction - Resultant')
    ID_WBS     = ID_WBS.astype(int)
    #ID_WBD     = ID_WBD.astype(int)
    print(years[k])
    
    #--stack
    IDWs      = np.column_stack((ID_1,ID_2,ID_3))
    IDsS4     = np.column_stack((ID_1,ID_2,ID_3,ID_WBS))
    UW_S4     = np.unique(IDsS4, axis=0)
    UW,cnts   = np.unique(UW_S4[:,0:3], return_counts=True,  axis=0)
    
    #--Important - the list of all stations with wind data for k-th year 
    UW=UW[cnts!=1]
    
    #--UW is now a list which can be searched along with PM10...
    file_path = os.path.join(files_dir, f'{fname_prefixV}_{years[k]}.csv')
    #--read important columns for scalar variable
    VARin       = pd.read_csv(file_path)
    VAR         = VARin["Sample Measurement"]
    VAR_POC     = VARin["POC"]
    VAR_datep   = VARin["Date GMT"]
    VAR_timep   = VARin["Time GMT"]
    VAR_date    = VAR_datep.to_numpy()
    VAR_time    = VAR_timep.to_numpy()
    ID_1        = VARin["State Code"]
    ID_2        = VARin["County Code"]
    ID_3        = VARin["Site Num"]
    ID_W        = VARin["Parameter Name"]
    State_Name  = VARin["State Name"]
    County_Name = VARin["County Name"]
    Lat         = VARin["Latitude"]
    Lon         = VARin["Longitude"]
    
    #stack
    IDs     = np.column_stack((ID_1,ID_2,ID_3))
    IDs_POC = np.column_stack((IDs, VAR_POC))
    UV,ind  = np.unique(IDs, return_index=True, axis=0)
    Lat     = Lat[ind]; Lon = Lon[ind] #to moze jer je ista postaja
    State_Name   = State_Name[ind];
    County_Name  = County_Name[ind];
    
    
    #matching rows for k-th year
    MATCH_R         = np.array([np.any(np.all(row==UW,axis=1)) for row in UV])
    STATIONS        = UV[MATCH_R]  
    Lat             = (np.array(Lat[MATCH_R]))
    Lon             = (np.array(Lon[MATCH_R]))
    State_Name      = (np.array(State_Name[MATCH_R]))
    County_Name     = (np.array(County_Name[MATCH_R]))
   
    #---search for POCs (Wind Speed and Direction have same POC)
    POC_WSy = []
    POC_PMy = []
    
    for j in range(len(STATIONS)):
        MATCH_WS  = np.array(np.all(IDWs==STATIONS[j,:],axis=1))
        POC_WStmp = np.unique(WND_POC[MATCH_WS])
        POC_WSy.append(POC_WStmp)
        
    for j in range(len(STATIONS)):
        MATCH_VAR  = np.array(np.all(IDs==STATIONS[j,:],axis=1))
        POC_PMtmp = np.unique(VAR_POC[MATCH_VAR])
        POC_PMy.append(POC_PMtmp)
    
    STATION_POC_ARRAY=np.empty((0,5),dtype=int)
    META_POC_ARRAY=np.empty((0,4),dtype=int)
    STATION_POC=[]
    for k in range(len(STATIONS)):
        for i in range(len(POC_WSy[k])):
            for j in range(len(POC_PMy[k])):
                STATION_POC = np.hstack([STATIONS[k],POC_WSy[k][i],POC_PMy[k][j]])
                STATION_POC_ARRAY=np.vstack((STATION_POC_ARRAY,STATION_POC)) 
                META_POC = np.hstack((Lat[k],Lon[k],State_Name[k],County_Name[k]))
                META_POC_ARRAY=np.vstack((META_POC_ARRAY,META_POC))
                
 
    #--make station list
    STATION_LST.append(STATION_POC_ARRAY)
    #--companion METAList
    META_LST.append(META_POC_ARRAY)
    
    #--make station Array
    STATION_ARRAY = np.vstack((STATION_ARRAY,STATION_POC_ARRAY)) 
    META_ARRAY    = np.vstack((META_ARRAY,META_POC_ARRAY)) 
    
#--extract the list of stations
ALL_STATIONS,inds = np.unique(STATION_ARRAY,return_index=True, axis=0) #mozda bi tu mogo izdvojit POCs
ALL_META          = META_ARRAY[inds]

STATION_LST2   = []
STATION_ARRAY2 = np.zeros(NoYears,dtype=int)
#STATION_ARRAY2 = np.empty()
#STATION_ARRAY2[:] = np.nan
#raspon godina za svaku postaju

#--match the stations containing both Wind and scalar varible data
for i in range(len(ALL_STATIONS)):
    for j in range(NoYears):
        #print(years[j])
        MATCH_STAT   =  np.array([np.all(row==ALL_STATIONS[i]) for row in STATION_LST[j]])
        #print(MATCH_STAT)
        #print(np.sum(MATCH_STAT))
        if np.sum(MATCH_STAT)==1:
            STATION_ARRAY2[j]=years[j]
        else:
            STATION_ARRAY2[j]=0
    STATION_LST2.append(STATION_ARRAY2)
    STATION_ARRAY2=np.zeros(NoYears,dtype=int)
    
matrix           = np.column_stack((ALL_STATIONS,ALL_META,STATION_LST2))

# Initial array
strg = np.array(['State Code', 'County Code', 'Site Number','POCW','POC'+fname_prefixV, 'Lat', 'Lon', 'State Name', 'County Name'])

# Initialize strgRow with the contents of strg
strgRow = strg.copy()

# Append strgRow NoYears times
for k in range(NoYears):
    strgRow = np.append(strgRow, '')

print(strgRow)

combined_matrix  = np.row_stack((np.transpose(strgRow),matrix))

#--convert the combined matrix to a Pandas DataFrame
df = pd.DataFrame(combined_matrix)

#--writing data to the CSV file
df.to_csv(outFile_path, index=False, na_rep='')

print(f'Data has been written to {outFile_path}')