# -*- coding: utf-8 -*-
"""
Script for processing DEMs for use with Asiaq's Wingtra and Ebee UAVs

@author: PENELOPE HOW
"""

#Import packages needed
import os, sys
import arcpy
from arcpy import env
from arcpy.sa import Con, IsNull, Raster, Plus, Minus, FocalStatistics, NbrRectangle      

# sys.path.append('.')
directory = 'D:/'
#INPUT PARAMETERS    

#DEM file names
demFiles = [directory + '18_38_2_1_2m_v3.0_reg_dem.tif', directory + '18_38_2_2_2m_v3.0_reg_dem.tif',
            directory + '18_39_1_1_2m_v3.0_reg_dem.tif', directory + '18_39_1_2_2m_v3.0_reg_dem.tif']

#Projection (e.g. UTM 22N)    
proj = 32622 

#UAV type (wingtra/ebee
uav = 'wingtra'

# #Working directory
# directory = 'P:/B35_Remote_Sensing/B35-15_UAS_drift/DEM_processing/'

#Cellsize
outCell = 30

# #ArcticDEM database location
# demLoc = 

#Mask file
maskFile = None

#Invert mask? (True/False)
invert = True

#Bounding box file
boundFile = 'P:/B62_Drone_Indtægt/B62-000 Potentielle Opgaver/P030_Ilulissat Icefiord/Project data/dem_extent.shp'

#Geoid file
geoidFile = 'G:/geoide_GGEIOD16/ggeoid16.tif'

#Output file name
outFile = directory + 'outputDEM.tif'

#Clean folder after processing? (True/False)
clean = False

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
print('Input files: ')

#Detect if input is either DEM files or shp
if isinstance(demFiles, list):
    [print(d) for d in demFiles]
    demFlag=True
elif isinstance(demFiles, str): 
    print(demFiles)
    demFlag=False
else:
    print('Invalid input files provided: ')
    print(demFiles)
    print('Amend input files and try again.')
    sys.exit(1)
    
print('UAV type: ' + uav)
print('Outputted cellsize: '+ str(outCell))
print('Outputted projection: EPSG' + str(proj))
print('Active directory: ' + str(directory))
print('Mask file: ' + str(maskFile))
print('Invert mask? ' + str(invert))
print('Bounding box file: ' + str(boundFile))
print('Geoid file: ' + str(geoidFile))
print('Outputted DEM file: ' + str(outFile))
print('Remove intermediary files when complete? ' + str(clean))

if demFlag==False:
    print('\nShapefile extent indicator detected. Proceeding to retrieve DEMs...')
    


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
print('\nFinished cleanDEM_script.py')
