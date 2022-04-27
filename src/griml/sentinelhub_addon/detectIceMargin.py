#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 15:35:05 2021

@author: pho
"""

from sentinelhub import SHConfig
import datetime
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio.features import shapes
from sentinelhub import MimeType, CRS, BBox, SentinelHubRequest, BBoxSplitter,\
    DataCollection, bbox_to_dimensions, read_data
import geopandas as gp
from shapely.geometry import shape


#------------------------   Input parameters   --------------------------------

#Input parameters
# INPUT_FILE = './icemargin_mask.json'                                          #Input mask
INPUT_FILE = './test_mask_json_pstereo.json'                                    #Input mask
OUTPUT_FILE = './icemargin_2020_mask_nomosaic.shp'
epsg = 3413                                                                    #EPSG of mask (and output)
date = (datetime.datetime(2020,7,1), datetime.datetime(2020,9,1))              #Start/end dates
resolution = 10                                                                #Output spatial resolution
bbox_col = 20                                                                  #Bbox width splitter 
bbox_row = 50                                                                  #Bbox length splitter

#---------------------   Scripts for classification   -------------------------

#SentinelHub script for classifying snow/ice 
evalscript = """
//VERSION=3
function setup() {
  return {
    input: {bands: ["B03","B11","CLM","dataMask"]},
    output: { bands: 1, 
             nodataValue: 0}
  }
}

function spectralIndices(cloud, mask, green, SWIR) {     
    if (cloud == 0) {                                 // Exclude cloudy pixels
        if (mask == 1) {                              // Exclude nodata pixels
            if (index(green, SWIR) >= 0.41) {         // NDSI threshold    
                return [1]
            }}}}

function evaluatePixel(sample) {   
    var ndsi = spectralIndices(sample.CLM, sample.dataMask, sample.B03, sample.B11)
    if (ndsi == 1) {
        return[1]
        }}             
"""


#Vectorisation function
def getGeodata(img, trans):
    '''Get vector features from binary raster image. Raster data is loaded 
    from array as a rasterio inmemory object, and returns features as a 
    geopandas dataframe

    Variables
    img (arr)                           Binary raster array
    trans (Affine):                     Raster transformation (computed using
                                        affine package, or 
                                        rasterio.transform) 
    Returns
    feats (Geodataframe):               Vector features geodataframe
    '''
    #Open array as rasterio memory object
    with rio.io.MemoryFile() as memfile:
        with memfile.open(
            driver='GTiff',
            height=img.shape[0],
            width=img.shape[1],
            count=1,
            dtype=img.dtype,
            transform=trans
        ) as dataset:
            dataset.write(img, 1)
        
        #Vectorize array
        with memfile.open() as dataset:
                image = dataset.read(1)
                mask = image==255
                results = (
                {'properties': {'raster_val': v}, 'geometry': s}
                for i, (s, v) 
                in enumerate(
                    shapes(image, 
                           mask=mask, 
                           transform=rio.transform.from_origin(transf[0], 
                                                               transf[3], 
                                                               transf[1], 
                                                               transf[5]))))
                
                ##Transform geometries to geodataframe
                geoms = list(results)
                feats = gp.GeoDataFrame.from_features(geoms)
                
    return feats

#--------------------   Configure SentinelHub client   ------------------------

#Configure Sentinelhub connection client    
config = SHConfig()
# config.instance_id = 'e4ac5ac3-ca5e-4624-ab3a-8214df144373'                  #Instance ID needed
# config.sh_client_id = '23032a7f-66c1-447e-99ed-44c10d13072f'                 #Client ID needed
# config.sh_client_secret = 'WZ|ufGd;yp|YW];2<qO;,]Yr>[aZ!Oh7uvr~r<g*'         #Client password needed
# config.save()                                                                #Save client login so not needed again

#-------------------------   SentinelHub request   ----------------------------

#Load mask and split into processing chunks
geo_json = read_data(INPUT_FILE)
gl_area = shape(geo_json["features"][0]["geometry"])
bbox_splitter = BBoxSplitter([gl_area], CRS(epsg), (bbox_col, bbox_row), reduce_bbox_sizes=True)  
geometry_list = bbox_splitter.get_geometry_list()
print('Area bounding box: {}'.format(bbox_splitter.get_area_bbox().__repr__()))
print(f'Number of bboxes: {len(geometry_list)}')

#Create empty geodataframe for outputs to be appended to
ice = gp.GeoDataFrame(crs='EPSG:'+str(epsg))

#Iterate through bbox list
count=1
for g in geometry_list[100:110]:
    
    #Construct bbox
    bbox_obj = BBox(bbox=g, crs=CRS(epsg))
    bbox_obj = bbox_obj.buffer(1)
    bbox_size = bbox_to_dimensions(bbox_obj, resolution=resolution)
    print(f'\nBbox {count} at {resolution} m resolution, {bbox_size} pixels') 
    
    #Fetch transform 
    transf = bbox_obj.get_transform_vector(resx=resolution, resy=resolution)
                
    #Construct SentinelHub request   
    request = SentinelHubRequest(evalscript=evalscript,                                
                                input_data=[
                                SentinelHubRequest.input_data(
                                data_collection=DataCollection.SENTINEL2_L1C,
                                time_interval=date,
                                maxcc=0.1                                      #Max cloud cover (0-1)
                                # mosaicking_order = 'ORBIT',                  #leastCC/mostRecent/leastRecent/Orbit
                                # other_args={'orbit_direction': 'ascending'}  #Not sure if this works so check it!
                                ),
                                SentinelHubRequest.input_data(
                                data_collection=DataCollection.DEM_COPERNICUS_30,
                                upsampling='BILINEAR',
                                # time_interval=date
                                )],
                                responses=[
                                SentinelHubRequest.output_response('default', MimeType.TIFF)],
                                bbox=bbox_obj,
                                size=bbox_size,
                                config=config)

    #Perform request 
    img = request.get_data()
    print(f'Single element returned of type {type(img[-1])} ({img[0].dtype})')

    # plt.imshow(img[0])
    # plt.show()
        
    #Vectorise array
    features = getGeodata(img[0], rio.transform.from_origin(transf[0], transf[3], transf[1],transf[5]))
    
    #Check if no features detected
    if features.empty:
        print('No features detected. Moving to next request.')

    #Append to final geodatabase
    else:
        ice = ice.append(features)
    count=count+1


#Dissolve all detected features
print('\nDissolving features...')
ice['dissolve']=1    
ice = ice.dissolve(by='dissolve')
ice['area'] = ice['geometry'].area/10**6

#Write to file
print(f'Saving to {OUTPUT_FILE}')
ice.to_file(OUTPUT_FILE)

#------------------------------------------------------------------------------
print('Finished')