from griml.convert import convert
from griml.filter import filter_vectors
from griml.merge import merge_vectors
from griml.metadata import add_metadata
import unittest, pkg_resources, os
import geopandas as gpd
import griml

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
        
        infile = os.path.join(os.path.dirname(griml.__file__),'test/test_north_greenland.tif')
        convert([infile], None, proj, band_info, start, end) 

    def test_filter(self):
        '''Test vector filtering'''  
        infile1 = os.path.join(os.path.dirname(griml.__file__),'test/test_icemask.shp')
        margin_buff = gpd.read_file(infile1)

        infile2 = os.path.join(os.path.dirname(griml.__file__),'test/test_filter.shp')       
        filter_vectors(infile2, None, margin_buff)

    def test_merge(self):
        '''Test vector merging'''
        infile1 = os.path.join(os.path.dirname(griml.__file__),'test/test_merge_1.shp')  
        merge1 = gpd.read_file(infile1) 

        infile2 = os.path.join(os.path.dirname(griml.__file__),'test/test_merge_2.shp')          
        merge2 = gpd.read_file(infile2)          
        
        features=[]
        methods=[]
        sources=[]
        starts=[]
        ends=[]    
        for infile in [merge1, merge2]:
            features.append(list(infile['geometry'])) 
            methods.append(list(infile['method'])) 
            sources.append(list(infile['source'])) 
            starts.append(list(infile['startdate'])) 
            ends.append(list(infile['enddate'])) 
        vectors = merge_vectors(features, methods, sources, starts, ends) 

    def test_metadata(self):
        '''Test metadata population'''
        infile1 = os.path.join(os.path.dirname(griml.__file__),'test/test_merge_2.shp')          
        iml = gpd.read_file(infile1) 
   
        infile2 = os.path.join(os.path.dirname(griml.__file__),'test/test_placenames.shp')              
        names = gpd.read_file(infile2)
        add_metadata(iml, names, None)

if __name__ == "__main__":  
    unittest.main()
