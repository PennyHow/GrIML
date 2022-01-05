# -*- coding: utf-8 -*-
"""
Script for processing DEMs for use with Asiaq's Wingtra and Ebee UAVs

@author: PENELOPE HOW
"""

#Import packages needed
import argparse
import os, sys
import arcpy
from arcpy import env
from arcpy.sa import Con, IsNull, Raster, Plus, Minus, FocalStatistics, NbrRectangle      
sys.path.append('.')

# #------------------------------------------------------------------------------
#Activate parser and parser arguments
parser = argparse.ArgumentParser(description='A script to merge, reproject ' 
                                  + 'and mask a set of DEMs')

parser.add_argument('--tifs', required=True, type=str, help='Filenames of ' +
                    'DEMs to process')

parser.add_argument('--uav', required=True, type=str, 
                    help='Drone type for DEM processing. If "wingtra", DEM '+
                    'will be processed with mean sea level datum. If ' + 
                    '"ebee", then DEM will be processing with ellipsoid datum')

parser.add_argument('--proj',  default=None, type=int,
                    help='ESPG number of projection that DEMs will be ' + 
                    'reprojected to')

parser.add_argument('--cellsize',  default=None, type=int,
                    help='Cell size that outputted raster will be resampled to')

parser.add_argument('--mask', default=None, type=str, help='Filename of mask shapefile')

parser.add_argument('--invert', default=False, type=bool, help='Flag to ' +
                    'denote if mask should be inverted e.g. if a coastline ' +
                    'shapefile is inputted as --mask')

parser.add_argument('--bound', default=None, type=str, help='Filename to ' +
                    'bounding box shapefile')

parser.add_argument('--geoid', default='G:/geoide_GGEIOD16/ggeoid16.tif', 
                    type=str, help='Geoid model to transform ellipsoid ' + 
                    'datum to mean sea level')

parser.add_argument('--outfile', default="output_dem.tif", type=str, 
                    help='Outputted DEM filename')

#parser.add_argument('--loc',  default=Path.getcwd(), type=str, 
#                    help='Directory (folder location) of files')

parser.add_argument('--loc',  default=os.getcwd(), type=str, 
                    help='Directory (folder location) of files')

parser.add_argument('--clean', default=True, type=bool, help='Flag to ' +
                    'denote if intermediary files should be cleaned after ' +
                    'successful processing')
#Retrieve arguments
args = parser.parse_args()

#Retrieve tif files from list    
demFiles = args.tifs
demFiles = demFiles.split(',')
    
#Retrieve other variables
proj = args.proj
uav = args.uav
directory = args.loc+'/'
outCell = args.cellsize
maskFile = directory + args.mask
invert = args.invert
boundFile = args.bound
geoidFile = args.geoid
outFile = directory + args.outfile
clean = args.clean

#------------------------------------------------------------------------------

def removeFile(filename):
    if os.path.isfile(filename) is True:
        try:
            os.remove(str(filename))
            print(filename + ' removed')
        except:
            print(filename + ' could not be removed. Check permissions.')
            pass

#------------------------------------------------------------------------------

#Begin procedure
print('Commencing DEM processing...')
env.workspace = directory
env.overwriteOutput = True
env.cellSize=outCell

print('Inputted parameters...')
print('DEM files: ')    
[print(d) for d in demFiles]
print('UAV type: ' + uav)
print('Outputted cellsize: '+ str(outCell))
print('Outputted projection: EPSG' + str(proj))
print('Active directory: ' + directory)
print('Mask file: ' + maskFile)
print('Invert mask? ' + str(invert))
print('Bounding box file: ' + boundFile)
print('Geoid file: ' + geoidFile)
print('Outputted DEM file: ' + outFile)
print('Remove intermediary files when complete? ' + str(clean))


#Retrieve tif files from list
count = 1
print('\nChecking DEM datum types...')
newFiles=[]
for d in demFiles:
    coord = arcpy.Describe(d).spatialReference
    print('\nFile ' + str(count) + '. ' + str(d) + ' (' + str(coord.name) +')')
    if uav in ['wingtra','Wingtra']:
        if coord.name in ['Polar_Stereographic']: 
            print(str(coord.name) + ' datum incompatible with Wingtra. ' +
                  'Converting ellipsoid to MSL datum...')            
            out = Minus(Raster(d), Raster(geoidFile))
            rasFile = d.split('.')[0] + '_msl.' + d.split('.')[-1]
            newFiles.append(rasFile)
            out.save(rasFile) 
        else:
            print('Datum compatible with Wingtra')
            newFiles.append(d)
    

    else:
        if coord.name in ['Polar_Stereographic']: 
            print('Datum compatible with Ebee')
            newFiles.append(d)
        else:
            print(str(coord.name) + ' datum incompatible with Ebee. ' +
                  'Converting MSL to ellipsoid datum...')
            out = Plus(Raster(d), Raster(geoidFile))
            rasFile = d.split('.')[0] + '_ellip.' + d.split('.')[-1]
            newFiles.append(rasFile)
            out.save(rasFile) 
    count=count+1


             
#Merge DEMs
print('\nMerging DEMs...')
arcpy.MosaicToNewRaster_management(newFiles, directory,'merged_dem.tif', "", 
                                   '32_BIT_FLOAT', '', '1', 'FIRST', 'FIRST')
dem = Raster('merged_dem.tif')


#Mask DEM
if maskFile is not None:
    print('\nPreparing mask...')
    field = arcpy.ListFields(maskFile)[0]
    field = str(field.name)
    arcpy.PolygonToRaster_conversion(maskFile, field, 'mask_raster.tif', '', '', '')
    
    print('Raster mask generated: mask_raster.tif')
    maskRas = Raster('mask_raster.tif')     
    if invert is False:
        print('Masking DEM...')
        masked = Con(IsNull(maskRas), dem, 0)       
    else:
        print('Inverse masking DEM...')
        masked = Con(IsNull(maskRas), 0, dem)     
    arcpy.MosaicToNewRaster_management([masked,dem], directory, 'masked_dem.tif',
                                        "", '32_BIT_FLOAT', '10', '1', 'FIRST', 'FIRST')    
    dem = Raster('masked_dem.tif')


#Fill DEM
print('\nFilling holes in DEM...')
dem = Con(IsNull(dem), FocalStatistics(dem, NbrRectangle(10, 10),'MEAN'), dem)

           
#Reproject DEM
if proj is not None:
    print('\nReprojecting DEM to EPSG:' + str(proj) + '...')
    outproj = arcpy.SpatialReference(int(proj))
    arcpy.ProjectRaster_management(dem, 'reprojected_dem.tif', outproj,
                                   'BILINEAR', str(outCell))
    dem = Raster('reprojected_dem.tif')
 
       
#Clip DEM
if boundFile is not None:
    print('\nClipping DEM to bounding box...')
    arcpy.Clip_management(dem, '', 'clipped_dem.tif', boundFile, '', 'ClippingGeometry') 
    dem = Raster('clipped_dem.tif')

#Save final DEM to file
dem.save(outFile)
    

#Clean folder
if clean is True:
    print('\nCleaning folder ' + str(directory))
    removeFile(directory + 'merged_dem.tif')
    removeFile(directory + 'mask_raster.tif')
    removeFile(directory + 'masked_dem.tif')    
    removeFile(directory + 'reprojected_dem.tif')            
    removeFile(directory + 'clipped_dem.tif')
    
#------------------------------------------------------------------------------
print('\nFinished cleanDEM_exe.py')
