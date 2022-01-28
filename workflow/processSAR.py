"""
GrIML SAR image processing module

@author: Penelope How
"""
import ee
import requests, zipfile, io
from rasterio.plot import show
import rasterio
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
    return scenes


def filterScenes(scenes, mode='IW', polar='HH'):
    '''Filter Google Earth Engine satellite scenes by mode and polarization

    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection object
    mode : str, optional
        Acquisition mode. The default is 'IW'.
    polar : str, optional
        Polarization. “VV” stands for vertical transmit, vertical recieved. 
        This means that both the signal transnmited from and recieved by from 
        the satellite is vertically polarized. Some surfaces alter the 
        polarization of the radar signal, but for water body detection, this is 
        usually unused. We only care that all of our images have the same kind 
        of transmit/recieve polarizations. The default is 'HH'.

    Returns
    -------
    filtered : ee.imagecollection.ImageCollection
        Filtered GEE image collection object
    '''
    filtered = scenes.filter(ee.Filter.listContains('transmitterReceiverPolarisation', 
                                                    polar)).filter(ee.Filter.eq(
                                                    'instrumentMode', mode))
    return filtered


def getSARaverage(scenes, band='HH'):
    '''Mosaic all satellite scenes in a GEE image collection    

    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection object
    band : str, optional
        Band name. The default is 'HH'.

    Returns
    -------
    scenes_mean : ee.image.Image
        Mosaicked GEE image object
    '''
    scenes_mean = scenes.select(band).mosaic()
    return scenes_mean


def classifyImage(image):
    '''Filter Google Earth Engine image for speckle, and then classify water bodies    

    Parameters
    ----------
    image : ee.image.Image
        GEE image object

    Returns
    -------
    water : ee.image.Image
        Classified GEE image object
    '''
    image = _mapSpeckle(image)
    water = _mapClassify(image)
    return water


def classifyImages(scenes):    
    '''Filter Google Earth Engine image collection for speckle, and then 
    classify water bodies. Image collection is mapped over using the ee map
    function    

    Parameters
    ----------
    image : ee.imagecollection.ImageCollection
        GEE image collection object

    Returns
    -------
    water : ee.imagecollection.ImageCollection
        Classified GEE image collection object
    '''
    scenes = scenes.map(_mapSpeckle)  
    water = scenes.map(_mapClassify)
    return water


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
    if proj==None:
        proj = image.projection().getInfo()
    # task = ee.batch.Export.image.toDrive(image=image.select('water'), 
    #                                region=bounding_box,
    #                                description=name,
    #                                crs=proj['crs'],
    #                                crsTransform = proj['transform'] )
    # task.start()
    # task.status() 
    
    link = image.select('water').getDownloadURL({
        'scale': 10,
      #   'width' : 720,
     	# 'height' : 391,
        'description': name,
        'crs': proj['crs'],
         'crsTransform' : proj['transform'],
        'fileFormat': 'GeoTIFF',
        'region': bounding_box})
    
    return link

    
def _mapSpeckle(img):
    '''Mapping function to perform speckle filter on all images in a GEE
    image collection

    Parameters
    ----------
    img : ee.image.Image
        GEE image object

    Returns
    -------
    ee.image.Image
        GEE image object with added speckle filter band
    '''
    hh = img.select('HH')
    hh_smooth = hh.focal_median(110,'circle', 'meters').rename('filtered')
    return img.addBands(hh_smooth)


def _mapClassify(img):
    '''Mapping function to perform water classification on all images in a GEE
    image collection

    Parameters
    ----------
    img : ee.image.Image
        GEE image object

    Returns
    -------
    ee.image.Image
        GEE image object with added water classification band
    '''
    hh = img.select('filtered')
    
    #Identify all pixels below threshold and set them to 1. All others=0
    water = hh.lt(-16).rename('water')
    
    #Remove all zero pixels
    water = water.updateMask(water)
    
    #Return image with classified water band
    return img.addBands(water)


if __name__ == "__main__": 
    
    # Set collection
    # collection = "LANDSAT/LC08/C01/T1_SR"
    # collection = "COPERNICUS/S2"
    collection = 'COPERNICUS/S1_GRD'
    
    # Set AOI
    aoi1=[66.38236994767789, -49.537254073395566]
    aoi2=[66.4159086348496, -49.696555831208066]
    
    # Set date range
    date1='2019-08-01'
    date2='2019-08-31'
    
    # Set maximum cloud cover
    cloud=80
    
    # Set mask location
    ice_mask = 'users/pennyruthhow/GIMP_iceMask_edit_buffer7km'
    
    ee.Initialize()
    
    # Set the Area of Interest (AOI) through box coordinates
    box = ee.Geometry.Rectangle([aoi1[1], aoi1[0],
                                aoi2[1], aoi2[0]])
    
    print(type(box))
    
    # Get image collection
    scenes = getScenes(collection, date1, date2, box)
    scenes = filterScenes(scenes)
    print('Total number of scenes: ', scenes.size().getInfo())
    print('Number of bands per scene: ' 
          + str(len(scenes.first().bandNames().getInfo())))
    print('Band names: ' + str(scenes.first().bandNames().getInfo()))
    
    # Get projection
    proj = scenes.first().select('HH').projection().getInfo()
     
    # Get average
    aver = getSARaverage(scenes)
    
    # Classify water from SAR average image
    water = classifyImage(aver)
    
    # Get image link
    out = collection.split('/')[-1] + '_' + date1 + '_' + date2
    link = getImageURL(water, out, box, proj)

    # Download image
    r = requests.get(link)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall("out")

    r = rasterio.open('out/download.water.tif')
    show(r)
    image = r.read(1)
    
