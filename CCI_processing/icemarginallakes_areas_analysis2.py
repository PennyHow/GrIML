# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 14:30:55 2020

@author: HOW
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
file1 = workspace1 + 'glacier_cci_lakes_20200819.shp'

#------------------------------------------------------------------------------

def getArea(geofile, calc='sum'):

    source17 = geofile['Source'].tolist()
    id17 = geofile['LakeID'].tolist()
    geom17 = geofile['geometry'].tolist()
    
    #Retrieve non-ADEM aggregated lake areas
    areas=[]
    for i in list(sorted(set(id17))):
        id_source=[]
        id_geometry=[]
        for l in range(len(id17)):
            if id17[l] == i:
                id_source.append(source17[l])
                id_geometry.append(geom17[l])
                
        #Clear previous
        geom_agg=[]
        id_agg=[]
        gf=None
        gdf=None      
        for s in range(len(id_source)):
            geom_agg.append(id_geometry[s])
            id_agg.append(i)
       
        if id_agg is not None:
            gf = {'LakeID':id_agg, 'geometry':geom_agg}
            gdf = gp.GeoDataFrame(gf, crs='EPSG:32624')
            
            if calc == 'agg':
                gdf = gdf.dissolve(by='LakeID')
                gdf['Area']=gdf['geometry'].area
                id_area = gdf['Area'].tolist()
                areas.append(float(id_area[0]))
                
            elif calc == 'aver':
                gdf['Area']=gdf['geometry'].area 
                id_area = gdf['Area'].tolist()
                areas.append(float(np.average(id_area)))
                
            elif calc == 'max':
                gdf['Area']=gdf['geometry'].area 
                id_area = gdf['Area'].tolist()
                areas.append(float(np.nanmax(id_area)))
                                            
        else:
            areas.append(float(0))

    print('Total area (' + calc + '): ' + str(sum(areas)/10**6) + ' sq km')
    print('Average area (' + calc + '): '+ str(np.average(areas)/10**6) + ' sq km')
    print('Lake frequency (' + calc + '): '+str(sum(i>0 for i in areas)) + '\n')
    return areas

def countArea(data, bins):
    bincount=[]
    
    #Iterate through bins
    for b in range(len(bins)-1):
        count=0
        
        #Count data point if lies within bin
        for d in data:
            if bins[b] >= d:
                count=count+1
        print('Bin <' + str(bins[b]) + ': ' + str(count))
        bincount.append(count)
    
    #Refine bins by removing previous bin count
    bincount2=[]
    bincount2.append(bincount[0])
    for i in range(len(bincount))[1:]:
        total=bincount[i]-bincount[i-1]
        bincount2.append(total)        
        print('Bin ' + str(bins[i-1]) + '-' + str(bins[i]) + ': ' + (str(total)) + ' lakes')
    
    print('Total lake count: ' + str(sum(bincount2)))
    
    return bincount2

#-----------------------   Define inputs and outputs   ------------------------

#Define input file and location 
workspace1 = 'P:/B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland/B71-04 Essential Climate Variable production/final lake products/'
workspace2 = 'D:/python_workspace/ice_marginal_lakes/'
file1 = workspace1 + 'glacier_cci_lakes_20200819.shp'
outtxt3 = workspace2 + 'new_stats_for_alex.csv'

#-------------------------   Load as dataframe   ------------------------------

print('\nLoading geodataframes...')    

#Read file as geopandas index
geofile = gp.read_file(file1)
geofile = geofile.sort_values('LakeID')

#Get areas in different calculations
agg_area = getArea(geofile, calc='agg')
aver_area = getArea(geofile, calc='aver')
max_area = getArea(geofile, calc='max')

#Append areas to dissolved geofile
agg_geofile = geofile.dissolve(by='LakeID')
agg_geofile['area_agg'] = agg_area
agg_geofile['area_aver'] = aver_area
agg_geofile['area_max'] = max_area


#-----------------   Get data from aggregated lake data   ---------------------
print('\nAggregating lake data...')

#Get data from columns
agg_geofile.sort_values('DrainageBa')  
aggfile_basin = agg_geofile['DrainageBa'].tolist()    #Get lake location
aggfile_area = agg_geofile['area_aver'].tolist()           #Get lake area
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



#--------------------   Write detailed stats to paper   -----------------------
print('Writing stats for paper to file...')

#Open stats file    
f = open(outtxt3, 'w+')

f.write('Basin, Total no. lakes,Average lake area (km), Median lake area (km),'+
        'Mode lake area (w/ count),Standard deviation,Total lake area (km),S1, S1%, S2, S2%, ADEM, '+
        'ADEM%, S1 S2, S1 S2%, S1 ADEM, S1 ADEM%, S2 ADEM, S2 ADEM%, All, '+
        ' All%' + '\n')

for i in range(len(label)):
    f.write(str(label[i]) + ',' +                                              #Basin name
            str(aggfile_basin.count(label[i])) + ',' +                         #Unique lakes
            str(np.average(aggfile_arealist[i])) + ',' +                       #Aver. lake area
            str(np.median(aggfile_arealist[i])) + ',' +                        #Median lake area
            str(stats.mode(aggfile_arealist_round[i]).mode[0]) + ' (' + 
            str(stats.mode(aggfile_arealist_round[i]).count[0]) + '),' +       #Mode lake area
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
