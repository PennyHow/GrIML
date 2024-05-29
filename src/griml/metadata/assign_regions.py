#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import itertools
from operator import itemgetter

import geopandas as gpd
import numpy as np
import pandas as pd

from griml.load import load
from scipy.spatial import cKDTree
from shapely.geometry import Point, LineString, Polygon

def assign_regions(gdf, gdf_regions, region_name='region'):
    '''Assign region to geodataframe geometries based on regions in another 
    geodataframe object

    Parameters
    ----------
    gdf : pandas.GeoDataFrame
        Vectors to assign region name to
    gdf_regions : pandas.GeoDataFrame
        Vector geodataframe with regions
    
    Returns
    -------
    gdf : pandas.GeoDataFrame
        Vectors with assigned IDs
    '''                                      

    # Load geodataframes
    gdf1 = load(gdf)
    gdf2 = load(gdf_regions)
    
    g = _get_nearest_polygon(gdf1, gdf2)

    return g


def _get_nearest_polygon(gdfA, gdfB, gdfB_cols=['subregion'], distance=100000.0):
    '''Return given properties of nearest polygon in Y to geometry in X'''  
    
    A = np.array(list(gdfA.geometry.centroid.apply(lambda x: (x.x, x.y))))
    # B = [np.array(geom.boundary.coords) for geom in gdfB.geometry.to_list()]

    B=[]    
    for geom in gdfB.geometry.to_list():
        try:
            g = np.array(geom.boundary.coords)
        except:
            g = np.array(geom.boundary.geoms[0].coords)
        B.append(g)

    
    B_ix = tuple(itertools.chain.from_iterable(
        [itertools.repeat(i, x) for i, x in enumerate(list(map(len, B)))]))
    B = np.concatenate(B)
    ckd_tree = cKDTree(B)
    
    dist, idx = ckd_tree.query(A, k=1)
    idx = itemgetter(*idx)(B_ix)
    
    gdf = pd.concat(
        [gdfA, gdfB.loc[idx, gdfB_cols].reset_index(drop=True),
         pd.Series(dist, name='dist')], axis=1)
    
    gdf.loc[gdf['dist']>=distance, 'subregion'] = 'Unknown'
    
    gdf = gdf.drop(columns=['dist'])   
    return gdf


if __name__ == "__main__": 

    # Define file attributes
    infile = '/home/pho/Desktop/python_workspace/GrIML/src/griml/test/test_merge_1.shp'
    regions = '/home/pho/python_workspace/GrIML/other/datasets/drainage_basins/greenland_basins_polarstereo.shp'
    regions=gpd.read_file(regions)

    regions_dissolve = regions.dissolve(by='subregion')
    

    # Perform conversion
    a = assign_regions(infile, regions)
    
