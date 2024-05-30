#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from griml.load import load
from griml.metadata import assign_id, assign_sources, assign_certainty, \
    assign_names, assign_regions
import geopandas as gpd

def add_metadata(iml, names, regions, outfile=None):
        
    iml = load(iml)
    names = load(names)
    regions = load(regions)
    
    print('Assigning ID...')
    iml = assign_id(iml)
        
    print('Assigning sources...')
    iml = assign_sources(iml)
        
    print('Assigning certainty scores...')
    n = ['S1','S2','ARCTICDEM']
    scores = [0.298, 0.398, 0.304]
    iml = assign_certainty(iml, n, scores)

    print('Assigning regions...')
    iml = assign_regions(iml, regions)
        
    print('Assigning placenames...')
    iml = assign_names(iml, names)
    
    if outfile:    
        print('Saving file...')
        iml.to_file(outfile)
        print('Saved to '+str(outfile)+"_metadata.shp")
        
        
if __name__ == "__main__": 
    infile1 = os.path.join(os.path.dirname(griml.__file__),'test/test_merge_2.shp')
    infile2 = os.path.join(os.path.dirname(griml.__file__),'test/test_placenames.shp')
    infile3 = os.path.join(os.path.dirname(griml.__file__),'test/greenland_basins_polarstereo.shp')
    add_metadata(infile1, infile2, infile3)
