#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 12:00:10 2022

@author: pho
"""
import ee, requests, zipfile, io
import datetime as dt



def getScenes(collection, date1, date2, box):
    scenes = ee.ImageCollection(collection).filterDate(date1, date2).filterBounds(box)
    
    # scenes = scenes.map(_mapRenameBands)
    
    # b,g,r,v,s1,s2 = getBands(scenes.first())
    # scenes = scenes.select([b,g,r,v,s1,s2])
    return scenes


def filterScenes(scenes, cloud):
    if cloud is not None:
        if scenes.getInfo()['id'][0:7] in 'LANDSAT':
            filtered = scenes.filter(ee.Filter.lte('CLOUD_COVER',cloud))       
        elif scenes.getInfo()['id'][0:7] in 'COPERNI':            
            filtered = scenes.filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE',cloud))

# #Potentially an additional filter by tile coverage using the 'system:footprint'
# #attribute. It is a LinearRing geometry and could be converted to an area
# #and then filtered by footprint area

    return filtered


def renameScenes(scenes):
    renamed_scenes = scenes.map(_mapRenameS2)
    return renamed_scenes
    

def resampleScenes(scenes):
    scenes_mosaic = scenes.map(_mapResample)
    return scenes_mosaic




def getMosaic(scenes, bands):
    scenes_all = scenes.select(bands)
    scenes_mean = scenes_all.mosaic()
    return scenes_mean





def classifyImage(image):
    image = _mapNDWI(image)
    image = _mapMNDWI(image)
    image = _mapAWEIsh(image)
    image = _mapAWEInsh(image)
    image = _mapBRIGHT(image)
    return image


# def classifyImages(scenes):    
#     scenes = scenes.map(_mapSpeckle)  
#     water = scenes.map(_mapClassify)
#     return water


def getImageURL(image, name, bounding_box, proj=None):
    # if proj==None:
    #     proj = image.projection().getInfo()
    # task = ee.batch.Export.image.toDrive(image=image.select('water'), 
    #                                region=bounding_box,
    #                                description=name,
    #                                crs=proj['crs'],
    #                                crsTransform = proj['transform'] )
    # task.start()
    # task.status() 
    
    link = image.getDownloadURL({
        'scale': 10,
      #   'width' : 720,
     	# 'height' : 391,
        'description': name,
        'crs': proj,
         # 'crsTransform' : proj['transform'],
        'fileFormat': 'GeoTIFF',
        'region': bounding_box})
    
    return link


def _mapRenameS2(img):
    b = img.select('B2').rename('blue')
    g = img.select('B3').rename('green')
    r = img.select('B4').rename('red') 
    v = img.select('B8').rename('vnir')
    s1 = img.select('B11').rename('swir1')
    s2 = img.select('B12').rename('swir2')               
    return img.addBands([b, g, r, v, s1, s2])

def _mapRenameLS(img):
    img.select('B2').rename('blue')
    img.select('B3').rename('green')
    img.select('B4').rename('red')        
    img.select('B5').rename('vnir')
    img.select('B6').rename('swir1')
    img.select('B7').rename('swir2')              
    return img


def _mapResample(img):
    resample = img.select(['swir1','swir2']).resample('bilinear').reproject(crs='EPSG:32622', scale=10)
    return img.addBands(resample)


def _mapNDWI(img):
    green = img.select('green')
    vnir = img.select('vnir')    
    ndwi = img.normalizedDifference([green,vnir]).rename('ndwi')   
    return img.addBands(ndwi)


def _mapMNDWI(img):
    green = img.select('green')
    swir1 = img.select('swir1')
    mndwi = img.normalizedDifference([green,swir1]).rename('mndwi')
    
    #Return image with classified water band
    return img.addBands(mndwi)


def _mapAWEIsh(img):
    aweish = img.expression('BLUE + 2.5 * GREEN - 1.5 * (VNIR + SWIR1) - 0.25 * SWIR2',
                            {'BLUE' : img.select('blue'), 
                            'GREEN' : img.select('green'),
                            'SWIR1' : img.select('swir1'),
                            'VNIR' : img.select('vnir'),
                            'SWIR2' : img.select('swir2')}).rename('aweish')
    return img.addBands(aweish)
 

def _mapAWEInsh(img):
    aweinsh = img.expression('4.0 * (GREEN - SWIR1) - (0.25 * VNIR + 2.75 * SWIR2)',
                             {'GREEN' : img.select('green'),
                             'SWIR1' : img.select('swir1'),
                             'VNIR' : img.select('vnir'),
                             'SWIR2' : img.select('swir2')}).rename('aweish')
    return img.addBands(aweinsh)   

def _mapBRIGHT(img):
    bright = img.expression('(RED + GREEN + BLUE) / 3',
                            {'BLUE' : img.select('blue'),
                            'GREEN' : img.select('green'),
                            'RED' : img.select('red')})
    return img.addBands(bright)



if __name__ == "__main__": 
    
    # Set collection
    # collection = "LANDSAT/LC08/C01/T1_SR"
    collection = "COPERNICUS/S2"
    # collection = 'COPERNICUS/S1_GRD'
    
    # Set AOI
    aoi1=[66.38236994767789, -49.537254073395566]
    aoi2=[66.4159086348496, -49.696555831208066]
    
    # Set date range
    date1='2019-08-01'
    date2='2019-08-31'
    
    # Set maximum cloud cover
    cloud=40
    
    # Set mask location
    ice_mask = 'users/pennyruthhow/GIMP_iceMask_edit_buffer7km'
    
    ee.Initialize()
    
    # Set the Area of Interest (AOI) through box coordinates
    box = ee.Geometry.Rectangle([aoi1[1], aoi1[0],
                                aoi2[1], aoi2[0]])
    
    # Get image collection
    scenes = getScenes(collection, date1, date2, box)
    scenes = filterScenes(scenes, cloud)
    print('Total number of scenes: ', scenes.size().getInfo())
    print('Number of bands per scene: ' 
          + str(len(scenes.first().bandNames().getInfo())))
    print('Band names: ' + str(scenes.first().bandNames().getInfo()))
     
    scenes = renameScenes(scenes)
    
    # Get average
    scenes = resampleScenes(scenes)
    aver = getMosaic(scenes, ['blue','green','red','vnir','swir1_1','swir2_1'])
    
    # # Classify water from SAR average image
    # water = classifyImage(aver)
    
    # # Get projection
    # proj = scenes.first().projection().getInfo()
    
    # Export to Drive
    out = collection.split('/')[-1] + '_' + date1 + '_' + date2
    link = getImageURL(aver, out, box, 'EPSG:32622')

    # Download image
    r = requests.get(link)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall("out")

    # r = rasterio.open('out/download.water.tif')
    # show(r)
    # image = r.read(1)




# image_list = scenes.toList(scenes.size())
# print(scenes.size().getInfo())  

  
# #Iterate through image collection (as list)    
# for i in range(scenes.size().getInfo()):
    
#     #Get image object
#     scene = ee.Image(image_list.get(i))

#     #Print acquisition information
#     date = ee.Date(scene.get('system:time_start'))
#     time = date.getInfo()['value']/1000.

#     #Assign band information
#     if scene.getInfo()['id'][0:7] in 'LANDSAT':
#         blue='B2'
#         green='B3'
#         red='B4'
#         vnir='B5'
#         swir1='B6'
#         swir2='B7' 
#         print('Scene number ' + str(i) + ': LANDSAT ' + 
#               str(dt.datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')) 
#               + ' (' + str(scene.get('CLOUD_COVER').getInfo()) + 
#               '% cloud cover)') 
#     elif scene.getInfo()['id'][0:7] in 'COPERNI':
#         blue='B2'
#         green='B3'
#         red='B4'
#         vnir='B8'
#         swir1='B11'
#         swir2='B12'
#         print('Scene number ' + str(i) + ': SENTINEL ' + 
#               str(dt.datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')) 
#               + ' (' + str(scene.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()) + 
#               '% cloud cover)') 
#     # else:
#     #     sys.exit('Image collection type not valid')
              
#     #Create NDWI image
#     ndwi = scene.normalizedDifference([green,vnir])   
    
#     #Create MNDWI image
#     mndwi = scene.normalizedDifference([green,swir1])

#     #Create AWEIsh
#     AWEIsh = scene.expression('BLUE + 2.5 * GREEN - 1.5 * (VNIR + SWIR1) - 0.25 * SWIR2',
#                               {'BLUE' : scene.select(blue),
#                                'GREEN' : scene.select(green),
#                                'SWIR1' : scene.select(swir1),
#                                'VNIR' : scene.select(vnir),
#                                'SWIR2' : scene.select(swir2)})
    
#     #Create AWEInsh
#     AWEInsh = scene.expression('4.0 * (GREEN - SWIR1) - (0.25 * VNIR + 2.75 * SWIR2)',
#                                {'GREEN' : scene.select(green),
#                                 'SWIR1' : scene.select(swir1),
#                                 'VNIR' : scene.select(vnir),
#                                 'SWIR2' : scene.select(swir2)})
   
#     #Create BRIGHT
#     bright = scene.expression('(RED + GREEN + BLUE) / 3',
#                               {'BLUE' : scene.select(blue),
#                                'GREEN' : scene.select(green),
#                                'RED' : scene.select(red)})
    
#     #Decision tree (con, true, false)
#     # classif=Con(bright<0, bright, Con(cloud==1,11, Con(bright>5000,7, Con(HS==0,1, Con(slp>15,2, Con(ndwi>0.3,10, Con(mndwi<0.1,3, Con((aweish<2000)|(aweish>5000),4, Con((aweinsh<4000)|(aweinsh>6000), 5, Con(((ndwi>0.05)&(slp<10)),10,6)))))))))) 
#     merged = ndwi.lt(0) and mndwi.lt(0) and AWEIsh.lt(0) and AWEInsh.lt(0) #and bright.lt(5000)
#     merged = merged.lt(1) 
    
        


   
        



# task = ee.batch.Export.image.toDrive(image=merged, 
#                                       region=merged.getInfo()['coordinates'],
#                                       description='imagetoDriveEg',
#                                       )


