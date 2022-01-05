# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 08:28:33 2019

@author: how
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 00:04:22 2019

@author: penhow
"""
import geopandas as gp

#Define input file and location 
workspace = '/home/penhow/Documents/PYTHON/asiaq'

#file1 = workspace + '/glacier_cci_lakes_removed.shp'
file1 = 'P:\\B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland\\B71-04 Essential Climate Variable production\\final lake products\\glacier_cci_lakes_20191104.shp'

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
    if ids[i] - ids[i-1] > 1:
        print(str(ids[i-1]) + ' >> ' + str(ids[i-1]))
        lakeid.append(count)

print('Finished')