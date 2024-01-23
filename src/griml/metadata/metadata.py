#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GrIML metadata assignment

@author: Penelope How
"""
from griml.metadata import assign_id, assign_sources, assign_certainty, \
    assign_names
import glob
import geopandas as gpd
from pathlib import Path

def metadata(indir, names):
    count=1
    for infile in glob.glob(indir):
        print('\n'+str(count)+'. Populating metadata for '+str(Path(infile).stem))
        iml = gpd.read_file(infile)
        
        print('Assigning ID...')
        iml = assign_id(iml)
        
        print('Assigning sources...')
        iml = assign_sources(iml)
        
        print('Assigning certainty scores...')
        iml = assign_certainty(iml)
        
        print('Assigning placenames...')
        iml = assign_names(iml)
        
        print('Saving file...')
        iml.to_file("metadata_vectors/"+str(Path(infile).stem)+"_metadata.shp")
        print('Saved to '+str(Path(infile).stem)+"_metadata.shp")
        count=count+1
        
        
if __name__ == "__main__": 
    indir = "/home/pho/python_workspace/GrIML/other/iml_2017/filtered_vectors/*.shp"
    
    infile_names = '/home/pho/python_workspace/GrIML/other/datasets/placenames/oqaasileriffik_placenames.shp'
    names = gpd.read_file(infile_names)
    
    metadata(indir, names)
