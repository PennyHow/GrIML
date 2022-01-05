# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 14:50:54 2021

@author: HOW
"""

import numpy as np
import arcpy
import geopandas as gp
from arcpy import env
from arcpy.sa import Con, Raster, Float, ExtractByMask, Reclassify, ZonalStatistics, Int

direct = "D:/python_workspace/greenland/data_handling/data_management/"

dykFile = direct + 'dykes.shp'
rockFile = direct + 'rocktypes.shp'

dykGF = gp.read_file(str(dykFile))
rockGF = gp.read_file(str(rockFile))

dykCOL = dykGF.columns.tolist()
rockCOL = rockGF.columns.tolist()


#Change chemistry str to float
for c in dykCOL[17:-1]:
    data = list(dykGF[c])
    data1=[]
    for d in data:
        try:
            d1 = round(float(d),2) 
        except:
            d1 = None
        data1.append(d1)
    dykGF[c]=data1

    
for c in rockCOL[14:-1]:
    data = list(rockGF[c])
    data1=[]
    for d in data:
        try:
            d1 = round(float(d),2) 
        except:
            d1 = None
        data1.append(d1)
    rockGF[c]=data1
    
    
#Save to file
dykGF.to_file(direct + 'dykes2.shp')
rockGF.to_file(direct + 'rocktypes2.shp')    