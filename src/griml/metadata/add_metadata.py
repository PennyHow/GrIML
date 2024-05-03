#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from griml.metadata import assign_id, assign_sources, assign_certainty, \
    assign_names
import geopandas as gpd

def add_metadata(iml, names, outfile):
        
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
    
    if outfile is not None:    
        print('Saving file...')
        iml.to_file(outfile)
        print('Saved to '+str(outfile))
        
        
if __name__ == "__main__": 
    # indir = "/home/pho/python_workspace/GrIML/other/iml_2017/merged_vectors/griml_2017_inventory.shp"
    indir = "/home/pho/python_workspace/GrIML/other/iml_2017/merged_vectors/griml_2017_inventory_first_intervention.shp"
    iml = gpd.read_file(indir)
    
    infile_names = '/home/pho/python_workspace/GrIML/other/datasets/placenames/oqaasileriffik_placenames.shp'
    names = gpd.read_file(infile_names)
    
    outfile = "/home/pho/python_workspace/GrIML/other/iml_2017/metadata_vectors/griml_2017_inventory_final_first_intervention.shp"
    add_metadata(iml, names, outfile)
