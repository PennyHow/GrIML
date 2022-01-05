# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 14:15:50 2019

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
workspace = '/home/penhow/Documents/PYTHON/asiaq'

file1 = workspace + '/glacier_cci_lakes_20191101_local.shp'


#-------------------   Import files as geopandas objects   --------------------

#Read file as geopandas index
geofile = gp.read_file(file1)
sortgeofile2 = geofile.sort_values('UniqueID')

#Get all variables from geodatabase
geometry = sortgeofile2['geometry'].tolist()
source = sortgeofile2['Source'].tolist()
basin = sortgeofile2['DrainageBa'].tolist()
ids = sortgeofile2['UniqueID'].tolist()
sat = sortgeofile2['Satellites'].tolist()
numsat = sortgeofile2['NumOfSate'].tolist()
cert = sortgeofile2['Certainty'].tolist()
area = sortgeofile2['Area'].tolist()
length = sortgeofile2['Length'].tolist()
sDate = sortgeofile2['StartDate'].tolist()
eDate = sortgeofile2['EndDate'].tolist()

dfindex = sortgeofile2.index

#Function for finding indexes of certain values
def indices(mylist, value):
    return[i for i, x in enumerate(mylist) if x==value]
    
def list_duplicates(seq):
    seen = set()
    seen_add = seen.add
    # adds all elements it doesn't know yet to seen and all other to seen_twice
    seen_twice = set( x for x in seq if x in seen or seen_add(x) )
    # turn the set into a list (as requested)
    return list( seen_twice )

ngeo = []
nsource = []
nbasin = []
nids = []
nsat = []
nnumsat = []
ncert = []
narea = []
nlength = []
nsDate = []
neDate = []

errors=[]
duplicate=[]
uduplicate=[]
count=1

#Iterate through ids
for x in dfindex:
    
    #Get indexes for each unique id
    indx = indices(ids, x)
    
    #If index is not empty
    if len(indx) != 0: 
        
        #If index is only one lake, then write to file
        if len(indx) == 1:
#            print(str(indx[0]) + ': unique lake \n')
            ngeo.append(geometry[indx[0]])
            nsource.append(source[indx[0]])
            nbasin.append(basin[indx[0]])
            nids.append(ids[indx[0]])
            nsat.append(sat[indx[0]])
            nnumsat.append(numsat[indx[0]])
            ncert.append(cert[indx[0]])
            narea.append(area[indx[0]])
            nlength.append(length[indx[0]])
            nsDate.append(sDate[indx[0]])
            neDate.append(eDate[indx[0]])
        
        
        #If index is more than one                
        else:            
            
            #List duplicate lakes from same satellite
#            print(ids[indx[0]:indx[-1]+1])
#            print(source[indx[0]:indx[-1]+1])
            s = list_duplicates(source[indx[0]:indx[-1]+1])

            #If no duplicates, append lakes to file
            if len(s) == 0:
                for ix in indx:
#                    print(str(ix) + ': lake from no duplicate sources \n')
                    ngeo.append(geometry[ix])
                    nsource.append(source[ix])
                    nbasin.append(basin[ix])
                    nids.append(ids[ix])
                    nsat.append(sat[ix])
                    nnumsat.append(numsat[ix])
                    ncert.append(cert[ix])
                    narea.append(area[ix])
                    nlength.append(length[ix])
                    nsDate.append(sDate[ix])
                    neDate.append(eDate[ix]) 

            
            #Else, find if ArcticDEM found in sources
            else:
                flag=False
                for item in s:
                    if item == 'ArcticDEM':
                        flag=True
                
                #Append if no ArcticDEM sources found
                if flag is False:
                    for ix in indx:
#                        print(str(ix) + ': lake from no ArcticDEM source \n')
                        ngeo.append(geometry[ix])
                        nsource.append(source[ix])
                        nbasin.append(basin[ix])
                        nids.append(ids[ix])
                        nsat.append(sat[ix])
                        nnumsat.append(numsat[ix])
                        ncert.append(cert[ix])
                        narea.append(area[ix])
                        nlength.append(length[ix])
                        nsDate.append(sDate[ix])
                        neDate.append(eDate[ix]) 
  
              
                #If ArcticDEM sources found
                else:
                    
                    #Find ArcticDEM lake lengths
                    sample1 = source[indx[0]:indx[-1]+1]
                    sample2 = length[indx[0]:indx[-1]+1]
                    sample3=[]
                    for a in range(len(sample1)):
                        if sample1[a]=='ArcticDEM':
                            sample3.append(sample2[a])
                    
                    #If 2 ArcticDEM found, find difference btwn lengths
                    if len(sample3)==2:
                        diff = sample3[1]-sample3[0]
                           
                        
                        #If length difference is more than 5, append
                        if diff>5.0:
                            for ix in indx:
#                                print(str(ix) + ': lake with length difference more than 5 \n')
                                ngeo.append(geometry[ix])
                                nsource.append(source[ix])
                                nbasin.append(basin[ix])
                                nids.append(ids[ix])
                                nsat.append(sat[ix])
                                nnumsat.append(numsat[ix])
                                ncert.append(cert[ix])
                                narea.append(area[ix])
                                nlength.append(length[ix])
                                nsDate.append(sDate[ix])
                                neDate.append(eDate[ix]) 
                        
                        #If length difference is less than 5, DUPLICATE FOUND
                        else:
                            if sample3[0]>sample3[1]:
                                for ix in indx:
                                    if length[ix] != sample3[1]:
#                                        print(str(ix) + ': lake with non-duplicate found \n')
                                        ngeo.append(geometry[ix])
                                        nsource.append(source[ix])
                                        nbasin.append(basin[ix])
                                        nids.append(ids[ix])
                                        nsat.append(sat[ix])
                                        nnumsat.append(numsat[ix])
                                        ncert.append(cert[ix])
                                        narea.append(area[ix])
                                        nlength.append(length[ix])
                                        nsDate.append(sDate[ix])
                                        neDate.append(eDate[ix])
                                    else:
                                        print(str(ix) + ': duplicate found\n')
                                        duplicate.append(ix)
                                        count=count+1
                                        
                            elif sample3[1]>sample3[0]:
                                for ix in indx:
                                    if length[ix] != sample3[0]:
#                                        print(str(ix) + ': lake with non-duplicate found \n')
                                        ngeo.append(geometry[ix])
                                        nsource.append(source[ix])
                                        nbasin.append(basin[ix])
                                        nids.append(ids[ix])
                                        nsat.append(sat[ix])
                                        nnumsat.append(numsat[ix])
                                        ncert.append(cert[ix])
                                        narea.append(area[ix])
                                        nlength.append(length[ix])
                                        nsDate.append(sDate[ix])
                                        neDate.append(eDate[ix])                                    
                                    else:
                                        print(str(ix) + ': duplicate found\n')
                                        duplicate.append(ix)
                                        count=count+1
                                                   
                    else:

                        for ix in indx:
                            print(str(ix) + ': too many numbers to correct for \n')
                            
                            ngeo.append(geometry[ix])
                            nsource.append(source[ix])
                            nbasin.append(basin[ix])
                            nids.append(ids[ix])
                            nsat.append(sat[ix])
                            nnumsat.append(numsat[ix])
                            ncert.append(cert[ix])
                            narea.append(area[ix])
                            nlength.append(length[ix])
                            nsDate.append(sDate[ix])
                            neDate.append(eDate[ix]) 
                            
                            errors.append(ix)
                            uduplicate.append(ids[ix])

print('Original number of lakes: ' + str(len(source)))
print('Lakes removed: ' + str(count))
print('Revised number of lakes: ' + str(len(nsource)))
print('Number of errors: ' + str(len(errors)))

print('Index number for each error:' + str(errors))
print('ID for each error: ' + str(uduplicate))
#
#print('Index number of each duplicate: ' + str(duplicate))
#print('Number of duplicates: ' + str(len(duplicate)))
#sortgeofile.drop([0])

newgeofile=sortgeofile2.copy()
newgeofile.drop(duplicate, inplace=True)

errordup=[1797, 1798, 2733, 2732, 2733, 2775, 2776, 3415, 3416, 3417, 3418, 
         3419, 4138, 4139,4386, 4387, 4388, 4389, 4390]
newgeofile.drop(errordup, inplace=True)


newgeofile.to_file(workspace+ '/glacier_cci_lakes_removed.shp')


#gdf = geopandas.GeoDataFrame(
#    df, geometry=geopandas.points_from_xy(df.Longitude, df.Latitude))
#
#newgeofile['Source']=nsource
#newgeofile['DrainageBa']=nbasin
#newgeofile['LakeID']=nids
#newgeofile['Satellites']=nsat
#newgeofile['NumOfSate']=nnumsat
#newgeofile['Certainty']=ncert
#newgeofile['Area']=narea
#newgeofile['Length']=nlength
#newgeofile['StartDate']=nsDate
#newgeofile['EndDate']=neDate
#
#newgeofile.to_file(workspace+ '/glacier_cci_lakes_removed.shp')

#                    print(ids[indx[0]:indx[-1]+1])
#                    print(source[indx[0]:indx[-1]+1])
#                    print(s)                    
#                    print(length[indx[0]:indx[-1]+1])
                        
                        
#            s = (source[indx[0]:indx[-1]+1])
#            if len(s)==len(set(s)):
#                nsource.append(source[indx[0]])
#                nbasin.append(basin[indx[0]])
#                nids.append(ids[indx[0]])
#                nsat.append(sat[indx[0]])
#                nnumsat.append(numsat[indx[0]])
#                ncert.append(cert[indx[0]])
#                narea.append(area[indx[0]])
#                nlength.append(length[indx[0]])
#                nsDate.append(sDate[indx[0]])
#                neDate.append(eDate[indx[0]])  
            
#            else:
#                for i in set(s):
#                    if i != 'ArcticDEM':
#                    
#                    elif i == 'ArcticDEM':
#                        print(source[indx[0]:indx[-1]+1])
#                        print(nlength[indx[0]:indx[-1]+1])

#            result = s.find('ArcticDEM')
#            print(result)


#            res.append(source[indx[0]])
#        else:
#            unid=[]
#            for dx in indx:
#                unid.append(source[dx])
#
#            res.append(list(set(unid)))
#        
#    
#        for z in range(len(indx)):
#            if len(indx) == 1:
#                satellites.append(res)
#            else:
#                satellites.append(res[0])
                


##------------------   List of satellites that detected lake   -----------------
#
##Function for finding indexes of certain values
#def indices(mylist, value):
#    return[i for i, x in enumerate(mylist) if x==value]
#
##Define empty output
#satellites=[]
#
##Iterate through ids
#for x in range(len(ids)):
#    
#    indx = indices(ids, x)
#    
#    if len(indx) != 0:
#        res = []
#        
##        for y in indx:
##            res.append(source[y])
#        
#        if len(indx) == 1:
#            res.append(source[indx[0]])
#        else:
#            unid=[]
#            for dx in indx:
#                unid.append(source[dx])
#
#            res.append(list(set(unid)))
#        
#    
#        for z in range(len(indx)):
#            if len(indx) == 1:
#                satellites.append(res)
#            else:
#                satellites.append(res[0])
#                
#
##----------------   Number of satellites that detected lake   -----------------
#
#number=[]
#for i in satellites:
#    number.append(len(i))
#
#
##--------------   Calculate certainty based on satellites   -------------------
#
##Define scale factors
#S1=0.7
#S2=0.52
#arcDEM=1.79
#
##Create empty output
#cert=[]
#
##Function for determining scale factor from string
#def scale(value):
#    if value == ['ArcticDEM']:
#        return arcDEM
#    elif value == ['S1']:
#        return S1
#    elif value == ['S2']:
#        return S2
#    else:
#        print('Invalid satellite name:' + str(value))
#        return None
#
#for a in range(len(ids)):
#    
#    if number[a]==1:
#        out = scale(satellites[a])
#        cert.append(out)
#        
#    else:
#        out=[]
#        for b in satellites[a]:
#            out.append(scale([b]))
#        cert.append(sum(out))
#
#cert2=[]
#for i in cert:
#    cert2.append(round(i, 1))
#
##-----------------------   Write data to shapefile   --------------------------
#    
##List of satellites that detected lake
#satellites2=[]
#for i in satellites:
#    satellites2.append(', '.join(i))
#    
#sortgeofile['Satellites']=satellites2
#
#
##Number of satellites that detected lake
#sortgeofile['NumOfSate']=number
#
##Number of satellites that detected lake
#sortgeofile['Certainty']=cert2
#
#
##Write shapefile
#sortgeofile.to_file(workspace + '\\all_lakes_merged_20191101.shp')
#
#
#
#
#
##print(len())
#    
#
##driver = ogr.GetDriverByName('ESRI Shapefile')
##
##dataSource = driver.Open(file1, 1)
##
### Check to see if shapefile is found.
##if dataSource is None:
##    print('Could not open ' + str(file1))
##else:
##    print('Opened ' + str(file1))
##    layer = dataSource.GetLayer()
##    featureCount = layer.GetFeatureCount()
##    print('Number of features in ' + str(file1) + ': ' + str(featureCount))
##
##
##for i in range(0, layer.GetFeatureCount()):
##    print(i)
##    g = layer.GetFeatureRef(i)
#    
##    geom = feature.GetGeometryRef()
##    print(geom.Centroid().ExportToWkt())

