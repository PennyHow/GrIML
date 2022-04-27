"""
GrIML DEM processing module

@author: Penelope How
"""
import ee, unittest
import numpy as np

def getElevation(collection):
    '''Get elevation from Google Earth Engine image collection
    
    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection object
        
    Returns
    -------
    ee.imagecollection.ImageCollection
      GEE image object
    '''
    return collection.select('elevation')


def getSlope(elevation):
    '''Return slope from elevation
    
    Parameters
    ----------
    elevation : ee.imagecollection.ImageCollection
      Elevation 
    
    Returns
    -------
    ee.image.Image
      GEE slope computation
    '''
    return ee.Terrain.slope(elevation)


def getSinks(elevation_int, border_val, kernel_size):
    '''Compute sinks in GEE DEM image
    
    Parameters
    ----------
    image : ee.image.Image
       GEE DEM image object representing elevation
    kernel_size : int
       Kernel size for computing sinks
    
    Returns
    -------
    sinks : ee.image.Image
       Computed hydrological sinks, represented as a binary image where 1=sink
    '''
    fill = ee.Terrain.fillMinima(elevation_int, border_val, kernel_size)
    diff = fill.subtract(elevation_int)
    sinks = diff.gt(0).rename('sinks')
    sinks = sinks.updateMask(sinks)
    return sinks


class TestDEM(unittest.TestCase): 
    def testSlope(self):
        if not ee.data._credentials:
            ee.Initialize()
        dem = ee.Image('UMN/PGC/ArcticDEM/V3/2m_mosaic')
        elevation = getElevation(dem)
        slope = getSlope(elevation)
        self.assertIsNotNone(slope.getInfo())
        
    def testSinks(self):
        if not ee.data._credentials:
            ee.Initialize()
        dem = ee.Image('UMN/PGC/ArcticDEM/V3/2m_mosaic')
        elevation = getElevation(dem) 
        elevation = ee.Image.int64(elevation)
        sinks = getSinks(elevation, 10, 50)
        self.assertIsNotNone(sinks.getInfo())                 
    
if __name__ == "__main__": 
    unittest.main() 
    
                       
    # # Strips
    # var dataset = ee.ImageCollection('UMN/PGC/ArcticDEM/V3/2m');
    # var elevation = dataset.select('elevation');
    # var elevationVis = {
    #   min: -50.0,
    #   max: 1000.0,
    #   palette: ['0d13d8', '60e1ff', 'ffffff'],
    # };
    # Map.setCenter(-63.402, 66.368, 7);
    # Map.addLayer(elevation, elevationVis, 'Elevation')