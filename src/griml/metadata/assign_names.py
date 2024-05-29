#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
from operator import itemgetter

import geopandas as gpd
import numpy as np
import pandas as pd

from scipy.spatial import cKDTree
from shapely.geometry import Point, LineString, Polygon
from griml.load import load

def assign_names(gdf, gdf_names):
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
    
    # Load geodataframes
    gdf1 = load(gdf)
    gdf2 = load(gdf_names)
    
    # Compile placenames into new dataframe
    names = _compile_names(gdf2)
    placenames = gpd.GeoDataFrame({"geometry": list(gdf2['geometry']),
                                   "placename": names})
                                    
    # Assign names based on proximity
    a = _get_nearest_point(gdf1, placenames)
    return a


def _get_nearest_point(gdA, gdB, distance=500.0):
    '''Return properties of nearest point in Y to geometry in X'''
    nA = np.array(list(gdA.geometry.centroid.apply(lambda x: (x.x, x.y))))
    nB = np.array(list(gdB.geometry.apply(lambda x: (x.x, x.y))))

    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k=1)
    gdB_nearest = gdB.iloc[idx].drop(columns="geometry").reset_index(drop=True)
    gdf = pd.concat(
        [
            gdA.reset_index(drop=True),
            gdB_nearest,
            pd.Series(dist, name='dist')
        ], 
        axis=1)
    
    gdf.loc[gdf['dist']>=distance, 'placename'] = 'Unknown'
    gdf = gdf.drop(columns=['dist'])    
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


if __name__ == "__main__": 

    # Define file attributes
    infile = '/home/pho/Desktop/python_workspace/GrIML/src/griml/test/test_merge_1.shp'
    names = '/home/pho/Desktop/python_workspace/GrIML/other/datasets/placenames/oqaasileriffik_placenames_polarstereo.shp'


    # Perform conversion
    a = assign_names(infile, names)