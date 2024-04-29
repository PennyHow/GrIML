# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 08:37:11 2020

@author: HOW
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 10:27:57 2019

Re-calculating and formating ice-marginal lakes dataset (ESA)

@author: Penelope How
"""

import geopandas as gp

#-----------------------   Define inputs and outputs   ------------------------

#Define input file and location 
workspace1 = '/home/pho/Desktop/useful_datasets/IIML_2017/'
file1 = workspace1 + '20170101-ESACCI-L3S_GLACIERS-IML-MERGED-fv1.shp'
file3 = workspace1 + '10170101-ESACCI-L3S_GLACIERS-IML-MERGED-fv1_centroid.shp'

#-------------------------   Load as dataframe   ------------------------------

print('\nLoading geodataframes...')    

#Read file as geopandas index
geofile = gp.read_file(file1)
geofile['area'] = geofile['geometry'].area
geofile['length'] = geofile['geometry'].length

# #-------------   Re-calculate data from non-aggregated lake data  -------------
# print('\nRecalculating lake data...')

# #Get data from columns
# geofile = geofile.sort_values('LakeID')
# #geofile = geofile.drop(['area','Length'], axis=1)
# geofile['Area'] = geofile['geometry'].area
# geofile['Length'] = geofile['geometry'].length
# #geofile.plot()

# geofile.to_file(file2)

# print('Number of total lake features exported: ' + str(len(geofile['LakeID'].tolist())))

#---------------------   Create aggregated lake data   ------------------------
print('Creating dissolved dataset...')

agg_geofile = geofile.dissolve(by='LakeID')
agg_geofile = agg_geofile.drop(['area','length'], axis=1)
agg_geofile['area_m'] = agg_geofile['geometry'].area
agg_geofile['length_m'] = agg_geofile['geometry'].length
agg_geofile['area_km'] = agg_geofile['area_m']/1000000
agg_geofile['length_km'] = agg_geofile['length_m']*0.001

print('Number of dissolved lake features exported: ' + str(len(agg_geofile['Source'].tolist())))

pt_geofile = [s['geometry'].centroid for i,s in agg_geofile.iterrows()]
agg_geofile['geometry'] = pt_geofile

agg_geofile.to_file(file3)



#------------------------------------------------------------------------------

print('Finished')