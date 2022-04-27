"""
GrIML Visible (VIS) image processing module

@author: Penelope How
"""
import ee, unittest

def filterS2scenes(scenes, cloud):
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
    filtered = scenes.filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE',cloud))

    # Potentially an additional filter by tile coverage using the 'system:footprint'
    # attribute. It is a LinearRing geometry and could be converted to an area
    # and then filtered by footprint area

    return filtered


def filterLSscenes(scenes, cloud):
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
    filtered = scenes.filter(ee.Filter.lte('CLOUD_COVER',cloud))       

    # Potentially an additional filter by tile coverage using the 'system:footprint'
    # attribute. It is a LinearRing geometry and could be converted to an area
    # and then filtered by footprint area

    return filtered


def maskS2clouds(scenes):
    '''Mask clouds from GEE Sentinel-2 image collection object

    Parameters
    ----------
    img: ee.imagecollection.ImageCollection
        GEE image object

    Returns
    -------
    ee.imagecollection.ImageCollection
        GEE image object with masked out cloud regions
    '''
    return scenes.map(_mapS2Clouds)
    

def maskL8clouds(scenes):
    '''Mask clouds from GEE Landsat 8 image collection object

    Parameters
    ----------
    img: ee.imagecollection.ImageCollection
        GEE image object

    Returns
    -------
    ee.imagecollection.ImageCollection
        GEE image object with masked out cloud regions
    '''
    return scenes.map(_mapL8Clouds)


def maskL7clouds(scenes):
    '''Mask clouds from GEE Landsat 7 image collection object

    Parameters
    ----------
    img: ee.imagecollection.ImageCollection
        GEE image object

    Returns
    -------
    ee.imagecollection.ImageCollection
        GEE image object with masked out cloud regions
    '''
    return scenes.map(_mapL7Clouds)


def renameS2scenes(scenes):
    '''Rename Sentinel-2 bands in GEE image collection object

    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection

    Returns
    -------
    ee.imagecollection.ImageCollection
        GEE image collection with renamed bands
    '''
    return scenes.map(_mapRenameS2)


def renameL8scenes(scenes):
    '''Rename Landsat 8 bands in GEE image collection object

    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection

    Returns
    -------
    ee.imagecollection.ImageCollection
        GEE image collection with renamed bands
    '''
    return scenes.map(_mapRenameL8)
  
    
def renameL7scenes(scenes):
    '''Rename Landsat 7 bands in GEE image collection object

    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection

    Returns
    -------
    ee.imagecollection.ImageCollection
        GEE image collection with renamed bands
    '''
    return scenes.map(_mapRenameL7)
  

def resampleS2scenes(scenes):
    '''Resample Sentinel-2 bands in GEE image collection object

    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection

    Returns
    -------
    ee.imagecollection.ImageCollection
        GEE image collection with resampled bands
    '''
    return scenes.map(_mapResampleS2)


# def maskS2shadow(scene, elevation):
    
#     # # Mask scenes for terrain shadowing using the ArcticDEM mosaic
#     # shadow_elev = getScene('UMN/PGC/ArcticDEM/V3/2m_mosaic', 
#     #                        box).select('elevation')
    
#     azimuth = scene.get('MEAN_SOLAR_AZIMUTH_ANGLE').getInfo()
#     zenith = scene.get('MEAN_SOLAR_ZENITH_ANGLE').getInfo()
#     mask = ee.Terrain.hillShadow(elevation, azimuth, zenith)
#     return scene.updateMask(mask) 


def getNDWI(image, g, vnir):
    '''Derive NDWI (Normalised Difference Water Index) band

    Parameters
    ----------
    image : ee.Image
        GEE image
    g : str
        Green band name
    vnir : str
        VNIR band name

    Returns
    -------
    ee.Image
        NDWI image
    '''
    return image.normalizedDifference([g, vnir]) 
 
def getMNDWI(image, g, swir1):
    '''Derive MNDWI (Modified Normalised Difference Water Index) band

    Parameters
    ----------
    image : ee.Image
        GEE image
    g : str
        Green band name
    swir1 : str
        SWIR band name

    Returns
    -------
    ee.Image
        MNDWI image
    '''
    return image.normalizedDifference([g, swir1])

def getAWEISH(image, b, g, vnir, swir1, swir2):
    '''Derive AWEIsh (Automated Water Extraction Index with shadowing) band

    Parameters
    ----------
    image : ee.Image
        GEE image
    b : str
        Blue band name
    g : str
        Green band name
    vnir : str
        VNIR band name
    swir1 : str
        SWIR 1 band name
    swir2 : str
        SWIR 2 band name

    Returns
    -------
    ee.Image
        AWEIsh image
    '''
    return image.expression('BLUE + 2.5 * GREEN - 1.5 * (VNIR + SWIR1) - 0.25 * SWIR2',
                            {'BLUE' : image.select(b), 
                            'GREEN' : image.select(g),
                            'SWIR1' : image.select(swir1),
                            'VNIR' : image.select(vnir),
                            'SWIR2' : image.select(swir2)})

def getAWEINSH(image, g, vnir, swir1, swir2):
    '''Derive AWEInsh (Automated Water Extraction Index without shadowing) band

    Parameters
    ----------
    image : ee.Image
        GEE image
    g : str
        Green band name
    vnir : str
        VNIR band name
    swir1 : str
        SWIR 1 band name
    swir2 : str
        SWIR 2 band name

    Returns
    -------
    ee.Image
        AWEInsh image
    '''
    return image.expression('4.0 * (GREEN - SWIR1) - (0.25 * VNIR + 2.75 * SWIR2)',
                              {'GREEN' : image.select(g),
                              'SWIR1' : image.select(swir1),
                              'VNIR' : image.select(vnir),
                              'SWIR2' : image.select(swir2)})

def getBRIGHT(image, r, g, b):
    '''Derive BRIGHT (simple RGB ratio) band

    Parameters
    ----------
    image : ee.Image
        GEE image
    r : str
        Red band name
    g : str
        Green band name
    b : str
        Blue band name

    Returns
    -------
    ee.Image
        AWEInsh image
    '''
    return image.expression('(RED + GREEN + BLUE) / 3',
                            {'BLUE' : image.select(b),
                            'GREEN' : image.select(g),
                            'RED' : image.select(r)})
    
def getClassification(ndwi, mndwi, aweish, aweinsh, bright): 
                      # ndwi_t, mndwi_t, aweish_t1, aweish_t2, aweinsh_t1, aweinsh_t2, bright_t):  
    '''Generate classification from thresholded multi-spectral indices
    
    ndwi : ee.Image
        NDWI band
    mndwi : ee.Image
        MNDWI band
    aweish : ee.Image
        AWEIsh band
    aweinsh : ee.Image
        AWEInsh band
    bright : ee.Image
        BRIGHT band
    '''
    classified =  ee.Image().expression("(BRIGHT > 5000) ? 0"
                                        ": (NDWI > 0.3) ? 1 "
                                        ": (MNDWI < 0.1) ? 0 "
                                        ": (AWEISH < 2000) ? 0"
                                        ": (AWEISH > 5000) ? 0"
                                        ": (AWEINSH < 4000) ? 0"
                                        ": (AWEINSH > 6000) ? 0"
                                        ": 1",
                                        {'NDWI' : ndwi,
                                        'MNDWI' : mndwi,
                                        'AWEISH' : aweish,
                                        'AWEINSH' : aweinsh,
                                        'BRIGHT' : bright}).rename('water') 
    return classified.updateMask(classified)


def classifyVISimage(image):
    '''Classify water bodies from all images in a GEE image collection, using
    the mapping function to iterate over all image objects
    
    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
       GEE image collection object

    Returns
    -------
    classified : ee.imagecollection.ImageCollection
       GEE image collection object with added water classification band 
    '''
    image = _mapNDWI(image)
    image = _mapMNDWI(image)
    image = _mapAWEIsh(image)
    image = _mapAWEInsh(image)
    image = _mapBRIGHT(image)

    classified = image.expression("(BRIGHT > 5000) ? 0"
                                ": (NDWI > 0.3) ? 1 "
                                ": (MNDWI < 0.1) ? 0 "
                                ": (AWEISH < 2000) ? 0"
                                ": (AWEISH > 5000) ? 0"
                                ": (AWEINSH < 4000) ? 0"
                                ": (AWEINSH > 6000) ? 0"
                                ": 1",
                               {'NDWI' : image.select('ndwi'),
                                'MNDWI' : image.select('mndwi'),
                                'AWEISH' : image.select('aweish'),
                                'AWEINSH' : image.select('aweinsh'),
                                'BRIGHT' : image.select('bright')}).rename('water') 
                
    # Remove all zero pixels
    classified = classified.updateMask(classified)
    
    return classified
    

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


def _mapRenameL8(img):
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
    b = img.select('B2').rename('blue')
    g = img.select('B3').rename('green')
    r = img.select('B4').rename('red')        
    v = img.select('B5').rename('vnir')
    s1 = img.select('B6').rename('swir1')
    s2 = img.select('B7').rename('swir2')              
    return img.addBands([b, g, r, v, s1, s2])


def _mapRenameL7(img):
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
    b = img.select('B1').rename('blue')
    g = img.select('B2').rename('green')
    r = img.select('B3').rename('red')        
    v = img.select('B4').rename('vnir')
    s1 = img.select('B5').rename('swir1')
    s2 = img.select('B7').rename('swir2')              
    return img.addBands([b, g, r, v, s1, s2])


def _mapS2Clouds(img):
    '''Mapping function to mask clouds from GEE Sentinel-2 image object,
    using the QA60 band

    Parameters
    ----------
    img: ee.image.Image
        GEE image object

    Returns
    -------
    ee.image.Image
        GEE image object with masked out cloud regions
    '''
    qa = img.select('QA60')
    mask = qa.bitwiseAnd(1<<10).Or(qa.bitwiseAnd(1<<11))
    return img.updateMask(mask.Not())                 


def _mapL8Clouds(img):
    '''Mapping function to mask clouds from GEE Landsat 8 image object,
    using the BQA band

    Parameters
    ----------
    img: ee.image.Image
        GEE image object

    Returns
    -------
    ee.image.Image
        GEE image object with masked out cloud regions
    '''
    qa = img.select('BQA');
    mask = qa.bitwiseAnd(1<<4).eq(0);
    return img.updateMask(mask) 


def _mapL7Clouds(img):
    '''Mapping function to mask clouds from GEE Landsat 7 image object,
    using the QA band

    Parameters
    ----------
    img: ee.image.Image
        GEE image object

    Returns
    -------
    ee.image.Image
        GEE image object with masked out cloud regions
    '''

    qa = img.select('pixel_qa')
    cloud = qa.bitwiseAnd(1<<5).And(qa.bitwiseAnd(1<<7)).Or(qa.bitwiseAnd(1 << 3))
    mask2 = img.mask().reduce(ee.Reducer.min());
    return img.updateMask(cloud.Not()).updateMask(mask2)
    

def _mapResampleS2(img):
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
    resample = img.select(['swir1',
                           'swir2']).resample('bilinear').reproject(crs='EPSG:4326', 
                           scale=10).rename(['swir1', 
                           'swir2'])
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
    ndwi = img.normalizedDifference(['green_mean', 'vnir_mean']).rename('ndwi')   
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
    mndwi = img.normalizedDifference(['green_mean','swir1_1_mean']).rename('mndwi')
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
                            {'BLUE' : img.select('blue_mean'), 
                            'GREEN' : img.select('green_mean'),
                            'SWIR1' : img.select('swir1_1_mean'),
                            'VNIR' : img.select('vnir_mean'),
                            'SWIR2' : img.select('swir2_1_mean')}).rename('aweish')
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
                             {'GREEN' : img.select('green_mean'),
                             'SWIR1' : img.select('swir1_1_mean'),
                             'VNIR' : img.select('vnir_mean'),
                             'SWIR2' : img.select('swir2_1_mean')}).rename('aweinsh')
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
                            {'BLUE' : img.select('blue_mean'),
                            'GREEN' : img.select('green_mean'),
                            'RED' : img.select('red_mean')}).rename('bright')
    return img.addBands(bright)


class TestVIS(unittest.TestCase): 
    def testS2(self):
        if not ee.data._credentials:
            ee.Initialize()
        scenes = ee.ImageCollection('COPERNICUS/S2').filterDate('2019-08-01',
                                '2019-08-05').filterBounds(ee.Geometry.Rectangle(
                                [-49.53, 66.38, -49.69, 66.41]))
        scenes = filterS2scenes(scenes, 50)
        scenes = maskS2clouds(scenes)  
        scenes = renameS2scenes(scenes)
        scenes = resampleS2scenes(scenes)
        aver = scenes.select(['blue','green','red','vnir',
                             'swir1_1','swir2_1']).reduce(ee.Reducer.mean())
        water_s2 = classifyVISimage(aver)
        self.assertIsNotNone(water_s2.getInfo())
 
    def testLS(self):
        if not ee.data._credentials:
            ee.Initialize()
        scenes = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR').filterDate('2019-08-01',
                                '2019-08-05').filterBounds(ee.Geometry.Rectangle(
                                [-49.53, 66.38, -49.69, 66.41]))
        scenes = filterLSscenes(scenes, 50)
        # scenes = renameLSscenes(scenes)
        # aver = scenes.select(['blue','green','red','vnir',
        #                      'swir1','swir2']).reduce(ee.Reducer.mean())       
        # water_ls = classifyVISimage(aver)
        self.assertIsNotNone(scenes.getInfo())                 
    
if __name__ == "__main__": 
    unittest.main() 