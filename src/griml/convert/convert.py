#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from griml.convert import raster_to_vector
import glob, os
from pathlib import Path

def convert(indir, proj, band_info, startdate, enddate, outdir=None):
    '''Compile features from multiple processings into one geodataframe

    Parameters
    ----------
    inlist : list
        List of files or geopandas.dataframe.DataFrame objects to merge

    Returns
    -------
    all_gdf : geopandas.dataframe.GeoDataFrame
        Compiled goedataframe
    '''
    
    # Iterate through files
    converted=[]
    count=1
    for i in indir:
        print('\n'+str(count) + '. Converting ' + str(Path(i).name))
        
        # Convert raster to vector
        if outdir is not None:
            outfile = str(Path(outdir).joinpath(Path(i).stem+'.shp'))
            g = raster_to_vector(str(i), proj, band_info, startdate, enddate, outfile)
            print('Saved to '+str(Path(outfile)))
            
        else:
            g = raster_to_vector(str(i), proj, band_info, startdate, enddate)
        
        converted.append(g)
        count=count+1
        
    return (converted)
    
if __name__ == "__main__": 

    infile = os.path.join(os.path.dirname(griml.__file__),'test/test_north_greenland.tif')
    proj = 'EPSG:3413'
    band_info = [{'b_number':1, 'method':'VIS', 'source':'S2'},
                 {'b_number':2, 'method':'SAR', 'source':'S1'},
                 {'b_number':3, 'method':'DEM', 'source':'ARCTICDEM'}]
    start='20170701'
    end='20170831'

    convert([infile], proj, band_info, start, end)          
