# -*- coding: utf-8 -*-
"""
Created on Fri Mar 23 12:03:10 2018

@author: kal
"""

#Import libraries
import os
import subprocess
import gdal
import ogr
from pathlib import Path

import arcpy
from arcpy import env
from arcpy.sa import Int, Con, IsNull, SetNull, Raster, Slope, Hillshade, MajorityFilter, Expand, Shrink

#Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")
env.overwriteOutput = True


#---------------------------  0. Get scenes   ---------------------------------

def getFolders(scenes, tiles):
    '''Get scene folder directories, based on tile name.
    Args
    scenes (str):           Folder directory where scenes are located.
    
    Returns
    tiles (list):           List of folder directories with specified tiles
    '''
    #Create empty output
    folders=[]
    
    #Create path object from string
    root = Path(scenes)
    
    #Iterate through tile list
    for t in tiles:
        
        #Merge tile name with directory and check if it exists
        tilepath = root.joinpath(t)
        if tilepath.exists():
            
            #Get all directories in tile folder and append to output
            pathlist = tilepath.glob('R*/*')
            for i in pathlist:
                folders.append(i)
                    
        #Print statement if file directory to tiles not found
        else:
            print('Path not found: ' + str(tilepath))
     
    #Return list of folder directories with specified tiles
    return folders

#-------------------------  1. Resize scene   ---------------------------------
# Function for setting null values to 0
def nullset(band):
    band=SetNull(band, band, "VALUE = 0")
    return band

# Adjust cell size
def resizeband(band, outfilename, cellsize):
    band = arcpy.Resample_management(band, outfilename, cellsize,"NEAREST")
    return 1

def resize1(folders, out_dir):
    print('\n\nResizing scenes...')
       
    #Make output directory if it does not exist
    if os.path.exists(out_dir)==False:
        os.mkdir(out_dir)   
    count=1
    
    #Go into each folder and process
    print('Resizing tiffs from ' + str(len(folders)) + ' files')
    for fold in folders:
        
        #Get list of JP2 files
        jp2 = [] 
        jp2 = list(fold.glob('*_B*[0-9].jp2'))
        name = str(jp2[0].stem).split('_B')[0]        
        print('\n' + str(count) + '. Resizing from scene ' + str(name))  


        #Define output location for scene using scene name
        outputB11 = Path(out_dir).joinpath(name + '_B11RS.tif')
        outputB12 = Path(out_dir).joinpath(name + '_B12RS.tif')

        #Check if files both exist
        if os.path.isfile(str(outputB11))==True and os.path.isfile(str(outputB12))==True:
            print('Resized files already exist:')
            print(str(outputB11))
            print(str(outputB12))
            print('Moving to next file')

        else:            
            #Get bands 2, 11 and 12        
            b2 = str(jp2[1])
            b11 = str(jp2[10])
            b12 = str(jp2[11])
    
            #Flag if filename is too long        
            if len(b2) > 267:
                print('Filename too long for GDAL to compute: ' + str(b2))
            else:
     
                #Reference properties
                desc=arcpy.Describe(b2)
                arcpy.env.extent = b2
                
                #Resize to 10m
                b2N=nullset(b2)
                b11N=nullset(b11)
                b12N=nullset(b12)
                cellsize = desc.meanCellWidth
    
                #Resize cell size if B11RS file does not exist           
                if os.path.isfile(str(outputB11))==True:
                    print('Resized B11 file already exists: ' + str(outputB11))
                else:
                    print('Writing resized file to ' + str(outputB11))
                    resizeband(b11N, str(outputB11), cellsize) 
    
                if os.path.isfile(str(outputB12))==True:
                    print('Resized B12 file already exists: ' + str(outputB12))
                else:                
                    print('Writing resized file to ' + str(outputB12))
                    resizeband(b12N, str(outputB12), cellsize) 
                
                b2=None
                b2N=None
                b11=None
                b11N=None
                b12=None
                b12N=None 
        count=count+1

    
#--------------------   2. Cloud gml to raster   ------------------------------

def cloudtoraster2(folders, out_dir):
    print('\n\nConverting cloud GMLs to rasters...')

    #Make output directory if it does not exist
    if os.path.exists(out_dir)==False:
        os.mkdir(out_dir) 
    count=1
    
    #Go into each folder and process
    print('Creating cloud masks from ' + str(len(folders)) + ' files')
    for fold in folders:
    
        #Define scene name
        output = Path(out_dir)
        jp2 = [] 
        jp2 = list(fold.glob('*_B*[0-9].jp2'))
        name = str(jp2[0].stem).split('_B')[0]        
        print('\n' + str(count) + '. Resizing from scene ' + str(name))     
        
        #Find cloud mask
        cld=None
        for root, dirs, files in os.walk(str(fold)):
            for file in files:
                if file.endswith('MSK_CLOUDS_B00.gml'):
                    cld = Path(root).joinpath(file) 
        
        #Move to next file if no cloud file found
        if cld is None:
            print('No cloud file found. Moving to next file')
        
        #Proceed if cloud file found
        else:
            print('Found cloud cover file: ' + str(cld.name))

            #Make cloud file if file does not exist        
            output_shp = output.joinpath(name + '_CLOUDMASK.shp')
            if os.path.isfile(output_shp)==True:
                print('Cloud shapefile already exists: ' + str(output_shp))             
            else:
                print('Creating cloud shapefile:  ' + str(output_shp.name))
                completed=subprocess.run("C:\\Program Files\\QGIS 3.4\\bin\\ogr2ogr.exe -f \"ESRI Shapefile\" " 
                                         + str(output_shp) + " " + str(cld))  
                print(completed)
            
            # Rasterise a shapefile to the same projection & pixel  
            #resolution as a reference image. 
            #https://gis.stackexchange.com/questions/222394/how-to-convert-file-shp-to-tif-using-ogr-or-python-or-gdal/222395
            
            #Create tif file for writing to
            output_rast = str(output_shp).split('.shp')[0]
            output_rast = output_rast + 'RAS.tif'

            #Does file already exist
            if os.path.isfile(output_rast)==True:
                print('Cloud raster file already exists: ' + str(output_rast))             
            else:
                print('Creating cloud shapefile:  ' + str(output_rast))
                
                #Read reference raster
                RefImage = jp2[1]
                print('Reading reference image: ' + str(RefImage.name))
                
                #Value for the output image pixels
                gdalformat = 'GTiff'
                datatype = gdal.GDT_Byte
                burnVal = 1                         
            
                #Get projection info from reference image
                b2_img = gdal.Open(str(RefImage), gdal.GA_ReadOnly)
            
                #Rasterise shapefile
                print('Rasterising shapefile: ' + str(output_rast))
                Output = gdal.GetDriverByName(gdalformat).Create(str(output_rast), 
                                             b2_img.RasterXSize, 
                                             b2_img.RasterYSize, 1, 
                                             datatype, 
                                             options=['COMPRESS=DEFLATE'])
                Output.SetProjection(b2_img.GetProjectionRef())
                Output.SetGeoTransform(b2_img.GetGeoTransform()) 
                
                #Write data to band 1
                Band = Output.GetRasterBand(1)
                Band.SetNoDataValue(0)
            
                #Open Shapefile
                if os.path.isfile(output_shp):
                    Shapefile = ogr.Open(str(output_shp))
                    Shapefile_layer = Shapefile.GetLayer()
                    gdal.RasterizeLayer(Output, [1], Shapefile_layer, 
                                        burn_values=[burnVal])
                    
                    #Close datasets
                    Band = None
                    Output = None
                    b2_img = None
                    Shapefile = None
                    
                else:
                   print('Shapefile does not exist. Moving to next file')
                   Band = None
                   Output = None
                   b2_img = None
                   Shapefile = None
           
        count=count+1
       
       
#----------------------   3. Terrain indices   --------------------------------

def sunparam(xmlfile):
        # set variable and search strings
    rootstr = "<Mean_Sun_Angle>"
    list_nm = []
    #open and extract parts of file
    with open(xmlfile,'rt') as infile:
        found = -1
        for (lineno, ln) in enumerate(infile):
            if ln.find(rootstr)>=0:
                found = lineno
                continue
            if 1<= (lineno-found) <=2:
                list_nm.append(ln.rstrip('\n'))           
    infile.close()
    #tidy up
    sunzenith=float(list_nm[2][33:-15])
    sunazimuth=float(list_nm[3][34:-16])
    sunaltitude=90-sunzenith
    return sunazimuth, sunaltitude

def resize_DEM(DEM, dem_temp, desc, b2):
    arcpy.env.extent = b2
    cellsize = desc.meanCellWidth
    dem=arcpy.ProjectRaster_management(DEM, dem_temp, desc.spatialReference, 
                                       "BILINEAR", cellsize) 
    return dem

def slp(dem, outfile):
    slope=Slope(dem, "DEGREE")
    slope.save(outfile)
    return
    
def hillsh(dem, sunazimuth, sunaltitude, outfile):
    HS=Hillshade(dem, sunazimuth, sunaltitude, "SHADOWS", 1)
    HS.save(outfile)
    return

def terrain3(folders, out_dir, DEM):
    print('\n\nGenerating terrain indices...')

    #Make output directory if it does not exist
    if os.path.exists(out_dir)==False:
        os.mkdir(out_dir) 
    count=1
            
    #Go into each folder and process
    print('Creating terrain masks from ' + str(len(folders)) + ' files')
    for fold in folders:
        
        #Define scene name
        jp2 = list(fold.glob('*_B*[0-9].jp2'))
        name = str(jp2[0].stem).split('_B')[0]        
        print('\n' + str(count) + '. Preparing terrain from ' + str(name)) 
                        
        #Reference properties
        b2 = jp2[1]
        desc=arcpy.Describe(str(b2))
        arcpy.env.extent = str(b2)
        print('Getting reference properties from ' + str(b2.name))
        
        #Get XML file from fold
        xmlfile=None
        for root, dirs, files in os.walk(str(fold)):
            for file in files:
                if file.endswith('MTD_TL.xml'):
                    xmlfile = Path(root).joinpath(file)
        
        if xmlfile is None:
            print('MTD_TL.xml file not found in directory. ' + 
                  'Moving to next file')
        else:
            print('XML file retrieved: ' + str(xmlfile))
            
            #Get scene sun parameters 
            (sunazimuth, sunaltitude) = sunparam(str(xmlfile))
        
            #Resample DEM to scene area and px size
            outfile = Path(out_dir).joinpath(str(name) + '_TMPDEM.tif')
            print('Creating resampled DEM... ')
            if os.path.isfile(outfile)==False:
                dem = resize_DEM(DEM, str(outfile), desc, str(b2))
                print('Resampled DEM created: ' + str(outfile))
            else:
                print('Resampled DEM file already exists: ' + str(outfile))
            
            #Calculate and save slope
            outfile = Path(out_dir).joinpath(str(name) + '_SLOPE.tif')
            print('Creating slope TIFF... ')
            if os.path.isfile(outfile)==False:
                slp(dem, str(outfile))
                print('Slope TIFF created: ' + str(outfile))
            else:
                print('Slope TIFF file already exists: ' + str(outfile))
                
            #Calc and save HS
            outfile = Path(out_dir).joinpath(str(name) + '_HILLSHADE.tif')
            print('Creating hillshade TIFF... ')
            if os.path.isfile(outfile)==False:
                hillsh(dem, sunazimuth, sunaltitude, str(outfile))
                print('Hilshade TIFF created: ' + str(outfile))
            else:
                print('Hillshade TIFF file already exists: ' + str(outfile))
                
        count=count+1
    
    
#----------------------   4. Spectral indices   -------------------------------
def MNDWI(b3, b11, outfilename):
    b3 = b3*1.0
    b11 = b11*1.0
    ind = ((b3-b11)/(b3+b11))
    ind.save(outfilename)
    return 1

def NDWI(b3, b8, outfilename):
    b3=b3*1.0
    b8 = b8*1.0
    ind = ((b3-b8)/(b3+b8))
    ind.save(outfilename)
    return 1

def AWEIsh(b2, b3, b8, b11, b12, outfilename):
    ind = (b2+2.5*b3-1.5*(b8+b11)-0.25*b12)
    ind.save(outfilename)
    return 1

def AWEInsh(b3, b8, b11, b12, outfilename):
    ind = (4*(b3-b11)-(0.25*b8+2.75*b12))
    ind.save(outfilename)
    return 1

def BRIGHT(b4, b3, b2, outfilename):
    ind = ((b4+b3+b2)/3)
    ind.save(outfilename)
    return 1

def spectral4(folders, resizedfiles, output):
    print('\n\nGenerating spectral indices...')
    
    #Make output directory if it does not exist
    if os.path.exists(output)==False:
        os.mkdir(output) 
    count=1
    
    #Go into each folder and process
    print('Creating spectral indices from ' + str(len(folders)) + ' files')
    for fold in folders:
        
        #Define scene name
        jp2 = list(fold.glob('*_B*[0-9].jp2'))
        name = str(jp2[0].stem).split('_B')[0]              
        print('\n' + str(count) + '. Creating spectral indices from ' + str(name))

        #Check if spectral indices have already been calculated
        if os.path.isfile(str(Path(output).joinpath(name+'_BRIGHT.tif')))==True:
            print('Spectral indices already calculated, moving to next file')
        else:
        
            #Get resized JP2 files             
            print('Fetching resized raster scenes from: ' + str(resizedfiles))        
            jp2rs = list(Path(resizedfiles).glob(name+'*RS.tif'))
    
            #Compile rasters
            b2f = nullset(str(jp2[1]))
            b3f = nullset(str(jp2[2]))
            b4f = nullset(str(jp2[3]))
            b8f = nullset(str(jp2[7]))
            b11f = nullset(str(jp2rs[0]))
            b12f = nullset(str(jp2rs[1]))
            b2 = str(jp2[0])
            desc=arcpy.Describe(b2)
            arcpy.env.extent = b2
            
            #Calculate indices and write out
            outfilename = Path(output).joinpath(name+'_MNDWI.tif')
            if os.path.isfile(outfilename)==False:
                print('Writing MNDWI file: ' + str(outfilename))
                MNDWI(b3f, b11f, str(outfilename))
            else:
                print('MNDWI file already exists: ' + str(outfilename))
                    
            outfilename = Path(output).joinpath(name+'_NDWI.tif')
            if os.path.isfile(outfilename)==False:
                print('Writing NDWI file: ' + str(outfilename))
                NDWI(b3f, b8f, str(outfilename))
            else:
                print('NDWI file already exists: ' + str(outfilename))
            
            outfilename = Path(output).joinpath(name+'_AWEIsh.tif')
            if os.path.isfile(outfilename)==False:
                print('Writing AWEIsh file: ' + str(outfilename))
                AWEIsh(b2f, b3f, b8f, b11f, b12f, str(outfilename))
            else:
                print('NDWI file already exists: ' + str(outfilename))
                
            outfilename = Path(output).joinpath(name+'_AWEInsh.tif')
            if os.path.isfile(outfilename)==False:
                print('Writing AWEInsh file: ' + str(outfilename))
                AWEInsh(b3f, b8f, b11f, b12f, str(outfilename))
            else:
                print('AWEInsh file already exists: ' + str(outfilename))
                
            outfilename = Path(output).joinpath(name+'_BRIGHT.tif')
            if os.path.isfile(outfilename)==False:
                print('Writing BRIGHT file: ' + str(outfilename))
                BRIGHT(b4f, b3f, b2f, str(outfilename))
            else:
                print('BRIGHT file already exists: ' + str(outfilename))
            
            b2f = None
            b3f = None
            b4f = None
            b8f = None
            b11f = None
            b12f = None
            b2 = None
            arcpy.env.extent = None
        count=count+1
    
#--------------------   5. Lake classification   ------------------------------
    
def isnullto0CL(rast, nullval, fold):
    rast = Con(IsNull(rast),nullval,rast)    
    rast.save(fold+'/MSK_CLOUDS_B00_1.tif')
    return rast

def tidy_class(classif):
    outMajFilt = MajorityFilter(classif, "EIGHT", "MAJORITY")
    outExpand = Expand(outMajFilt, 2, [10])
    outShrink = Shrink(outExpand, 2, [10])
    return outShrink

def rast_filt(outShrink):
    water = Con(outShrink==10,1,0)
    water=SetNull(water, water, "VALUE = 0")
    return water

def lakeclass5(indices_dir, terrain_dir, cloud_dir, out_dir):
    print('\n\nClassifying lakes...') 

    #Make output directory if it does not exist
    if os.path.exists(out_dir)==False:
        os.mkdir(out_dir) 
    
    #Set workspace
    workspace = indices_dir
    env.workspace = workspace
    count=1
    
    #List of S2 folders
    uniquenames = list(Path(indices_dir).glob('*_NDWI.tif'))
    names=[]
    for u in uniquenames:
        names.append(str(u.name).split('_NDWI')[0])
    print('Classifying lakes from ' + str(len(names)) + ' files')
    
    #Call each name and process 
    for n in names:
        print('\n' + str(count) + '. Executing lake classification on ' 
              + str(n))
        
        #Check to see if lake classification files already exist
        if os.path.isfile(str(Path(out_dir).joinpath(n + '_WATERFILT.shp'))):
            print('Lake classification files already exist, moving to next file')
        else:
        
            #Get hillshade tiff
            HS = Raster(str(Path(terrain_dir).joinpath(n+'_HILLSHADE.tif')))
            outHS = Con(IsNull(HS),-9999,HS)
            outHS.save(str(Path(terrain_dir).joinpath(n+'_HILLSHADENULL.tif')))
            print('Hillshade null mask saved: ' + 
                  str(Path(terrain_dir).joinpath(n+'_HILLSHADENULL.tif')))
            
            #Get cloud mask
            cloudn = Path(cloud_dir).joinpath(n+'_CLOUDMASKRAS.tif')
            print('Using cloud TIF for masking: ' + str(cloudn))        
            cloud = Con(IsNull(str(cloudn)), 0, str(cloudn))  
            cloud.save(str(Path(cloud_dir).joinpath(n+'_CLOUDMASKNULL.tif')))
            print('Cloud null mask saved: ' + 
                  str(Path(cloud_dir).joinpath(n+'_CLOUDMASKNULL.tif')))
            
            #Get slope tiff
            slp = Raster(str(Path(terrain_dir).joinpath(n+'_SLOPE.tif')))
            print('Slope mask loaded: ' + 
                  str(Path(terrain_dir).joinpath(n+'_SLOPE.tif')))
    
            #Get indices tiffs        
            ndwi = Raster(str(Path(indices_dir).joinpath(n+'_NDWI.tif')))
            mndwi = Raster(str(Path(indices_dir).joinpath(n+'_MNDWI.tif')))
            aweish = Raster(str(Path(indices_dir).joinpath(n+'_AWEIsh.tif')))
            aweinsh = Raster(str(Path(indices_dir).joinpath(n+'_AWEInsh.tif')))
            bright = Raster(str(Path(indices_dir).joinpath(n+'_BRIGHT.tif')))
            print('Spectral indices tiffs loaded')
                      
            #Decision tree (con, true, false)
            classif=Con(bright<0, bright, 
                        Con(cloud==1,11, 
                        Con(bright>5000,7, 
                        Con(HS==0,1, 
                        Con(slp>15,2, 
                        Con(ndwi>0.3,10, 
                        Con(mndwi<0.1,3, 
                        Con((aweish<2000)|(aweish>5000),4, 
                        Con((aweinsh<4000)|(aweinsh>6000), 5, 
                        Con(((ndwi>0.05)&(slp<10)),10,6))))))))))
            
            #Save raw classification
            classif=Int(classif)
            outfile=Path(out_dir).joinpath(n + '_RASTPREFILT.tif')
            print('Outputting pre-filtered classification: ' + str(outfile))
            classif.save(str(outfile))
            
            #Tidy up classification
            outShrink = tidy_class(classif)
            outfile=Path(out_dir).joinpath(n + '_RASTFILT.tif')
            print('Outputting filtered classification: ' + str(outfile))
            outShrink.save(str(outfile))
            
            #Raster to vector water class
            water = rast_filt(outShrink)
            outfile=Path(out_dir).joinpath(n + '_WATERUNFILT.shp')
            print('Outputting vector water class: ' + str(outfile))
            water_vec=arcpy.RasterToPolygon_conversion(water, str(outfile), 
                                                       'SIMPLIFY', 'VALUE')
            
            #Add attributes
            arcpy.AddField_management(water_vec, "area", "DOUBLE", "#", 0, "#", 
                                      "#", "#", "#", "#")
            arcpy.CalculateField_management(water_vec, "area", 
                                            "!shape.area@squaremeters!",
                                            "PYTHON_9.3", "#")
        
            #Filter by size
            arcpy.MakeFeatureLayer_management(water_vec, "lyr") 
            arcpy.SelectLayerByAttribute_management ("lyr", "NEW_SELECTION", 
                                                     '"area" > 25000')
            
            #Write the selected features to a new featureclass
            outfile=Path(out_dir).joinpath(n + '_WATERFILT.shp')
            print('Adding info to vector water class: ' + str(outfile))
            arcpy.CopyFeatures_management("lyr", str(outfile))
            #NB or use intersect with land polygon - reverse selection - delete
            
            #Close variable tmp files
            HS = None
            cloud = None
            slp = None
            ndwi = None
            mndwi = None
            aweish = None
            aweinsh = None
            bright = None
        count=count+1
    
#-----------------------   6. Merge features   --------------------------------
def getIndices(mylist, value):
    '''Quick and dirty method for retrieving the list index of a certain 
    value.'''
    return[i for i, x in enumerate(mylist) if x==value] 

def merge6(in_dir, out_dir):
    print('\n\nMerging detected lake features...')           

    #Make output directory if it does not exist
    if os.path.exists(out_dir)==False:
        os.mkdir(out_dir) 
        
    #Making an empty list to put filepaths to feature classes in  
    feature_classes = []  
    
    #Get list of files
    feature_classes=list(Path(in_dir).glob('*_WATERFILT.shp'))
    print('Looking at merging common dates from ' + str(len(feature_classes)) 
          + ' shapefiles')    
    
    #Get all dates from shapefiles, and unique dates
    dates=[]
    for s in feature_classes:
        dates.append(str(s.name).split('_')[4])
    unique = set(dates)
    count=1

    #Iterate through unique dates
    for u in unique:
        fname = Path(out_dir).joinpath(str(u) + '_MERGED.shp')
        print('\n' + str(count) + '. Merging all shapefiles from ' + str(u)) 
        
        #Don't merge if shapefile already exists
        if os.path.isfile(str(fname))==True:
            print('Merged shapefile already exists: ' + str(fname))
        
        #Find indices and merge all shapefiles with same date
        else:            
            index = getIndices(dates, u)

            #Compile all shapefiles with same date into list of strings
            shplist=[]
            for i in index:
                print('Merging file... ' + str(feature_classes[i].name))
                shplist.append(str(feature_classes[i]))
            if len(feature_classes)==1:
                print('Only one shapefile found. Saving individual file to output')
            
            #Merge with arcpy
            arcpy.Merge_management(shplist, str(fname))

            #Delete duplicates
            arcpy.DeleteIdentical_management(str(fname), ['Shape'], 
                                             '1 kilometer')
            print('Merging successful: ' + str(fname))
                        
#            #Make layer file
#            fname2 = Path(out_dir).joinpath(str(u) + '_waterlyr')
#            arcpy.MakeFeatureLayer_management(str(fname), str(fname2))
#            print('Merged shapefile saved to ' + str(fname2))
#            
#            #Output KMZ file
#            fname3 = Path(out_dir).joinpath(str(u) + '_MERGEDKMZ.kmz') 
#            arcpy.LayerToKML_conversion(str(fname2), str(fname3)) 
#            print('Merged KMZ saved to ' + str(fname3))
    
        count=count+1


#------------------------------------------------------------------------------
    
#Directories (remember, all '\' brackets and no bracket at the end!)
#Be careful with length of filepaths. Not over 250 characters!
    
in_dir = r'G:\Satellitdata\S2\S2'
out_dir = r'D:\python_workspace\ice_marginal_lakes\timeseries_detection\23VMJ'

#DEM directory
DEM = ("P:\B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland\B71-02 " + 
       "Algorithm development\productionplan\ArcticDEM_10mTile_Merged.tif") 

#QGIS directory (should not need to change this)
qgis_dir = "C:\\Program Files\\QGIS 3.4\\bin\\ogr2ogr.exe -f \"ESRI Shapefile\" "

#Get folders for classification based on tile identifiers
folders = getFolders(in_dir, ['T23VMJ'])

#Resize rasters
resize1(folders, out_dir+r'\resize')

#Rasterise cloud masks
cloudtoraster2(folders, out_dir+r'\cloudraster')

#Create terrain masks
terrain3(folders, out_dir+r'\terrain', DEM)

#Create spectral indices tiffs
spectral4(folders, out_dir+r'\resize', out_dir+r'\spectralindices')

#Create lake classification tiffs/shpfiles
lakeclass5(out_dir+r'\spectralindices', out_dir+r'\terrain', out_dir+r'\cloudraster', out_dir+r'\lakes')

#Merge lakes with common dates
merge6(out_dir+r'\lakes', out_dir+r'\mergedlakes')
