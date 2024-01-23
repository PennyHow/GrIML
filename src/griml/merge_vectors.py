#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 13:36:35 2024

@author: pho
"""
import geopandas as gpd
import pandas as pd

def merge_vectors(feature_list, method_list, collection_list, date_list,
                    proj='EPSG:4326'):
    '''Compile features from multiple processings into one geodataframe

    Parameters
    ----------
    feature_list : list
        List of shapely features
    method_list : list
        List of strings denoting processing method
    collection_list : list
        List of strings denoting dataset collection
    date_list : list
        List of start and end date for processing

    Returns
    -------
    all_gdf : geopandas.GeoDataFrame
        Compiled goedataframe
    '''
    dfs=[]
    for a,b,c in zip(feature_list, method_list, collection_list):
        if a is not None:
            
            #Construct geodataframe with basic metadata
            gdf = gpd.GeoDataFrame(geometry=a, crs=proj)
            gdf = dissolvePolygons(gdf)
            dfs.append(pd.DataFrame({'geometry': list(gdf.geometry), 
                                     'method': b, 
                                     'source': c, 
                                     'startdate' : date_list[0], 
                                     'enddate':date_list[1]}))   
           
    # Construct merged geodataframe
    all_gdf = pd.concat(dfs)
    all_gdf = gpd.GeoDataFrame(all_gdf, geometry=all_gdf.geometry, 
                               crs=proj)
    return all_gdf


def dissolvePolygons(gdf):
    '''Dissolve overlapping polygons in a Pandas GeoDataFrame

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        Geodataframe with polygons for dissolving

    Returns
    -------
    gdf2 : geopandas.GeoDataFrame
        Geodataframe with dissolved polygons
    '''
    geoms = gdf.geometry.unary_union
    gdf2 = gpd.GeoDataFrame(geometry=[geoms])
    gdf2 = gdf2.explode().reset_index(drop=True)
    return gdf2