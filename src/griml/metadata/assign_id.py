#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scipy.sparse.csgraph import connected_components

def assign_id(gdf, col_name='unique_id'):
    '''Assign unique identification numbers to non-overlapping geometries in
    geodataframe
    
    Parameters
    ----------
    gdf : pandas.GeoDataFrame
        Vectors to assign identification numbers to
    col_name : str
        Column name to assign ID from
    
    Returns
    -------
    gdf : pandas.GeoDataFrame
        Vectors with assigned IDs
    '''
    # Find overlapping geometries
    geoms = gdf['geometry']
    geoms.reset_index(inplace=True, drop=True)        
    overlap_matrix = geoms.apply(lambda x: geoms.overlaps(x)).values.astype(int)
    
    # Get unique ids for non-overlapping geometries
    n, ids = connected_components(overlap_matrix)
    ids=ids+1
    
    # Assign ids and realign geoedataframe index 
    gdf[col_name]=ids
    gdf = gdf.sort_values(col_name)
    gdf.reset_index(inplace=True, drop=True) 
    return gdf
