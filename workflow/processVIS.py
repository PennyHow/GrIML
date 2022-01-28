"""
GrIML Visible (BIS) image processing module

@author: Penelope How
"""
import ee, requests, zipfile, io
import datetime as dt


def getScenes(collection, date1, date2, box):
    '''Get satellite scenes from Google Earth Engine collection    

    Parameters
    ----------
    collection : str
        GEE collection
    date1 : str DESCRIPTION
        Start date, YY-MM-DD
    date2 : str
        date, YY-MM-DD
    box : ee.geometry.Geometry
        Bounding box

    Returns
    -------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection object
    '''
    scenes = ee.ImageCollection(collection).filterDate(date1, date2).filterBounds(box)
    
    # scenes = scenes.map(_mapRenameBands)
    
    # b,g,r,v,s1,s2 = getBands(scenes.first())
    # scenes = scenes.select([b,g,r,v,s1,s2])
    return scenes


def filterScenes(scenes, cloud):
    '''Filter Google Earth Engine satellite scenes by cloud cover

    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection object
    cloud : int, optional
        Maximum cloud cover %

    Returns
    -------
    filtered : ee.imagecollection.ImageCollection
        Filtered GEE image collection object
    '''
    if cloud is not None:
        if scenes.getInfo()['id'][0:7] in 'LANDSAT':
            filtered = scenes.filter(ee.Filter.lte('CLOUD_COVER',cloud))       
        elif scenes.getInfo()['id'][0:7] in 'COPERNI':            
            filtered = scenes.filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE',cloud))

    # Potentially an additional filter by tile coverage using the 'system:footprint'
    # attribute. It is a LinearRing geometry and could be converted to an area
    # and then filtered by footprint area

    return filtered


def renameScenes(scenes):
    '''Rename bands in GEE image collection object

    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection

    Returns
    -------
    renamed_scenes : ee.imagecollection.ImageCollection
        GEE image collection with renamed bands
    '''
    renamed_scenes = scenes.map(_mapRenameS2)
    return renamed_scenes
    

def resampleScenes(scenes):
    '''Resample bands in GEE image collection object

    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection

    Returns
    -------
    scenes_resample : ee.imagecollection.ImageCollection
        GEE image collection with resampled bands
    '''
    scenes_resample = scenes.map(_mapResample)
    return scenes_resample


def getMosaic(scenes, bands):
    '''Mosaic all satellite scenes in a GEE image collection    

    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection object
    bands : str/list
        Band name/s

    Returns
    -------
    scenes_mean : ee.image.Image
        Mosaicked GEE image object
    '''
    scenes_all = scenes.select(bands)
    scenes_mean = scenes_all.mosaic()
    return scenes_mean


def classifyImage(image):
    '''Classify water bodies from all images in a GEE image collection, using
    the mapping function to iterate over all image objects
    
    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection object

    Returns
    -------
    scenes_mean : ee.imagecollection.ImageCollection
        GEE image collection object with added water classification band 
    '''
    image = _mapNDWI(image)
    image = _mapMNDWI(image)
    image = _mapAWEIsh(image)
    image = _mapAWEInsh(image)
    image = _mapBRIGHT(image)
    return image


def getImageURL(image, name, bounding_box, proj=None):
    '''Get download url for GEE image

    Parameters
    ----------
    image : ee.image.Image
        GEE image object
    name : str
        Description name
    bounding_box : ee.geometry.Geometry
        Bounding box
    proj : dict, optional
        Projection dictionary. The default is None.

    Returns
    -------
    link : str
        Download url
    '''
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
    '''Mapping function to rename Sentinel-2 bands in GEE image object

    Parameters
    ----------
    img: ee.image.Image
        GEE image object

    Returns
    -------
    ee.image.Image
        GEE image object with renamed bands
    '''
    b = img.select('B2').rename('blue')
    g = img.select('B3').rename('green')
    r = img.select('B4').rename('red') 
    v = img.select('B8').rename('vnir')
    s1 = img.select('B11').rename('swir1')
    s2 = img.select('B12').rename('swir2')               
    return img.addBands([b, g, r, v, s1, s2])

def _mapRenameLS(img):
    '''Mapping function to rename Landsat 8 bands in GEE image object

    Parameters
    ----------
    img: ee.image.Image
        GEE image object

    Returns
    -------
    ee.image.Image
        GEE image object with renamed bands
    '''
    img.select('B2').rename('blue')
    img.select('B3').rename('green')
    img.select('B4').rename('red')        
    img.select('B5').rename('vnir')
    img.select('B6').rename('swir1')
    img.select('B7').rename('swir2')              
    return img


def _mapResample(img):
    '''Mapping function to resample Sentinel-2 SWIR bands from 20 m to 10 m

    Parameters
    ----------
    img: ee.image.Image
        GEE image object

    Returns
    -------
    ee.image.Image
        GEE image object with resampled bands
    '''
    resample = img.select(['swir1','swir2']).resample('bilinear').reproject(crs='EPSG:32622', scale=10)
    return img.addBands(resample)


def _mapNDWI(img):
    '''Mapping function to generate NDWI band in GEE image object

    Parameters
    ----------
    img: ee.image.Image
        GEE image object

    Returns
    -------
    ee.image.Image
        GEE image object with added NDWI band
    '''
    green = img.select('green')
    vnir = img.select('vnir')    
    ndwi = img.normalizedDifference([green,vnir]).rename('ndwi')   
    return img.addBands(ndwi)


def _mapMNDWI(img):
    '''Mapping function to generate MNDWI band in GEE image object

    Parameters
    ----------
    img: ee.image.Image
        GEE image object

    Returns
    -------
    ee.image.Image
        GEE image object with added MNDWI band
    '''
    green = img.select('green')
    swir1 = img.select('swir1')
    mndwi = img.normalizedDifference([green,swir1]).rename('mndwi')
    return img.addBands(mndwi)


def _mapAWEIsh(img):
    '''Mapping function to generate AWEIsh band in GEE image object

    Parameters
    ----------
    img: ee.image.Image
        GEE image object

    Returns
    -------
    ee.image.Image
        GEE image object with added AWEIsh band
    '''
    aweish = img.expression('BLUE + 2.5 * GREEN - 1.5 * (VNIR + SWIR1) - 0.25 * SWIR2',
                            {'BLUE' : img.select('blue'), 
                            'GREEN' : img.select('green'),
                            'SWIR1' : img.select('swir1'),
                            'VNIR' : img.select('vnir'),
                            'SWIR2' : img.select('swir2')}).rename('aweish')
    return img.addBands(aweish)
 

def _mapAWEInsh(img):
    '''Mapping function to generate AWEInsh band in GEE image object

    Parameters
    ----------
    img: ee.image.Image
        GEE image object

    Returns
    -------
    ee.image.Image
        GEE image object with added AWEInsh band
    '''
    aweinsh = img.expression('4.0 * (GREEN - SWIR1) - (0.25 * VNIR + 2.75 * SWIR2)',
                             {'GREEN' : img.select('green'),
                             'SWIR1' : img.select('swir1'),
                             'VNIR' : img.select('vnir'),
                             'SWIR2' : img.select('swir2')}).rename('aweish')
    return img.addBands(aweinsh)   


def _mapBRIGHT(img):
    '''Mapping function to generate BRIGHT band in GEE image object

    Parameters
    ----------
    img: ee.image.Image
        GEE image object

    Returns
    -------
    ee.image.Image
        GEE image object with added BRIGHT band
    '''
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
