# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 11:16:33 2020

Ice marginal lake certainty analysis

@author: HOW
"""

import numpy as np
import os, sys
#import pandas as pd
import geopandas as gp
from pathlib import Path
#from osgeo import osr, ogr
from shapely.geometry import Point, Polygon, MultiPolygon

#------------------------------------------------------------------------------

#Define input file and location 
workspace = Path(r'P:/B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland/B71-05 '
            +'Product validation and user assessment/certainty_recalculation')

#Define output file location and create if doesn't exist
output = Path('P:\B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland\B71-05 '
             +'Product validation and user assessment\certainty_recalculation'
             + '\output')
if os.path.exists(str(output)) is False:
    os.makedirs(str(output))


#------------------------------------------------------------------------------

def findOverlaps(ufile1, ufile2, usrnames, S1, S2, adem, all_file, geomid=True, threshold=10.0):
    '''Find overlaps between user-defined points and detected polygons from
    S1, S2, ArcticDEM, and an emalgamation of all three.
    
    Variables
    usr (list):                 List containing file names of user-defined
                                points
    usrnames (list):            List of user names (for print out)
    S1 (str):                   File location of S1-detected polygons
    S2 (str):                   File location of S2-detected polygons
    adem (str):                 File location of adem-detected polygons
    all_file (str):             File location of all (S1, S2, adem) polygons
    
    Returns
    usr_count (list):           List of values indicating overlaps between
                                users and lake detections:
                                1. User vs. S1; 2. User vs. S2; 3. User vs. 
                                ADEM; 4. User vs. all lakes
    '''
    #Load all shapefiles as geodatabases
    print('Loading geodatabases...')
    usr1 = gp.read_file(str(ufile1))
    usr2 = gp.read_file(str(ufile2))
    #usr3 = gp.read_file(str(ufile3))
    S1 = gp.read_file(str(S1))
    S2 = gp.read_file(str(S2))
    adem = gp.read_file(str(adem))
    alls = gp.read_file(str(all_file))
        
    #Look for overlapping points and polygons
    print('Determining overlaps...')
    usr_count=[]
    usr_total=[]
    for usr in [usr1, usr2]:
        usr_out=[]          
        usr_pts=[]
        
        if geomid is False:
            usr_total.append(len(usr.index))                                              
            for i,v in usr.iterrows():                              #Iterate over pts
                geom = Point(v['geometry'])
                usr_pts.append(geom)
        else:                                               
            for i,v in usr.iterrows():                              #Iterate over pts
                geomid = int(v['id'])
                if geomid==1:
                    geom = Point(v['geometry'])
                    usr_pts.append(geom)
            usr_total.append(len(usr_pts))
        
        for polygons in [S1, S2, adem, alls]:  
            count=0
            for i,v in polygons.iterrows():                     #Iterate over polys    
                try:                                            #Try create polygon
                    geom = Polygon(v['geometry'])
                except:                                         #Else create multipolygon
                    geom = MultiPolygon(v['geometry']) 
            
                for pt in range(len(usr_pts)):        
        
                    if geom.contains(usr_pts[pt]) == True:          #If pt coincides with polygon
                        count=count+1                    
                    elif usr_pts[pt].distance(geom) < threshold:    #If pt is within threshold   
                        count=count+1
            usr_out.append(count) 
        usr_count.append(usr_out)
                
    for u in range(len(usr_count)):
        print('\n' + str(usrnames[u]) + ' count: ' + str(usr_total[u]))
        print(str(usrnames[u]) + ' vs. S1: ' + str(usr_count[u][0]))                    
        print(str(usrnames[u]) + ' vs. S2: ' + str(usr_count[u][1]))
        print(str(usrnames[u]) + ' vs. ADEM: ' + str(usr_count[u][2]))
        print(str(usrnames[u]) + ' vs. all lakes: ' + str(usr_count[u][3]))
    
    return usr_count, usr_total


def calcCertainty(usr_count, usr_total):

#    print('\nAverage user count: ' + str((np.mean(usr_total))))
#    print('Average rounded user count: ' + str(round(np.mean(usr_total))))
#    usr_aver = round(np.mean(usr_total))
    
    certainty=[]
    count=1
    
    for u in range(len(usr_count)):
        print('\nUser ' + str(count) + ' certainty analysis')

        missed=[]
        weight=[]
        
        S1 = (usr_total[u]-usr_count[u][0])/usr_total[u]
        S2 = (usr_total[u]-usr_count[u][1])/usr_total[u]
        ADEM = (usr_total[u]-usr_count[u][2])/usr_total[u]
        alllakes = (usr_total[u]-usr_count[u][3])/usr_total[u]
        missed.append([S1,S2,ADEM,alllakes])

        print('S1 % missed: ' + str(round(S1*100)) + '%')
        print('S2 % missed: ' + str(round(S2*100)) + '%')
        print('ADEM % missed: ' + str(round(ADEM*100)) + '%')  
        print('Total missed: ' + str(round(alllakes*100)) + '%')
        
        S1_weight = ((S1+S2+ADEM)-S1)/(S1+S2+ADEM)
        S2_weight = ((S1+S2+ADEM)-S2)/(S1+S2+ADEM)
        ADEM_weight = ((S1+S2+ADEM)-ADEM)/(S1+S2+ADEM)
        weight.append([S1_weight, S2_weight, ADEM_weight])

        print('S1 weighting: ' + str(S1_weight))
        print('S2 weighting: ' + str(S2_weight))
        print('ADEM weighting: ' + str(ADEM_weight))
        
        certainty.append([missed, weight])
        count=count+1
    
    return certainty      

#------------------------------------------------------------------------------    
#Tile 22WES (KNS area)
geom=True
threshold=10.0

print('\n\n22WES tile detection')
        
#Define user-detected files
usr1_file = workspace.joinpath('22WES/how_T22WES_01-08-2017_reproj.shp')
usr2_file = workspace.joinpath('22WES/ame_T22WES_01-08-2017_reproj.shp')
usr3_file = None
usr_name=['HOW','AME']

#Define raw lake detection output files
S1_file = workspace.joinpath('22WES/S1_raw2_reproj.shp')
S2_file = workspace.joinpath('22WES/S2_raw2_reproj_dissolved2.shp')
adem_file = workspace.joinpath('22WES/ADEM_raw2_reproj.shp')
all_file = workspace.joinpath('22WES/S1_S2_ADEM_raw2_reproj_dissolve2.shp')
 
#Find overlaps   
count, total = findOverlaps(usr1_file, usr2_file, usr_name, S1_file, S2_file, 
                            adem_file, all_file, geom, threshold)    

#Calculate certainty score
c22WES = calcCertainty(count, total)

#------------------------------------------------------------------------------
#Tile 26XNQ    
print('\n\n26XNQ tile detection')

#Define user-detected files
usr1_file = workspace.joinpath('26XNQ/how_T26XNQ_11-08-2017_reproj.shp')
usr2_file = workspace.joinpath('26XNQ/ame_T26XNQ_11-08-2017_reproj.shp')
usr3_file = None
usr_name=['HOW','AME']

#Define raw lake detection output files
S1_file = workspace.joinpath('26XNQ/S1_26XNQ.shp')
S2_file = workspace.joinpath('26XNQ/S2_26XNQ_dissolved.shp')
adem_file = workspace.joinpath('26XNQ/ADEM_26XNQ_reproj.shp')
all_file = workspace.joinpath('26XNQ/S1_S2_ADEM_26XNQ_dissolved2.shp')
 
#Find overlaps   
count, total = findOverlaps(usr1_file, usr2_file, usr_name, S1_file, S2_file, 
                            adem_file, all_file, geom, threshold) 

#Calculate certainty score
c26XNQ = calcCertainty(count, total)

#------------------------------------------------------------------------------    
#Tile 23VLH    
print('\n\n23VLH tile detection')

#Define user-detected files
usr1_file = workspace.joinpath('23VLH/how_T23VLH_13-09-2017_reproj.shp')
usr2_file = workspace.joinpath('23VLH/ame_T23VLH_13-09-2017_reproj.shp')
usr3_file = None
usr_name=['HOW','AME']

#Define raw lake detection output files
S1_file = workspace.joinpath('23VLH/S1_23VLH.shp')
S2_file = workspace.joinpath('23VLH/S2_23VLH_reproj_dissolved.shp')
adem_file = workspace.joinpath('23VLH/ADEM_23VLH_reproj.shp')
all_file = workspace.joinpath('23VLH/S1_S2_ADEM_23VLH_dissolved.shp')
 
#Find overlaps   
count, total = findOverlaps(usr1_file, usr2_file, usr_name, S1_file, S2_file, 
                            adem_file, all_file, geom, threshold) 

#Calculate certainty score
c23VLH = calcCertainty(count, total)

#------------------------------------------------------------------------------   
#Tile 21XWB
print('\n\n21XWB tile detection')

#Define user-detected files
usr1_file = workspace.joinpath('21XWB/how_T21XWB_21-08-2017_reproj.shp')
usr2_file = workspace.joinpath('21XWB/ame_T21XWB_21-08-2017_reproj.shp')
usr3_file = None
usr_name=['HOW','AME']

#Define raw lake detection output files
S1_file = workspace.joinpath('21XWB/S1_21XWB.shp')
S2_file = workspace.joinpath('21XWB/S2_21XWB_dissolved.shp')
adem_file = workspace.joinpath('21XWB/ADEM_21XWB_reproj.shp')
all_file = workspace.joinpath('21XWB/S1_S2_ADEM_21XWB_dissolved.shp')
 
#Find overlaps   
count, total = findOverlaps(usr1_file, usr2_file, usr_name, S1_file, S2_file, 
                            adem_file, all_file, geom, threshold) 

#Calculate certainty score
c21XWB = calcCertainty(count, total)


#------------------------------------------------------------------------------
#Calculate average weighting
#c22WES, c26XNQ, c23VLH, c21XWB
s1Av=[]
s2Av=[]
adAv=[]
total_missed=[]

for i in [c22WES, c26XNQ, c23VLH, c21XWB]:
    s1Av.append(i[0][1][0][0])
    s2Av.append(i[0][1][0][1])
    adAv.append(i[0][1][0][2])
    total_missed.append(i[0][0][0][3])
print('\nS1 average weighting: ' +str(np.average(s1Av)))
print('S2 average weighting: ' +str(np.average(s2Av)))
print('AD average weighting: ' +str(np.average(adAv)))  

s1Av=np.average(s1Av)
s2Av=np.average(s2Av)
adAv=np.average(adAv)
s1AvW=s1Av/(s1Av+s2Av+adAv)
s2AvW=s2Av/(s1Av+s2Av+adAv)
adAvW=adAv/(s1Av+s2Av+adAv)
print('\nS1 normalised weighting: ' +str(s1AvW))
print('S2 normalised weighting: ' +str(s2AvW))
print('AD normalised weighting: ' +str(adAvW))  


print('\nTotal average certainty: ' + str((np.average(total_missed))*100) + '%')
print('Plus-minus average certainty: ' + str(((np.average(total_missed))*100)/2) + '%')

#------------------------------------------------------------------------------
print('\n\nFinished') 