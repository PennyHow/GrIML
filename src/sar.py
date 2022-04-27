"""
GrIML SAR image processing module

@author: Penelope How
"""
import ee, unittest

def filterSARscenes(scenes, mode='IW', polar='HH'):
    '''Filter Google Earth Engine satellite scenes by mode and polarization

    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection object
    mode : str, optional
        Acquisition mode. The default is 'IW'.
    polar : str, optional
        Polarization. “VV” stands for vertical transmit, vertical recieved. 
        This means that both the signal transnmited from and recieved by 
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
    # Filter for ascending and descending paths
    # ascend = filtered.filter(ee.Filter.eq('orbitProperties_pass', 
    #                                       'ASCENDING'))
    # descend = filtered.filter(ee.Filter.eq('orbitProperties_pass', 
    #                                        'DESCENDING'))
    return filtered


def classifySARimage(image, threshold, polar, smooth):
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
    # Select polarization and smooth
    p = image.select(polar)
    p_smooth = p.focal_median(smooth,'circle', 'meters')

    # Identify all pixels below threshold and set them to 1. All others=0
    water = p_smooth.lt(threshold).rename('water')
    
    # Remove all zero pixels
    water = water.updateMask(water)
    
    # Return image with classified water band
    return water


def classifySARimages(scenes):    
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
    return water.select('water')

    
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
    
    # Identify all pixels below threshold and set them to 1. All others=0
    water = hh.lt(-20).rename('water')
    
    # Remove all zero pixels
    water = water.updateMask(water)
    
    # Return image with classified water band
    return img.addBands(water)


class TestSAR(unittest.TestCase): 
    def testSARscenes(self):
        if not ee.data._credentials:
            ee.Initialize()
        scenes = ee.ImageCollection('COPERNICUS/S1_GRD').filterDate('2019-08-01',
                                '2019-08-05').filterBounds(ee.Geometry.Rectangle(
                                [-49.53, 66.38, -49.69, 66.41]))
        filtered = filterSARscenes(scenes)
        classified = classifySARimages(filtered)
        self.assertIsNotNone(classified.getInfo())
 
    def testSARimage(self):
        if not ee.data._credentials:
            ee.Initialize()
        scenes = ee.ImageCollection('COPERNICUS/S1_GRD').filterDate('2019-08-01',
                                '2019-08-05').filterBounds(ee.Geometry.Rectangle(
                                [-49.53, 66.38, -49.69, 66.41]))
        image = scenes.first()
        classified = classifySARimage(image)
        self.assertIsNotNone(classified.getInfo())                 
    
if __name__ == "__main__": 
    unittest.main() 