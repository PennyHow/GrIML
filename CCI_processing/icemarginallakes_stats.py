# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 10:27:57 2019

Statistical analysis on ice-marginal lakes (ESA)

@author: Penelope How
"""

import os
import numpy as np
import geopandas as gp
import matplotlib.pyplot as plt
from scipy import stats

#-----------------------   Define inputs and outputs   ------------------------

#Define input file and location 
workspace1 = 'P:/B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland/B71-04 Essential Climate Variable production/final lake products/'
workspace2 = 'D:/python_workspace/ice_marginal_lakes/'
file1 = workspace1 + 'glacier_cci_lakes_20200724.shp'
file2 = workspace1 + 'other products/GL_basin_areas.shp'
file3 = workspace1 + 'other products/GL_basin_perimeters.shp'

outtxt1 = workspace2 + 'generalstats4.csv'
outtxt2 = workspace2 + 'detailedstats4.csv'
outtxt3 = workspace2 + 'stats_for_alex.csv'

#-------------------------   Load as dataframe   ------------------------------
print('\nLoading geodataframes...')    

#Read file as geopandas index
geofile = gp.read_file(file1)
basinfile = gp.read_file(file2)
extfile = gp.read_file(file3)
agg_geofile = geofile.dissolve(by='LakeID')
#agg_geofile.to_file(workspace + '\gl_aggr_lakes2.shp')


#---------------   Get data from non-aggregated lake data  --------------------
print('\nRetrieving lake data...')

#Get data from columns
geofile = geofile.sort_values('DrainageBa')
geofile_id = geofile['LakeID'].tolist()                 #Get lake IDs
geofile_uncertain = geofile['Certainty'].tolist()       #Get lake uncertainty
geofile_source = geofile['Source'].tolist()             #Get lake source
geofile_basin = geofile['DrainageBa'].tolist()          #Get lake location
geofile_area = geofile['Area'].tolist() 
geofile_name = geofile['LakeName'].tolist() 
unique_name = set(geofile_name)
print(unique_name)
print(len(unique_name))

#Get unique values for basin area and satellite source 
uniquebasin = list(set(geofile_basin))
uniquesource = list(set(geofile_source))

#Get all lake data for basins
geofile_SW=[]
geofile_NE=[]
geofile_SE=[]
geofile_ICECAP=[]
geofile_CW=[]
geofile_NO=[]
geofile_NW=[]
label=['CW', 'ICE_CAP', 'NE', 'NO', 'NW', 'SE', 'SW']
geofile_arealist=[geofile_CW,geofile_ICECAP,geofile_NE,geofile_NO,geofile_NW,
                   geofile_SE,geofile_SW]

for i in range(len(geofile_basin)):
    for l in range(len(label)):
        if label[l] in geofile_basin[i]:
            geofile_arealist[l].append(geofile_area[i])

#-------------------   Get Greenland basin area data   ------------------------
print('\nRetrieving basin area data...')

#Get basin info        
basinfile.sort_values('SUBREGION1')
basinfile['area'] = basinfile['geometry'].area/10**6
basinfile['total_perimeter'] = basinfile['geometry'].length
basinfile.to_file(workspace2+'\gl_basin_withareaperimeter.shp')
                    
basinfile_area = basinfile['area'].tolist()  
basinfile_name = basinfile['SUBREGION1'].tolist()

print(basinfile_name)
print(basinfile_area)


#-------------   Get Greenland external ice margin perimeter data   -----------
print('\nRetrieving basin perimeter data...')

extfile=extfile.sort_values('MARGIN')          
extfile['LENGTH'] = extfile['geometry'].length/1000
perimfile_length = extfile['LENGTH'].tolist()  
perimfile_name = extfile['MARGIN'].tolist()

print(perimfile_name)
print(perimfile_length)


#-----------------   Get data from aggregated lake data   ---------------------
print('\nAggregating lake data...')

#Get data from columns
agg_geofile['Area'] = geofile['geometry'].area
agg_geofile['Length'] = geofile['geometry'].length
agg_geofile.sort_values('DrainageBa')  
aggfile_basin = agg_geofile['DrainageBa'].tolist()    #Get lake location
aggfile_area = agg_geofile['Area'].tolist()           #Get lake area
aggfile_sat = agg_geofile['Satellites'].tolist()      #Get lake source

aggfile_areakm = []
for i in aggfile_area:
    aggfile_areakm.append(i/10**6)

#Get all lake data for basins
aggfile_CW=[]
aggfile_ICECAP=[]
aggfile_NE=[]
aggfile_NO=[]
aggfile_NW=[]
aggfile_SE=[]
aggfile_SW=[]
label=['CW', 'ICE_CAP', 'NE', 'NO', 'NW', 'SE', 'SW']
aggfile_arealist=[aggfile_CW,aggfile_ICECAP,aggfile_NE,aggfile_NO,aggfile_NW,
                   aggfile_SE,aggfile_SW]
for i in range(len(aggfile_basin)):
    for l in range(len(label)):
        if label[l] in aggfile_basin[i]:
            aggfile_arealist[l].append(aggfile_areakm[i])


#Get all lake data for basins, rounded
aggfiler_CW = [round(n, 2) for n in aggfile_CW]
aggfiler_ICECAP = [round(n, 2) for n in aggfile_ICECAP]
aggfiler_NE = [round(n, 2) for n in aggfile_NE]
aggfiler_NO = [round(n, 2) for n in aggfile_NO]
aggfiler_NW = [round(n, 2) for n in aggfile_NW]
aggfiler_SE = [round(n, 2) for n in aggfile_SE]
aggfiler_SW = [round(n, 2) for n in aggfile_SW]
aggfile_arealist_round=[aggfiler_CW,aggfiler_ICECAP,aggfiler_NE,aggfiler_NO,aggfiler_NW,
                        aggfiler_SE,aggfiler_SW]
# for i in range(len(aggfile_basin)):
#     for l in range(len(label)):
#         if label[l] in aggfile_basin[i]:
#             aggfile_arealist_round[l].append(aggfile_areakm[i])
            
            
#Get all lake data for basins
aggsat_CW=[]
aggsat_ICECAP=[]
aggsat_NE=[]
aggsat_NO=[]
aggsat_NW=[]
aggsat_SE=[]
aggsat_SW=[]
aggfile_satlist=[aggsat_CW,aggsat_ICECAP,aggsat_NE,aggsat_NO,aggsat_NW,
                   aggsat_SE,aggsat_SW]
for i in range(len(aggfile_sat)):
    for l in range(len(label)):
        if label[l] in aggfile_basin[i]:
            aggfile_satlist[l].append(aggfile_sat[i])
            
#----------------------   Write general stats to file   -----------------------
print('\nWriting general stats file...')
        
#Open stats file    
f = open(outtxt1, 'w+')

#Total number of lakes in dataset and total number of unique lakes
f.write('Total number of detected lakes , ' + str(len(geofile_id)) + '\n')
f.write('Total number of unique lakes , ' + str(max(geofile_id)) + '\n\n')

#Total lake count for each sector
for i in range(len(label)):
    f.write(label[i] + ' total lake count , ' + str(geofile_basin.count(label[i])) + '\n')
f.write('\n')

#Unique lake count for each sector
for i in range(len(label)):
    f.write(label[i] + ' unique lake count , ' + str(aggfile_basin.count(label[i])) + '\n')
f.write('\n')

#Source count
for i in uniquesource:
    f.write('Lakes detected using ' + i + ',' + str(geofile_source.count(i)) + '\n')
f.write('\n')

#Min, max and average lake area
f.write('Min. lake area (km), ' + str(min(aggfile_areakm)) + '\n')
f.write('Max. lake area (km), ' + str(max(aggfile_areakm)) + '\n')
f.write('Average lake area (km), ' + str(np.average(aggfile_areakm)) + '\n')
f.write('\n')

#Min, max and average uncertainty
f.write('Min. uncertainty , ' + str(min(geofile_uncertain)) + '\n')
f.write('Max. uncertainty , ' + str(max(geofile_uncertain)) + '\n')
f.write('Average uncertainty , ' + str(np.average(geofile_uncertain)) + '\n\n')

f.close()


#---------------------   Write detailed stats to file   -----------------------
print('Writing detailed stats file...')

#Open stats file    
f = open(outtxt2, 'w+')

f.write('Basin, Basin area, Basin perimeter, Number of lakes, Total lake area (km),' + 
        'Average lake area (km), Median lake area (km), Mode lake area (w/ count), Standard deviation, ' +
        ' % basin area covered by lakes, Lake frequency (average dist. btwn lakes)' + '\n')

for i in range(len(basinfile_name)):
    f.write(str(basinfile_name[i]) + ',' +                                     #Basin name
            str(basinfile_area[i]) + ',' +                                     #Basin area
            str(perimfile_length[i]) + ',' +                                   #Basin perimeter
            str(aggfile_basin.count(label[i])) + ',' +                         #Unique lakes
            str(sum(aggfile_arealist[i])) + ',' +                              #Total lake area
            str(np.average(aggfile_arealist[i])) + ',' +                       #Aver. lake area
            str(np.median(aggfile_arealist[i])) + ',' +                        #Median lake area
            str(stats.mode(aggfile_arealist_round[i]).mode[0]) + ' (' + 
            str(stats.mode(aggfile_arealist_round[i]).count[0]) + '),' +        #Mode lake area
            str(np.std(aggfile_arealist[i])) + ',' +                           #Standard deviation
            str((sum(aggfile_arealist[i])/basinfile_area[i])*100) + ',' +      #% basin covered by lakes
            str(perimfile_length[i]/len(aggfile_arealist[i])) +                #Lake frequency along perimeter
            '\n')

f.close()


#--------------------   Write detailed stats to paper   -----------------------
print('Writing stats for paper to file...')

#Open stats file    
f = open(outtxt3, 'w+')

f.write('Basin, Total no. lakes,Average lake area (km), Median lake area (km),'+
        'Mode lake area (w/ count),Standard deviation,Total lake area (km),S1, S1%, S2, S2%, ADEM, '+
        'ADEM%, S1 S2, S1 S2%, S1 ADEM, S1 ADEM%, S2 ADEM, S2 ADEM%, All, '+
        ' All%' + '\n')

for i in range(len(basinfile_name)):
    f.write(str(basinfile_name[i]) + ',' +                                     #Basin name
            str(aggfile_basin.count(label[i])) + ',' +                         #Unique lakes
            str(np.average(aggfile_arealist[i])) + ',' +                       #Aver. lake area
            str(np.median(aggfile_arealist[i])) + ',' +                        #Median lake area
            str(stats.mode(aggfile_arealist_round[i]).mode[0]) + ' (' + 
            str(stats.mode(aggfile_arealist_round[i]).count[0]) + '),' +        #Mode lake area
            str(np.std(aggfile_arealist[i])) + ',' +                           #Standard deviation
            str(sum(aggfile_arealist[i])) + ',' +                              #Total lake area
            str(aggfile_satlist[i].count('S1')) + ',' + str(round((aggfile_satlist[i].count('S1')/aggfile_basin.count(label[i]))*100,2)) + '%,' +
            str(aggfile_satlist[i].count('S2')) + ',' + str(round((aggfile_satlist[i].count('S2')/aggfile_basin.count(label[i]))*100,2)) + '%,' +
            str(aggfile_satlist[i].count('ArcticDEM')) + ',' + str(round((aggfile_satlist[i].count('ArcticDEM')/aggfile_basin.count(label[i]))*100,2)) + '%,' +
            str(aggfile_satlist[i].count('S2, S1')) + ',' + str(round((aggfile_satlist[i].count('S2, S1')/aggfile_basin.count(label[i]))*100,2)) + '%,' +
            str(aggfile_satlist[i].count('ArcticDEM, S1')) + ',' + str(round((aggfile_satlist[i].count('ArcticDEM, S1')/aggfile_basin.count(label[i]))*100,2)) + '%,' +
            str(aggfile_satlist[i].count('S2, ArcticDEM')) + ',' + str(round((aggfile_satlist[i].count('S2, ArcticDEM')/aggfile_basin.count(label[i]))*100,2)) + '%,' +
            str(aggfile_satlist[i].count('S2, ArcticDEM, S1')) + ',' + str(round((aggfile_satlist[i].count('S2, ArcticDEM, S1')/aggfile_basin.count(label[i]))*100,2)) + '%\n')

f.close()    