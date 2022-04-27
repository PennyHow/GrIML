"""
GrIML ice marginal lake (IML) data compiling module

@author: Penelope How
"""

import geopandas as gpd
import pandas as pd
from scipy.sparse.csgraph import connected_components


def assignNames(gdf, gdf_names, distance=500.0):
    '''Assign placenames to geodataframe geometries based on names in another 
    geodataframe point geometries
    
    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
       Geodataframe for placenames to be added to
    gdf_names: geopandas.GeoDataFrame
       Geodataframe of point placenames
    
    Returns
    -------
    gdf : geopandas.GeoDataFrame
       Revised geodataframe
    '''  
    placenames = _compileNames(gdf_names)
                                    
    lakename=[]     
    for i,v in gdf.iterrows():  
        
        geom = v['geometry']
        
        polynames=[] 
        for pt in range(len(placenames)):
            if geom.contains(gdf_names['geometry'][pt]) == True:
                polynames.append(placenames[pt])  
                
        if len(polynames)==0:
            for pt in range(len(placenames)):  
                if gdf_names['geometry'][pt].distance(geom) < distance: 
                    polynames.append(placenames[pt]) 
            lakename.append(polynames)
            
        elif len(polynames)==1:  
            lakename.append(polynames)    
            
        else: 
            out=[]          
            for p in polynames:  
                out.append(p) 
            lakename.append(out) 
            
    lakeid = gdf['unique_id'].tolist()      
    lakename2 = []     
    
    for x in gdf.index:        
        indx = _getIndices(lakeid, x)                                         
        findname=[]
        for l in indx:
            if len(lakename[l])!=0: 
                findname.append(lakename[l])
        
        for i in range(len(indx)):  
            if len(findname)==0:
                lakename2.append('')
        
            else:                                           
                unique = set(findname[0])  
                unique = list(unique)  
                
                if len(unique)==1:
                    lakename2.append(findname[0][0]) 
                    
                else:
                    out2 = ', '
                    out2 = out2.join(unique) 
                    lakename2.append(out2) 
    gdf['placename'] = lakename2
    return gdf



def assignCertainty(gdf, search_names, scores, source='all_src'):
    '''Assign certainty score to geodataframe based on sources
    
    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
       Geodataframe for certainty score to be added to
    search_names : list
       List of source names to search for
    scores : list
       List of certainty scores for each source name
    source : str
       Geodataframe column name containing sources
    
    Returns
    -------
    gdf : geopandas.GeoDataFrame
       Revised geodataframe
    '''
    cert=[]
    srcs = list(gdf[source])

    for a in range(len(srcs)):
        if srcs[a].split(', ')==1:
            out = _getScore(srcs.split(', '))
            cert.append(out)    
        else:
            out=[]
            for b in srcs[a].split(', '):
                out.append(_getScore(b, search_names, scores))
            cert.append(sum(out))

    gdf['certainty'] = cert
    return gdf
    

def assignSources(gdf, col_names=['unique_id', 'source']):
    '''Assign source metadata to geodataframe, based on unique lake id and
    individual source information
    
    Parameters
    ----------
    gdf : pandas.GeoDataFrame
       Geodataframe to assign source metadata to
    col_names : list
       List of geodataframe column names to find lake ids and individual source
    
    Returns 
    -------
    gdf : pandas.GeoDataFrame
       Revised geodataframe
    '''
    ids = gdf[col_names[0]].tolist()
    source = gdf[col_names[1]].tolist()
    satellites=[]
    
    # Construct source list
    for x in range(len(ids)):
        indx = _getIndices(ids, x)
        if len(indx) != 0:
            res = []
            if len(indx) == 1:
                res.append(source[indx[0]].split('/')[-1])
            else:
                unid=[]
                for dx in indx:
                    unid.append(source[dx].split('/')[-1])
                res.append(list(set(unid)))
            for z in range(len(indx)):
                if len(indx) == 1:
                    satellites.append(res)
                else:
                    satellites.append(res[0])
                    
    # Compile lists for appending
    satellites_names = [', '.join(i) for i in satellites]
    number = [len(i) for i in satellites]
    
    # Return updated geodataframe    
    gdf['all_src']=satellites_names
    gdf['num_src']=number
    return gdf
    

def assignID(gdf, col_name='unique_id'):
    '''Assign unique identification numbers to non-overlapping geometries in
    geodataframe
    
    Parameters
    ----------
    gdf : pandas.GeoDataFrame
       Geodataframe to assign unique ids to
    '''
    # Find overlapping geometries
    geoms = gdf['geometry']
    geoms.reset_index(inplace=True, drop=True)        
    overlap_matrix = geoms.apply(lambda x: geoms.overlaps(x)).values.astype(int)
    
    # Get unique ids for non-overlapping geometries
    n, ids = connected_components(overlap_matrix)
    ids=ids+1
    
    # Assign ids and realign geoedataframe index 
    gdf[col_name]=ids
    gdf = gdf.sort_values(col_name)
    gdf.reset_index(inplace=True, drop=True) 
    return gdf


def compileFeatures(feature_list, method_list, collection_list, date_list):
    '''Compile features from multiple processings into one geodataframe

    Parameters
    ----------
    feature_list : list
        List of shapely features
    method_list : list
        List of strings denoting processing method
    collection_list : list
        List of strings denoting dataset collection
    date_list : list
        List of start and end date for processing

    Returns
    -------
    all_gdf : geopandas.GeoDataFrame
        Compiled goedataframe
    '''
    dfs=[]
    for a,b,c in zip(feature_list, method_list, collection_list):
        if a is not None:
            
            #Construct geodataframe with basic metadata
            gdf = gpd.GeoDataFrame(geometry=a, crs='EPSG:4326')
            gdf = dissolvePolygons(gdf)
            dfs.append(pd.DataFrame({'geometry': list(gdf.geometry), 
                                     'method': b, 
                                     'source': c, 
                                     'startdate' : date_list[0], 
                                     'enddate':date_list[1]}))   
           
    # Construct merged geodataframe
    all_gdf = pd.concat(dfs)
    all_gdf = gpd.GeoDataFrame(all_gdf, geometry=all_gdf.geometry, 
                               crs='EPSG:4326')
    return all_gdf


def dissolvePolygons(gdf):
    '''Dissolve overlapping polygons in a Pandas GeoDataFrame

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        Geodataframe with polygons for dissolving

    Returns
    -------
    gdf2 : geopandas.GeoDataFrame
        Geodataframe with dissolved polygons
    '''
    geoms = gdf.geometry.unary_union
    gdf2 = gpd.GeoDataFrame(geometry=[geoms])
    gdf2 = gdf2.explode().reset_index(drop=True)
    return gdf2


def _compileNames(gdf):
    '''Get preferred placenames from placename geodatabase'''  
    placenames=[]
    for i,v in gdf.iterrows():
        if v['Ny_grønla'] != None: 
            placenames.append(v['Ny_grønla'])
        else:
            if v['Dansk'] != None: 
                placenames.append(v['Dansk'])
            else:
                if v['Alternativ'] != None:
                    placenames.append(v['Alternativ'])
                else:
                    placenames.append(None)
    return placenames


def _getScore(value, search_names, scores):
    '''Determine score from search string'''
    if search_names[0] in value:
        return scores[0]
    elif search_names[1] in value:
        return scores[1]
    elif search_names[2] == value:
        return scores[2]
    else:
        return None
 
    
def _getIndices(mylist, value):
    '''Get indices for value in list'''
    return[i for i, x in enumerate(mylist) if x==value]
   

#------------------------------------------------------------------------------

# class IML(object):
    
#     def __init__(self, database):
#         self.gpd= database
    
#     def getGeometry(self):
#         return self.geometry
    
    
#     def removeDuplicates(self):
#         pass

# def fromMemory(img, shape_mask, mask_value, transf):
#     '''Get vector features from binary raster image. Raster data is loaded 
#     from array as a rasterio inmemory object, and returns features as a 
#     geopandas dataframe.

#     Parameters
#     ----------
#     img : arr
#        Binary raster array
#     mask_value : int
#        Value for classified cells
#     trans : Affine                     
#        Raster transformation (computed using affine package, or 
#        rasterio.transform) 
       
#     Returns
#     -------
#     feats : geopandas.Geodataframe
#        Vector features geodataframe
#     '''
#     # Open array as rasterio memory object
#     with rasterio.io.MemoryFile() as memfile:
#         with memfile.open(
#             driver='GTiff',
#             height=img.shape[0],
#             width=img.shape[1],
#             count=1,
#             dtype=img.dtype,
#             transform=transf
#         ) as dataset:
#             dataset.write(img, 1)
        
#         # Read binary band
#         with memfile.open() as src:

#             # Get raster transform
#             t = _getTransform(transf)
            
#             feats = fromBinFile(src, shape_mask, mask_value, t)

#         #     image = src.read(1)
                    
#         #     # Vectorise binary band
#         #     geoms = _reclassBinary(image, t, mask_value)
                
#         # # Return as geodataframe
#         # feats = gpd.GeoDataFrame.from_features(geoms)
#     return feats


# def fromBinFile(raster, shape_mask, mask_value, transf=None):
#     '''Get vector features from binary raster image. Raster data is loaded 
#     from raster file, and returns features as a geopandas dataframe.

#     Parameters
#     ----------
#     raster : rasterio.io.DatasetReader
#        Raster file as loaded rasterio dataset
#      shape_mask : list
#        List of vector GeoJSON-like dict or an object that implements the Python 
#        geo interface protocol (such as a Shapely Polygon)
#     mask_value : int
#        Value for classified cells
#     transf : list/affine.Affine, optional
#        Raster transformation properties

#     Returns
#     -------
#     feat : geopandas.Geodataframe
#        Vector features geodataframe
#     '''    
#     # Mask raster with mask shapefile
#     if shape_mask != None:
#         cropped = _maskRaster(src, shape_mask)
    
#     else:    
#         # Read transformation and band info
#         cropped = src.read(1)

#     # Check transform
#     if transf != None:
#         t = _getTransform(transf)
#     else:
#        t = _getTransform(src.transform)
            
#     # Vectorise and transform to geodatabase
#     binary = _reclassBinary(cropped, t, mask_value)
#     feats = gpd.GeoDataFrame.from_features(binary, crs = src.crs)   
     
#     return feats


# def _maskRaster(raster, shps):
#     '''Mask raster with shapefile

#     Parameters
#     ----------
#     raster : arr
#         Raster array
#     shps : TYPE
#         Masking shapes

#     Returns
#     -------
#     arr 
#        Masked raster array
#     '''
#     # with fiona.open("tests/data/box.shp", "r") as shapefile:
#     #     shapes = [feature["geometry"] for feature in shapefile]

#     out_image, out_transform = mask(raster, shps, crop=False)
    
#     return out_image
      
  
# def _reclassBinary(binary, transf, reclass):  
#     '''Vectorise binary raster
    
#     Parameters
#     ----------
#     binary : arr
#        Binary raster band array
#     transf : affine.Affine
#        Raster transformation
#     reclass : int
#        Value for classified cells
    
#     Returns
#     -------
#     list
#        Shape features (as list of dictionaries)
#     '''
#     mask_value = binary == reclass 
    
#     # Vectorise
#     results = (
#         {'properties': {'raster_val': v}, 'geometry': s}
#         for i, (s, v) 
#         in enumerate(
#             features.shapes(binary, 
#                     mask=mask_value, 
#                     transform=transf)))
        
#     # Return as list of geometries
#     return list(results)


# def _getTransform(transf):
#     '''Raster transformation checker'''
#     if isinstance(transf, affine.Affine):
#         return transf
#     elif isinstance(transf, list):
#         transf = rasterio.transform.from_origin(transf[0], transf[3], 
#                                            transf[1], transf[5])
#     return transf
    
# if __name__ == "__main__":   
#     r =   'test/S2A_L1C_T22WEV_R025_20190802_RECLASS3.tif'  
#     shp = 'test/test_mask.shp'  

#     with rasterio.open(r) as src:
#         with fiona.open(shp, "r") as shapefile:
#             shapes = [feature["geometry"] for feature in shapefile]
#             s = fromBinFile(src, shapes, 1)
            
#     s.plot()
#     # print(s.crs)