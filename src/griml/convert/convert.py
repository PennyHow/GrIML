#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 14:27:48 2023

GrIML convert rasters to vectors

@author: Penelope How
"""

from griml.convert import raster_to_vector
import glob
from pathlib import Path

def convert(indir, outdir, proj, band_info, startdate, enddate, outfile=None):
    
    # Iterate through files
    converted=[]
    count=1
    for i in indir:
        print('\n'+str(count) + '. Converting ' + str(Path(i).name))
        
        # Convert raster to vector
        if outfile is not None:
            outfile = str(Path(outdir).joinpath(Path(i).stem+'.shp'))
            g = raster_to_vector(str(i), proj, band_info, startdate, enddate, None)
            print('Saved to '+str(Path(outfile).name))
            
        else:
            g = raster_to_vector(str(i), proj, band_info, startdate, enddate, outfile)
        
        converted.append(g)
        count=count+1
        
    print('Finished')
    return (converted)
    
if __name__ == "__main__": 

    # Define file attributes
    indir = list(glob.glob('/home/pho/Desktop/python_workspace/GrIML/other/iml_2017/binary_images/*.tif'))
    outdir = '/home/pho/Desktop/python_workspace/GrIML/other/iml_2017/vectors/'
    proj = 'EPSG:3413'
    band_info = [{'b_number':1, 'method':'VIS', 'source':'S2'},
                 {'b_number':2, 'method':'SAR', 'source':'S1'},
                 {'b_number':3, 'method':'DEM', 'source':'ARCTICDEM'}]
    start='20170701'
    end='20170831'

    # Perform conversion
    convert(indir, outdir, proj, band_info, start, end)    