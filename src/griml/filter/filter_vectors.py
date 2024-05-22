#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from griml.filter import filter_margin, filter_area
from griml.load import load
import geopandas as gpd
from pathlib import Path

def filter_vectors(inlist, margin_file, outdir=None, min_area=0.05):
    '''Filter vectors by area and margin proximity

    Parameters
    ----------
    inlist : list
        List of either file paths of GeoDataFrame objects to filter
    margin_file : str, geopandas.GeoSeries
        Bufferred margin to perform margin proximity filter
    outdir : str, optional
        Output directory to write files to
    min_area: int, optional
        Threshold area (sq km) to filter by
        
    Returns
    -------
    filtered : list
        List of filtered GeoDataFrame objects

    '''
    
    # Load margin
    margin_buff = load(margin_file)
    
    # Iterate through input list
    count=1
    filtered=[]
    for infile in inlist:
    
        # Load and define name
        if type(infile)==str:
            print('\n'+str(count)+'/'+str(len(inlist)) +
                  ': Filtering vectors in '+str(Path(infile).name))   
            name = str(Path(infile).stem)+"_filtered.shp"
            
        else:
            print('\n'+str(count)+'/'+str(len(inlist))) 
            name = 'lakes_' + str(count) + "_filtered.shp"
        
        vectors = load(infile)

        # Perform filtering steps
        vectors = filter_area(vectors, min_area)
        print(f'{vectors.shape[0]} features over 0.05 sq km')
        
        vectors = filter_margin(vectors, margin_buff)
        print(f'{vectors.shape[0]} features within 500 m of margin')    

        # Retain and save if vectors are present after filtering
        if vectors.shape[0]>0:
            if outdir is not None:
                vectors.to_file(Path(outdir).joinpath(name))
            filtered.append(vectors)
        else:
        	print('No vectors present after filter. Moving to next file.')
        count=count+1
        


if __name__ == "__main__": 
    infile1 = '../test/test_icemask.shp'
    margin_buff = gpd.read_file(infile1)
    
    infile2 = ['../test/test_filter.shp']       
    filter_vectors(infile2, margin_buff)
