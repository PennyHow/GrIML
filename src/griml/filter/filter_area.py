#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def filter_area(iml, min_area=0.05):
    '''Filter vectors in GeoDataframe object by a defined area
    
    Parameters
    ----------
    iml : geopandas.GeoDataframe
        Vector object to filter by area
    min_area: int, optional
        Threshold area (sq km) to filter by
    
    Returns
    -------
    iml : geopandas.GeoDataframe
        Filtered vector object
    '''
    iml['area_sqkm'] = iml['geometry'].area/10**6
    iml['length_km'] = iml['geometry'].length/1000
    iml = iml[(iml.area_sqkm >= min_area)]
    return iml
