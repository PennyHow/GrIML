# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 10:27:55 2020

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
from scipy import stats

#-------------------------   File locations   ---------------------------------

#Workspace for files
workspace = ('D:/python_workspace/ice_marginal_lakes/')

#2017 Inventory subset
inventory = workspace + 'products/glacier_cci_lakes_20200819.shp'

#Carrivick time steps
carr1 = workspace + 'carrivick_validation/carrivick_lakes/all_carrivick_reproj.shp'

#West coast mask
mask = workspace + 'carrivick_validation/west_coast_mask.shp'

#-------------------------   Load as dataframe   ------------------------------

print('\nLoading geodataframes...')    

#Read file as geopandas index
geofile17 = gp.read_file(inventory)
geofile17 = geofile17.sort_values('LakeID')

#Read Carrivick files where lakes are region-wide
geofile87_18 = gp.read_file(carr1)

#Read mask file
geofile_mask = gp.read_file(mask)


#----------------------------   Mask IIML  ------------------------------------

print('\nRetrieving inventory lake stats...')

def findOverlaps(ufile1, ufile2):
    '''Find overlaps between polygons and mask   
    '''
    #Load all shapefiles as geodatabases
    mask = ufile2['geometry'].iloc[0]
    try:                                            #Try create polygon
        mask_geom = Polygon(mask)
    except:                                         #Else create multipolygon
        mask_geom = MultiPolygon(mask)    
    
    print(mask_geom)
        
    #Look for overlapping points and polygons
    print('Determining overlaps...')
    overlaps=[]                                             
    for i,v in ufile1.iterrows():  
        try:                                            #Try create polygon
            geom = Polygon(v['geometry'])
        except:                                         #Else create multipolygon
            geom = MultiPolygon(v['geometry']) 
                   
        if mask_geom.contains(geom) == False:          #If pt coincides with polygon
            overlaps.append(i)
        
    print('Percentage overlap: ' + str((len(overlaps)/ufile1.shape[0])*100))
    out = ufile1.drop(ufile1.index[overlaps])            
    return out

geofile17_masked = findOverlaps(geofile17, geofile_mask)
idx = geofile17_masked[geofile17_masked['DrainageBa'] == 'ICE_CAP'].index 

#Omit certain lakes from index list to drop
idx = idx.tolist()
exceptions=[571,572,                        #Lake ID 486
            632,633,634,                    #Lake ID 525
            852,853,854,855,856,857,        #Lake ID 652
            4363,4367,4371]                 #Lake ID 3250
idx2 = []
for i in idx:
    flag=False
    for e in exceptions:
        if e==i:
            flag=True
    if flag is False:
        idx2.append(i)

geofile17_masked = geofile17_masked.drop(idx2)


#-------------------------   Obtain areas   -----------------------------------

print('\nRetrieving non-ADEM aggregated lake areas...')

source17 = geofile17_masked['Source'].tolist()
id17 = geofile17_masked['LakeID'].tolist()
geom17 = geofile17_masked['geometry'].tolist()

def getArea(geofile, calc='sum', ADEM=True):

    source17 = geofile['Source'].tolist()
    id17 = geofile['LakeID'].tolist()
    geom17 = geofile['geometry'].tolist()
    
    #Retrieve non-ADEM aggregated lake areas
    areas=[]
    for i in list(sorted(set(id17))):
        id_source=[]
        id_geometry=[]
        for l in range(len(id17)):
            if id17[l] == i:
                id_source.append(source17[l])
                id_geometry.append(geom17[l])
                
        #Clear previous
        geom_agg=[]
        id_agg=[]
        gf=None
        gdf=None
        flag=False        
        for s in range(len(id_source)):
            if id_source[s] in ['S1','S2']:
                geom_agg.append(id_geometry[s])
                id_agg.append(i)
                flag=True
        
        if flag is False:
            if ADEM is True:
                for s in range(len(id_source)):
                    if id_source[s] in ['ArcticDEM']:
                        geom_agg.append(id_geometry[s])
                        id_agg.append(i) 
            else:
                id_agg=None
        
        if id_agg is not None:
            gf = {'LakeID':id_agg, 'geometry':geom_agg}
            gdf = gp.GeoDataFrame(gf, crs='EPSG:32624')
            
            if calc == 'sum':
                gdf = gdf.dissolve(by='LakeID')
                gdf['Area']=gdf['geometry'].area
                id_area = gdf['Area'].tolist()
                areas.append(float(id_area[0]))
                
            elif calc == 'aver':
                gdf['Area']=gdf['geometry'].area 
                id_area = gdf['Area'].tolist()
                areas.append(float(np.average(id_area)))
                
            elif calc == 'median':
                gdf['Area']=gdf['geometry'].area 
                id_area = gdf['Area'].tolist()
                areas.append(float(np.median(id_area)))
                
            elif calc == 'mode':
                 gdf['Area']=gdf['geometry'].area 
                 id_area1 = gdf['Area'].tolist()
                 id_area2 = [round(n, 2) for n in id_area1]
                 areas.append(float(stats.mode(id_area2).mode[0]))
                            
        else:
            areas.append(float(0))

    print('Total area (S1 and S2 '+calc+' (ADEM '+str(ADEM)+'): '+str(sum(areas)/10**6) + ' sq km')
    print('Average area (S1 and S2 '+calc+' (ADEM '+str(ADEM)+'): '+str(np.average(areas)/10**6) + ' sq km')
    print('Lake frequency (S1 and S2 '+calc+' (ADEM '+str(ADEM)+'): '+str(sum(i>0 for i in areas)) + '\n')
    return areas


def getArea_S2only(geofile):
    source17 = geofile['Source'].tolist()
    id17 = geofile['LakeID'].tolist()
    geom17 = geofile['geometry'].tolist()
    
    #Retrieve non-ADEM aggregated lake areas
    areas=[]
    for i in list(sorted(set(id17))):
        id_source=[]
        id_geometry=[]
        for l in range(len(id17)):
            if id17[l] == i:
                id_source.append(source17[l])
                id_geometry.append(geom17[l])
                
        #Clear previous
        geom_agg=[]
        id_agg=[]
        gf=None
        gdf=None
        flag=False        
        for s in range(len(id_source)):
            if id_source[s] in ['S2']:
                geom_agg.append(id_geometry[s])
                id_agg.append(i)
                flag=True
        
        if flag is True:
            gf = {'LakeID':id_agg, 'geometry':geom_agg}
            gdf = gp.GeoDataFrame(gf, crs='EPSG:32624')

            gdf = gdf.dissolve(by='LakeID')
            gdf['Area']=gdf['geometry'].area
            id_area = gdf['Area'].tolist()
            areas.append(float(id_area[0]))

    print('Total area (S2) : '+str(sum(areas)/10**6) + ' sq km')
    print('Average area (S2): '+str(np.average(areas)/10**6) + ' sq km')
    print('Lake frequency (S2): '+str(sum(i>0 for i in areas)) + '\n')
    return areas


#print('\nALL LAKES IN IIML')
#area17_all1 = getArea(geofile17, calc='sum', ADEM=True) 
#area17_all2 = getArea(geofile17, calc='sum', ADEM=False) 
#area17_all3 = getArea(geofile17, calc='aver', ADEM=True) 
#area17_all4 = getArea(geofile17, calc='aver', ADEM=False) 

print('\nWEST COAST SUBSET')
#area17_1 = getArea(geofile17_masked, calc='sum', ADEM=True) 
#area17_2 = getArea(geofile17_masked, calc='sum', ADEM=False) 
area17_3 = getArea(geofile17_masked, calc='aver', ADEM=True) 
area17_4 = getArea(geofile17_masked, calc='aver', ADEM=False)
area17_5 = getArea_S2only(geofile17_masked)
# area17_6 = getArea(geofile17_masked, calc='median', ADEM=True)
# area17_7 = getArea(geofile17_masked, calc='median', ADEM=False)

#Add amended areas to geofile upper limit
geofile17_dissolved1 = geofile17_masked.dissolve(by='LakeID')
geofile17_dissolved1['Area1'] = area17_3
idx = geofile17_dissolved1[geofile17_dissolved1['Area1'] == 0].index 
geofile17_dissolved1 = geofile17_dissolved1.drop(idx)

#Add amended areas to geofile lower limit
geofile17_dissolved2 = geofile17_masked.dissolve(by='LakeID')
geofile17_dissolved2['Area1'] = area17_4
idx = geofile17_dissolved2[geofile17_dissolved2['Area1'] == 0].index 
geofile17_dissolved2 = geofile17_dissolved2.drop(idx)

#Retrieve upper limit data from geofile
source17 = geofile17_dissolved1['DrainageBa'].tolist()
area17 = geofile17_dissolved1['Area1'].tolist()   
iiml_area_max = sum(area17)/10**6
iiml_aver_max = np.average(area17)/10**6
iiml_med_max = np.median(area17)/10**6
iiml_std_max = np.std(area17)/10**6
iiml_freq_max = len(area17)

#Retrieve lower limit data from geofile
source17 = geofile17_dissolved2['DrainageBa'].tolist()
area17 = geofile17_dissolved2['Area1'].tolist()   
iiml_area_min = sum(area17)/10**6
iiml_aver_min = np.average(area17)/10**6
iiml_med_min = np.median(area17)/10**6
iiml_std_min = np.std(area17)/10**6
iiml_freq_min = len(area17)

#Retrieve average values from max and min
iiml_area = [(iiml_area_min+iiml_area_max)/2]
iiml_aver = [(iiml_aver_min+iiml_aver_max)/2]
iiml_med = [(iiml_med_min+iiml_med_max)/2]
iiml_std = [(iiml_std_min+iiml_std_max)/2]
iiml_freq = [(iiml_freq_min+iiml_freq_max)/2]
iiml_date = [dt.date(2017,1,1)]


#Source breakdown
sat17 = geofile17_dissolved1['Satellites'].tolist()
print('Sentinel-1 only lakes: ' + str(sat17.count('S1')))
print('Sentinel-2 only lakes: ' + str(sat17.count('S2')))
print('ADEM only lakes: ' + str(sat17.count('ArcticDEM')))
print('S1 and ADEM lakes: ' + str(sat17.count('ArcticDEM, S1')))
print('S2 and ADEM lakes: ' + str(sat17.count('S2, ArcticDEM')))
print('S1 and S2 lakes: ' + str(sat17.count('S2, S1')))
print('S1, S2 and ADEM lakes: ' + str(sat17.count('S2, ArcticDEM, S1')))

#-----------------------   Get Carrivick stats   ------------------------------

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

print('Total number of lakes in 2017 inventory subset: ' + str(len(area17)))
print('Number of lakes in 1987 Carrivick dataset: ' + str(len(area87)))
print('Number of lakes in 1992 Carrivick dataset: ' + str(len(area92)))
print('Number of lakes in 2000 Carrivick dataset: ' + str(len(area00)))
print('Number of lakes in 2005 Carrivick dataset: ' + str(len(area05)))
print('Number of lakes in 2010 Carrivick dataset: ' + str(len(area10)) + '\n')

print('Average lake size in 1987 carrivick dataset: ' + str(np.average(area87)/10**6))
print('Average lake size in 1992 carrivick dataset: ' + str(np.average(area92)/10**6))
print('Average lake size in 2000 carrivick dataset: ' + str(np.average(area00)/10**6))
print('Average lake size in 2005 carrivick dataset: ' + str(np.average(area05)/10**6))
print('Average lake size in 2010 carrivick dataset: ' + str(np.average(area10)/10**6))
print('Average lake size in 2017 inventory subset: ' + str(np.average(area17)/10**6)+ '\n')

print('Median lake size in 1987 carrivick dataset: ' + str(np.median(area87)/10**6))
print('Median lake size in 1992 carrivick dataset: ' + str(np.median(area92)/10**6))
print('Median lake size in 2000 carrivick dataset: ' + str(np.median(area00)/10**6))
print('Median lake size in 2005 carrivick dataset: ' + str(np.median(area05)/10**6))
print('Median lake size in 2010 carrivick dataset: ' + str(np.median(area10)/10**6))
print('Median lake size in 2017 inventory subset: ' + str(np.median(area17)/10**6)+ '\n')

print('Total lake size in 2017 inventory subset: ' + str(sum(area17)))
print('Total lake size in 1987 carrivick dataset: ' + str(sum(area87)))
print('Total lake size in 1992 carrivick dataset: ' + str(sum(area92)))
print('Total lake size in 2000 carrivick dataset: ' + str(sum(area00)))
print('Total lake size in 2005 carrivick dataset: ' + str(sum(area05)))
print('Total lake size in 2010 carrivick dataset: ' + str(sum(area10)))

carr_iiml_date = [dt.date(1987,1,1),dt.date(1992,1,1),
                  dt.date(2000,1,1),dt.date(2005,1,1), 
                  dt.date(2010,1,1)]
carr_iiml_freq = [len(area87),len(area92),len(area00),len(area05),len(area10)]
carr_iiml_area = [sum(area87)/10**6,sum(area92)/10**6,sum(area00)/10**6,
                  sum(area05)/10**6,sum(area10)/10**6]
carr_iiml_aver = [np.average(area87)/10**6, np.average(area92)/10**6,
                  np.average(area00)/10**6, np.average(area05)/10**6,
                  np.average(area10)/10**6]
carr_iiml_med = [np.median(area87)/10**6, np.median(area92)/10**6,
                  np.median(area00)/10**6, np.median(area05)/10**6,
                  np.median(area10)/10**6]
carr_iiml_std = [np.std(area87)/10**6, np.std(area92)/10**6,
                  np.std(area00)/10**6, np.std(area05)/10**6,
                  np.std(area10)/10**6]
freq_err=0.065
area_err=0.07
carr_err_freq = [(i*freq_err)/2 for i in carr_iiml_freq] 
carr_err_area = [(i*area_err)/2 for i in carr_iiml_area]
carr_err_aver = [(i*area_err)/2 for i in carr_iiml_aver]
   
#----------------------------   Plotting 2   ----------------------------------

#Plot change in lake area through time
print('Plotting inventory...')

#Set plot feature sizes
lwidth=0.65
scatwidth=60
tickpad=4
yloc1=[-0.07, 0.5]
yloc2=[1.11, 0.45]
yloc3=[-0.052, 0.45]
cols = ['#2D92BD','#D79311', '#0EB033']

#Error paramters
elinecol = '#6A6A6A'
elinewidth = 1
elinecap = 2

#Set font sizes
fsize=12
labsize=10
legsize=10

#Prime figure plot
fig = plt.figure(figsize=(10,10))
ax1 = plt.subplot2grid((16,1), (8,0), rowspan=8, colspan=1)
ax2 = plt.subplot2grid((16,1),(6,0), rowspan=2, colspan=1, sharex=ax1)
ax3 = plt.subplot2grid((16,1),(4,0), rowspan=2, colspan=1, sharex=ax1)
ax4 = plt.subplot2grid((16,1),(2,0), rowspan=2, colspan=1, sharex=ax1)
ax5 = plt.subplot2grid((16,1),(0,0), rowspan=2, colspan=1, sharex=ax1)

#Plot bars
ax1.bar(range(len(carr_iiml_date)), carr_iiml_freq, color=cols[0], width=lwidth, label='Carrivick & Quincey (2014) lakes')
ax1.bar([len(carr_iiml_date)], iiml_freq, color=cols[1], width=lwidth, label='IIML average')
ax1.tick_params(direction='out', pad=tickpad)
ax1.set_ylabel('Lake count', fontsize=fsize)
ax1.yaxis.set_label_coords(yloc1[0], yloc1[1])
ax1.set_ylim(0, 800)
ax1.set_yticks([0,100,200,300,400,500,600,700,800]) 
ax1.set_yticklabels(['0','','200','','400','','600','','800'], fontsize=labsize)

#Plot total lake area
ax2twin = ax2.twinx()
ax2twin.scatter(range(len(carr_iiml_date)), carr_iiml_area, s=scatwidth, c=cols[0])
ax2twin.scatter([len(carr_iiml_date)], iiml_area, s=scatwidth, c=cols[1])
ax2twin.set_xlim(-1,6)
ax2twin.set_ylim(400, 1000)
ax2twin.set_yticks([400,600,800,1000]) 
ax2twin.set_yticklabels(['400','600','800','1000'], fontsize=labsize)
ax2twin.set_ylabel('Total lake \narea (km' + r'$^2$'+')', fontsize=fsize, rotation=270)
ax2twin.tick_params(direction='out', pad=tickpad)
ax2twin.yaxis.set_label_coords(yloc2[0], yloc2[1])

#Plot std lake area
ax3.scatter(range(len(carr_iiml_date)), carr_iiml_std, s=50, c=cols[0], marker='D')
ax3.scatter([len(carr_iiml_date)], iiml_std, s=50, c=cols[1], marker='D')
ax3.tick_params(direction='out', pad=tickpad)
ax3.set_ylabel('Standard deviation\nlake area (km' + r'$^2$'+')', fontsize=fsize)
ax3.yaxis.set_label_coords(yloc3[0], yloc3[1])
ax3.set_ylim(4, 7)
ax3.set_yticks([4,5,6,7]) 
ax3.set_yticklabels(['4.0','5.0','6.0','7.0'], fontsize=labsize)

#Plot median lake area
ax4twin = ax4.twinx()
ax4twin.scatter(range(len(carr_iiml_date)), carr_iiml_med, s=scatwidth, c=cols[0], marker='^')
ax4twin.scatter([len(carr_iiml_date)], iiml_med, s=scatwidth, c=cols[1], marker='^')
ax4twin.set_xlim(-1,6)
ax4twin.set_ylim(0.1, 0.25)
ax4twin.set_yticks([0.10,0.15,0.20,0.25]) 
ax4twin.set_yticklabels(['0.10','0.15','0.20','0.25'], fontsize=labsize)
ax4twin.set_ylabel('Median lake\narea (km' + r'$^2$'+')', fontsize=fsize, rotation=270)
ax4twin.tick_params(direction='out', pad=tickpad)
ax4twin.yaxis.set_label_coords(yloc2[0], yloc2[1])

#Plot average lake area
ax5.scatter(range(len(carr_iiml_date)), carr_iiml_aver, s=scatwidth, c=cols[0],
            marker='s')
ax5.scatter([len(carr_iiml_date)], iiml_aver, s=scatwidth, c=cols[1], marker='s')
ax5.set_xlim(-1,6)
ax5.set_ylim(0.8, 2)
ax5.set_yticks([0.8,1.2,1.6,2.0]) 
ax5.set_yticklabels(['0.8','1.2','1.6','2.0'], fontsize=labsize)
ax5.set_ylabel('Average lake\narea (km' + r'$^2$'+')', fontsize=fsize)
ax5.tick_params(direction='out', pad=tickpad)
ax5.yaxis.set_label_coords(yloc3[0], yloc3[1])

#Set primary x axis 
ax1.set_xlim(-0.5,5.5)
labels=['','1985-88\nWest inventory','1992-94\nWest inventory',
        '1999-2001\nWest inventory','2004-07\nWest inventory',
        '2009-11\nWest inventory','2017\n IIML subset']
ax1.set_xticklabels(labels, fontsize=labsize, wrap=True)    

#Set plot grids
for ax in [ax1,ax2twin,ax3,ax4twin,ax5]:
    ax.set_axisbelow(True)
    ax.yaxis.grid(True)


#Set x/y ticks off for other axes
ax1.tick_params(axis='y',which='both',right=True) 
ax3.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
ax3.tick_params(axis='y',which='both',right=True)
ax5.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
ax5.tick_params(axis='y',which='both',right=True)

ax2.set_yticklabels([])
ax4.set_yticklabels([])
ax2.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False) 
ax4.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
ax2twin.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
ax2twin.tick_params(axis='y',which='both',left=True) 
ax4twin.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
ax4twin.tick_params(axis='y',which='both',left=True)

ax2twin.spines['bottom'].set_visible(False)
ax3.spines['bottom'].set_visible(False)
ax4twin.spines['bottom'].set_visible(False)
ax5.spines['bottom'].set_visible(False)

#Save plot
plt.subplots_adjust(left=0.11, bottom=0.24, right=0.90, top=0.90, wspace=0.2, hspace=0)
plt.savefig(r'P:\B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland\B71-05 Product validation and user assessment\publication\figures\old\inventory_validation_final.png', dpi=300)
plt.show()