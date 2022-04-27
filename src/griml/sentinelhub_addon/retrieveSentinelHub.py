#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 12:55:07 2022

@author: pho
"""

import rasterio as rio
import geopandas as gp
from rasterio.features import shapes


def fromSHRequest():
    pass


def fromSHBatch():
    pass


#Vectorisation function
def getGeodata(img, trans):
    '''Get vector features from binary raster image. Raster data is loaded 
    from array as a rasterio inmemory object, and returns features as a 
    geopandas dataframe.

    Variables
    img (arr)                           Binary raster array
    trans (Affine):                     Raster transformation (computed using
                                        affine package, or 
                                        rasterio.transform) 
    Returns
    feats (Geodataframe):               Vector features geodataframe
    '''
    #Open array as rasterio memory object
    with rio.io.MemoryFile() as memfile:
        with memfile.open(
            driver='GTiff',
            height=img.shape[0],
            width=img.shape[1],
            count=1,
            dtype=img.dtype,
            transform=trans
        ) as dataset:
            dataset.write(img, 1)
        
        #Vectorize array
        with memfile.open() as dataset:
                image = dataset.read(1)
                mask = image==255
                results = (
                {'properties': {'raster_val': v}, 'geometry': s}
                for i, (s, v) 
                in enumerate(
                    shapes(image, 
                           mask=mask, 
                           transform=rio.transform.from_origin(trans[0], 
                                                               trans[3], 
                                                               trans[1], 
                                                               trans[5]))))
                
                ##Transform geometries to geodataframe
                geoms = list(results)
                feats = gp.GeoDataFrame.from_features(geoms)
                
    return feats