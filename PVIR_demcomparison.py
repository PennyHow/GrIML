# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 09:03:28 2020

CCI Ice-marginal Lake Inventory PVIR analysis

Script for vector comparison for ADEM- and SPOT-derived lakes using the DEM
sink detection method.

@author: HOW
"""

import os
import numpy as np
import geopandas as gp
import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

#-------------------------   File locations   ---------------------------------

#Workspace for files
workspace = ('P:/B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland/' +
             'B71-02 Algorithm development/Test_area_Disko/APM_ADEM_comparison/')

#ArcticDEM IML shapefiles
adem_freq = workspace + 'IIML_ADEM_subset_freq.shp'
adem_area = workspace + 'IIML_ADEM_subset_area.shp'

#SPOT DEM IML shapefiles
spot_freq = workspace + 'APM_lakes_5kmbuffer_freq_reproj.shp'
spot_area = workspace + 'APM_lakes_5kmbuffer_area_reproj.shp'


#-------------------------   Load as dataframe   ------------------------------

print('\nLoading geodataframes...\n')    

#Read file as geopandas index
geofile1 = gp.read_file(adem_freq)
geofile2 = gp.read_file(adem_area)
geofile3 = gp.read_file(spot_freq)
geofile4 = gp.read_file(spot_area)


#--------------------------   Assign Lake IDs   -------------------------------

print('Assigning IML ids...\n')

#Iterate through area polygons
idlist=[]
for index4, poly4 in geofile4.iterrows():
    idlake=None
    for index2, poly2 in geofile2.iterrows():
        if poly2['geometry'].intersects(poly4['geometry']):
            idlake=int(poly2['LakeID'])
    idlist.append(idlake)
geofile4['LakeID']=idlist 


#Iterate through frequency polygons
idlist=[]
count=1
for index4, poly4 in geofile3.iterrows():
    idlake=None
    for index2, poly2 in geofile1.iterrows():
        if poly2['geometry'].intersects(poly4['geometry']):
            idlake=int(poly2['LakeID'])
    if idlake is None:
        idlake=count
        count=count+1        
    idlist.append(idlake)
geofile3['LakeID']=idlist 


#-------------------------   Frequency analysis   -----------------------------

print('Performing IML frequency analysis...\n')

adem_count1 = geofile1['LakeID'].tolist()
spot_count1 = geofile3['LakeID'].tolist()
print('Number of IMLs in ADEM record (unmerged): ' + str(len(adem_count1)))
print('Number of IMLs in SPOT record (unmerged): ' + str(len(spot_count1)))
print('\n')


agg_geofile1 = geofile1.dissolve(by='LakeID')
agg_geofile3 = geofile3.dissolve(by='LakeID')
adem_count2 = agg_geofile1['Area'].tolist()
spot_count2 = agg_geofile3['area'].tolist()
print('Number of IMLs in ADEM record (merged): ' + str(len(adem_count2)))
print('Number of IMLs in SPOT record (merged): ' + str(len(spot_count2)))
print('\n')

#---------------------------   Area analysis   --------------------------------

print('Performing IML area analysis...\n')

adem_id = geofile2['LakeID'].tolist()
adem_a = geofile2['Area'].tolist()

spot_id = geofile4['LakeID'].tolist()
spot_a = geofile4['area'].tolist()

print('Comparing ' + str(len(adem_a)) + ' ADEM polygons with ' +
      str(len(spot_a)) + ' SPOT polygons')

uniqueids = set(adem_id)

grouped=[]
for u in sorted(uniqueids):
    adem_iml=[]
    spot_iml=[]
    for i in range(len(adem_a)):
        if str(u) in str(adem_id[i]):
            adem_iml.append(adem_a[i])
    for i in range(len(spot_id)):
        if str(u) in str(spot_id[i]):
            spot_iml.append(spot_a[i])
    grouped.append([u, sum(adem_iml), sum(spot_iml)])

diff=[]
diffids=[]
diff_adem=[]
diff_spot=[]

for g in grouped:
    if g[2]==0:
        print('Invalid comparison. Moving to next\n')
    else:
        print('Id ' + str(g[0]))
        print('ADEM area: ' + str(g[1]/1000000) + ' sq km')
        print('SPOT area: ' + str(g[2]/1000000) + ' sq km')
        print('Difference: ' + str((g[2]-g[1])/1000000) + ' sq km\n')
        if (g[2]-g[1])/1000000 > -20:
            diff.append((g[2]-g[1])/1000000)
            diffids.append(g[0])
            diff_adem.append(g[1]/1000000)
            diff_spot.append(g[2]/1000000)
        
print('Minimum difference: ' + str(min(diff)) + ' sq km') 
print('Maximum difference: ' + str(max(diff)) + ' sq km')        
print('Average difference: ' + str(np.mean(diff)) + ' sq km')        
print('Standard deviation: ' + str(np.std(diff)) + ' sq km')

ademlarger=0
ademsmaller=0
for d in diff:
    if d>0:
        ademsmaller=ademsmaller+1
    else:
        ademlarger=ademlarger+1
print('ADEM > SPOT instances: ' + str(ademlarger))
print('ADEM < SPOT instance: ' + str(ademsmaller))        

        
#------------------------------------------------------------------------------

print('Plotting DEM lake differences')    

#Plot and show if True
plot=True

#Set plot feature sizes
lwidth=0.3
dashwidth=0.5
scatwidth=15
legloc=1
lpad=40
yloc1=[-0.033,0.39]
yloc2=[1.053,0.84]

#Set font sizes
fsize=16
labsize=14
legsize=14

#Set colours
lakecol=['#0097fc','#db5a5a']
cols=['#C78502','#2D8408']
         
#Prime figure plot
fig, (ax1) = plt.subplots(1, 1, figsize=(20,10), sharex=True)
   
#Plot 1: Bars of area
plottingx1 = list(range(len(diffids)))
plottingx2 = [x+lwidth for x in plottingx1]

ax1.bar(plottingx1, diff_adem, color=cols[0], width=lwidth,
        label='ADEM lake area')
ax1.bar(plottingx2, diff_spot, color=cols[1], width=lwidth,
        label='SPOT lake area')
#ax1.grid(True)
ax1.set_axisbelow(True)
ax1.yaxis.grid(True)
ax1.set_ylabel('Area (km' + r'$^2$' + ')', labelpad=lpad, fontsize=fsize)

ax1.set_ylim(0, 9)
ax1.set_yticks([0,1,2,3,4,5,6,7,8,9,10,11,12]) 
ax1.set_yticklabels(['0','1.0','2.0','3.0','4.0','5.0','6.0','7.0','8.0','','','',''], 
                    fontsize=labsize)
ax1.yaxis.set_label_coords(yloc1[0], yloc1[1])


#Scatter of difference
ax1twin=ax1.twinx()
ax1twin.scatter(plottingx1, diff, color='#000000', s=scatwidth, label='Area difference')        
ax1twin.set_ylabel('Area difference (km' + r'$^2$' + ')', labelpad=lpad, rotation=270,
                   fontsize=fsize)
ax1twin.set_ylim(-20, 6)
ax1twin.set_yticks([-2,0,2,4,6]) 
ax1twin.set_yticklabels([r'$-$2.0','0.0','2.0','4.0','6.0'], fontsize=labsize)
ax1twin.yaxis.set_label_coords(yloc2[0], yloc2[1])

#X axis (bottom)
ax1.tick_params(axis="x", labelsize=labsize)
ax1.set_xlim(min(plottingx1), max(plottingx2))
ax1.set_xticks(plottingx1)
ax1.set_xticklabels(diffids, fontsize=labsize) 
ax1.set_xlabel('Lake ID', labelpad=10, fontsize=fsize)
ax1.tick_params(direction='out', pad=6)

#Legend
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax1twin.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc=legloc, fontsize=legsize)      


#Save and show
plt.savefig(workspace + r'dem_lake_comparison.png', dpi=300)
plt.show() 
    
    

