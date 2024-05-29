from griml.convert.convert import convert
from griml.filter.filter_vectors import filter_vectors
from griml.merge.merge_vectors import merge_vectors
from griml.metadata.add_metadata import add_metadata
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
        convert([infile], proj, band_info, start, end) 

    def test_filter(self):
        '''Test vector filtering'''  
        infile1 = os.path.join(os.path.dirname(griml.__file__),'test/test_filter.shp') 
        infile2 = os.path.join(os.path.dirname(griml.__file__),'test/test_icemask.shp')      
        filter_vectors([infile1], infile2)

    def test_merge(self):
        '''Test vector merging'''
        infile1 = os.path.join(os.path.dirname(griml.__file__),'test/test_merge_1.shp')  
        infile2 = os.path.join(os.path.dirname(griml.__file__),'test/test_merge_2.shp')                  
        merge_vectors([infile1,infile2]) 

    def test_metadata(self):
        '''Test metadata population'''
        infile1 = os.path.join(os.path.dirname(griml.__file__),'test/test_merge_2.shp')             
        infile2 = os.path.join(os.path.dirname(griml.__file__),'test/test_placenames.shp')              
        infile3 = os.path.join(os.path.dirname(griml.__file__),'test/greenland_basins_polarstereo.shp') 
        add_metadata(infile1, infile2, infile3)

if __name__ == "__main__":  
    unittest.main()
