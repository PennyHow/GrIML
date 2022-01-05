# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 08:08:37 2020

@author: HOW
"""

import geopandas as gp
from pathlib import Path

#------------------------------------------------------------------------------

#Define input file and location 
workspace = Path(r'P:\B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland\B71-04 Essential Climate Variable production\final lake products')

#Input file
iiml_file = workspace.joinpath('glacier_cci_lakes_20200724.shp')

#Output file
output1 = workspace.joinpath('glacier_cci_lakes_20200819.shp')
output2 = workspace.joinpath('glacier_cci_lakes_20200819_aggregated.shp')

#Define weightings
S1_weight = 0.298
S2_weight = 0.398
ADEM_weight = 0.304

#------------------------------------------------------------------------------

print('\nLoading geodataframes...')    

#Read file as geopandas index
geofile = gp.read_file(str(iiml_file))
geofile = geofile.sort_values('LakeID')

#Get satellites column
num = geofile['NumOfSate'].tolist()
sats = geofile['Satellites'].tolist()

print('Determining Certainty scores...') 

#Determine certainty from weightings
certainty=[]
for s in range(len(sats)):
    if num[s]==1:
        if sats[s] in ['S1']:
            certainty.append(S1_weight)
        elif sats[s] in ['S2']:
            certainty.append(S2_weight)
        elif sats[s] in ['ArcticDEM']:
            certainty.append(ADEM_weight)
    elif num[s]==2:
        if sats[s] in ['S2, S1', 'S1, S2']:
            certainty.append(S1_weight+S2_weight)
        elif sats[s] in ['S1, ArcticDEM', 'ArcticDEM, S1']:
            certainty.append(S1_weight+ADEM_weight)
        elif sats[s] in ['S2, ArcticDEM', 'ArcticDEM, S2']:
            certainty.append(S2_weight+ADEM_weight)
    elif num[s]==3:
        certainty.append(S1_weight + S2_weight + ADEM_weight)

print('Writing to dataset file...')

#Write certainty scorings to database and file
geofile['Certainty'] = certainty
geofile.to_file(str(output1))

#------------------------------------------------------------------------------

print('Creating dissolved dataset...')

agg_geofile = geofile.dissolve(by='LakeID')
agg_geofile.to_file(str(output2))

#------------------------------------------------------------------------------
print('Finished')