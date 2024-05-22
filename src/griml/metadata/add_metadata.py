#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from griml.metadata import assign_id, assign_sources, assign_certainty, \
    assign_names
from griml.load import load
import geopandas as gpd

def add_metadata(iml_file, names_file, outfile=None):
    '''Add metadata to collection of features
    
    Parameters
    ----------
    iml_file : str, geopandas.dataframe.DataFrame
        Filepath or geopandas.dataframe.DataFrame object to assign metadata to

    Returns
    -------
    iml: geopandas.dataframe.GeoDataFrame
        Geodataframe with metadata
    '''
    
    # Load files
    iml = load(iml_file)
    names = load(names_file)
    
    # Perform metadata steps
    print('Assigning ID...')
    iml = assign_id(iml)
        
    print('Assigning sources...')
    iml = assign_sources(iml)
        
    print('Assigning certainty scores...')
    n = ['S1','S2','ARCTICDEM']
    scores = [0.298, 0.398, 0.304]
    iml = assign_certainty(iml, n, scores)
        
    print('Assigning placenames...')
    iml = assign_names(iml, names)
    
    # Save to file if given
    if outfile is not None:    
        print('Saving file...')
        iml.to_file(outfile)
        print('Saved to '+str(outfile))
    
    return iml
        
        
if __name__ == "__main__": 
    infile1 = '../test/test_merge_2.shp'            
    infile2 = '../test/test_placenames.shp'              
    add_metadata(infile1, infile2)
    
    iml = gpd.read_file(infile1) 
    names = gpd.read_file(infile2)
    add_metadata(iml, names)