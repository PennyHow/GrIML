#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import geopandas as gpd

def filter_margin(iml, margin_buffer):
    '''Filter vectors by polygon (such as a margin buffer) using a spatial join
    
    Parameters
    ----------
    iml : geopandas.GeoDataframe
        Vector object to filter by area
    margin_buffer: geopandas.GeoSeries
        Vector shape which will be used to filter
    
    Returns
    -------
    iml : geopandas.GeoDataframe
        Filtered vector object
    '''
    iml = gpd.sjoin(iml, margin_buffer, how='left')
    iml = iml[iml['index_right']==0]
    iml = iml.drop(columns='index_right')

    # Calculate geometry info
    iml.reset_index(inplace=True, drop=True)
    return iml
