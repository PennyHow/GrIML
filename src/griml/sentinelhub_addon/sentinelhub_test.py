#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 15:35:05 2021

@author: pho
"""



import datetime
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio.features import shapes
import geopandas as gp
from shapely.geometry import shape
from sentinelhub import SHConfig, MimeType, CRS, BBox, SentinelHubRequest, \
    DataCollection, bbox_to_dimensions, read_data, BBoxSplitter
    
import xarray as xr
from sentinelhub import OsmSplitter, TileSplitter, CustomGridSplitter, UtmZoneSplitter, UtmGridSplitter
import matplotlib.pyplot as plt

#------------------------   Input parameters   --------------------------------

#Input parameters
INPUT_FILE = './test_mask_json_pstereo.json'                                   #Input mask
OUTPUT_FILE = './IMLs.shp'
epsg = 3413                                                                    #EPSG of mask (and output)

date = (datetime.datetime(2020,7,1), datetime.datetime(2020,7,10))             #Start/end dates
maxcloud = 0.4                                                                 #Maximum cloud cover (0-1)
# n_chunks = 2

resolution = 10                                                                #Output spatial resolution

bbox_col = 20                                                                  #Bbox width splitter 
bbox_row = 50                                                                  #Bbox length splitter

#---------------------------   Functions   ------------------------------------

evalscript = """
//VERSION=3
function setup() {
  return {
    input: [
        {bands: ["B02", "B03", "B04", "B08", "B11", "B12", "CLM", "dataMask"]},
        {bands: ["VH", "VV", "dataMask"]}  //"shadowMask"]} 
        ],
    output: { bands: 1, 
//             sampleType: "UNIT8",
             nodataValue: 0}
  }
}

function classMultiSpectral(cloud, nodata, blue, green, red, nir, swir11, swir12) {
    
    // Exclude cloudy pixels
    if (cloud== 0) {
            
    // Exclude nodata pixels
    if (nodata == 1) { 
            
    // NDWI threshold    
    if (index(green, nir) >= 0.3) {
                    
    // MNDWI threshold
    if (index(green, swir11 <= 0.1)) {
                           
    // AWEIsh threshold
    if (50 <= (blue + 2.5 * green - 
               1.5 * (nir + swir11) - 
               0.25 * swir12) <= 200) {
                                                  
    // AWEInsh threshold
    if (50 <= (4 * (green - swir11) - 
               (0.25 * nir + 2.75 * swir12)) <= 254) {
                                                                                    
    // Brightness threshold
    if (((red + green + blue)/3) <= 70) {
                                            
        return [1]
}}}}}}}}

                   
function classBackScatter(sigmaHH, sigmaHV) {
    // Convert sigma0 to Decibels
    let vh_Db = toDb(sigmaVH)
    let vv_Db = toDb(sigmaVV)
  
    // Calculate NRPB (Filgueiras et al. (2019), eq. 4)
    let NRPB = (vh_Db - vv_Db) / (vh_Db + vv_Db)
  
    // Calculate NDVI_nc with approach A3 (Filgueiras et al. (2019), eq. 14)
    let NDVInc = 2.572 - 0.05047 * vh_Db + 0.176 * vv_Db + 3.422 * NRPB
    return NDVInc
}
 
                    
function evaluatePixel(sample) {
    optical = sample["0"][0]
    var opt = classMultiSpectral(optical.CLM, optical.dataMask, 
                                 optical.B02, optical.B03, optical.B04, 
                                 optical.B08, optical.B11, optical.B12) 
    return [opt]
}
"""

#Vectorisation function
def getGeodata(img, trans):
    '''Get vector features from binary raster image. Raster data is loaded 
    from array as a rasterio inmemory object, and returns features as a 
    geopandas dataframe.

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

#-----------------------   Sentinelhub request   ------------------------------

#Load mask and split into processing chunks
geo_json = read_data(INPUT_FILE)


#Split bbox into processing pieces
gl_area = shape(geo_json["features"][0]["geometry"])
bbox_splitter = BBoxSplitter([gl_area], CRS(epsg), 
                             (bbox_col, bbox_row), 
                             reduce_bbox_sizes=True)  
geometry_list = bbox_splitter.get_geometry_list()
# bbox_list = bbox_splitter.get_bbox_list()
# info_list = bbox_splitter.get_info_list()
print('Area bounding box: {}'.format(bbox_splitter.get_area_bbox().__repr__()))
print(f'Number of bboxes: {len(geometry_list)}')


##Split datetime range into equal chunks
# tdelta = (end - start) / n_chunks
# edges = [(start + i*tdelta).date().isoformat() for i in range(n_chunks)]
# slots = [(edges[i], edges[i+1]) for i in range(len(edges)-1)]
# print('Monthly time windows:')
# for slot in slots:
#     print(slot)


#Create empty geodataframe for outputs to be appended to
lakes = gp.GeoDataFrame(crs='EPSG:'+str(epsg))


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

    # bb_utm = geo_utils.to_utm_bbox(bbox_obj)                                   #Convert bounding box to UTM coordinates 
    # transf = bb_utm.get_transform_vector(resx=resolution, resy=resolution)     #Fetch transform 
    # pix_lat = np.array(np.arange(0, bbox_size[1]))                             #Generate latitude grid
    # lats = np.array([pix_lat] * bbox_size[0]).transpose()
    # pix_lon = np.array(np.arange(0, bbox_size[0]))                             #Generate longitude grid
    # lons = np.array([pix_lon] * bbox_size[1])
    # lon, lat = geo_utils.pixel_to_utm(lats, lons, transf)                      #Convert px pos to UTM
    # lon_degrees, lat_degrees = geo_utils.to_wgs84(lon, lat, bb_utm.crs)        #Convert UTM to WGS84
    # da=[]


                
    #Construct SentinelHub request  
    # for s in slots:
    request = SentinelHubRequest(evalscript=evalscript,                                
                                input_data=[
                                SentinelHubRequest.input_data(
                                data_collection=DataCollection.SENTINEL2_L1C,
                                time_interval=date,
                                maxcc=maxcloud                                 
                                #mosaicking_order = 'leastCC'                  #leastCC/mostRecent/leastRecent
                                ),
                                SentinelHubRequest.input_data(
                                data_collection=DataCollection.SENTINEL1_IW_DES,
                                time_interval=date,
                                #mosaicking_order = 'leastCC'                  #leastCC/mostRecent/leastRecent
                                other_args={'type': 'sentinel-1-grd', 
                                            'orthorectify': True,
                                            'demInstance': 'COPERNICUS',       #MAPZEN/COPERNICUS/COPERNICUS_30/COPERNICUS_90
                                            'backCoeff': 'GAMMA0_TERRAIN',     #BETA0/SIGMA0_ELLIPSOID/GAMMA0_ELLIPSOID/GAMMA0_TERRAIN
                                            'speckleFilter': {'type': 'LEE',
                                            'windowSizeX': 5, 'windowSizeY': 5}}
                                )],                                
                                # SentinelHubRequest.input_data(
                                # data_collection=DataCollection.DEM_COPERNICUS_30,
                                # upsampling='BILINEAR',
                                # # time_interval=date
                                # )],
                                responses=[
                                SentinelHubRequest.output_response('default', MimeType.TIFF)],
                                bbox=bbox_obj,
                                size=bbox_size,
                                config=config)

    #Perform request 
    img = request.get_data()
    # plt.imshow(img[0])
    # plt.show()
    print(f'Single element returned of type {type(img[-1])} ({img[0].dtype})')

    # #Construct array
    # xout = xr.DataArray(
    #     data=img[0].reshape(img[0].shape[0], img[0].shape[1]),
    #     dims=["x", "y"],
    #     coords=dict(
    #     lon=(["x", "y"], lon),
    #     lat=(["x", "y"], lat),
    #     time=s[1],
    #     reference_time=s[0],
    #     ),
    #     attrs=dict(
    #     description="Binary",
    #     units="0=no water; 1=water"
    #     ),
    #     ) 
    # da.append(xout)                                                          #Need np.dstack but for xarray
        
    #Vectorise array
    features = getGeodata(img[0], rio.transform.from_origin(transf[0], transf[3], transf[1],transf[5]))
    
    #Check if no features detected
    if features.empty:
        print('No features detected. Moving to next request.')

    #Append to final geodatabase
    else:
        
        #Filter features by area
        print(f'{len(features.index)} features detected. Filtering by area...')
        features['area'] = features['geometry'].area/10**6
        # features.drop(features['raster_val']) 
        features.drop(features.index[features['area'] < 0.05], inplace=True) 
        
        #Check features
        if features.empty:
            print('No features left after filtering. Moving to next request.')
        
        #Populate metadata and append to final geodatabase
        else:
            print(f'{len(features.index)} features remaining')
            #Populate metadata
            features['startdate'] = date[0].strftime('%Y%m%d')
            features['enddate'] = date[1].strftime('%Y%m%d')
            lakes = lakes.append(features)
    count=count+1

 
#Write to file
print(f'\nSaving to {OUTPUT_FILE}')
lakes.to_file(OUTPUT_FILE)

#------------------------------------------------------------------------------
print('Finished)')