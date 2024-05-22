#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import geopandas as gpd
import pandas as pd
import os, errno
from pathlib import Path

def load(i): 
    '''Load vectors into appropriate format for processing

    Parameters
    ----------
    i : str, geopandas.geodataframe.GeoDataFrame, pandas.core.series.Series
        Input vectors (either from file or vector object)

    Returns
    -------
    out : geopandas.geodataframe.GeoDataFrame
        Output vector object
    '''
    if is_string(i):
        if is_filepath(i):
            out = load_vector_from_file(i)
            return out
        
        else:
            ValueError('Expected valid vector filepath, but instead got '+i)

    elif is_geo_object(i):
        out = i
        return out
    
    else:  
        TypeError('Expected str, geopandas.geodataframe.GeoDataFrame or pandas.core.series.Series object, but instead got '+str(type(i)))
    
def load_vector_from_file(infile):
    '''Load vector object from file'''
    gdf = gpd.read_file(infile)
    return gdf

def is_string(n):
    '''Check if input for loading is string'''
    if type(n)==str:
        return True
    else:
        return False

def is_filepath(n):
    '''Check if string is valid file'''
    if os.path.isfile(n):
        return True
    else:
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), n)

def is_dir(n):
    '''Check if string is valid directory'''
    if os.path.isdir(str(Path(n).parent)):
        return True
    else:
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), n)
    
def is_geo_object(typ):
    '''Check if object is valid vector object'''
    if type(typ)==gpd.geodataframe.GeoDataFrame or type(typ)==pd.core.series.Series:
        return True
    else:
        return False
        
if __name__ == "__main__": 
    infile1 = '../test/test_icemask.shp'
    test1 = load(infile1)
    
    g = gpd.read_file(infile1)
    test2 = load(g)

    infile2 = '../test/test_icemsak.shp'
    test2 = load(infile2)