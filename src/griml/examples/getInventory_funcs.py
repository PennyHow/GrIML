"""
GrIML processing module playground (experimental)

@author: Penelope How
"""

import ee, time, sys
from time import gmtime, strftime
import requests, zipfile, io, urllib
from urllib.error import HTTPError

import numpy as np
from shapely.ops import split
from shapely.geometry import Polygon, LineString, MultiPolygon
import geopandas as gpd
import multiprocessing as mp

sys.path.append('../')
from retrieve import getScenes, getScene, getInt, getSmooth, getMosaic, \
    getMean, maskImage, splitBBox, getVectors, extractFeatures, getFeatures, \
    getFeaturesSplit
from sar import filterSARscenes, classifySARimage
from vis import filterS2scenes, maskS2clouds, renameS2scenes, \
    resampleS2scenes, classifyVISimage, filterLSscenes, maskL8clouds, \
    renameL8scenes
from dem import getElevation, getSlope, getSinks
from lake import compileFeatures, assignID, assignSources, assignNames

start=time.time()

#------------------------------------------------------------------------------

# Set AOI

aoi1 = [-50.94, 67.98]            # SW test region
aoi2 = [-49.66, 67.58]

# aoi1 = [-54.68242187500001,68.8415979398901]
# aoi2 = [-47.21171875000001,60.62185574504481]            # SW region

# aoi1 = [-10.297656250000014,59.03190534154833]             # All Greenland
# aoi2 = [-74.98515625000002,83.9867103173338]

print('Loading bounding box')
aoi = '/home/pho/Desktop/python_workspace/GrIML/other/datasets/aoi/test_mask_4326.shp'
aoi = gpd.read_file(aoi)
aoi_poly = aoi.geometry.iloc[0]
xmin, ymin, xmax, ymax = aoi_poly.bounds 

# Set AOI box splitter parameters
wh=0.3                                       # Window height
ww=0.3                                       # Window width
oh = 0.05                                   # Overlap height
ow = 0.05                                   # Overlap width

# Set date range
date1='2017-07-01'
date2='2017-08-31'

# Set maximum cloud cover
cloud=50

# Set mask location
ice_mask = 'users/pennyruthhow/GIMP_iceMask_edit_buffer7km'

# Set output projection 
proj = 'EPSG:3413'                                # Polar stereographic


#---------------------------   Initialise GEE   -------------------------------
    
ee.Initialize()
print('EE initialized')

# Set the Area of Interest (AOI) through box coordinates
box = ee.Geometry.Rectangle([xmin, ymin, xmax, ymax])

# Split box into grid for exporting
bbox = splitBBox(aoi_poly, wh, ww, oh, ow)
print('grid completed')
# # Remove boxes that don't overlap with AOI polygon
# grid = [Polygon([[g[0],g[1]], [g[0],g[3]], [g[2],g[3]],
#                   [g[2],g[1]], [g[0],g[1]]]) for g in grid]
# bbox = [ee.Geometry.Rectangle(min(g.exterior.coords.xy[0]), 
#                               min(g.exterior.coords.xy[1]), 
#                               max(g.exterior.coords.xy[0]), 
#                               max(g.exterior.coords.xy[1])) for g in grid if g.intersects(aoi_poly)]


print(f'Computed {len(bbox)} bounding boxes')
print(f'Total area covered: {aoi_poly.area} sq km')




# bbox = bbox[100:105]

# # Set the Area of Interest (AOI) through box coordinates
# box = ee.Geometry.Rectangle([aoi1[0], aoi1[1],
#                             aoi2[0], aoi2[1]])

# bbox = [ee.Geometry.Rectangle(g[0], g[1], g[2], g[3]) for g in grid]

# print(f'Computed {len(bbox)} bounding boxes from {aoi1}, {aoi2}')
# print(f'Total area covered: {box.area().getInfo()/10**6} sq km')


#---------------------   Get basic ocean mask ---------------------------------

# Retrieve ice-ocean mask
img = ee.Image("OSU/GIMP/2000_ICE_OCEAN_MASK")
ocean_mask = img.select('ocean_mask').eq(0)
# ice_mask = img.select('ice_mask').eq(0)

# imask0 = ice_mask.reduceToVectors(geometryType='polygon', labelProperty='v', scale=10, bestEffort=True)
# def _mapBuffer(feature):
#     return feature.buffer(-10000)
# imask01 = imask0.map(_mapBuffer)
# imask0 = imask01.reduceToImage(properties=['v'], reducer=ee.Reducer.mean())

# sys.exit(1)

# # Construct vector features
# def getFeaturesSplit(image, bbox):
#     features=[]
#     for b in range(len(bbox)):
#         print(f'Fetching vectors from bbox {b}...')
#         v = getVectors(image, 10, bbox[b])
#         features.append(extractFeatures(v))
#     features = [val for sublist in features for val in sublist]
#     print(f'{len(features)} vector features identified')    
#     return features

# def getFeatures(image, bbox):
#     features=[]
#     v = getVectors(image, 10, bbox)
#     features = extractFeatures(v)
#     print(f'{len(features)} vector features identified')    
#     return features
    
# def getParallelFeatures1(image, bbox):
#     # Parallel process vector generation
#     pool = mp.Pool(mp.cpu_count())
#     v = [pool.apply(getVectors, args=(image, 10, bbox[b])) for b in range(len(bbox))]
#     pool.close()    
     
#     # Parallel process feature extraction
#     pool = mp.Pool(mp.cpu_count())
#     features = pool.map(extractFeatures, [row for row in v])
#     pool.close()    

#     features = [val for sublist in features for val in sublist]
#     print(f'{len(features)} vector features identified')    
#     return features

# def getDownload(v):
#     link = v.getDownloadURL('csv')
#     req = urllib.request.Request(url=link)
#     try:
#         handler = urllib.request.urlopen(req)
#     except HTTPError as e:
#         handler = e.read()
#     lines = []
#     for l in handler:
#         lines.append(str(l))
#     features_dem.append(lines)
        
#---------------------------   DEM processing   -------------------------------

# Set collection
dem_col = 'UMN/PGC/ArcticDEM/V3/2m_mosaic'

# Get image collection
scenes = getScene(dem_col, box)
print(f'\nScenes gathered from {dem_col}')
    
# Get elevation and slope
elevation = getElevation(scenes)
slope = getSlope(elevation)

elevation = getSmooth(elevation, 110)

# Mask out ocean pixels
elevation = maskImage(elevation, ocean_mask)

# Get sinks
elevation = getInt(elevation)
sinks = getSinks(elevation, 10, 50)
    
# Remove speckle with smoothing
sinks = getSmooth(sinks, 50).rename('dem_sinks')
sinks = getInt(sinks)
print(f'{dem_col} scenes classified')
print('Band names: ' + str(sinks.bandNames().getInfo())) 
  
try:                     
    features_dem = getFeatures(sinks, 10, box)
except:
    features_dem = getFeaturesSplit(sinks, 10, bbox)
    

#---------------------------   SAR processing   -------------------------------
    
# Set collection
sar_col = 'COPERNICUS/S1_GRD'
 
# Get image collection
scenes = getScenes(sar_col, date1, date2, box)
if scenes.size().getInfo() > 0: 
    scenes = filterSARscenes(scenes)
    print(f'\nScenes gathered from {sar_col}')
    print('Total number of scenes: ', scenes.size().getInfo())
    print('Number of bands per scene: ' 
          + str(len(scenes.first().bandNames().getInfo())))
    print('Band names: ' + str(scenes.first().bandNames().getInfo()))
        
    # Get average
    aver = getMosaic(scenes, 'HH')
    
    # Mask out ocean pixels
    aver = maskImage(aver, ocean_mask)
    
    # Classify water from SAR average image
    water_sar = classifySARimage(aver, -20, 'HH', 50)
    print(f'{sar_col} scenes classified')
    print('Band names: ' + str(water_sar.bandNames().getInfo()))      
 
    try:                     
        features_sar = getFeatures(water_sar, 10, box)
    except:
        features_sar = getFeaturesSplit(water_sar, 10, bbox)

else:
    features_sar = None
    print(f'\nNo {sar_col} scenes identified between {date1} and {date2}')  
    
#-------------------------   VIS processing (S2)   -----------------------------

# Set collection
vis_col1 = "COPERNICUS/S2"

# Get image collection
scenes = getScenes(vis_col1, date1, date2, box)
if scenes.size().getInfo() > 0: 
    scenes = filterS2scenes(scenes, cloud)
    print(f'\nScenes gathered from {vis_col1}')
    print('Total number of scenes: ', scenes.size().getInfo())
    print('Number of bands per scene: ' 
          + str(len(scenes.first().bandNames().getInfo())))
    print('Band names: ' + str(scenes.first().bandNames().getInfo()))
    
    # Mask scenes for clouds
    scenes = maskS2clouds(scenes)  
    # ee.Terrain.hillshade(image, azimuth, elevation)
        
    # Get average of spectific bands
    scenes = renameS2scenes(scenes)
    scenes = resampleS2scenes(scenes)
    aver = getMean(scenes, ['blue','green','red','vnir','swir1_1','swir2_1'])   
    print('Scenes resampled and mosiacked')
    print('Band names: ' + str(aver.bandNames().getInfo())) 
    
    # Classify water from VIS average image, and mask out ocean pixels
    water_s2 = classifyVISimage(aver)
    water_s2 = maskImage(water_s2, ocean_mask)
    print(f'{vis_col1} scenes classified')
    print('Band names: ' + str(water_s2.bandNames().getInfo()))        
    
    try:                     
        features_s2 = getFeatures(water_s2, 10, box)
    except:
        features_s2 = getFeaturesSplit(water_s2, 10, bbox)
else:
    features_s2 = None
    print(f'\nNo {vis_col1} scenes identified between {date1} and {date2}')      

#-----------------------   VIS processing (Landsat 8)   -----------------------

# Set collection
vis_col2 = "LANDSAT/LC08/C01/T1_TOA"

# Get image collection
scenes = getScenes(vis_col2, date1, date2, box)
if scenes.size().getInfo() > 0: 
    scenes = filterLSscenes(scenes, cloud)
    print(f'\nScenes gathered from {vis_col2}')
    print('Total number of scenes: ', scenes.size().getInfo())
    print('Number of bands per scene: ' 
          + str(len(scenes.first().bandNames().getInfo())))
    print('Band names: ' + str(scenes.first().bandNames().getInfo()))
    
    # Mask scenes for clouds
    scenes = maskL8clouds(scenes)  
    # ee.Terrain.hillshade(image, azimuth, elevation)
        
    # Get average of spectific bands
    scenes = renameL8scenes(scenes)
    aver = getMean(scenes, ['blue','green','red','vnir','swir1','swir2'])
    print('Scenes resampled and mosiacked')
    print('Band names: ' + str(aver.bandNames().getInfo())) 
    
    # Classify water from VIS average image, and mask out ocean pixels
    ndwi = aver.normalizedDifference(['green_mean', 'vnir_mean']).rename('ndwi') 
    mndwi = aver.normalizedDifference(['green_mean','swir1_mean']).rename('mndwi')
    aweish = aver.expression('BLUE + 2.5 * GREEN - 1.5 * (VNIR + SWIR1) - 0.25 * SWIR2',
                            {'BLUE' : aver.select('blue_mean'), 
                            'GREEN' : aver.select('green_mean'),
                            'SWIR1' : aver.select('swir1_mean'),
                            'VNIR' : aver.select('vnir_mean'),
                            'SWIR2' : aver.select('swir2_mean')}).rename('aweish')  
    aweinsh = aver.expression('4.0 * (GREEN - SWIR1) - (0.25 * VNIR + 2.75 * SWIR2)',
                             {'GREEN' : aver.select('green_mean'),
                             'SWIR1' : aver.select('swir1_mean'),
                             'VNIR' : aver.select('vnir_mean'),
                             'SWIR2' : aver.select('swir2_mean')}).rename('aweinsh')
    bright = aver.expression('(RED + GREEN + BLUE) / 3',
                            {'BLUE' : aver.select('blue_mean'),
                            'GREEN' : aver.select('green_mean'),
                            'RED' : aver.select('red_mean')}).rename('bright') 
    
    aver = aver.addBands([ndwi, mndwi, aweish, aweinsh, bright])
    classified = aver.expression("(BRIGHT > 5000) ? 0"
                                ": (NDWI > 0.3) ? 1 "
                                ": (MNDWI < 0.1) ? 0 "
                                ": (AWEISH < 2000) ? 0"
                                ": (AWEISH > 5000) ? 0"
                                ": (AWEINSH < 4000) ? 0"
                                ": (AWEINSH > 6000) ? 0"
                                ": 1",
                               {'NDWI' : aver.select('ndwi'),
                                'MNDWI' : aver.select('mndwi'),
                                'AWEISH' : aver.select('aweish'),
                                'AWEINSH' : aver.select('aweinsh'),
                                'BRIGHT' : aver.select('bright')}).rename('water')             
    water_ls8 = classified.updateMask(classified)
    water_ls8 = maskImage(water_ls8, ocean_mask)
    print(f'{vis_col2} scenes classified')
    print('Band names: ' + str(water_ls8.bandNames().getInfo()))     
    
    try:                     
        features_ls8 = getFeatures(water_ls8, 10, box)
    except:
        features_ls8 = getFeaturesSplit(water_ls8, 10, bbox)  

else:
    features_ls8 = None
    print(f'\nNo {vis_col2} scenes identified between {date1} and {date2}')  


#------------------------   Compile geodatabase   -----------------------------

iml = compileFeatures([features_s2, features_ls8, features_sar, features_dem],
                      ['VIS','VIS','SAR','DEM'],
                      [vis_col1, vis_col2, sar_col, dem_col], 
                      [date1, date2])
print(f'\nCompiled {iml.shape[0]} geodatabase features')

# Reproject geometries
iml = iml.to_crs(proj)
print(f'{iml.shape[0]} unfiltered features')

iml.to_file(f"out/iiml_{date1}_{date2}_{aoi1[0]}_{aoi1[1]}_unfiltered.shp")


#--------------------   Filter database by ice margin   -----------------------

# Load margin and add buffer
margin = gpd.read_file("../../../other/datasets/ice_margin/gimp_icemask_line_polstereo.shp")
margin_buff = margin.buffer(500)
margin_buff = gpd.GeoDataFrame(geometry=margin_buff, crs=margin.crs)

# Perform spatial join
iml = gpd.sjoin(iml, margin_buff, how='left')
iml = iml[iml['index_right']==0]
iml = iml.drop(columns='index_right')
print(f'{iml.shape[0]} features within 500 m of margin')

# Filter lakes by area
iml['area_sqkm'] = iml['geometry'].area/10**6
iml['length_km'] = iml['geometry'].length/1000
iml = iml[(iml.area_sqkm >= 0.05)]

# Calculate geometry info
iml.reset_index(inplace=True, drop=True)
print(f'{iml.shape[0]} features over 0.05 sq km')
iml.to_file(f"out/iiml_{date1}_{date2}_{aoi1[0]}_{aoi1[1]}_filtered.shp")

#-------------------------   Populate metadata   ------------------------------

iml = assignID(iml)
iml = assignSources(iml)

names = gpd.read_file('../../../other/datasets/placenames/oqaasileriffik_placenames.shp')
iml = assignNames(iml, names)
        
#-----------------------   Write data to shapefile   -------------------------- 
    
iml.to_file(f"/home/pho/Desktop/python_workspace/GrIML/other/out/iiml_{date1}_{date2}_{aoi1[0]}_{aoi1[1]}_final.shp")
print(f'Saved to out/iiml_{date1}_{date2}_{aoi1[0]}_{aoi1[1]}_final.shp')

# Plot lakes
iml.plot(figsize=(10, 10), alpha=0.5, edgecolor='k')

print('\nFinished')
end=time.time()
print('Total run time: ' + strftime("%H:%M:%S", gmtime(round(end-start))))
