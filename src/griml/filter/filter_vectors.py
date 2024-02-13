#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GrIML filter vectors

@author: Penelope How
"""

from griml.filter import filter_margin, filter_area
import geopandas as gpd
from pathlib import Path
import glob

def filter_vectors(indir, outdir, margin_buff):
    count=1
    for infile in list(glob.glob(indir)):
        
        print('\n'+str(count)+'. Filtering vectors in '+str(Path(infile).stem))
        vectors = gpd.read_file(infile)

        vectors = filter_area(vectors)
        print(f'{vectors.shape[0]} features over 0.05 sq km')
        
        vectors = filter_margin(vectors, margin_buff)
        print(f'{vectors.shape[0]} features within 500 m of margin')    

        if vectors.shape[0]>0:
            if outdir is not None:
                vectors.to_file(outdir+str(Path(infile).stem)+"_filtered.shp")
        else:
        	print('No vectors present after filter. Moving to next file.')
        count=count+1


if __name__ == "__main__": 
    indir = "/home/pho/python_workspace/GrIML/other/iml_2017/vectors/*.shp"   
    
    infile_margin = "/home/pho/python_workspace/GrIML/other/datasets/ice_margin/gimp_icemask_line_polstereo_simple_buffer.shp"
    print('Preparing ice margin buffer...')
    margin_buff = gpd.read_file(infile_margin)   
    # margin_buff = margin.buffer(500)
    # margin_buff = gpd.GeoDataFrame(geometry=margin_buff, crs=margin.crs)
    
    filter_vectors(indir, margin_buff)