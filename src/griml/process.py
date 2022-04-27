"""
GrIML process module

@author: Penelope How
"""

import ee

try:
    from griml.retrieve import getScenes, getScene, getInt, getSmooth, getMosaic, \
        getMean, maskImage, splitBBox, getFeatures, getFeaturesSplit
    from griml.sar import filterSARscenes, classifySARimage
    from griml.vis import filterS2scenes, maskS2clouds,  filterLSscenes, maskL8clouds, \
        maskL7clouds, getNDWI, getMNDWI, getAWEISH, getAWEINSH, getBRIGHT, \
        getClassification
    from griml.dem import getElevation, getSinks 
except:
    from retrieve import getScenes, getScene, getInt, getSmooth, getMosaic, \
        getMean, maskImage, splitBBox, getFeatures, getFeaturesSplit
    from sar import filterSARscenes, classifySARimage
    from vis import filterS2scenes, maskS2clouds,  filterLSscenes, maskL8clouds, \
        maskL7clouds, getNDWI, getMNDWI, getAWEISH, getAWEINSH, getBRIGHT, \
        getClassification
    from dem import getElevation, getSinks 

class gee(object):
    '''Class object for rigid classification workflows using the 
    Google Earth Engine (GEE) Python API
    
    Variables
    ---------
    date0 : str
        Start date
    date1 : str
        End date
    aoi : list
        AOI coordinates
    box : ee.Geometry.Box
        AOI bounding box
    bbox : list
        List of split bounding boxes
    mask : ee.Image/None
        Coastal mask
    parameters : list
        Classification parameters
    '''
    def __init__(self, date_range, aoi, parameters, 
                 aoi_params=None, mask=False):
        '''GEE object initialisation
        
        Parameters
        ----------
        date_range : list
            Start and end date
        aoi : list
            AOI bounding box coordinates
        parameters : list
            List of classification parameter dictionaries
        aoi_params : list, optional
            AOI boundin box splitting parameters. Default is None
        mask : bool
            Coastal mask flag
        '''
        if not ee.data._credentials:
            ee.Initialize()
            
        self.date0 = date_range[0]
        self.date1 = date_range[1]
        
        self.aoi = aoi 
        self.box = ee.Geometry.Rectangle(aoi.bounds)
        
        if aoi_params:
            self.bbox = splitBBox(aoi, aoi_params[0], aoi_params[1], 
                                  aoi_params[2], aoi_params[3])
        else:
            self.bbox = splitBBox(aoi, 0.3, 0.3, 0.01, 0.01)   
        
        if mask:
            img = ee.Image("OSU/GIMP/2000_ICE_OCEAN_MASK")
            self.mask = img.select('ocean_mask').eq(0)

        else:
            self.mask=None
        
        self.parameters = parameters
        
        print(f'Processing workflow initialised to process {len(self.parameters)}'+
              f' image collections from {self.date0} to {self.date1}')


    def retrieveAll(self, images):
        '''Retrieve binary classified regions from all image collections
        
        Parameters
        ----------
        images : list
            List of binary image classification
        
        Returns
        -------
        feature_all : list
           List of shapely.geometry.Polygon vector features
       '''
        feature_all=[]
        params = self._getParameters()
        
        for i in range(len(images)):
            if 'LANDSAT' in params[i]['collection']:
                scale=30
            else:
                scale=10
            
            print(f'\nRetrieving classifications from {params[i]["collection"]}'+
                  f' at {scale} m resolution')
            features = self.retrieveVectors(images[i], scale)
            feature_all.append(features)
            
        return feature_all


    def retrieveVectors(self, classification, scale):
        '''Retrieve binary classified regions as vectors
        
        Parameters
        ----------
        classification : ee.Image
            Binary image classification
        scale : int
            Output spatial resolution of vectors
        
        Returns
        -------
        features : list
           List of shapely.geometry.Polygon vector features
       '''
        try:
            print('Attempting to retrieve classifications from AOI...')
            features = getFeatures(classification, scale, self.box) 
        except:
            print(f'AOI too big. Attempting to retrieve from {len(self.bbox)}'+
                  ' split boxes...')
            features = getFeaturesSplit(classification, scale, self.bbox) 
        return features
    
    
    def processAll(self):
        '''Classify all image collections

        Returns
        -------
        all_out : list
            List of GEE binary image classifications
        '''
        all_out = []
        params = self._getParameters()
        for p in params:
            out = self.process(p)
            all_out.append(out)
        return all_out
    
    
    def process(self, parameters):
        '''Classify image collection based on inputted classification 
        parameters
        
        Parameters
        ----------
        parameters : dict
            Dictionary of parameters
        
        Returns
        -------
        out : ee.Image
            GEE binary image classification
        '''
        if 'S2' in parameters['collection'] or 'LANDSAT' in parameters['collection']:
            out = self.processVIS(parameters)
        elif 'S1' in parameters['collection']:
            out = self.processSAR(parameters)
        elif 'ArcticDEM' in parameters['collection']:
            out = self.processDEM(parameters)
        return out

    
    def processSAR(self, parameters):
        '''Classify SAR image collection based on inputted classification
        parameters
        
        Parameters
        ----------
        parameters : dict
            Dictionary of parameters
        
        Returns
        -------
        water : ee.Image
            GEE binary image classification of water bodies
        ''' 
        # Get image collection
        scenes = getScenes(parameters['collection'], self.date0, 
                           self.date1, self.box)
        scenes = filterSARscenes(scenes)
        
        if scenes.size().getInfo() > 0:
            self._reportScenes(scenes, self.date0, self.date1)
                
            # Get average
            aver = getMosaic(scenes, parameters['polar'])
            
            # Mask out ocean pixels
            aver = maskImage(aver, self.mask)
            
            # Classify water from SAR average image
            water = classifySARimage(aver, parameters['threshold'], 
                                     parameters['polar'], parameters['smooth'])
            print(f'{parameters["collection"]} scenes classified')
            print('Band names: ' + str(water.bandNames().getInfo()))  

        else:
            water = None
            print(f'\nNo {parameters["collection"]} scenes identified ' +
                  f'between {self.date0} - {self.date1}')
        
        return water


    def processVIS(self, parameters):   
        '''Classify optical (VIS) image collection based on inputted 
        classification parameters
        
        Parameters
        ----------
        parameters : dict
            Dictionary of parameters
        
        Returns
        -------
        water : ee.Image
            GEE binary image classification of water bodies
        ''' 
        # Get image collection
        scenes = getScenes(parameters['collection'], self.date0, 
                           self.date1, self.box)
        
        scenes = self._filterVISscenes(scenes, parameters['cloud'], 
                        parameters['collection'])       
        
        if scenes.size().getInfo() > 0:
            self._reportScenes(scenes, self.date0, self.date1)
            
            # Mask scenes for clouds
            scenes = self._maskClouds(scenes, parameters['collection']) 
                
            # Resample if Sentinel-2
            if 'S2' in parameters['collection']:
                scenes = scenes.map(self._resampleSWIR)
            
            b,g,r,vnir,swir1,swir2 = self._assignBands(parameters['collection'])
                
            aver = getMean(scenes, [b,g,r,vnir,swir1,swir2])   
            print('Scenes resampled and mosiacked')
            print('Band names: ' + str(aver.bandNames().getInfo())) 
            
            # Classify water from VIS average image, and mask out ocean pixels
            ndwi = getNDWI(aver, g+'_mean', vnir+'_mean') 
            mndwi = getMNDWI(aver, g+'_mean', swir1+'_mean')
            aweish = getAWEISH(aver, b+'_mean', g+'_mean', vnir+'_mean', 
                               swir1+'_mean', swir2+'_mean')
            aweinsh = getAWEINSH(aver, g+'_mean', vnir+'_mean', 
                                 swir1+'_mean', swir2+'_mean')
            bright = getBRIGHT(aver, r+'_mean', g+'_mean', b+'_mean')
            water = getClassification(ndwi, mndwi, aweish, aweinsh, bright)
            
            # Mask classified water
            water = maskImage(water, self.mask)
            print(f'{parameters["collection"]} scenes classified')
            print('Band names: ' + str(water.bandNames().getInfo()))     
            
        else:
            water = None
            print(f'\nNo {parameters["collection"]} scenes identified between'+
                  f' {self.date0} and {self.date1} (<{parameters["cloud"]}% '+
                  'cloud cover)') 
        return water
        
    
    def processDEM(self, parameters):
        '''Classify DEM image or image collection based on inputted 
        classification parameters
        
        Parameters
        ----------
        parameters : dict
            Dictionary of parameters
        
        Returns
        -------
        sinks : ee.Image
            GEE binary image classification of sinks
        ''' 
        try:
            # Get image collection
            scenes = getScenes(parameters['collection'], self.date0, 
                               self.date1, self.box)
            if scenes.size().getInfo() == 0:
                print(f'\nNo {parameters["collection"]} scenes identified ' +
                      f' between {self.date0} and {self.date1}')
                return None
            else:
                self._reportScenes(scenes, self.date0, self.date1)
                elevation = getElevation(scenes)
                elevation = getMean(elevation, ['elevation'])
        except:
            scenes = getScene(parameters['collection'], self.box)
            print(f'\nScenes gathered from {parameters["collection"]}')
            elevation = getElevation(scenes)
        
        # Get smoothed elevation with integer values
        elevation = getSmooth(elevation, parameters['smooth'])
        
        # Mask out ocean pixels
        elevation = maskImage(elevation, self.mask)
        
        # Get sinks
        elevation = getInt(elevation)
        sinks = getSinks(elevation, parameters['fill'], parameters['kernel'])
            
        # Remove speckle with smoothing
        sinks = getSmooth(sinks, parameters['speckle']).rename('dem_sinks')
        sinks = getInt(sinks)
        print(f'{parameters["collection"]} scenes classified')
        print('Band names: ' + str(sinks.bandNames().getInfo())) 
        return sinks     
    

    def _getParameters(self):
        '''Return parameter dictionaries'''
        return self.parameters
    

    def _filterVISscenes(self, scenes, cloud, collection):
        '''Filter optical images by cloud cover percentage, based on collection
        type

        Parameters
        ----------
        scenes : ee.ImageCollection
            GEE image collection
        cloud : int
            Maximum cloud cover percentage
        collection : str
            Image collection name

        Returns
        -------
        scenes : ee.ImageCollection
            Filtered GEE image collection
        '''
        if 'S2' in collection:
            scenes = filterS2scenes(scenes, cloud)
        elif 'LC08' in collection or 'LE07' in collection:
            scenes = filterLSscenes(scenes, cloud)
        return scenes


    def _resampleSWIR(self, img):
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
        resample = img.select(['B11',
                               'B12']).resample('bilinear').reproject(crs='EPSG:4326', 
                               scale=10)
        return img.addBands(resample)    
    
    
    def _assignBands(self, collection):
        '''Assign names to desired optical bands for classification, based on
        collection type'''
        if 'S2' in collection:
            b,g,r,vnir,swir1,swir2 = 'B2', 'B3', 'B4', 'B8', 'B11_1', 'B12_1'
        elif 'LC08' in collection:
            b,g,r,vnir,swir1,swir2 = 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'
        elif 'LE07' in collection:
            b,g,r,vnir,swir1,swir2 = 'B1', 'B2', 'B3', 'B4', 'B5', 'B7'  
        return b,g,r,vnir,swir1,swir2
            
            
    def _maskClouds(self, scenes, collection):
        '''Mask clouds from optical image collection, based on image collection
        type'''
        if 'S2' in collection:
            scenes = maskS2clouds(scenes)
        elif 'LC08' in collection:
            scenes = maskL8clouds(scenes)
        elif 'LE07' in collection:
            scenes = maskL7clouds(scenes)         
        return scenes
       
    
    def _reportScenes(self, scenes, date0, date1):
        '''Scene hits reporter'''
        print(f'\nScenes gathered from {scenes.getInfo()["id"]} ' +
              f'({date0} - {date1})')
        print(f'Total number of scenes: {scenes.size().getInfo()}')
        print('Number of bands per scene: ' +
              f'{len(scenes.first().bandNames().getInfo())}')
        print(f'Band names: {scenes.first().bandNames().getInfo()}')
