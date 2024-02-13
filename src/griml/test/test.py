from griml.convert import convert
from griml.filter import filter_vectors
from griml.merge import merge_vectors
from griml.metadata import add_metadata
import unittest, pkg_resources
import geopandas as gpd


class TestGrIML(unittest.TestCase):
    '''Unittest for the GrIML post-processing workflow'''

    def test_convert(self):
        '''Test vector to raster conversion''' 
        proj = 'EPSG:3413' 
        band_info = [{'b_number':1, 'method':'VIS', 'source':'S2'}, 
                     {'b_number':2, 'method':'SAR', 'source':'S1'},
                     {'b_number':3, 'method':'DEM', 'source':'ARCTICDEM'}] 
        start='20170701' 
        end='20170831'
        with pkg_resources.resource_stream('griml', 'test/test_north_greenland.tif') as stream:
            vectors = convert([stream], None, proj, band_info, start, end) 

    def test_filter(self):
        '''Test vector filtering'''        
        with pkg_resources.resource_stream('griml', 'test/test_icemask.shp') as stream:
            margin_buff = gpd.read_file(stream)
        with pkg_resources.resource_stream('griml', 'test/test_filter.shp') as stream:
            filter_vectors([stream], None, margin_buff)

    def test_merge(self):
        '''Test vector merging'''
        with pkg_resources.resource_stream('griml', 'test/test_merge_1.shp') as stream:
            merge1 = gpd.read_file(stream) 
        with pkg_resources.resource_stream('griml', 'test/test_merge_2.shp') as stream:
            merge2 = gpd.read_file(stream)             
        features=[]
        methods=[]
        sources=[]
        starts=[]
        ends=[]    
        for i in [merge1, merge2]: 
            features.append(list(i['geometry'])) 
            methods.append(list(i['method'])) 
            sources.append(list(i['source'])) 
            starts.append(list(i['startdate'])) 
            ends.append(list(i['enddate'])) 
        vectors = merge_vectors(features, methods, sources, starts, ends) 

    def test_metadata(self):
        '''Test metadata population'''

        with pkg_resources.resource_stream('griml', 'test/test_merge_2.shp') as stream:
            iml = gpd.read_file(stream)               
        with pkg_resources.resource_stream('griml', 'test/test_placenames.shp') as stream:
            names = gpd.read_file(stream)
        add_metadata(iml, names, None)
