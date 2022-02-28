"""
GrIML process module and GEE class

@author: Penelope How
"""
import ee
from retrieve import getScenes, getScene, getInt, getSmooth, getMosaic, \
    getMean, maskImage, splitBBox, getFeatures
from processSAR import filterSARscenes, classifySARimage
from processVIS import filterS2scenes, maskS2clouds, renameS2scenes, \
    resampleS2scenes, classifyVISimage, filterLSscenes, maskL8clouds, \
    renameL8scenes, maskL7clouds, renameL7scenes
from processDEM import getElevation, getSinks

#------------------------------------------------------------------------------

class GEE(object):
    '''Class object for rigid classification workflows using the 
    Google Earth Engine (GEE) Python API'''
    
    def __init__(self, date_range, aoi_range):
        '''GEE object initialisation
        
        Parameters
        ----------
        date_range : list
           Date 1 and date 2 for image search
        aoi_range : list
           xy1 and xy2 for image search
        '''
        self.date0 = date_range[0]
        self.date1 = date_range[1]
        
        self.aoi0, self.aoi1 = self.checkAOI(aoi_range[0], aoi_range[1])
        self.bbox = self.getBBox(self.aoi0, self.aoi1)

        ee.Initialize()
        
    def checkAOI(self):
        '''AOI input checker'''
        # Check size of aoi (for download/vector retrieval limits)
        pass
    
    def checkDate(self):
        '''Date period input checker'''
        # If date is string, check it is correctly formatted. If datetime then
        # convert it to formatted string
        pass
    
    def getBBox(self, aoi0, aoi1):
        '''Bounding box generator'''
        return ee.Geometry.Rectangle([aoi0[0], aoi0[1],
                                    aoi1[0], aoi1[1]])

    def divideBBox(self, wh=0.3, ww=0.3, oh=0.05, ow=0.05):
        '''Split bounding box into gridded regions of specific size and 
        overlap'''
        grid = splitBBox(self.aoi0, self.aoi1, wh, ww, oh, ow)
        return [ee.Geometry.Rectangle(g[0], g[1], g[2], g[3]) for g in grid]
    
    def getGIMPMask(self, image='OSU/GIMP/2000_ICE_OCEAN_MASK'):
        '''Get GIMP mask for masking ocean and ice regions'''
        img = ee.Image(image)
        ocean_mask = img.select('ocean_mask').eq(0)
        ice_mask = img.select('ice_mask').eq(0)
        return ocean_mask, ice_mask

    def processADEM_strip(self):
        '''Classify water bodies from ArcticDEM strip data'''
        pass
    
    def processADEM_mosaic(self, smooth=110, fill=7, speckle=50, mask=None):
        '''Classify water bodies from ArcticDEM mosaic data
        
        Parameters
        ----------
        smooth : int, optional
           Pre-classification image smoothing coefficient, default is 110 
        fill : int, optional
           Sink fill coefficient, default is 7
        speckle : int, optional
           Post-classification speckle filtering, default is 50
           
        Returns
        -------
        features : list
           List of classified shapely.geometry.polygon objects
        '''
        dem_col = 'UMN/PGC/ArcticDEM/V3/2m_mosaic'
        scenes = getScene(dem_col, self.bbox)
        print(f'\nScenes gathered from {dem_col}')
        
        # Get elevation and slope
        elevation = getElevation(scenes)
        
        # Get smoothed elevation
        elevation = getSmooth(elevation, smooth)
        
        # Mask out ocean pixels
        ocean_mask, ice_mask = self.getGIMPMask()
        elevation = maskImage(elevation, ocean_mask)
        elevation = maskImage(elevation, ice_mask)
        
        # Get sinks
        # sinks = ee.Terrain.fillMinima(elev_int, 10, 50).rename('sinks')
        sinks = getSinks(elevation, 7)
            
        # Remove speckle with smoothing
        sinks = getSmooth(sinks, 50).rename('dem_sinks')
        sinks = getInt(sinks)
        print(f'{dem_col} scenes classified')
        print('Band names: ' + str(sinks.bandNames().getInfo())) 
        
        # Make function for guiding retrieval approach             
        features = getFeatures(sinks, self.bbox)
        print(f'{len(features)} vector features identified')  
        
        return features
    
    
    def processS1(self, polar='HH', mask=None):
        '''Classify water bodies from Sentinel-1 GRD image collection
        
        Parameters
        ----------
        polar : str, optional
           Polarization, default is "HH" 
        
        Returns
        -------
        features : list
           List of classified shapely.geometry.polygon objects
        '''
        # Set collection
        sar_col = 'COPERNICUS/S1_GRD'
         
        # Get image collection
        scenes = getScenes(sar_col, self.date0, self.date1, self.bbox)
        scenes = filterSARscenes(scenes)
        print(f'\nScenes gathered from {sar_col}')
        print('Total number of scenes: ', scenes.size().getInfo())
        print('Number of bands per scene: ' 
              + str(len(scenes.first().bandNames().getInfo())))
        print('Band names: ' + str(scenes.first().bandNames().getInfo()))
            
        # Get average
        aver = getMosaic(scenes, 'HH')
        
        # Mask out ocean pixels
        ocean_mask, ice_mask = self.getGIMPMask()
        aver = maskImage(aver, ocean_mask)
        aver = maskImage(aver, ice_mask)
        
        # Classify water from SAR average image
        water_sar = classifySARimage(aver)
        print(f'{sar_col} scenes classified')
        print('Band names: ' + str(water_sar.bandNames().getInfo()))  
          
        features = getFeatures(water_sar, self.bbox)
        print(f'{len(features)} vector features identified')  
        
        return features
    
    
    def processS2(self, cloud=50):
        '''Classify water bodies from Sentinel-2 image collection
        
        Parameters
        ----------
        cloud: int, optional
           Maximum cloud cover percentage, default is 50 
        
        Returns
        -------
        features : list
           List of classified shapely.geometry.polygon objects
        '''  
        # Set collection
        vis_col1 = "COPERNICUS/S2"
        
        # Get image collection
        scenes = getScenes(vis_col1, self.date0, self.date1, self.bbox)
        scenes = filterS2scenes(scenes, cloud)
        print(f'\nScenes gathered from {vis_col1}')
        print('Total number of scenes: ', scenes.size().getInfo())
        print('Number of bands per scene: ' 
              + str(len(scenes.first().bandNames().getInfo())))
        print('Band names: ' + str(scenes.first().bandNames().getInfo()))
        
        # Mask scenes for clouds
        scenes = maskS2clouds(scenes)  
            
        # Get average of spectific bands
        scenes = renameS2scenes(scenes)
        scenes = resampleS2scenes(scenes)
        aver = getMean(scenes, ['blue','green','red','vnir','swir1_1','swir2_1'])   
        print('Scenes resampled and mosiacked')
        print('Band names: ' + str(aver.bandNames().getInfo())) 
        
        # Classify water from VIS average image, and mask out ocean pixels
        water_s2 = classifyVISimage(aver)
        
        # Mask out ocean pixels
        ocean_mask, ice_mask = self.getGIMPMask()        
        water_s2 = maskImage(water_s2, ocean_mask)
        water_s2 = maskImage(water_s2, ice_mask)
        print(f'{vis_col1} scenes classified')
        print('Band names: ' + str(water_s2.bandNames().getInfo()))     
        
        features = getFeatures(water_s2, self.bbox)
        print(f'{len(features)} vector features identified')  
        
        return features


    def processL8(self, cloud=50):
        '''Classify water bodies from Landsat 8 image collection
        
        Parameters
        ----------
        cloud: int, optional
           Maximum cloud cover percentage, default is 50 
        
        Returns
        -------
        features : list
           List of classified shapely.geometry.polygon objects
        '''  
        # Set collection
        vis_col2 = "LANDSAT/LC08/C01/T1_TOA"
        
        # Get image collection
        scenes = getScenes(vis_col2, self.date0, self.date1, self.bbox)
        scenes = filterLSscenes(scenes, cloud)
        print(f'\nScenes gathered from {vis_col2}')
        print('Total number of scenes: ', scenes.size().getInfo())
        print('Number of bands per scene: ' 
              + str(len(scenes.first().bandNames().getInfo())))
        print('Band names: ' + str(scenes.first().bandNames().getInfo()))
        
        # Mask scenes for clouds
        scenes = maskL8clouds(scenes)  
        # ee.Terrain.hillshade(image, azimuth, elevation)
            
        # Get average of spectific bands
        scenes = renameL8scenes(scenes)
        aver = getMean(scenes, ['blue','green','red','vnir','swir1','swir2'])
        print('Scenes resampled and mosiacked')
        print('Band names: ' + str(aver.bandNames().getInfo())) 
        
        # Classify water from VIS average image, and mask out ocean pixels
        # water_ls = classifyVISimage(aver)
        
        ndwi = aver.normalizedDifference(['green_mean', 'vnir_mean']).rename('ndwi') 
        mndwi = aver.normalizedDifference(['green_mean','swir1_mean']).rename('mndwi')
        aweish = aver.expression('BLUE + 2.5 * GREEN - 1.5 * (VNIR + SWIR1) - 0.25 * SWIR2',
                                {'BLUE' : aver.select('blue_mean'), 
                                'GREEN' : aver.select('green_mean'),
                                'SWIR1' : aver.select('swir1_mean'),
                                'VNIR' : aver.select('vnir_mean'),
                                'SWIR2' : aver.select('swir2_mean')}).rename('aweish')  
        aweinsh = aver.expression('4.0 * (GREEN - SWIR1) - (0.25 * VNIR + 2.75 * SWIR2)',
                                 {'GREEN' : aver.select('green_mean'),
                                 'SWIR1' : aver.select('swir1_mean'),
                                 'VNIR' : aver.select('vnir_mean'),
                                 'SWIR2' : aver.select('swir2_mean')}).rename('aweinsh')
        bright = aver.expression('(RED + GREEN + BLUE) / 3',
                                {'BLUE' : aver.select('blue_mean'),
                                'GREEN' : aver.select('green_mean'),
                                'RED' : aver.select('red_mean')}).rename('bright') 
        
        aver = aver.addBands([ndwi, mndwi, aweish, aweinsh, bright])
        classified = aver.expression("(BRIGHT > 5000) ? 0"
                                    ": (NDWI > 0.3) ? 1 "
                                    ": (MNDWI < 0.1) ? 0 "
                                    ": (AWEISH < 2000) ? 0"
                                    ": (AWEISH > 5000) ? 0"
                                    ": (AWEINSH < 4000) ? 0"
                                    ": (AWEINSH > 6000) ? 0"
                                    ": 1",
                                   {'NDWI' : aver.select('ndwi'),
                                    'MNDWI' : aver.select('mndwi'),
                                    'AWEISH' : aver.select('aweish'),
                                    'AWEINSH' : aver.select('aweinsh'),
                                    'BRIGHT' : aver.select('bright')}).rename('water')             
        water_ls8 = classified.updateMask(classified)

        # Mask out ocean pixels
        ocean_mask, ice_mask = self.getGIMPMask()        
        water_ls8 = maskImage(water_ls8, ocean_mask)
        water_ls8 = maskImage(water_ls8, ice_mask)
        
        print(f'{vis_col2} scenes classified')
        print('Band names: ' + str(water_ls8.bandNames().getInfo()))     
        
        
        features = getFeatures(water_ls8, self.bbox)
        print(f'{len(features)} vector features identified')  
        
        return features
    
    
    def processL7(self, cloud=50):
        '''Classify water bodies from Landsat 7 image collection
        
        Parameters
        ----------
        cloud: int, optional
           Maximum cloud cover percentage, default is 50 
        
        Returns
        -------
        features : list
           List of classified shapely.geometry.polygon objects
        ''' 
        
        # Set collection
        vis_col3 = "LANDSAT/LE07/C02/T1_TOA"
        
        # Get image collection
        scenes = getScenes(vis_col3, self.date0, self.date1, self.bbox)
        scenes = filterLSscenes(scenes, cloud)
        print(f'\nScenes gathered from {vis_col3}')
        print('Total number of scenes: ', scenes.size().getInfo())
        print('Number of bands per scene: ' 
              + str(len(scenes.first().bandNames().getInfo())))
        print('Band names: ' + str(scenes.first().bandNames().getInfo()))
        
        # Mask scenes for clouds
        scenes = maskL7clouds(scenes)  
        # ee.Terrain.hillshade(image, azimuth, elevation)
            
        # Get average of spectific bands
        scenes = renameL7scenes(scenes)
        aver = getMean(scenes, ['blue','green','red','vnir','swir1','swir2'])
        print('Scenes resampled and mosiacked')
        print('Band names: ' + str(aver.bandNames().getInfo())) 
        
        # Classify water from VIS average image, and mask out ocean pixels
        # water_ls = classifyVISimage(aver)
        
        ndwi = aver.normalizedDifference(['green_mean', 'vnir_mean']).rename('ndwi') 
        mndwi = aver.normalizedDifference(['green_mean','swir1_mean']).rename('mndwi')
        aweish = aver.expression('BLUE + 2.5 * GREEN - 1.5 * (VNIR + SWIR1) - 0.25 * SWIR2',
                                {'BLUE' : aver.select('blue_mean'), 
                                'GREEN' : aver.select('green_mean'),
                                'SWIR1' : aver.select('swir1_mean'),
                                'VNIR' : aver.select('vnir_mean'),
                                'SWIR2' : aver.select('swir2_mean')}).rename('aweish')  
        aweinsh = aver.expression('4.0 * (GREEN - SWIR1) - (0.25 * VNIR + 2.75 * SWIR2)',
                                  {'GREEN' : aver.select('green_mean'),
                                  'SWIR1' : aver.select('swir1_mean'),
                                  'VNIR' : aver.select('vnir_mean'),
                                  'SWIR2' : aver.select('swir2_mean')}).rename('aweinsh')
        bright = aver.expression('(RED + GREEN + BLUE) / 3',
                                {'BLUE' : aver.select('blue_mean'),
                                'GREEN' : aver.select('green_mean'),
                                'RED' : aver.select('red_mean')}).rename('bright') 
        
        aver = aver.addBands([ndwi, mndwi, aweish, aweinsh, bright])
        classified = aver.expression("(BRIGHT > 5000) ? 0"
                                    ": (NDWI > 0.3) ? 1 "
                                    ": (MNDWI < 0.1) ? 0 "
                                    ": (AWEISH < 2000) ? 0"
                                    ": (AWEISH > 5000) ? 0"
                                    ": (AWEINSH < 4000) ? 0"
                                    ": (AWEINSH > 6000) ? 0"
                                    ": 1",
                                    {'NDWI' : aver.select('ndwi'),
                                    'MNDWI' : aver.select('mndwi'),
                                    'AWEISH' : aver.select('aweish'),
                                    'AWEINSH' : aver.select('aweinsh'),
                                    'BRIGHT' : aver.select('bright')}).rename('water')             
        water_ls7 = classified.updateMask(classified)

        ocean_mask, ice_mask = self.getGIMPMask()        
        water_ls7 = maskImage(water_ls7, ocean_mask)
        water_ls7 = maskImage(water_ls7, ice_mask)
        print(f'{vis_col3} scenes classified')
        print('Band names: ' + str(water_ls7.bandNames().getInfo()))     
               
        features = getFeatures(water_ls7, self.bbox) 
        print(f'{len(features)} vector features identified')  
          
        return features