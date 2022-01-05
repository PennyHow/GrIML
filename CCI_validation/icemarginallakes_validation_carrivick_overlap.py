# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 11:24:30 2020

@author: HOW
"""

import fiona
import numpy as np
import geopandas as gp
from rtree import index
from shapely.geometry import shape

#------------------------------------------------------------------------------
#Workspace for files
workspace = ('D:/python_workspace/ice_marginal_lakes/carrivick_validation/')

#2017 Inventory subset
file1 = workspace + 'inventory17_subset/glacier_cci_lakes_subset_for_carrivick.shp'

#Carrivick time steps
file2 = workspace + 'carrivick_lakes/all_carrivick_reproj.shp'

#Open shapefiles using fiona
shp1 = fiona.open(file1, 'r')
print('Number of lakes in IIML inventory: ' + str(len(list(shp1))))

shp2 = fiona.open(file2,'r')
print('Number of lakes in Carrivick inventories: ' + str(len(list(shp2))))



#-------------------------   Load as dataframe   ------------------------------

print('\nLoading geodataframes...')    

#Read file as geopandas index
geofile17 = gp.read_file(file1)
agg_gf17 = geofile17.dissolve(by='LakeID')


#Read Carrivick files where lakes are region-wide
geofile_time2 = gp.read_file(file2)



#------------------------------------------------------------------------------

# List to collect pairs of intersecting features
fc_intersect = []
for featA in shp1:
    featAintersect=[]
    for featB in shp2:
        if shape(featA['geometry']).intersects(shape(featB['geometry'])):
            featAintersect.append(featB)    
    fc_intersect.append([featA, featAintersect])

lakeids=[]
for features in fc_intersect:
    lakeids.append(features[0]['id'])

commonids=[]
for i in set(lakeids):
    if lakeids.count(i) > 5:
        commonids.append(i)
            
#Compile intersecting polygons into inventory years
years=[]
areas87=[]
areas92=[]
areas00=[]
areas05=[]
areas10=[]
areas17=[]

for features in fc_intersect:
    match=False
    for ids in commonids:
        if int(features[0]['id']) ==int(ids):
            match=True
    
    if match is True:
        for polygon in features:
            try:
                year = str(polygon['properties']['layer'])
            except:
                year = ('2017')        
            if year in ['1987']:
                areas87.append(polygon['properties']['Area'])        
            elif year in ['1992']:
                areas92.append(polygon['properties']['Area']) 
            elif year in ['2000']:
                areas00.append(polygon['properties']['Area']) 
            elif year in ['2005']:
                areas05.append(polygon['properties']['Area']) 
            elif year in ['2010']:
                areas10.append(polygon['properties']['Area'])  
            else:
                areas17.append(polygon['properties']['Area'])

areas17=list(set(areas17))
print(len(areas87)+len(areas92)+len(areas00)+len(areas05)+len(areas10)+len(areas17))

print('Average common lake size in 1987 carrivick dataset: ' + str(np.average(areas87)/10**6))
print('Average common lake size in 1992 carrivick dataset: ' + str(np.average(areas92)/10**6))
print('Average common lake size in 2000 carrivick dataset: ' + str(np.average(areas00)/10**6))
print('Average common lake size in 2005 carrivick dataset: ' + str(np.average(areas05)/10**6))
print('Average common lake size in 2010 carrivick dataset: ' + str(np.average(areas10)/10**6))
print('Average common lake size in 2017 inventory subset: ' + str(np.average(areas17)/10**6)+ '\n')


## Instantiate index class
#idx = index.Index()
#for i,featA in enumerate(shp1):
#    idx.insert(i, shape(featA['geometry']).bounds)
#
#for featB in shp2:
#    # Test for potential intersection with each feature of the other feature collection
#    for intersect_maybe in idx.intersection(shape(featB['geometry']).bounds):
#        # Confirm intersection
#        if shape(featB['geometry']).intersects(shape(shp2[intersect_maybe]['geometry'])):
#            fc_intersect.append([shp1[intersect_maybe], featB])