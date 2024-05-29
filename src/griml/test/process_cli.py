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
import glob, os
from argparse import ArgumentParser

def parse_griml_arguments():
    parser = ArgumentParser(description="Full post-processing workflow for "+
                            "creating ice marginal lake inventory")
    parser.add_argument('-r', '--root_dir', type=str, required=True,
                        help='Root directory to write files to')
    parser.add_argument('-i', '--in_dir', type=str, required=True,
                        help='Directory path to input raster files')
    parser.add_argument('-y', '--year', type=str, required=True, 
                        help='Year of inventory')
    parser.add_argument('-m', '--margin_file', type=str, required=True, 
                        help='File path to ice margin for spatial filtering')
    parser.add_argument('-n', '--names_file', type=str, required=True, 
                        help='File path to placenames file for metadata population')
    parser.add_argument('-p', '--proj', type=str, default='EPSG:3413', 
                        required=False, help='Projection (of input and output)')
    parser.add_argument('-s', '--steps', type=str, default='1111', 
                        required=False, help='Define which steps to include in'+
                        ' processing, where each value indicates: convert, '+
                        'filter, merge, and metadata. If set to zero, the '+
                        'step associated with that position is skipped')
    
    args = parser.parse_args()
    return args

def get_step_flags(a):
    '''Return step flags'''
    return a[0],a[1],a[2],a[3]
    

def check_dir(d):
    '''Check if directory exists and create it if it does not'''
    if not os.path.exists(d):
        os.mkdir(d)
     

def griml_process():
    '''Perform processing workflow'''
    args = parse_griml_arguments()
    
    s1, s2, s3, s4 = get_step_flags(args.steps)
    
    print('Commencing post processing for inventory year ' + args.year)
    print('Adopted projection: ' + args.proj)
    print('Writing outputs to ' + args.root_dir)
    
    root_dir = Path(args.root_dir)
    
    # Convert to vectors
    if s1:
        print('Converting rasters to vectors...')
        
        src=args.in_dir
        dest = str(root_dir.joinpath('vectors'))
        check_dir(dest)
        
        print('Reading from ' + src)
        print('Writing to ' + dest)
        
        band_info = [{'b_number':1, 'method':'VIS', 'source':'S2'}, 
                     {'b_number':2, 'method':'SAR', 'source':'S1'},
                     {'b_number':3, 'method':'DEM', 'source':'ARCTICDEM'}] 
        start=args.year+'0701' 
        end=args.year+'0831'
        
        infiles = list(glob.glob(src+'/*.tif'))    
        
        convert(infiles, args.proj, band_info, start, end, str(dest)) 


    # Filter vectors by area and proximity to margin
    if s2:        
        print('Filtering vectors...')
        
        src = str(root_dir.joinpath('vectors')) 
        dest = str(root_dir.joinpath('filtered')) 
        check_dir(dest)
       
        print('Reading from ' + src)
        print('Writing to ' + dest)
        
        # margin_buff = gpd.read_file(infile_margin)   
        # margin_buff = margin.buffer(500)
        # margin_buff = gpd.GeoDataFrame(geometry=margin_buff, crs=margin.crs)
        
        infiles = list(glob.glob(src+'/*.shp'))  
        
        filter_vectors(infiles, args.margin_file, dest)


    # Merge vectors    
    if s3:
        print('Merging vectors...')
        
        src = str(root_dir.joinpath('filtered'))  
        dest = root_dir.joinpath('merged/'+args.year+'_merged.shp')
        check_dir(dest.parent)
        
        print('Reading from ' + src)
        print('Writing to ' + str(dest))
        
        infiles = list(glob.glob(src+'/*.shp')) 
        
        merge_vectors(infiles, str(dest))    
    
    
    # Add metadata
    if s4:
        print('Adding metadata...')
        
        src = str(root_dir.joinpath('merged/'+args.year+'_merged.shp'))
        dest = root_dir.joinpath('metadata/'+args.year+'_metadata.shp')
        check_dir(dest.parent)
        
        print('Reading from ' + src)
        print('Writing to ' + str(dest))
         
        add_metadata(src, args.names_file, str(dest))

    print('Finished')
