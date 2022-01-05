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
workspace1 = 'D:/python_workspace/ice_marginal_lakes/'
workspace2 = 'P:/B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland/B71-05 Product validation and user assessment/publication/Data_eds/'
file1 = workspace2 + 'inventory_plus_inderhytten.shp'
file2 = workspace2 + 'glacier_cci_lakes_20200724.shp'
file3 = workspace2 + 'glacier_cci_lakes_20200724_aggregated.shp'

#-------------------------   Load as dataframe   ------------------------------

print('\nLoading geodataframes...')    

#Read file as geopandas index
geofile = gp.read_file(file1)


#-------------   Re-calculate data from non-aggregated lake data  -------------
print('\nRecalculating lake data...')

#Get data from columns
geofile = geofile.sort_values('LakeID')
#geofile = geofile.drop(['area','Length'], axis=1)
geofile['Area'] = geofile['geometry'].area
geofile['Length'] = geofile['geometry'].length
#geofile.plot()

geofile.to_file(file2)

print('Number of total lake features exported: ' + str(len(geofile['LakeID'].tolist())))

#---------------------   Create aggregated lake data   ------------------------
print('Creating dissolved dataset...')

agg_geofile = geofile.dissolve(by='LakeID')
agg_geofile = agg_geofile.drop(['Area','Length'], axis=1)
agg_geofile['Area'] = agg_geofile['geometry'].area
agg_geofile['Length'] = agg_geofile['geometry'].length
agg_geofile.to_file(file3)

print('Number of dissolved lake features exported: ' + str(len(agg_geofile['Source'].tolist())))

#------------------------------------------------------------------------------

print('Finished')