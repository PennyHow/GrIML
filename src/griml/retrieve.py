"""
GrIML data retrieval module

@author: Penelope How
"""
import ee, re, unittest
from shapely.geometry import Polygon 

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
    scenes = ee.ImageCollection(collection).filterDate(date1, 
                                                       date2).filterBounds(box)
    return scenes


def getScene(image, box):
    '''Get satellite scene from Google Earth Engine image  

    Parameters
    ----------
    image : str
        GEE image repository
    box : ee.geometry.Geometry
        Bounding box

    Returns
    -------
    scenes : ee.image.Image
        GEE image object
    '''
    return ee.Image(image)


def getMean(scenes, bands):
    '''Average all satellite scenes in a GEE image collection    

    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection object
    bands : str/list
        Band name/s

    Returns
    -------
    ee.image.Image
        Mosaicked GEE image object
    '''
    return scenes.select(bands).reduce(ee.Reducer.mean())


def getMosaic(scenes, bands):
    '''Mosaic all satellite scenes in a GEE image collection    

    Parameters
    ----------
    scenes : ee.imagecollection.ImageCollection
        GEE image collection object
    bands : str
        Band name/s

    Returns
    -------
    ee.image.Image
        Mosaicked GEE image object
    '''
    return scenes.select(bands).mosaic()


def getSmooth(image, kernel_size, window='circle', units='meters'):
    '''Smooth GEE image object    

    Parameters
    ----------
    image : ee.image.Image
       GEE image object
    kernel_size : int
       Smoothing window size
    window : str, optional
       Window shape. The default is 'circle'
    units : str, optional
       Units for smoothing parameters. The default is 'meters'
       

    Returns
    -------
    ee.image.Image
        Mosaicked GEE image object
    '''
    return image.focal_median(kernel_size, window, units)

def getInt(image):
    '''Return GEE image with integer pixel values
    
    Parameters
    ----------
    scenes : ee.image.Image
        GEE image object

    Returns
    -------
    ee.image.Image
        GEE image object with integer pixel values
    '''
    return ee.Image.int64(image)


def maskImage(image, image_mask):
    '''Return masked image

    Parameters
    ----------
    image : ee.image.Image
        GEE image object
    image_mask : ee.image.Image
        GEE image object mask

    Returns
    -------
    ee.image.Image
        Masked GEE image object
    '''
    return image.updateMask(image_mask)
    

def getImageURL(image, scale, bounding_box, crs=None, transform=None):
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
    link = image.getDownloadURL({
        'scale': scale,
        'crs': crs,
         'crsTransform' : transform,
        'fileFormat': 'GeoTIFF',
        'region': bounding_box})
    return link


def getImageDrive(image, name, bounding_box, proj=None):
    '''Export GEE image to Google Drive

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
    ''' 
    if proj==None:
        proj = image.projection().getInfo()
    task = ee.batch.Export.image.toDrive(image=image.select('water'), 
                                    region=bounding_box,
                                    description=name,
                                    crs=proj['crs'],
                                    crsTransform = proj['transform'] )
    task.start()
    task.status() 


def splitBBox(aoi, window_height, window_width, 
              overlap_height, overlap_width):
    '''Split AOI polgyon into multiple smaller box grid of set dimensions 
    with a defined overlap
    
    Parameters
    ----------
    aoi : shapely.geometry.polygon.Polygon
       Bounding box coordinate 1 (upper left)
    window_height : int
       Pixel grid height
    window_width : int
       Pixel grid width
    overlap_height : int
       Grid height overlap (must be smaller than window height to create 
       overlap)
    overlap_width : int
       Grid width overlap (must be smaller than window width to create 
       overlap)       
    
    Returns
    -------
    grid : list
       List of bounding box coordinates for generated grid
    '''
    # Get xy limits
    xmin, ymin, xmax, ymax = aoi.bounds
    
    # Split box into grid for exporting
    grid = createGrid([xmin, ymin], [xmax, ymax], window_height, window_width, 
                      overlap_height, overlap_width)
    
    # Remove boxes that don't overlap with AOI polygon
    grid = [Polygon([[g[0],g[1]], [g[0],g[3]], [g[2],g[3]],
                      [g[2],g[1]], [g[0],g[1]]]) for g in grid]
    bbox = [ee.Geometry.Rectangle(min(g.exterior.coords.xy[0]), 
                                  min(g.exterior.coords.xy[1]), 
                                  max(g.exterior.coords.xy[0]), 
                                  max(g.exterior.coords.xy[1])) for g in grid if g.intersects(aoi)]
    return bbox


def createGrid(xy1, xy2, window_height, window_width, 
              overlap_height, overlap_width):
    '''Split xy bounding box into multiple smaller box grid of set dimensions 
    with a defined overlap
    
    Parameters
    ----------
    xy1 : list
       Bounding box coordinate 1 (upper left)
    xy2 : list
       Bounding box coordinate 2 (lower right)
    window_height : int
       Pixel grid height
    window_width : int
       Pixel grid width
    overlap_height : int
       Grid height overlap (must be smaller than window height to create 
       overlap)
    overlap_width : int
       Grid width overlap (must be smaller than window width to create 
       overlap)       
    
    Returns
    -------
    grid : list
       List of bounding box coordinates for generated grid
    '''
    # Find xy min and max
    xmin = min([xy1[0],xy2[0]])
    xmax = max([xy1[0],xy2[0]])
    ymin = min([xy1[1],xy2[1]])
    ymax = max([xy1[1],xy2[1]])
    
    # Determine overlap positions
    ow = window_width - overlap_width
    oh = window_height - overlap_height
    
    # Generate vector grid
    grid=[]
    y = ymax
    while y >= ymin:
        x = xmin
        while x <= xmax:
            grid.append([x, y, x + ow, y - oh])
            x = x + ow
        y = y - oh  
    return grid


def getFeatures(image, scale, bbox):
    '''Fetch GEE features
    
    Parameters
    ----------
    image : ee.image.Image
       Binary classification GEE image
    bbox : ee.geometry.Geometry
       Bounding box
    
    Returns
    -------
    features : list
       List of classified shapely.geometry.polygon objects
   '''
    features=[]
    v = getVectors(image, scale, bbox)
    features = extractFeatures(v)  
    return features
 
def getFeaturesSplit(image, scale, bbox):
    features=[]
    for b in range(len(bbox)):
        print(f'Fetching vectors from bbox {b}...')
        v = getVectors(image, scale, bbox[b])
        features.append(extractFeatures(v))
    features = [val for sublist in features for val in sublist]
    print(f'{len(features)} vector features identified')    
    return features
   

# def getParallelFeatures1(image, bbox):
#     # Parallel process vector generation
#     pool = mp.Pool(mp.cpu_count())
#     v = [pool.apply(getVectors, args=(image, 10, bbox[b])) for b in range(len(bbox))]
#     pool.close()    
     
#     # Parallel process feature extraction
#     pool = mp.Pool(mp.cpu_count())
#     features = pool.map(extractFeatures, [row for row in v])
#     pool.close()    

#     features = [val for sublist in features for val in sublist]
#     print(f'{len(features)} vector features identified')    
#     return features


# def getDownload(v):
#     link = v.getDownloadURL('csv')
#     req = urllib.request.Request(url=link)
#     try:
#         handler = urllib.request.urlopen(req)
#     except HTTPError as e:
#         handler = e.read()
#     lines = []
#     for l in handler:
#         lines.append(str(l))
#     features_dem.append(lines)
    

def getVectors(image, scale, box):
    '''Return vector objects from GEE binary image classification

    Parameters
    ----------
    image : ee.image.Image
       GEE image object, representing binary classification of features

    Returns
    -------
    ee.featurecollection.FeatureCollection
       GEE vector feature collection
    '''
    return image.reduceToVectors(geometryType='polygon',
                                 geometry=box,
                                 # reducer=ee.Reducer.countEvery(),
                                  scale=scale,
                                 # crs=proj,
                                 # crsTransform = transform,
                                 maxPixels=5000000000,
                                 labelProperty='label',
                                 bestEffort=False)


def splitVectors(vectors, chunk_size=4999, max_size=1000000):
    '''Split GEE feature collection into chunks
    
    Parameters
    ----------
    vectors : ee.featurecollection.FeatureCollection
       GEE vector feature collection for splitting
    
    Returns
    -------
    vector_chunks : list
       List of split GEE feature collections
    '''
    try:
        size = vectors.size().getInfo()
    except:
        size = max_size
        
    vector_chunks = []
    i=0
    while i < size:
        vector_chunks.append(ee.FeatureCollection(vectors.toList(chunk_size, i)))
        i = i + chunk_size
    return vector_chunks


def extractFeatures(vectors):
    '''Return polygon geometries from GEE feature collection

    Parameters
    ----------
    image : ee.featurecollection.FeatureCollection
       GEE vector feature collection

    Returns
    -------
    shapes : list
       List of shapely.geometry.Polygon vector features
    '''    
    # Extract feature coordinates from vectors str
    vectors_str = _vectorsToStr(vectors)
    
    # Split features
    shapes=[]
    vstr = vectors_str.split("'Feature'")[1:]
    for v in vstr:
        c = v.split('[[')[1:]
        
        # If polygon with holes
        if len(c) > 1:
            xy=[]
            for i in c:
                d = i.split(']]')[0]
                xy.append(_strToCoords(d))
            s = Polygon(xy[0], xy[1:])
        
        # If polygon with no holes
        elif len(c)==1:
            d = c[0].split(']]')[0]
            xy = _strToCoords(d)
            s = Polygon(xy)
        else:
            pass        
        shapes.append(s)
    
    # Return list of geometries
    return shapes


def _vectorsToStr(vectors):
    '''Return GEE feature collection object as string'''
    return str(vectors.getInfo())


def _strToCoords(string):
    '''Return xy coordinates from string'''
    xy = [float(s) for s in re.findall(r'[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?', string)]
    return list(zip(xy[::2], xy[1::2]))


class TestRetrieve(unittest.TestCase): 
    def testScenesMean(self):
        if not ee.data._credentials:
            ee.Initialize()
        scenes = getScenes('COPERNICUS/S2', '2019-08-01','2019-08-05', 
                           ee.Geometry.Rectangle([-49.53, 66.38, -49.69, 66.41]))
        mean = getMean(scenes, 'B2')        
        self.assertIsNotNone(mean.getInfo())

    def testScenesMosaic(self):
        if not ee.data._credentials:
            ee.Initialize()
        scenes = getScenes('COPERNICUS/S2', '2019-08-01','2019-08-05', 
                           ee.Geometry.Rectangle([-49.53, 66.38, -49.69, 66.41]))
         
        mosaic = getMosaic(scenes, 'B3')
        self.assertIsNotNone(mosaic.getInfo())
        
    def testImageSmooth(self):
        if not ee.data._credentials:
            ee.Initialize()
        image = getScene('UMN/PGC/ArcticDEM/V3/2m_mosaic', 
                         ee.Geometry.Rectangle([-49.53, 66.38, -49.69, 66.41]))
        smooth = getSmooth(image, 50)
        self.assertIsNotNone(smooth.getInfo())

    def testImageInt(self):
        if not ee.data._credentials:
            ee.Initialize()
        image = getScene('UMN/PGC/ArcticDEM/V3/2m_mosaic', 
                         ee.Geometry.Rectangle([-49.53, 66.38, -49.69, 66.41]))
        image_int = getInt(image)
        self.assertIsNotNone(image_int.getInfo())              
   
if __name__ == "__main__": 
    unittest.main() 
    