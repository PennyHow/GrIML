#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 14:14:23 2021

Calculate percentage of a line passing through polygons

@author: pho
"""

import fiona
import geopandas as gpd
from shapely.geometry import shape


f1 = '/home/pho/Documents/LPF/2017_inventory/20170101-ESACCI-L3S_GLACIERS-IML-MERGED-fv1.shp'
f2 = '/home/pho/Documents/LPF/gimp_icemask_line_utm24n.shp'

polygons = fiona.open(f1)
line = fiona.open(f2)

geom_p1 = [ shape(feat["geometry"]) for feat in polygons ]
sline = [ shape(feat["geometry"]) for feat in line ]
sline = sline[0]

intersect=[]

for j, g8 in enumerate(geom_p1):
    if sline.intersects(g8):
        try:
            i = sline.intersection(g8)
            intersect.append(i.length)
        except:
            print('Invalid geometry!')

inter_sum = sum(intersect)
print(f'Intersecting line length: {inter_sum}')
print(f'Total ice margin length: {sline.length}')
print(f'% of intersection: {(inter_sum/sline.length)*100}%')
