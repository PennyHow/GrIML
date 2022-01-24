#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 11:57:31 2022

@author: pho
"""
# import process
# import analyse

import affine
import fiona
import geopandas as gpd
import rasterio
from rasterio import features
from rasterio.mask import mask 
import matplotlib.pyplot as plt

# class IML(object):
    
#     def __init__(self, database):
#         self.gpd= database
    
#     def getGeometry(self):
#         return self.geometry
    
    
#     def removeDuplicates(self):
#         pass


def fromMemory(img, shape_mask, mask_value, transf):
    '''Get vector features from binary raster image. Raster data is loaded 
    from array as a rasterio inmemory object, and returns features as a 
    geopandas dataframe.

    Parameters
    ----------
    img : arr
       Binary raster array
    mask_value : int
       Value for classified cells
    trans : Affine                     
       Raster transformation (computed using affine package, or 
       rasterio.transform) 
       
    Returns
    -------
    feats : geopandas.Geodataframe
       Vector features geodataframe
    '''
    # Open array as rasterio memory object
    with rasterio.io.MemoryFile() as memfile:
        with memfile.open(
            driver='GTiff',
            height=img.shape[0],
            width=img.shape[1],
            count=1,
            dtype=img.dtype,
            transform=transf
        ) as dataset:
            dataset.write(img, 1)
        
        # Read binary band
        with memfile.open() as src:

            # Get raster transform
            t = _getTransform(transf)
            
            feats = fromBinFile(src, shape_mask, mask_value, t)

        #     image = src.read(1)
                    
        #     # Vectorise binary band
        #     geoms = _reclassBinary(image, t, mask_value)
                
        # # Return as geodataframe
        # feats = gpd.GeoDataFrame.from_features(geoms)
    return feats


def fromBinFile(raster, shape_mask, mask_value, transf=None):
    '''Get vector features from binary raster image. Raster data is loaded 
    from raster file, and returns features as a geopandas dataframe.

    Parameters
    ----------
    raster : rasterio.io.DatasetReader
       Raster file as loaded rasterio dataset
     shape_mask : list
       List of vector GeoJSON-like dict or an object that implements the Python 
       geo interface protocol (such as a Shapely Polygon)
    mask_value : int
       Value for classified cells
    transf : list/affine.Affine, optional
       Raster transformation properties

    Returns
    -------
    feat : geopandas.Geodataframe
       Vector features geodataframe
    '''    
    # Mask raster with mask shapefile
    if shape_mask != None:
        cropped = _maskRaster(src, shape_mask)
    
    else:    
        # Read transformation and band info
        cropped = src.read(1)

    # Check transform
    if transf != None:
        t = _getTransform(transf)
    else:
       t = _getTransform(src.transform)
    print(t)
            
    # Vectorise and transform to geodatabase
    binary = _reclassBinary(cropped, t, mask_value)
    feats = gpd.GeoDataFrame.from_features(binary, crs = src.crs)   
     
    return feats


def _maskRaster(raster, shps):
    '''Mask raster with shapefile

    Parameters
    ----------
    raster : arr
        Raster array
    shps : TYPE
        Masking shapes

    Returns
    -------
    arr 
       Masked raster array
    '''
    # with fiona.open("tests/data/box.shp", "r") as shapefile:
    #     shapes = [feature["geometry"] for feature in shapefile]

    out_image, out_transform = mask(raster, shps, crop=False)
    
    return out_image
      
  
def _reclassBinary(binary, transf, reclass):  
    '''Vectorise binary raster
    
    Parameters
    ----------
    binary : arr
       Binary raster band array
    transf : affine.Affine
       Raster transformation
    reclass : int
       Value for classified cells
    
    Returns
    -------
    list
       Shape features (as list of dictionaries)
    '''
    mask_value = binary == reclass 
    
    # Vectorise
    results = (
        {'properties': {'raster_val': v}, 'geometry': s}
        for i, (s, v) 
        in enumerate(
            features.shapes(binary, 
                    mask=mask_value, 
                    transform=transf)))
        
    # Return as list of geometries
    return list(results)


def _getTransform(transf):
    '''Raster transformation checker'''
    if isinstance(transf, affine.Affine):
        return transf
    elif isinstance(transf, list):
        transf = rasterio.transform.from_origin(transf[0], transf[3], 
                                           transf[1], transf[5])
    return transf
    
if __name__ == "__main__":   
    r =   'test/S2A_L1C_T22WEV_R025_20190802_RECLASS3.tif'  
    shp = 'test/test_mask.shp'  

    with rasterio.open(r) as src:
        with fiona.open(shp, "r") as shapefile:
            shapes = [feature["geometry"] for feature in shapefile]
            s = fromBinFile(src, shapes, 1)
            
    s.plot()
    # print(s.crs)