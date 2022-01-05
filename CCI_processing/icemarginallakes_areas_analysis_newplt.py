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


def countArea(data, bins):
    bincount=[]
    
    #Iterate through bins
    for b in range(len(bins)-1):
        count=0
        
        #Count data point if lies within bin
        for d in data:
            if bins[b] >= d:
                count=count+1
        print('Bin <' + str(bins[b]) + ': ' + str(count))
        bincount.append(count)
    
    #Refine bins by removing previous bin count
    bincount2=[]
    bincount2.append(bincount[0])
    for i in range(len(bincount))[1:]:
        total=bincount[i]-bincount[i-1]
        bincount2.append(total)        
        print('Bin ' + str(bins[i-1]) + '-' + str(bins[i]) + ': ' + (str(total)) + ' lakes')    
    print('Total lake count: ' + str(sum(bincount2)))    
    return bincount2


#----------------------------   Get IIML stats   ------------------------------

print('\nWEST COAST SUBSET')
area17_3 = getArea(geofile17_masked, calc='aver', ADEM=True) 
area17_4 = getArea(geofile17_masked, calc='aver', ADEM=False)
area17_5 = getArea_S2only(geofile17_masked)

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
area17_1 = geofile17_dissolved1['Area1'].tolist()   
iiml_area_max = sum(area17_1)/10**6
iiml_aver_max = np.average(area17_1)/10**6
iiml_med_max = np.median(area17_1)/10**6
iiml_freq_max = len(area17_1)

#Retrieve lower limit data from geofile
area17_2 = geofile17_dissolved2['Area1'].tolist()   
iiml_area_min = sum(area17_2)/10**6
iiml_aver_min = np.average(area17_2)/10**6
iiml_med_min = np.median(area17_2)/10**6
iiml_freq_min = len(area17_2)

#Retrieve average values from max and min
iiml_area = [(iiml_area_min+iiml_area_max)/2]
iiml_aver = [(iiml_aver_min+iiml_aver_max)/2]
iiml_med = [(iiml_med_min+iiml_med_max)/2]
iiml_freq = [(iiml_freq_min+iiml_freq_max)/2]
iiml_date = [dt.date(2017,1,1)]

#Areas list
area17_3 = []
[area17_3.append(((i+j)/10**6)/2) for i,j in zip(area17_1,area17_2)]


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
        area87.append(a/10**6)
    elif y in '1992':
        area92.append(a/10**6)
    elif y in '2000':
        area00.append(a/10**6)
    elif y in '2005':
        area05.append(a/10**6)
    elif y in '2010':
        area10.append(a/10**6)        

carr_iiml_date = [dt.date(1987,1,1),dt.date(1992,1,1),
                  dt.date(2000,1,1),dt.date(2005,1,1), 
                  dt.date(2010,1,1)]
carr_iiml_freq = [len(area87),len(area92),len(area00),len(area05),len(area10)]
carr_iiml_area = [sum(area87),sum(area92),sum(area00),sum(area05),sum(area10)]
carr_iiml_aver = [np.average(area87), np.average(area92),np.average(area00), np.average(area05),np.average(area10)]
carr_iiml_med = [np.median(area87), np.median(area92), np.median(area00), np.median(area05), np.median(area10)]
carr_iiml_std = [np.std(area87), np.std(area92), np.std(area00), np.std(area05), np.std(area10)]


#-----------------------------   Get bins   -----------------------------------

bins=[0.00,0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,1.05,200.00,250.00]
area17 = countArea(area17_3, bins)
area87 = countArea(area87, bins)
area92 = countArea(area92, bins)
area00 = countArea(area00, bins)
area05 = countArea(area05, bins)
area10 = countArea(area10, bins)
  
#----------------------------   Plotting 1   ----------------------------------

#Plot change in lake area through time
print('Plotting histograms...')

#Set plot feature sizes
lwidth=0.65
scatwidth=60
tickpad=4
yloc1=[-0.05, 0]
cols = ['#4E4E4E','#D79311','#2D92BD','#0EB033','#FAF86D']

#Set font sizes
fsize=13
labsize=9
legsize=10

#Prime figure plot
# fig, ((ax1,ax2),(ax3,ax4),(ax5,ax6)) = plt.subplots(3, 2, figsize=(15,10), sharex=True)
fig = plt.figure(figsize=(10,10))
ax1 = plt.subplot2grid((12,1), (0,0), rowspan=2, colspan=1)
ax2 = plt.subplot2grid((12,1),(2,0), rowspan=2, colspan=1, sharex=ax1)
ax3 = plt.subplot2grid((12,1),(4,0), rowspan=2, colspan=1, sharex=ax1)
ax4 = plt.subplot2grid((12,1), (6,0), rowspan=2, colspan=1, sharex=ax1)
ax5 = plt.subplot2grid((12,1),(8,0), rowspan=2, colspan=1, sharex=ax1)
ax6 = plt.subplot2grid((12,1),(10,0), rowspan=2, colspan=1, sharex=ax1)


#Plot Carrivick subset bars
for ax,b,n in zip([ax1,ax2,ax3,ax4,ax5],
                  [area87,area92,area00,area05,area10],
                  ['1985-88','1992-94',None,'2004-07','2009-11']):
    barrange=[]
    for a in range(len(bins)-1):
        barrange.append(a*(lwidth*1.0))
    ax.bar(barrange, b, color=cols[2], width=lwidth, edgecolor=cols[0])
    ax.tick_params(direction='out', pad=tickpad)

    if n is not None:
        ax.text(6.83, 200 , n , fontsize=legsize, bbox={'facecolor': cols[2], 'alpha': 0.3, 'pad': 4})
        
    ax.set_ylim(0, 250)
    ax.set_yticks([0,50,100,150,200,250]) 
    ax.set_yticklabels(['0','50','100','150','200',''], fontsize=labsize)
    
    # #Set primary x axis 
    ax.set_xlim(barrange[1]-(lwidth/2), barrange[-1]+(lwidth/2))
    ax.set_xticks(barrange[1:]) 
     
    #Set plot grids
    ax.tick_params(axis='y',which='both',right=True) 
    ax.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True)
    ax.spines['bottom'].set_visible(False)
    
ax3.text(6.68, 200 , '1999-2001' , fontsize=legsize, bbox={'facecolor': cols[2], 'alpha': 0.3, 'pad': 4})
'1999-2001'   
ax3.set_ylabel('Count', fontsize=fsize)
ax3.yaxis.set_label_coords(yloc1[0], yloc1[1])    

#Plot IIML subset bars
barrange=[]
for a in range(len(bins)-1):
    barrange.append(a*(lwidth*1.0))
ax6.bar(barrange, area17, color=cols[1], width=lwidth, edgecolor=cols[0])
ax6.tick_params(direction='out', pad=tickpad)
ax6.set_xlabel(r'Area bin (km$^2$)', fontsize=fsize)

# ax1.yaxis.set_label_coords(yloc1[0], yloc1[1])
ax6.set_ylim(0, 250)
ax6.set_yticks([0,50,100,150,200,250]) 
ax6.set_yticklabels(['0','50','100','150','200',''], fontsize=labsize)
ax6.text(6.65, 200 , '2017 (IIML)' , fontsize=legsize, bbox={'facecolor': cols[1], 'alpha': 0.3, 'pad': 4})

# #Set primary x axis 
ax6.set_xlim(barrange[1]-(lwidth/2), barrange[-1]+(lwidth/2))
ax6.set_xticks(barrange[1:]) 
labels=['0.05-0.15','0.15-0.25','0.25-0.35',
        '0.35-0.45','0.45-0.55', '0.55-0.65','0.65-0.75','0.75-0.85',
        '0.85-0.95','0.95-1.05','1.05<']
ax6.set_xticklabels(labels, fontsize=labsize, wrap=True)    
ax6.set_axisbelow(True)
ax6.yaxis.grid(True)
ax6.tick_params(axis='y',which='both',right=True) 
# ax1.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False) 
# ax1.spines['bottom'].set_visible(False)


#Save plot
plt.subplots_adjust(left=0.11, bottom=0.24, right=0.90, top=0.90, wspace=0.2, hspace=0)
plt.savefig(r'P:\B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland\B71-05 Product validation and user assessment\publication\figures\old\west_histogram.png', dpi=300)
plt.show()