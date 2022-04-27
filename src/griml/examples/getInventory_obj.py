"""
GrIML processing module playground (experimental)

@author: Penelope How
"""

import time
from time import gmtime, strftime
import geopandas as gpd

from process import gee
from lake import compileFeatures, assignID, assignSources, assignNames

start=time.time()

#------------------------------------------------------------------------------

# Set AOI
aoi = '/home/pho/Desktop/python_workspace/GrIML-personal/workflow/test/AOI_mask.shp'
aoi = gpd.read_file(aoi)
aoi_poly = aoi.geometry.iloc[0]
xmin, ymin, xmax, ymax = aoi_poly.bounds 

# Set AOI box splitter parameters
wh=0.3                                       # Window height
ww=0.3                                       # Window width
oh = 0.05                                   # Overlap height
ow = 0.05                                   # Overlap width

# Set date range
date1='2017-08-01'
date2='2017-08-10'

# Set maximum cloud cover
cloud=50

# Set output projection 
proj = 'EPSG:3413'                                # Polar stereographic


#---------------------------   Initialise GEE   -------------------------------

parameters = [{'collection' : 'UMN/PGC/ArcticDEM/V3/2m',
               'smooth' : 100, 'fill' : 100, 'kernel' : 100, 'speckle' : 50},
              {'collection' : 'UMN/PGC/ArcticDEM/V3/2m_mosaic',
               'smooth' : 100, 'fill' : 100, 'kernel' : 100, 'speckle' : 50},              
              {'collection' : 'COPERNICUS/S1_GRD',
               'polar' : 'HH', 'threshold' : -10, 'smooth' : 50},
              {'collection' : 'COPERNICUS/S2', 
               'cloud' : 20},
              {'collection' : 'LANDSAT/LC08/C01/T1_TOA',
               'cloud' : 50}]
              # {'collection' : 'LANDSAT/LE07/C02/T1_TOA',
              #  'cloud' : 50}]

proc = gee([date1, date2], aoi_poly, parameters, [wh, ww, oh, ow], True)
water = proc.processAll()
features = proc.retrieveAll(water)


#------------------------   Compile geodatabase   -----------------------------

iml = compileFeatures(features,
                      ['DEM', 'DEM', 'SAR', 'VIS', 'VIS'],
                      ['UMN/PGC/ArcticDEM/V3/2m', 'UMN/PGC/ArcticDEM/V3/2m_mosaic', 
                      'COPERNICUS/S1_GRD', 'COPERNICUS/S2',
                      'LANDSAT/LC08/C01/T1_TOA'], 
                      [date1, date2])
print(f'\nCompiled {iml.shape[0]} geodatabase features')

# Reproject geometries
iml = iml.to_crs(proj)
print(f'{iml.shape[0]} unfiltered features')

iml.to_file(f"out/iiml_{date1}_{date2}_{xmin}_{ymin}_unfiltered.shp")


#--------------------   Filter database by ice margin   -----------------------

# Load margin and add buffer
margin = gpd.read_file("../datasets/ice_margin/gimp_icemask_line_polstereo.shp")
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
iml.to_file(f"out/iiml_{date1}_{date2}_{xmin}_{ymin}_filtered.shp")


#--------------------   Populate metadata and write to file   -----------------

iml = assignID(iml)
iml = assignSources(iml)

names = gpd.read_file('../datasets/placenames/oqaasileriffik_placenames.shp')
iml = assignNames(iml, names)
            
iml.to_file(f"out/iiml_{date1}_{date2}_{xmin}_{ymin}_final.shp")
print(f'Saved to out/iiml_{date1}_{date2}_{xmin}_{ymin}_final.shp')

# Plot lakes
iml.plot(figsize=(10, 10), alpha=0.5, edgecolor='k')


#------------------------------------------------------------------------------
print('\nFinished')
end=time.time()
print('Total run time: ' + strftime("%H:%M:%S", gmtime(round(end-start))))
