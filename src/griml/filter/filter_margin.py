#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GrIML filter vectors

@author: Penelope How
"""

import geopandas as gpd

def filter_margin(iml, margin_buffer):
    '''Perform spatial join'''
    iml = gpd.sjoin(iml, margin_buffer, how='left')
    iml = iml[iml['index_right']==0]
    iml = iml.drop(columns='index_right')

    # Calculate geometry info
    iml.reset_index(inplace=True, drop=True)
    return iml
