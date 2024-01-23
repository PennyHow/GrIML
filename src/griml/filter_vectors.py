#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GrIML processing module playground (experimental)

@author: Penelope How
"""

import geopandas as gpd
from pathlib import Path
import glob


def filter_area(iml, max_area=0.05):
    '''Filter lakes by area'''
    iml['area_sqkm'] = iml['geometry'].area/10**6
    iml['length_km'] = iml['geometry'].length/1000
    iml = iml[(iml.area_sqkm >= max_area)]
    return iml

def filter_margin(iml, margin_buffer):
    '''Perform spatial join'''
    iml = gpd.sjoin(iml, margin_buffer, how='left')
    iml = iml[iml['index_right']==0]
    iml = iml.drop(columns='index_right')

    # Calculate geometry info
    iml.reset_index(inplace=True, drop=True)
    return iml
    

if __name__ == "__main__": 
    indir = "/home/pho/python_workspace/GrIML/other/iml_2017/vectors/*.shp"   
    
    infile_margin = "/home/pho/python_workspace/GrIML/other/datasets/ice_margin/gimp_icemask_line_polstereo_simple_buffer.shp"
    print('Preparing ice margin buffer...')
    margin_buff = gpd.read_file(infile_margin)   
    # margin_buff = margin.buffer(500)
    # margin_buff = gpd.GeoDataFrame(geometry=margin_buff, crs=margin.crs)
    
    count=1
    for infile in list(glob.glob(indir)):
        
        print('\n'+str(count)+'. Filtering vectors in '+str(Path(infile).stem))
        vectors = gpd.read_file(infile)

        vectors = filter_area(vectors)
        print(f'{vectors.shape[0]} features over 0.05 sq km')
        
        vectors = filter_margin(vectors, margin_buff)
        print(f'{vectors.shape[0]} features within 500 m of margin')    

        if vectors.shape[0]>0:   
        	vectors.to_file("filtered_vectors/"+str(Path(infile).stem)+"_filtered.shp")
        else:
        	print('No vectors present after filter. Moving to next file.')
        count=count+1
