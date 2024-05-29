#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: pho
"""
from griml.convert import convert
from griml.filter import filter_vectors
from griml.merge import merge_vectors
from griml.metadata import add_metadata
from pathlib import Path
import glob

root_dir = Path('/home/pho/python_workspace/GrIML/other/')
year='2016'

print('Commencing post processing for inventory year ' + year)

# Convert to vectors
print('Converting rasters to vectors...')

src = str(root_dir.joinpath('iml_2016-2023/rasters/'+year+'_iml'))
dest = str(root_dir.joinpath('iml_2016-2023/vectors/'+year))

print('Reading from ' + src)
print('Writing to ' + dest)

proj = 'EPSG:3413' 
band_info = [{'b_number':1, 'method':'VIS', 'source':'S2'}, 
             {'b_number':2, 'method':'SAR', 'source':'S1'},
             {'b_number':3, 'method':'DEM', 'source':'ARCTICDEM'}] 
start=year+'0701' 
end=year+'0831'

infiles = list(glob.glob(src+'/*.tif'))    

convert(infiles, proj, band_info, start, end, str(dest)) 


# Filter vectors by area and proximity to margin
print('Filtering vectors...')

src = dest 
dest = str(root_dir.joinpath('iml_2016-2023/filtered/'+year)) 
infile_margin = str(root_dir.joinpath('datasets/ice_margin/gimp_icemask_line_polstereo_simple_buffer.shp'))

print('Reading from ' + src)
print('Writing to ' + dest)

# margin_buff = gpd.read_file(infile_margin)   
# margin_buff = margin.buffer(500)
# margin_buff = gpd.GeoDataFrame(geometry=margin_buff, crs=margin.crs)

infiles = list(glob.glob(src+'/*.shp'))  

filter_vectors(infiles, infile_margin, dest)


# Merge vectors
print('Merging vectors...')

src = dest 
dest = str(root_dir.joinpath('iml_2016-2023/merged/'+year+'_merged.shp'))

print('Reading from ' + src)
print('Writing to ' + dest)

infiles = list(glob.glob(src+'/*.shp')) 

merge_vectors(infiles, dest)      
        

# Add metadata
print('Adding metadata...')

src = dest
dest = str(root_dir.joinpath('iml_2016-2023/metadata/'+year+'_metadata.shp'))

print('Reading from ' + src)
print('Writing to ' + dest)

infile_names = str(root_dir.joinpath('datasets/placenames/oqaasileriffik_placenames.shp'))

add_metadata(src, infile_names, dest)

print('Finished')
