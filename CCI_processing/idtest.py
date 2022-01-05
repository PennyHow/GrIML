#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 00:04:22 2019

@author: penhow
"""
import geopandas as gp

#Define input file and location 
workspace = 'D:\python_workspace\ice_marginal_lakes'

#file1 = workspace + '/glacier_cci_lakes_removed.shp'
file1 = workspace + '\glacier_cci_lakes_20200709.shp'

#-------------------   Import files as geopandas objects   --------------------

#Read file as geopandas index
geofile = gp.read_file(file1)
sortgeofile = geofile.sort_values('LakeID')
ids = sortgeofile['LakeID'].tolist()
#cert = sortgeofile['Certainty'].tolist()

count=1
lakeid=[]
lakeid.append(count)
for i in range(len(ids))[1:]:
    if ids[i] == ids[i-1]:
        print(str(ids[i]) + ' >> ' + str(count))
        lakeid.append(count)
        
    elif ids[i]-ids[i-1]==1:
        count=count+1
        print(str(ids[i]) + ' >> ' + str(count))
        lakeid.append(count)
    else:
        count=count+1
        print(str(ids[i]) + ' >> ' + str(count))
        lakeid.append(count)
        
print('Number of unique lakes: ' + str(count))
print('Length of new field: ' + str(len(lakeid)))
print('Length of old field: ' + str(len(ids)))

sortgeofile['LakeID']=lakeid
#sortgeofile.drop(columns=['UniqueID'], inplace=True)
#
#newcert=[]
#for c in cert:
#    value = float(c)
#    newcert.append(round(value,1))
#
#sortgeofile.drop(columns=['Certainty'], inplace=True)
#sortgeofile['cert1']=newcert
#
#
sortgeofile.to_file(workspace + '/glacier_cci_lakes_20200709_newid.shp')
