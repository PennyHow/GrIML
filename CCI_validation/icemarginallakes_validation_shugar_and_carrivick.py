# -*- coding: utf-8 -*-
"""
Created on Fri May 29 08:34:45 2020

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
from shapely.geometry import Point, Polygon, MultiPolygon
#-------------------------   File locations   ---------------------------------

#Workspace for files
workspace = ('P:/B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland' +
              '/B71-05 Product validation and user assessment/validation_' +
              'datasets')

#2017 Inventory 
inventory = workspace + '/inventory17_subset/glacier_cci_lakes_subset_for_carrivick.shp'

#Shugar time steps
shug90 = workspace + '/shugar_2020_dataset/greenland_only/HMA_GLI_glacial_lakes_LatLonWGS84_1990_99_WGRL_reproj.shp'
shug00 = workspace + '/shugar_2020_dataset/greenland_only/HMA_GLI_glacial_lakes_LatLonWGS84_2000_04_WGRL_reproj.shp'
shug05 = workspace + '/shugar_2020_dataset/greenland_only/HMA_GLI_glacial_lakes_LatLonWGS84_2005_09_WGRL_reproj.shp'
shug10 = workspace + '/shugar_2020_dataset/greenland_only/HMA_GLI_glacial_lakes_LatLonWGS84_2010_14_WGRL_reproj.shp'
shug15 = workspace + '/shugar_2020_dataset/greenland_only/HMA_GLI_glacial_lakes_LatLonWGS84_2015_18_WGRL_reproj.shp'

#Carrivick inventories
carr87_18 = workspace + '/carrivick_IMLs_for_validation/Total_lakes/all_carrivick_reproj.shp'

#-------------------------   Load as dataframe   ------------------------------

print('\nLoading geodataframes...')    

#Read file as geopandas index
geofile17 = gp.read_file(inventory)

#Read Shugar files where lakes are GL-wide
geofile90 = gp.read_file(shug90)
geofile00 = gp.read_file(shug00)
geofile05 = gp.read_file(shug05)
geofile10 = gp.read_file(shug10)
geofile15 = gp.read_file(shug15)

#Read Carrivick's west inventory files
geofile87_18 = gp.read_file(carr87_18)


#--------------------   Get inventory stats for Shugar  -----------------------

print('\nRetrieving inventory lake stats...')

#Get 2017 lake areas
geofile17['Area1'] = geofile17['geometry'].area
area17 = geofile17['Area1'].tolist()         

#Get data from Shugar columns
area90 = geofile90['Area_m2'].tolist()          
area00 = geofile00['Area_m2'].tolist()       
area05 = geofile05['Area_m2'].tolist()          
area10 = geofile10['Area_m2'].tolist()   
area15 = geofile15['Area_m2'].tolist()   

#Get data from Carrivick columns
area_carr = geofile87_18['Area'].tolist()

#Set 2017 IIML date
date_iiml = [dt.date(2017,1,1), dt.date(2017,12,31)]

#Set Shugar dates
date_shug = [[dt.date(1990,1,1),dt.date(1999,12,31)],[dt.date(2000,1,1),dt.date(2004,12,31)],
            [dt.date(2005,1,1),dt.date(2009,12,31)],[dt.date(2010,1,1),dt.date(2014,12,31)],
            [dt.date(2015,1,1),dt.date(2018,12,31)]]
     
#Get shugar info
freq_shug=[]
for a in [area90, area00, area05, area10, area15]:
    freq_shug.append(len(a))

aver_shug=[]
for a in [area90, area00, area05, area10, area15]:
    aver_shug.append(np.average(a)/10**6)

area_shug=[]
for a in [area90, area00, area05, area10, area15]:
    area_shug.append(sum(a)/10**6)
    
#Get IIML info
freq_iiml = len(area17)
aver_iiml = np.average(area17)/10**6
area_iiml = sum(area17)/10**6


#--------------------   Get inventory stats for Carrivick  --------------------

print('\nRetrieving inventory lake stats...')

#Get data from Carrivick columns
yearcarr = geofile87_18['Year'].tolist()          #Lake year
layercarr = geofile87_18['layer'].tolist()        #Inventory year
areacarr = geofile87_18['Area'].tolist()          #Get lake areas

area87=[]
area92=[]
area00=[]
area05=[]
area10=[]

for a,y in zip(areacarr, layercarr):
    if y in '1987':
        area87.append(a)
    elif y in '1992':
        area92.append(a)
    elif y in '2000':
        area00.append(a)
    elif y in '2005':
        area05.append(a)
    elif y in '2010':
        area10.append(a)        

#Get carrivick date spans
date_carr = [[dt.date(1985,1,1),dt.date(1988,12,31)],
            [dt.date(1992,1,1),dt.date(1994,12,31)],
            [dt.date(1999,1,1),dt.date(2001,12,31)],
            [dt.date(2004,1,1),dt.date(2007,12,31)], 
            [dt.date(2009,1,1),dt.date(2011,12,31)]]

#Get carrivick info
freq_carr=[]
for a in [area87, area92, area00, area05, area10]:
    freq_carr.append(len(a))

aver_carr=[]
for a in [area87, area92, area00, area05, area10]:
    aver_carr.append(np.average(a)/10**6)

area_carr=[]
for a in [area87, area92, area00, area05, area10]:
    area_carr.append(sum(a)/10**6)


#----------------------------   Plotting 1   ----------------------------------

#Plot change in lake area through time
print('Plotting west coast comparison...')

#Set plot feature sizes
lwidth=1.5
scatwidth=60
tickpad=4
yloc1=[-0.07, 0.5]
yloc2=[-0.07, 0.5]
yloc3=[-0.07, 0.5]
cols = ['#2D92BD','#D79311','#22A216']

#Set font sizes
fsize=12
labsize=10
legsize=8
legloc=2

#Prime figure plot
fig = plt.figure(figsize=(10,10))
ax1 = plt.subplot2grid((12,1), (8,0), rowspan=4, colspan=1)
ax2 = plt.subplot2grid((12,1),(4,0), rowspan=4, colspan=1, sharex=ax1)
ax3 = plt.subplot2grid((12,1),(0,0), rowspan=4, colspan=1, sharex=ax1)

#Plot frequency in ax1
for a,b in zip(date_shug, freq_shug):
    ax1.plot([a[0],a[1]], [b,b], color=cols[2], linewidth=lwidth)
for a,b in zip(date_carr, freq_carr):
    ax1.plot([a[0],a[1]], [b,b], color=cols[0], linewidth=lwidth)
ax1.plot(date_iiml, [freq_iiml,freq_iiml], color=cols[1], linewidth=lwidth)
ax1.tick_params(direction='out', pad=tickpad)
ax1.set_ylabel('Lake count', fontsize=fsize)
ax1.yaxis.set_label_coords(yloc1[0], yloc1[1])
ax1.set_ylim(0, 2500)
ax1.set_yticks([0,500,1000,1500,2000,2500]) 
ax1.set_yticklabels(['0','500','1000','1500','2000',''], 
                    fontsize=labsize)
ax1.set_xlim(dt.date(1985,1,1),dt.date(2020,1,1))
ax1.set_xticks([dt.date(1985,1,1),dt.date(1990,1,1),dt.date(1995,1,1),
                dt.date(2000,1,1),dt.date(2005,1,1),dt.date(2010,1,1),
                dt.date(2015,1,1),dt.date(2020,1,1)]) 
ax1.set_xticklabels(['1985','1990','1995','2000','2005','2010','2015','2020'],
                    fontsize=labsize)

#Plot average area on ax2
for a,b in zip(date_shug, aver_shug):
    ax2.plot([a[0],a[1]], [b,b], color=cols[2], linewidth=lwidth)
for a,b in zip(date_carr, aver_carr):
    ax2.plot([a[0],a[1]], [b,b], color=cols[0], linewidth=lwidth)
ax2.plot(date_iiml, [aver_iiml,aver_iiml], color=cols[1], linewidth=lwidth)
ax2.set_ylim(0.4, 2)
ax2.set_yticks([0.4,0.8,1.2,1.6,2.0]) 
ax2.set_yticklabels(['0.4','0.8','1.2','1.6',''], fontsize=labsize)
ax2.set_ylabel('Average lake area (km' + r'$^2$'+')', fontsize=fsize)
ax2.tick_params(direction='out', pad=tickpad)
ax2.yaxis.set_label_coords(yloc2[0], yloc2[1])
ax1.set_xlim(dt.date(1985,1,1),dt.date(2020,1,1))

#Plot total area on ax3
for a,b in zip(date_shug, area_shug):
    ax3.plot([a[0],a[1]], [b,b], color=cols[2], linewidth=lwidth)
for a,b in zip(date_carr, area_carr):
    ax3.plot([a[0],a[1]], [b,b], color=cols[0], linewidth=lwidth)
ax3.plot(date_iiml, [area_iiml,area_iiml], color=cols[1], linewidth=lwidth)
ax3.set_ylim(500, 2500)
ax3.set_yticks([500,1000,1500,2000,2500]) 
ax3.set_yticklabels(['500','1000','1500','2000','2500'], fontsize=labsize)
ax3.set_ylabel('Total lake area (km' + r'$^2$'+')', fontsize=fsize)
ax3.tick_params(direction='out', pad=tickpad)
ax3.yaxis.set_label_coords(yloc3[0], yloc3[1])
ax1.set_xlim(dt.date(1985,1,1),dt.date(2020,1,1))
  
#Set plot grids
ax1.set_axisbelow(True)
ax1.yaxis.grid(True)
ax2.set_axisbelow(True)
ax2.yaxis.grid(True)
ax3.set_axisbelow(True)
ax3.yaxis.grid(True)

#Set x/y ticks off for other axes
ax2.tick_params(axis='y',which='both',right=True) 
ax1.tick_params(axis='y',which='both',right=True) 
ax3.tick_params(axis='y',which='both',right=True)

ax2.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False) 
ax2.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False) 
ax3.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
ax2.spines['bottom'].set_visible(False)
ax3.spines['bottom'].set_visible(False)

#Add common legend
scatwidth1=10
legend_elements = [Line2D([0], [1], color=cols[0], linewidth=lwidth, label='Carrivick & Quincey (2014) west coast inventory'),
                  Line2D([0], [1], color=cols[1], linewidth=lwidth, label='2017 IIML inventory (west coast subset)'),
                  Line2D([0], [1], color=cols[2], linewidth=lwidth, label='Shugar et al. (2020) glacial lake inventory (west coast subset)')]
ax1.legend(handles=legend_elements, fontsize=legsize, bbox_to_anchor=(0.5, -0.35),
          loc='lower center', ncol=3, edgecolor='black')

#Save plot
plt.subplots_adjust(left=0.11, bottom=0.24, right=0.90, top=0.90, wspace=0.2, hspace=0)
plt.savefig(r'P:\B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland\B71-05 Product validation and user assessment\publication\figures\old\inventory_west_coast_comparison.png', dpi=300)
plt.show()