# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 15:50:09 2019


For re-calculating ice-marginal lake shapefile product

@author: how
"""

import os
import numpy as np
import geopandas as gp
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from osgeo import ogr
import pandas as pd

#------------------------   Define file locations   ---------------------------

#Define input file and location 
workspace = 'D:\\python_workspace\\ice_marginal_lake_stats\\test'

file1 = workspace + '\\all_lakes_merged_eva.shp'


#-------------------   Import files as geopandas objects   --------------------

#Read file as geopandas index
geofile = gp.read_file(file1)
sortgeofile = geofile.sort_values('UniqueID')

ids = sortgeofile['UniqueID'].tolist()
source = sortgeofile['Source'].tolist()


#------------------   List of satellites that detected lake   -----------------

#Function for finding indexes of certain values
def indices(mylist, value):
    return[i for i, x in enumerate(mylist) if x==value]

#Define empty output
satellites=[]

#Iterate through ids
for x in range(len(ids)):
    
    indx = indices(ids, x)
    
    if len(indx) != 0:
        res = []
        
#        for y in indx:
#            res.append(source[y])
        
        if len(indx) == 1:
            res.append(source[indx[0]])
        else:
            unid=[]
            for dx in indx:
                unid.append(source[dx])

            res.append(list(set(unid)))
        
    
        for z in range(len(indx)):
            if len(indx) == 1:
                satellites.append(res)
            else:
                satellites.append(res[0])
                

#----------------   Number of satellites that detected lake   -----------------

number=[]
for i in satellites:
    number.append(len(i))


#--------------   Calculate certainty based on satellites   -------------------

#Define scale factors
S1=0.7
S2=0.52
arcDEM=1.79

#Create empty output
cert=[]

#Function for determining scale factor from string
def scale(value):
    if value == ['ArcticDEM']:
        return arcDEM
    elif value == ['S1']:
        return S1
    elif value == ['S2']:
        return S2
    else:
        print('Invalid satellite name:' + str(value))
        return None

for a in range(len(ids)):
    
    if number[a]==1:
        out = scale(satellites[a])
        cert.append(out)
        
    else:
        out=[]
        for b in satellites[a]:
            out.append(scale([b]))
        cert.append(sum(out))

cert2=[]
for i in cert:
    cert2.append(round(i, 1))

#-----------------------   Write data to shapefile   --------------------------
    
#List of satellites that detected lake
satellites2=[]
for i in satellites:
    satellites2.append(', '.join(i))
    
sortgeofile['Satellites']=satellites2


#Number of satellites that detected lake
sortgeofile['NumOfSate']=number

#Number of satellites that detected lake
sortgeofile['Certainty']=cert2


#Write shapefile
sortgeofile.to_file(workspace + '\\all_lakes_merged_20191101.shp')





#print(len())
    

#driver = ogr.GetDriverByName('ESRI Shapefile')
#
#dataSource = driver.Open(file1, 1)
#
## Check to see if shapefile is found.
#if dataSource is None:
#    print('Could not open ' + str(file1))
#else:
#    print('Opened ' + str(file1))
#    layer = dataSource.GetLayer()
#    featureCount = layer.GetFeatureCount()
#    print('Number of features in ' + str(file1) + ': ' + str(featureCount))
#
#
#for i in range(0, layer.GetFeatureCount()):
#    print(i)
#    g = layer.GetFeatureRef(i)
    
#    geom = feature.GetGeometryRef()
#    print(geom.Centroid().ExportToWkt())

