#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 13:36:35 2024

GrIML merge vectors

@author: Penelope How
"""
import geopandas as gpd
import pandas as pd
from glob import glob

def merge_vectors(feature_list, method_list, collection_list, start_date_list,
                  end_date_list, proj='EPSG:3413'):
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
    for a,b,c,d,e in zip(feature_list, method_list, collection_list, start_date_list, end_date_list):
        if a is not None:
            
            #Construct geodataframe with basic metadata
            gdf = gpd.GeoDataFrame(geometry=a, crs=proj)
            # gdf = _dissolve_vectors(gdf)
            dfs.append(pd.DataFrame({'geometry': list(gdf.geometry), 
                                      'method': b, 
                                      'source': c, 
                                      'startdate' : d, 
                                      'enddate' : e}))   
           
    # Construct merged geodataframe
    all_gdf = pd.concat(dfs)
    all_gdf = gpd.GeoDataFrame(all_gdf, crs=proj, geometry=list(all_gdf.geometry))
    
    all_gdf["row_id"] = all_gdf.index + 1
    all_gdf.reset_index(drop=True, inplace=True)
    all_gdf.set_index("row_id", inplace = True)

    all_gdf['area_sqkm'] = all_gdf['geometry'].area/10**6
    all_gdf['length_km'] = all_gdf['geometry'].length/1000
    all_gdf = gpd.GeoDataFrame(all_gdf, geometry=all_gdf.geometry, 
                                crs=proj)
    return all_gdf


def _dissolve_vectors(gdf):
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

if __name__ == "__main__": 
    indir = "/home/pho/python_workspace/GrIML/other/iml_2017/test/*.shp"
    outfile = "/home/pho/python_workspace/GrIML/other/iml_2017/merged_vectors/griml_2017_inventory.shp"
    features=[]
    methods=[]
    sources=[]
    starts=[]
    ends=[]
    
    for f in list(glob(indir)):
        i = gpd.read_file(f)
    
        features.append(list(i['geometry']))
        methods.append(list(i['method']))
        sources.append(list(i['source']))
        starts.append(list(i['startdate']))
        ends.append(list(i['enddate']))
    vectors = merge_vectors(features, methods, sources, starts, ends)
    
    # features.append(i)
    # vectors = pd.concat(features, ignore_index=True)
    

    vectors.to_file(outfile)