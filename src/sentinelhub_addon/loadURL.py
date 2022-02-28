#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 10:15:32 2021

@author: pho
"""

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from urllib.request import urlopen, HTTPError, URLError
from collections import OrderedDict
import matplotlib.pyplot as plt
# import xarray as xr
import os, sys


from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import requests
# or: requests.get(url).content
        

weblink1 = 'https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/22/W/ES/S2A_MSIL1C_20210801T150911_N0301_R025_T22WES_20210801T171130.SAFE/GRANULE/L1C_T22WES_A031911_20210801T150914/IMG_DATA/T22WES_20210801T150911_B02.jp2'
weblink2 = 'https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/22/W/ES/S2A_MSIL1C_20210801T150911_N0301_R025_T22WES_20210801T171130.SAFE/GRANULE/L1C_T22WES_A031911_20210801T150914/IMG_DATA/T22WES_20210801T150911_B04.jp2'


# def openURL(weblink):
# with rasterio.open(weblink1) as dataset1:
#     rplot.show(dataset1)
#     band1 = dataset1.read(1)
#     bounds1 = dataset1.bounds
#     transform1 = dataset1.transform
#     crs1 = dataset1.crs
#     idx = dataset1.res
#     # crs=dataset.read_crs()
#     print(sys.getsizeof(dataset1))
#     dataset1.close()

# with xr.open_rasterio(weblink2, chunks={'band':1, 'x':1000, 'y':1000}) as dataset1:
#     # rplot.show(dataset1)
#     # band1 = dataset1.read(1)
#     transform1 = dataset1.transform
#     crs1 = dataset1.crs
#     # crs=dataset.read_crs()
#     print(sys.getsizeof(dataset1))
#     dataset1.close()    

  
# membytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
# mem_gib = membytes/(1024. **3)
# print(membytes)

# dataset1 = dataset1.squeeze()

# im = dataset1.compute().plot.imshow()
# plt.show()


from io import BytesIO
from zipfile import ZipFile


def get_zip(file_url):
    url = requests.get(file_url)
    zipfile = ZipFile(BytesIO(url.content))
    files = [zipfile.open(file_name) for file_name in zipfile.namelist()]
    return files.pop() if en(files) == 1 else files



# resp = urlopen("http://www.test.com/file.zip")
# zipfile = ZipFile(BytesIO(resp.read()))
# files = zipfile.namelist()
# file = files[0]
# for line in zipfile.open(file).readlines():
#     print(line.decode('utf-8'))
    
    

#Log on to SciHub
def getSentinelLinks(user, password, tilenames, start, end, cloud, product):
    print('Logging onto SciHub...')
    api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')
    print('Login successful\n\n')
    
    # #Gather products to download from aoi
    # if tiles is None:
        
    #     #Load geojson file
    #     print('Loading AOI from geojson file: ' + str(json))
    #     footprint = geojson_to_wkt(read_geojson(json))
    #     print('AOI loaded\n\n')
        
    #     print('Retrieving Sentinel products from geojson file ...')
    #     if cloud is not None:
    #         products = api.query(footprint, date=(start, end), platformname="Sentinel-2",
    #                              producttype= product, cloudcoverpercentage = cloud)
    #     else:
    #         print('Cloud cover percentage not specified')
    #         products = api.query(footprint, date=(start, end), platformname="Sentinel-2",
    #                              producttype= product)
    
    # #Gather products to download from tiles
    # elif json is None:
    print('Retrieving Sentinel products from tile identifiers: ' + str(tilenames)) 
    products = OrderedDict()
    for t in tilenames:
        if cloud is not None:
            p = api.query(tileid=t, date=(start, end), platformname="Sentinel-2",
                          producttype= product, cloudcoverpercentage = cloud)
        else:
            print('Cloud cover percentage not specified')
            p = api.query(tileid=t, date=(start, end), platformname="Sentinel-2",
                          producttype= product)
        products.update(p)
            
    
    #Exit program if no products retrieved
    if len((list(products.keys())))==0:
        sys.exit('No products retrieved. Check input parameters')
    
    #Compile keys and file titles
    keys = list(products.keys())
    titles=[]
    idx = list(products.values())
    for i in idx:
        titles.append(i['title'])
    print(str(len(titles)) + ' products retrieved')
    
    return keys, idx 

# k,i = getSentinelLinks('penelopehow', 'CoreyFeldman1', ['22WES', '22WET'], '20210801', '20210901', [0,0.5], 'S2MSI1C')
# print(k[0])
# print(i[0])

# i1 = i[0]
# weblink = i1['link_alternative']
