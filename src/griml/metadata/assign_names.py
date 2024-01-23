#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GrIML metadata assignment

@author: Penelope How
"""

def assign_names(gdf, gdf_names, distance=500.0):
    '''Assign placenames to geodataframe geometries based on names in another 
    geodataframe point geometries

    Parameters
    ----------
    gdf : pandas.GeoDataFrame
        Vectors to assign uncertainty to
    gdf_names : pandas.GeoDataFrame
        Vector geodataframe with placenames
    distance : int
        Distance threshold between a given vector and a placename
    
    Returns
    -------
    gdf : pandas.GeoDataFrame
        Vectors with assigned IDs
    '''  
    placenames = _compile_names(gdf_names)
                                    
    lakename=[]     
    for i,v in gdf.iterrows():  
        
        geom = v['geometry']
        
        polynames=[] 
        for pt in range(len(placenames)):
            if geom.contains(gdf_names['geometry'][pt]) == True:
                polynames.append(placenames[pt])  
                
        if len(polynames)==0:
            for pt in range(len(placenames)):  
                if gdf_names['geometry'][pt].distance(geom) < distance: 
                    polynames.append(placenames[pt]) 
            lakename.append(polynames)
            
        elif len(polynames)==1:  
            lakename.append(polynames)    
            
        else: 
            out=[]          
            for p in polynames:  
                out.append(p) 
            lakename.append(out) 
            
    lakeid = gdf['unique_id'].tolist()      
    lakename2 = []     
    
    for x in gdf.index:        
        indx = _get_indices(lakeid, x)                                         
        findname=[]
        for l in indx:
            if len(lakename[l])!=0: 
                findname.append(lakename[l])
        
        for i in range(len(indx)):  
            if len(findname)==0:
                lakename2.append('')
        
            else:                                           
                unique = set(findname[0])  
                unique = list(unique)  
                
                if len(unique)==1:
                    lakename2.append(findname[0][0]) 
                    
                else:
                    out2 = ', '
                    out2 = out2.join(unique) 
                    lakename2.append(out2) 
    gdf['placename'] = lakename2
    return gdf


def _get_indices(mylist, value):
    '''Get indices for value in list'''
    return[i for i, x in enumerate(mylist) if x==value]


def _compile_names(gdf):
    '''Get preferred placenames from placename geodatabase'''  
    placenames=[]
    for i,v in gdf.iterrows():
        if v['Ny_grønla'] != None: 
            placenames.append(v['Ny_grønla'])
        else:
            if v['Dansk'] != None: 
                placenames.append(v['Dansk'])
            else:
                if v['Alternativ'] != None:
                    placenames.append(v['Alternativ'])
                else:
                    placenames.append(None)
    return placenames 