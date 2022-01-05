# -*- coding: utf-8 -*-
"""
Created on Fri May 29 08:34:45 2020

@author: HOW
"""

import os,sys
import numpy as np
import geopandas as gp
import datetime as dt
from rtree import index
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from shapely.geometry import Point, Polygon, MultiPolygon, shape
#-------------------------   File locations   ---------------------------------

#Workspace for files
workspace1 = ('P:/B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland/B71-04 '+ 
              'Essential Climate Variable production/final lake products')

workspace2 = ('P:/B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland/B71-05 '+
             'Product validation and user assessment/validation_datasets' + 
             '/shugar_2020_dataset/greenland_only')

#2017 Inventory 
inventory1 = workspace1 + '/glacier_cci_lakes_20200819.shp'
inventory2 = workspace1 + '/glacier_cci_lakes_20200819_aggregated.shp'

#Shugar time steps
shug90 = workspace2 + '/HMA_GLI_glacial_lakes_LatLonWGS84_1990_99_GRL_reproj.shp'
shug00 = workspace2 + '/HMA_GLI_glacial_lakes_LatLonWGS84_2000_04_GRL_reproj.shp'
shug05 = workspace2 + '/HMA_GLI_glacial_lakes_LatLonWGS84_2005_09_GRL_reproj.shp'
shug10 = workspace2 + '/HMA_GLI_glacial_lakes_LatLonWGS84_2010_14_GRL_reproj.shp'
shug15 = workspace2 + '/HMA_GLI_glacial_lakes_LatLonWGS84_2015_18_GRL_reproj.shp'

#-------------------------   Load as dataframe   ------------------------------

print('\nLoading geodataframes...')    

#Read file as geopandas index
geofile17 = gp.read_file(inventory1)
agg_gf17 = gp.read_file(inventory2)

#Read Shugar files where lakes are GL-wide
geofile90 = gp.read_file(shug90)
geofile00 = gp.read_file(shug00)
geofile05 = gp.read_file(shug05)
geofile10 = gp.read_file(shug10)
geofile15 = gp.read_file(shug15)


#-----------------   Calculate overlap between inventories   ------------------
print('Calculating inventory overlap...')


#def findOverlaps(ufile1, ufile2, threshold=1.0):
#    ''' '''        
#    # List to collect pairs of intersecting features
#    fc_intersect = []
#    count=0
#    
#    # Instantiate index class
#    for i,featA in ufile1.iterrows():        
#        for i,featB in ufile2.iterrows():
#                if shape(featA['geometry']).intersects(shape(featB['geometry'])):
#                    fc_intersect.append([featA, featB])
#                    count=count+1
#    
#    print('Overlapping polygon count: ' + str(count))
#    return fc_intersect

      
#------------------------   Calculate IIML area   -----------------------------
print('Calculating aggregated areas for IIML...')
geofile17 = geofile17.sort_values('LakeID')
source17 = geofile17['Source'].tolist()
id17 = geofile17['LakeID'].tolist()
area17_1 = geofile17['Area'].tolist()
geom17 = geofile17['geometry'].tolist()
lakenames = geofile17['LakeName'].tolist()

#Retrieve non-ADEM aggregated lake areas
areas=[]
areas_indy=[]
for i in range(3348)[1:]:
    id_area=[]
    id_source=[]
    id_geometry=[]
    id_name=[]
    for l in range(len(id17)):
        if id17[l] == i:
            id_area.append(area17_1[l])
            id_source.append(source17[l])
            id_geometry.append(geom17[l])
            id_name.append(lakenames[l])
    
    if len(id_source)==1:
        areas.append(id_area)
    else:
        #Clear previous
        geom_agg=[]
        id_agg=[]
        gf=None
        gdf=None
        
        for s in range(len(id_source)):
            if id_source[s] in ['S1','S2']:
                geom_agg.append(id_geometry[s])
                id_agg.append(i)
        gf = {'LakeID':id_agg, 'geometry':geom_agg}
        gdf = gp.GeoDataFrame(gf, crs='EPSG:32624')
        
        if gdf.shape[0]>1:
            gdf = gdf.dissolve(by='LakeID')  
            
        gdf['Area']=gdf['geometry'].area
        id_area = gdf['Area'].tolist()
        areas.append(id_area)
    
    flag=False
    for i in id_name:
        if i in ['Inderhytten']:
            print('Inderhytten FOUND')
            flag=True
    if flag is True:
       inder_area = id_area 
       print(inder_area)
    else:
        areas_indy.append(id_area)
    
area17 = [item for sublist in areas for item in sublist]
area17_2 = [item for sublist in areas_indy for item in sublist]

#Get additional data
print('Retrieving additional IIML data...')
agg_gf17 = geofile17.dissolve(by='LakeID')
#agg_gf17['Area'] = agg_gf17['geometry'].area
#agg_gf17.to_file(workspace1+'/glacier_cci_lakes_20200907_aggregated.shp')
source17 = agg_gf17['Source'].tolist()
    
#-------------------------   Get Shugar data   --------------------------------            

#Get data from Shugar columns
area90 = geofile90['Area_m2'].tolist()          
area00 = geofile00['Area_m2'].tolist()       
area05 = geofile05['Area_m2'].tolist()          
area10 = geofile10['Area_m2'].tolist()   
area15 = geofile15['Area_m2'].tolist()   

#Set dates
date = [dt.date(1990,1,1),dt.date(2000,1,1),dt.date(2005,1,1),
        dt.date(2010,1,1),dt.date(2015,1,1),dt.date(2017,1,1)]

        
#Print frequency, area and average area information
freq=[]
for a,n in zip([area90, area00, area05, area10, area15, area17, area17_2],
               ['1990-99','2000-04', '2005-09','2010-14','2015-18',
                '2017 inventory incl. Inderhytten']):
    print('Total number of lakes in ' + str(n) + ': ' + str(len(a)))
    freq.append(len(a))
print('\n')

aver=[]
for a,n in zip([area90, area00, area05, area10, area15, area17, area17_2],
               ['1990-99','2000-04', '2005-09','2010-14','2015-18',
                '2017 inventory incl. Inderhytten', '2017 inventory w/o Inderhytten']):
    print('Average lake size in ' + str(n) + ': ' + str(np.average(a)/10**6))
    aver.append(np.average(a)/10**6)
print('\n')

area=[]
for a,n in zip([area90, area00, area05, area10, area15, area17, area17_2],
               ['1990-99','2000-04', '2005-09','2010-14','2015-18',
                '2017 inventory incl. Inderhytten', '2017 inventory w/o Inderhytten']):
    print('Total lake size in ' + str(n) + ': ' + str(sum(a)/10**6))
    area.append(sum(a)/10**6)
print('\n')


#----------------------------   Plotting 1   ----------------------------------

#Plot change in lake area through time
print('Plotting inventory...')

#Set plot feature sizes
lwidth=0.75
scatwidth=40
tickpad=4
yloc1=[-0.07, 0.5]
yloc2=[1.11, 0.45]
yloc3=[-0.052, 0.45]
cols = ['#2D92BD','#D79311','#22A216']

#Set font sizes
fsize=12
labsize=10
legsize=8
legloc=2

#Prime figure plot
fig = plt.figure(figsize=(10,10))
ax1 = plt.subplot2grid((12,1), (4,0), rowspan=8, colspan=1)
ax2 = plt.subplot2grid((12,1),(2,0), rowspan=2, colspan=1, sharex=ax1)
ax3 = plt.subplot2grid((12,1),(0,0), rowspan=2, colspan=1, sharex=ax1)

#Plot bars
ax1.bar(range(len(date[:-1])), freq[:-1], color=cols[0], width=lwidth)
ax1.bar([len(date)-1], freq[-1], color=cols[1], width=lwidth)
ax1.tick_params(direction='out', pad=tickpad)
ax1.set_ylabel('Lake count', fontsize=fsize)
ax1.yaxis.set_label_coords(yloc1[0], yloc1[1])
ax1.set_ylim(0, 5000)
ax1.set_yticks([0,500,1000,1500,2000,2500,3000,3500,4000,4500,5000]) 
ax1.set_yticklabels(['0','','1000','','2000','','3000','','4000','','5000'], 
                    fontsize=labsize)

#Plot scatters on same axis
ax2twin = ax2.twinx()
ax2twin.scatter(range(len(date[:-1])), area[:-2], s=scatwidth, c=cols[0], label='Shugar et al. (2020) total area')
ax2twin.scatter(len(date)-1, area[-2], s=scatwidth, color=cols[1], label='IIML total area incl. Inderhytten')
ax2twin.scatter(len(date)-1, area[-1], s=scatwidth, color=cols[2], label='IIML total area w/o Inderhytten')
ax2twin.set_xlim(-1,6)
ax2twin.set_ylim(2000, 3200)
ax2twin.set_yticks([2000,2400,2800,3200]) 
ax2twin.set_yticklabels(['2000','2400','2800','3200'], fontsize=labsize)
ax2twin.set_ylabel('Total lake \narea (km' + r'$^2$'+')', fontsize=fsize, rotation=270)
ax2twin.tick_params(direction='out', pad=tickpad)
ax2twin.yaxis.set_label_coords(yloc2[0], yloc2[1])
ax2twin.legend(loc=legloc, fontsize=legsize)

#Plot scatters on twin axis
ax3.scatter(range(len(date[:-1])), aver[:-2], s=scatwidth, c=cols[0], marker='s',label='Shugar et al. (2020) average area')
ax3.scatter(len(date)-1, aver[-2],  s=scatwidth, c=cols[1], marker='s', label='IIML average area incl. Inderhytten')
ax3.scatter(len(date)-1, aver[-1],  s=scatwidth, c=cols[2], marker='s', label='IIML average area w/o Inderhytten')
ax3.set_xlim(-1,6)
ax3.set_ylim(0.6, 1.0)
ax3.set_yticks([0.6,0.7,0.8,0.9,1.0]) 
ax3.set_yticklabels(['0.6','0.7','0.8','0.9','1.0'], fontsize=labsize)
ax3.set_ylabel('Average lake\narea (km' + r'$^2$'+')', fontsize=fsize)
ax3.tick_params(direction='out', pad=tickpad)
ax3.yaxis.set_label_coords(yloc3[0], yloc3[1])
ax3.legend(loc=legloc, fontsize=legsize)

#Set primary x axis 
ax1.set_xlim(-0.5,5.5)
labels=['','1990-99\nlake inventory','2000-04\nlake inventory',
        '2005-09\nlake inventory','2010-14\nlake inventory',
        '2015-18\nlake inventory','2017\nIIML inventory']
ax1.set_xticklabels(labels, fontsize=labsize, wrap=True)    

#Set plot grids
ax1.set_axisbelow(True)
ax1.yaxis.grid(True)
ax2twin.set_axisbelow(True)
ax2twin.yaxis.grid(True)
ax3.set_axisbelow(True)
ax3.yaxis.grid(True)

#Set x/y ticks off for other axes
ax2.set_yticklabels([])
ax2twin.tick_params(axis='y',which='both',left=True) 
ax1.tick_params(axis='y',which='both',right=True) 
ax3.tick_params(axis='y',which='both',right=True)

ax2.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False) 
ax2twin.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False) 
ax3.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
ax2twin.spines['bottom'].set_visible(False)
ax3.spines['bottom'].set_visible(False)

##Add common legend
#scatwidth1=10
#legend_elements = [Line2D([0], [0], marker='o', color='w', label='Shugar et al. (2020) glacial lake inventory', 
#                         markerfacecolor=cols[0], markersize=scatwidth1),
#                  Line2D([0], [0], marker='o', color='w', label='2017 IIML inventory incl. Inderhytten', 
#                         markerfacecolor=cols[1], markersize=scatwidth1),
#                  Line2D([0], [0], marker='o', color='w', label='2017 IIML inventory w/o Inderyhytten', 
#                         markerfacecolor=cols[2], markersize=scatwidth1)]
#ax1.legend(handles=legend_elements, fontsize=legsize, bbox_to_anchor=(0.5, -0.85),
#          loc='lower center', ncol=9, edgecolor='black')

#Save plot
plt.subplots_adjust(left=0.11, bottom=0.24, right=0.90, top=0.90, wspace=0.2, hspace=0)
plt.savefig(workspace2 + r'inventory_shugar_validation.png', dpi=300)
plt.show()