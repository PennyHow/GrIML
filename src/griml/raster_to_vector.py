#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 14:27:48 2023

@author: pho
"""

import rasterio as rio
from shapely.geometry import shape
from rasterio.features import shapes
import geopandas as gpd
import pandas as pd
import glob
from pathlib import Path
# import numpy as np

def get_band_vectors(infile, band):
    '''Read raster band and extract shapes as polygon vectors'''
    mask = None
    with rio.Env():
        with rio.open(infile) as src:
            image = src.read(band) # first band
            mask = image == 1
            results = (
            {'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v) 
            in enumerate(
                shapes(image, mask=mask, transform=src.transform)))
            
    geoms = list(results)
    polys = [shape(g['geometry']) for g in geoms]
    return polys

def raster_to_vector(infile, outfile, proj, band_info, startdate, enddate):
    '''Convert raster to vector file with geopandas'''
    # Get vectors from bands
    dfs=[]
    for b in band_info:
        print('Retrieving vectors from band ' + str(b['source']) + '...')
        p = get_band_vectors(infile, b['b_number'])
        df = pd.DataFrame({'geometry': p, 'method': b['method'], 
                           'source': b['source'], 'startdate' : start, 
                           'enddate' : end})
        dfs.append(df)
            
    # Merge into single geodataframe
    all_gdf = pd.concat(dfs, ignore_index=True)
    all_gdf = gpd.GeoDataFrame(all_gdf, geometry=all_gdf.geometry, crs=proj)
    
    # Assign compatible index
    all_gdf["row_id"] = all_gdf.index + 1
    # all_gdf = all_gdf.reset_index(drop=False, inplace=False)
    all_gdf = all_gdf.set_index("row_id") 
    
    # Save and return
    all_gdf.to_file(outfile)
    return all_gdf    
    
if __name__ == "__main__": 

    # Define file attributes
    indir = list(glob.glob('/home/pho/Desktop/python_workspace/GrIML/other/iml_2017/binary_images/*.tif'))
    outdir = '/home/pho/Desktop/python_workspace/GrIML/other/iml_2017/vectors/'
    proj = 'EPSG:3413'
    band_info = [{'b_number':1, 'method':'VIS', 'source':'S2'},
                 {'b_number':2, 'method':'SAR', 'source':'S1'},
                 {'b_number':3, 'method':'DEM', 'source':'ARCTICDEM'}]
    start='20170701'
    end='20170831'
    
    # Iterate through files
    count=1
    for i in indir:
        print('\n'+str(count) + '. Converting ' + str(Path(i).name))
        
        # Convert raster to vector
        outfile = str(Path(outdir).joinpath(Path(i).stem+'.shp'))
        raster_to_vector(str(i), outfile, proj, band_info, start, end)
        
        print('Saved to '+str(Path(outfile).name))
        count=count+1
        
    print('Finished')
