#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GrIML filter vectors

@author: Penelope How
"""

def filter_area(iml, max_area=0.05):
    '''Filter lakes by area'''
    iml['area_sqkm'] = iml['geometry'].area/10**6
    iml['length_km'] = iml['geometry'].length/1000
    iml = iml[(iml.area_sqkm >= max_area)]
    return iml
