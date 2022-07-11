"""
GrIML processing module playground (experimental)

@author: Penelope How
"""

import time,sys
from time import gmtime, strftime
import geopandas as gpd

try:
    sys.path.append('../')
    from process import gee
    from lake import dissolvePolygons, compileFeatures, assignID, assignSources, assignNames
except:
    from griml.process import gee
    from griml.lake import dissolvePolygons, compileFeatures, assignID, \
        assignSources, assignNames
    
start=time.time()

#------------------------------------------------------------------------------

# Set AOI box splitter parameters
wh=0.3                                       # Window height
ww=0.3                                       # Window width
oh = 0.05                                   # Overlap height
ow = 0.05                                   # Overlap width

# Set date range
date1='2017-07-01'
date2='2017-08-31'

# Set output projection 
proj = 'EPSG:3413'                                # Polar stereographic

# Set AOI
# aoi = '/home/pho/python_workspace/GrIML/other/datasets/aoi/AOI_mask_split2.shp'
aoi = '/home/pho/python_workspace/GrIML/other/datasets/aoi/test_mask.shp'
aoi = gpd.read_file(aoi).to_crs('EPSG:4326')

# Load ice margin with buffer
print('Preparing ice margin buffer...')
margin_buff = gpd.read_file("/home/pho/python_workspace/GrIML/other/datasets/ice_margin/gimp_icemask_line_polstereo_simple_buffer.shp")
# margin_buff = margin.buffer(500)
# margin_buff = gpd.GeoDataFrame(geometry=margin_buff, crs=margin.crs)

# Load name database
print('Loading placename database...')
names = gpd.read_file('/home/pho/python_workspace/GrIML/other/datasets/placenames/oqaasileriffik_placenames.shp')


#---------------------------   Initialise GEE   -------------------------------

parameters = [{'collection' : 'UMN/PGC/ArcticDEM/V3/2m_mosaic',
              'smooth' : 100, 'fill' : 100, 'kernel' : 100, 'speckle' : 50},  
              # {'collection' : 'UMN/PGC/ArcticDEM/V3/2m',
              # 'smooth' : 100, 'fill' : 100, 'kernel' : 100, 'speckle' : 50},
              {'collection' : 'COPERNICUS/S1_GRD',
              'polar' : 'HH', 'threshold' : -20, 'smooth' : 50},
              #{'collection' : 'COPERNICUS/S2', `
              #'cloud' : 20},
              {'collection' : 'LANDSAT/LC08/C01/T1_TOA',
              'cloud' : 20}]
              # {'collection' : 'LANDSAT/LE07/C02/T1_TOA',
              #  'cloud' : 50}]
              


for i in range(len(aoi.index)):
    print(f'\nCommencing processing of {list(aoi["catch"])[i]} catchment area')
    aoi_poly = aoi.geometry.iloc[i]
    xmin, ymin, xmax, ymax = aoi_poly.bounds 
    
    print('Clipping margin to catchment area...')
    aoi_poly_proj = gpd.GeoDataFrame(geometry=[aoi_poly], crs=aoi.crs).to_crs(proj)
    margin_clip = gpd.clip(margin_buff, aoi_poly_proj)
    
    print('Conducting classifications...')
    proc = gee([date1, date2], aoi_poly, parameters, [wh, ww, oh, ow], True)
    water = proc.processAll()
    features = proc.retrieveAll(water)

    # Filter features
    filtered=[]
    for f in features:
        print('Filtering features...')
        
        # Remove duplicates
        print('Dissolving polygons...')
        gdf = gpd.GeoDataFrame(geometry=f, crs='EPSG:4326')
        gdf = dissolvePolygons(gdf)
        
        # Remove lakes below size threshold
        print('Filtering by size...')
        gdf = gdf.set_crs('EPSG:4326')
        gdf = gdf.to_crs(proj)
        gdf['area_sqkm'] = gdf['geometry'].area/10**6
        gdf = gdf[(gdf.area_sqkm >= 0.05)]

        # # Remove lakes outside of margin boundary
        # print('Filtering by bounds...')
        # gdf = gpd.sjoin(gdf, margin_clip, how='left')
        # gdf = gdf[gdf['index_right']==0]
        # gdf = gdf.drop(columns='index_right')
        filtered.append(gdf.geometry)
        
        
#------------------------   Compile geodatabase   -----------------------------
#    lakes=[]
#    for f in features:
#        gdf = gpd.GeoDataFrame(geometry=f, crs='EPSG:4326')
#        gdf = dissolvePolygons(gdf)
#        gdf['area'] = gdf['geometry'].area/10**6
#        gdf = gdf[(gdf.area >= 0.05)]
        
#        gdf = gpd.sjoin(gdf, margin_buff, how='left')
#        gdf = gdf[gdf['index_right']==0]
#        gdf = gdf.drop(columns='index_right')
#        lakes.append(list(gdf['geometry']))
    
    # Compile all features    
    iml = compileFeatures(filtered,
                          ['DEM', 'SAR', 'VIS'],
                          ['UMN/PGC/ArcticDEM/V3/2m_mosaic', 'COPERNICUS/S1_GRD', 
                          'LANDSAT/LC08/C01/T1_TOA'], 
                          [date1, date2], proj)
    print(f'\nCompiled {iml.shape[0]} geodatabase features')
        
    # Calculate geometry attributes
    iml['area_sqkm'] = iml['geometry'].area/10**6
    iml['length_km'] = iml['geometry'].length/1000
    iml = iml[(iml.area_sqkm >= 0.05)]
    iml['catch'] = str(list(aoi["catch"])[i])
    
    # Calculate geometry info
    iml.reset_index(inplace=True, drop=True)    
    
    print(f'{iml.shape[0]} filtered features')
    
    iml.to_file(f'out/iiml_{date1}_{date2}_{list(aoi["catch"])[i]}_filtered.shp')
    
    
# #--------------------   Filter database by ice margin   -----------------------
        
#     # Perform spatial join
#     aoi_poly_proj = aoi_poly.to_crs(proj)
#     margin_clip = gpd.clip(margin_buff, aoi_poly_proj)
    
#     iml = gpd.sjoin(iml, margin_clip, how='left')
#     iml = iml[iml['index_right']==0]
#     iml = iml.drop(columns='index_right')
#     print(f'{iml.shape[0]} features within 500 m of margin')
        
#     # Calculate geometry info
#     iml.reset_index(inplace=True, drop=True)
#     print(f'{iml.shape[0]} features over 0.05 sq km')
#     iml.to_file(f'out/iiml_{date1}_{date2}_{list(aoi["catch"])[i]}_filtered.shp')
    
    
#--------------------   Populate metadata and write to file   -----------------
       
#    iml = assignID(iml)
    # iml = assignSources(iml)
    
    # iml = assignNames(iml, names)
                
    # iml.to_file(f'out/iiml_{date1}_{date2}_{list(aoi["catch"])[i]}_final.shp')
    # print(f'Saved to out/iiml_{date1}_{date2}_{list(aoi["catch"])[i]}_final.shp')
    
    # # Plot lakes
    # iml.plot(figsize=(10, 10), alpha=0.5, edgecolor='k')


#------------------------------------------------------------------------------
print('\nFinished')
end=time.time()
print('Total run time: ' + strftime("%H:%M:%S", gmtime(round(end-start))))
