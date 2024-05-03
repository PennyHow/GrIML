#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rasterio as rio
from shapely.geometry import shape
from rasterio.features import shapes
import geopandas as gpd
import pandas as pd

def raster_to_vector(infile, proj, band_info, startdate, enddate, outfile=None):
    '''Convert raster to vector file with geopandas
    
    Parameters
    ----------
    infile : str
        Input file location as string
    band_info : int
        Band number
    startdate : str
        Start date 
    enddate : str
        End date
     outfile : str, optional
         Output file location as string
         
    Returns
    -------
    all_gdf : geopandas.GeoDataFrame
        Converted vectors geodataframe
    '''
    # Get vectors from bands
    dfs=[]
    for b in band_info:
        print('Retrieving vectors from band ' + str(b['source']) + '...')
        p = _get_band_vectors(infile, b['b_number'])
        df = pd.DataFrame({'geometry': p, 'method': b['method'], 
                           'source': b['source'], 'startdate' : startdate, 
                           'enddate' : enddate})
        dfs.append(df)
            
    # Merge into single geodataframe
    all_gdf = pd.concat(dfs, ignore_index=True)
    all_gdf = gpd.GeoDataFrame(all_gdf, geometry=all_gdf.geometry, crs=proj)
    
    # Assign compatible index
    all_gdf["row_id"] = all_gdf.index + 1
    # all_gdf = all_gdf.reset_index(drop=False, inplace=False)
    all_gdf = all_gdf.set_index("row_id") 
    
    # Save and return
    if outfile is not None:
        all_gdf.to_file(outfile)
    return all_gdf

def _get_band_vectors(infile, band):
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
