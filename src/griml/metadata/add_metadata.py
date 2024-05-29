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
    # indir = "/home/pho/python_workspace/GrIML/other/iml_2017/merged_vectors/griml_2017_inventory.shp"
    indir = "/home/pho/python_workspace/GrIML/other/iml_2017/inspected_vectors/lakes_all-0000000000-0000037888_filtered.shp"

    
    infile_names = '/home/pho/python_workspace/GrIML/other/datasets/placenames/oqaasileriffik_placenames.shp'
    infile_regions = '/home/pho/python_workspace/GrIML/other/datasets/drainage_basins/greenland_basins_polarstereo.shp'

    
    outfile = "/home/pho/python_workspace/GrIML/other/iml_2017/metadata_vectors/griml_2017_inventory_final.shp"
    add_metadata(indir, infile_names, infile_regions, outfile)
