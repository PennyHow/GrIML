# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 12:06:48 2019

Script used in the CCI ice-marginal lakes project. 

The aim of this script is to find lake points that coincide with lake polygons,
and assign the name of the lake point to the polygon.
 
Firstly the point file is converted to two items: the individual point 
geometries and a list of the names (which has the same index structure as the 
point geometries item). The Greenlandic name is appended if it is present. 
If the Greenlandic name does not exist, then the Danish or alternative name is 
appended.
 
Secondly, the polygon geometries are extracted from the lake polygon file. 
These are iterated through to look for coinciding points. If a point is found 
to coincide with the polygon, then the name associated with that point is 
added to the polygon geometry.

@author: how
"""

import geopandas as gp
from shapely.geometry import Point, Polygon, MultiPolygon

#------------------------   Define file locations   ---------------------------

#Define input file and location 
workspace = 'D:\python_workspace\ice_marginal_lakes\lakenames'

file1 = workspace + '\glacier_cci_lakes_20200819.shp'
file2 = workspace + '\lakenames_pts.shp'


#-------------------   Import files as geopandas objects   --------------------

#Read icemargin lake file as geopandas index and sort by LakeID
geofile1 = gp.read_file(file1)
sortgeofile1 = geofile1.sort_values('LakeID')

#Read placenames file as geopandas index
geofile2 = gp.read_file(file2)


#---   1. Extract point geometries and lake names from placenames geofile   ---
shapelypts = []
shapelynames = []                                       #Create empty lists

for i,v in geofile2.iterrows():                         #Iterate over geofile
    
    geom1 = Point(v['geometry'])                        #Create pt geometry                     
    shapelypts.append(geom1)                            #Append geometry to list
    
    if v['Ny_grønla'] != None:                          #Append Greenlandic name 
        shapelynames.append(v['Ny_grønla'])             #if it exists
        
    else:
        if v['Dansk'] != None:                          #Append Danish name if
            shapelynames.append(v['Dansk'])             #it exists
        
        else:
            if v['Alternativ'] != None:                 #Append alternative name
                shapelynames.append(v['Alternativ'])    #if it exists
                
            else:
                shapelynames.append(None)               #Else, append none
    

#-------   2. Assign lake name if point intersects with lake polygon    -------    
                
lakename=[]                                             #Create empty list

for i,v in sortgeofile1.iterrows():                     #Iterate over geofile rows
    
    try:                                                #Try create polygon
        geom2 = Polygon(v['geometry'])
    except:                                             #Else create multipolygon
        geom2 = MultiPolygon(v['geometry'])
    
    polynames=[]                                        #Create empty list for 
                                                        #names
    
    for pt in range(len(shapelypts)):                   #Iterate over points
        
        if geom2.contains(shapelypts[pt]) == True:      #If point coincides with 
                                                        #polygon
            print('Coinciding point found for lake '    #Print statement 
                  + str(i) +': ' + shapelynames[pt])
            
            polynames.append(shapelynames[pt])          #Append name to list
            
    if len(polynames)==0:                               #If list is empty,
        for pt in range(len(shapelypts)):               #iterate through pts again
            
            if shapelypts[pt].distance(geom2) < 500.0:  #If pt is within 500 m
                
                print('Near point found for lake '      #Print statement 
                      + str(i) +': ' + 
                      shapelynames[pt])  
                
                polynames.append(shapelynames[pt])      #Append nearest pt name
        lakename.append(polynames)
        
    elif len(polynames)==1:                             #If list has one element,
        lakename.append(polynames)                      #append polyname
        
    else:                                               #If list has more than
        out=[]                                          #one element,
        for p in polynames:                             #Merge all names into
            out.append(p)                               #one string and append
        lakename.append(out) 

 

#---------------   Assign name to lakes with same id   ------------------------
        
lakeid = sortgeofile1['LakeID'].tolist()                #Get lakeid as list
dfindex = sortgeofile1.index                            #Get geofile index
lakename2 = []                                          #Create empty list

#Function to find index of a given value
def indices(mylist, value):
    return[i for i, x in enumerate(mylist) if x==value]
      
#Iterate through index
for x in dfindex:
    
    indx = indices(lakeid, x)                           #Get indexes for each 
                                                        #unique id                                      
    findname=[]
    for l in indx:                                      #Iterate through indices
        if len(lakename[l])!=0:                         #Get lake name if exists
            findname.append(lakename[l])
    
    for i in range(len(indx)):                          #If lake name not found,
        if len(findname)==0:                            #append empty cell ('')
            lakename2.append('')
    
        else:                                           
            unique = set(findname[0])                   #If lake name found,
            unique = list(unique)                       #get all unique names
            
            if len(unique)==1:
                lakename2.append(findname[0][0])        #Append name if only one 
                                                        #given
                
            else:                                       #If more than one name 
                out2 = ', '                             #given, join all names
                out2 = out2.join(unique)                #and append
                lakename2.append(out2) 
   

#-----------   Add lake names to geofile and save to shapefile  ---------------
    
#Add lake names list to geofile under the heading 'LakeName'            
sortgeofile1['LakeName'] = lakename2

#Save geofile to shapefile
sortgeofile1.to_file(workspace + '\glacier_cci_lakes_20200819_withnames.shp')

#Print 'Finished' to indicate when the script has finished
print('Finished')

