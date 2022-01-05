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
workspace = ('D:/python_workspace/ice_marginal_lakes/')

#2017 Inventory subset
inventory = workspace + 'products/glacier_cci_lakes_20200819.shp'

#Inventory time-series
timeseries = workspace + 'carrivick_validation/inventory_timeseries/glaciers_cci_IMLI_rgi05_var_v1.shp'

#Carrivick time steps
carr1 = workspace + 'carrivick_validation/carrivick_lakes/all_carrivick_reproj.shp'
carr2 = workspace + 'carrivick_validation/carrivick_lakes/select_carrivick_reproj.shp'

#West coast mask
mask = workspace + 'carrivick_validation/west_coast_mask.shp'

#DOP GLOF record
dop = workspace + 'carrivick_validation/dop_glof_record/dop_glof_record.csv'

#-------------------------   Load as dataframe   ------------------------------

print('\nLoading geodataframes...')    

#Read file as geopandas index
geofile17 = gp.read_file(inventory)
geofile17 = geofile17.sort_values('LakeID')

#Read time-series
geofile_time1 = gp.read_file(timeseries)
geofile_time1 = geofile_time1.sort_values('date')

#Read Carrivick files where lakes are region-wide
geofile87_18 = gp.read_file(carr1)
geofile_time2 = gp.read_file(carr2)
geofile_time2 = geofile_time2.sort_values('Year')

#Read mask file
geofile_mask = gp.read_file(mask)

#--------------------------   Loading DOP data   ------------------------------

print('\nLoading GLOF dates...')    

#Read file
f=open(dop,'r')      
alllines=[]
for line in f.readlines():
    alllines.append(line)  #Read lines in file             
print('\nDetected ' + str(len(alllines)) + ' from file')
f.close() 

#Print headers
print('\nHeaders for columns:')
print(alllines[0])

#Take all data except headers
alllines = alllines[1:]

#Import data into raw elements
dop_date=[]                         #date, yyyy-mm-dd
dop_lakeid =[]                      #Lake ID
dop_comment =[]                     #Comment
for i in alllines:
    data=i.split(',')
    dop_date.append(dt.datetime.strptime(data[0],'%d/%m/%Y').date())
    dop_lakeid.append(str(data[1]))
    dop_comment.append(str(data[2]))

dop_526=[]
dop_1020=[]
for a,b,c in zip(dop_date, dop_lakeid, dop_comment):
    if b in '526':
        dop_526.append([a, a+timedelta(days=7), c])
    elif b in '1020':
        dop_1020.append([a, a+timedelta(days=7), c])
    else:
        print(b)

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
#geofile17_masked.plot()


#-------------------------   Obtain areas   -----------------------------------

print('\nRetrieving non-ADEM aggregated lake areas...')

source17 = geofile17_masked['Source'].tolist()
id17 = geofile17_masked['LakeID'].tolist()
geom17 = geofile17_masked['geometry'].tolist()

#Retrieve non-ADEM aggregated lake areas
areas=[]
basin17=[]
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
    
    for s in range(len(id_source)):
        flag=False
        if id_source[s] in ['S1','S2']:
            geom_agg.append(id_geometry[s])
            id_agg.append(i)
            flag=True
    
    if flag is False:
        for s in range(len(id_source)):
            if id_source[s] in ['ArcticDEM']:
                geom_agg.append(id_geometry[s])
                id_agg.append(i)          
    
    gf = {'LakeID':id_agg, 'geometry':geom_agg}
    gdf = gp.GeoDataFrame(gf, crs='EPSG:32624')
    
#        if gdf.shape[0]>1:
    gdf = gdf.dissolve(by='LakeID')
    gdf['Area']=gdf['geometry'].area
    id_area = gdf['Area'].tolist()
    areas.append(float(id_area[0]))
                
#Add amended areas to geofile
geofile17_dissolved = geofile17_masked.dissolve(by='LakeID')
geofile17_dissolved['Area1'] = areas

source17 = geofile17_dissolved['DrainageBa'].tolist()
area17 = geofile17_dissolved['Area1'].tolist()

area17_sw=[]
for a,s in zip(area17, source17):
    if s in ['SW','CW']:
        area17_sw.append(a)
     
#iiml_area = [sum(area17)]
#iiml_aver = [np.average(area17)/10**6] 
#iiml_freq = [len(area17)]  
#iiml_date = [dt.date(2017,1,1)]
    
iiml_area = [sum(area17_sw)/10**6]
iiml_aver = [np.average(area17_sw)/10**6]
iiml_freq = [len(area17_sw)]
iiml_date = [dt.date(2017,1,1)]

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
print('Total number of SW lakes in 2017 inventory subset: ' + str(basin17.count('SW')) + '\n')
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


#------------------------   Get time-series stats   ---------------------------

print('\nRetrieving time-series lake stats...')

#Get inventory time-series lake info
cci_id = geofile_time1['lakeid'].tolist()
cci_area = geofile_time1['area'].tolist()
cci_date = geofile_time1['date'].tolist()
cci_source = geofile_time1['sensor'].tolist()

#Get Carrivick time-series lake info
carr_id = geofile_time2['LakeID'].tolist()
carr_yr = geofile_time2['Year'].tolist()
carr_aream = geofile_time2['Area'].tolist()
carr_area = [i/(10**6) for i in carr_aream]
carr_source = geofile_time2['layer'].tolist()

#Function for dividing lake area and year by ID
def filterLakes(lakeid, lakearea, lakeyear, lakesource):
    lake526=[]                                      #Unnamed, above Ilulialup
    lake653=[]                                      #Ilulialup Tasia
    lake770=[]                                      #Russel Lake
    lake1020=[]                                     #Unnamed, sourthernmost
    lake1118=[]                                     #Iluliaqtoq
    for i,a,y,s in zip(lakeid, lakearea, lakeyear, lakesource):
        if i == 526:
            if type(y)==int:
                d = dt.datetime.strptime(str(y),'%Y').date()
                lake526.append([d,a,s])
            else:
                d = dt.datetime.strptime(str(y),'%Y-%m-%d').date()
                lake526.append([d,a,s])
        elif i == 653:
            if type(y)==int:
                d = dt.datetime.strptime(str(y),'%Y').date()
                lake653.append([d,a,s])
            else:
                d = dt.datetime.strptime(str(y),'%Y-%m-%d').date()
                lake653.append([d,a,s])
        elif i == 770:
            if type(y)==int:
                d = dt.datetime.strptime(str(y),'%Y').date()
                lake770.append([d,a,s])
            else:
                d = dt.datetime.strptime(str(y),'%Y-%m-%d').date()
                lake770.append([d,a,s])            
        elif i == 1020:
            if type(y)==int:
                d = dt.datetime.strptime(str(y),'%Y').date()
                lake1020.append([d,a,s])
            else:
                d = dt.datetime.strptime(str(y),'%Y-%m-%d').date()
                lake1020.append([d,a,s])
        else:
            if type(y)==int:
                d = dt.datetime.strptime(str(y),'%Y').date()
                lake1118.append([d,a,s])
            else:
                d = dt.datetime.strptime(str(y),'%Y-%m-%d').date()
                lake1118.append([d,a,s])   
    return [lake526, lake653, lake770, lake1020, lake1118]


out1 = filterLakes(cci_id, cci_area, cci_date, cci_source)
out2 = filterLakes(carr_id, carr_area, carr_yr, carr_source)

def getIndices(mylist, value):
    '''Quick and dirty method for retrieving the list index of a certain 
    value.'''
    return[i for i, x in enumerate(mylist) if x==value] 
    
def aggregateLakes(out1):
    out3=[]
    for o in out1:
        merge=[] 
        dates = [i[0] for i in o]
        area = [i[1] for i in o]
        source = [i[2] for i in o]
        unique_dates = sorted(set(dates))
        for d in unique_dates:
            idx = getIndices(dates, d)
            if len(idx)==1:
                merge.append([dates[idx[0]], area[idx[0]], source[idx[0]]])
            else:
                sumarea=[]
                for x in idx:
                    sumarea.append(area[x])
                merge.append([dates[idx[0]], sum(sumarea), source[idx[0]]])
        out3.append(merge)
    return out3

out3 = aggregateLakes(out1)
out4 = aggregateLakes(out2)


#----------------------   Calculate moving averages   -------------------------

#Calculate moving averages
def calcMoving(a, n=5):
    '''Compute an n period moving average.'''
    a1=np.asarray(a)
    a2=[]    
    for i in a1:
        if i > -1:
            a2.append(i)    
        elif i == 'nan':
            a2.append(np.nan)
    a2=np.asarray(a1)
    a3=np.ma.masked_array(a2,np.isnan(a2))
               
    ret = np.cumsum(a3.filled(0))
    ret[n:] = ret[n:] - ret[:-n]
    counts = np.cumsum(~a3.mask)
    counts[n:] = counts[n:] - counts[:-n]
    ret[~a3.mask] /= counts[~a3.mask]
    ret[a3.mask] = np.nan
    
    return ret
   
#-----------------------------   Plotting   -----------------------------------

#Plot change in lake area through time
print('Plotting change in lake area through time 1...')

#Set plot feature sizes
lwidth=2
dashwidth=0.5
scatwidth1=25
scatwidth2=45
legloc=2
yloc1=[-0.05,0.25]
yloc2=[1.075,0.73]

#Set font sizes
fsize=12
labsize=10
legsize=12

#Set labels
label=['Unnamed lake (526)', 'Iluliallup Tasia (653)', 'Russell Lake (770)', 
       'Unnamed lake (1020)', 'Iluliartoq (1118)']    

#Set GLOF record for select lakes
glofs=[dop_526, None, None, dop_1020, None]
    
#Set colours
lakecol=['#1D0363','#7F5FF5','#4D7EE6','#78D1EB','#16CDA0','#13A825']
  
#Prime figure plot
fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1, figsize=(20,10), sharex=True)

for ax,b,c,l,g in zip([ax1,ax2,ax3,ax4,ax5], out3, out4, label, glofs):
    
    #Get lake time-series
    date1 = [i[0] for i in b]
    area1 = [i[1] for i in b]
    source1=[i[2] for i in b]
    date2 = [i[0] for i in c]
    area2 = [i[1] for i in c]    
#    average = calcMoving(area1, n=10)
    
    date1_2=[]
    area1_2=[]
    area_adem=[]
    colours=[]
    for s in range(len(source1)):
        if source1[s] in ['ERS','ENVISAT']:
            date1_2.append(date1[s])
            area1_2.append(area1[s])
            colours.append(lakecol[0])
        elif source1[s] in ['S1']:
            date1_2.append(date1[s])
            area1_2.append(area1[s])
            colours.append(lakecol[1])
        elif source1[s] in ['LANDSAT_1','LANDSAT_2','LANDSAT_3','LANDSAT_4',
                   'LANDSAT_5','LANDSAT_7','LANDSAT_8']:
            date1_2.append(date1[s])
            area1_2.append(area1[s])
            colours.append(lakecol[2])
        elif source1[s] in ['S2A','S2B','S2']:
            date1_2.append(date1[s])
            area1_2.append(area1[s])
            colours.append(lakecol[3])
        elif source1[s] in 'AERIAL':
            date1_2.append(date1[s])
            area1_2.append(area1[s])
            colours.append(lakecol[4]) 
        elif source1[s] in 'ArcticDEM':
            area_adem.append(area1[s])
        else:
            print(date1[s])
            print(area1[s])
            print(source1[s])

    ax.scatter(date1_2, area1_2, s=scatwidth1, c=colours, label='Time-series')
    ax.hlines(sum(area_adem), dt.date(1970,1,1), dt.date(2020,1,1), 
              colors=lakecol[5], linestyle='dashed', label='ADEM maximum')
    ax.scatter(date2, area2, s=scatwidth2, c='#FF0000', marker='^', label='Carrivick')
    ax.grid()
#    ax.legend(loc=legloc)
    ax.set_ylabel('Area (km' + r'$^2$'+')', fontsize=fsize, labelpad=5)
    
#    if g is not None:
#        print(g)
#        dop_glof1=[date[0] for date in g]
#        dop_glof2=[date[1] for date in g]
#        for a,b in zip(dop_glof1, dop_glof2):
#            ax.axvspan(a, b, alpha=0.5, color='#D79311')

#Y axis range
ax1.set_ylim(0,8)
ax1.set_yticks([0,2,4,6,8]) 
ax1.set_yticklabels(['0.0','2.0','4.0','6.0','8.0'], fontsize=labsize) 
ax2.set_ylim(0,80)
ax2.set_yticks([0,20,40,60,80]) 
ax2.set_yticklabels(['0.0','20.0','40.0','60.0','80.0'], fontsize=labsize)    
ax3.set_ylim(0,1.6)
ax3.set_yticks([0,0.4,0.8,1.2,1.6]) 
ax3.set_yticklabels(['0.0','0.4','0.8','1.2','1.6'], fontsize=labsize)
ax4.set_ylim(0,2)
ax4.set_yticks([0,0.5,1.0,1.5,2]) 
ax4.set_yticklabels(['0.0','0.5','1.0','1.5','2.0'], fontsize=labsize) 
ax5.set_ylim(0,20)
ax5.set_yticks([0,5,10,15,20]) 
ax5.set_yticklabels(['0.0','5.0','10.0','15.0','20.0'], fontsize=labsize) 

#Labels
col='#C3EDF7'
ax1.text(dt.date(1970,6,1), 1, label[0], fontsize=labsize,
         bbox={'facecolor': col, 'alpha': 0.5, 'pad': 5})
ax2.text(dt.date(1970,6,1), 10, label[1],fontsize=labsize,
         bbox={'facecolor': col, 'alpha': 0.5, 'pad': 5})
ax3.text(dt.date(1970,6,1), 0.2, label[2],fontsize=labsize,
         bbox={'facecolor': col, 'alpha': 0.5, 'pad': 5})
ax4.text(dt.date(1970,6,1), 0.25, label[3],fontsize=labsize,
         bbox={'facecolor': col, 'alpha': 0.5, 'pad': 5})
ax5.text(dt.date(1970,6,1), 2.5, label[4],fontsize=labsize,
         bbox={'facecolor': col, 'alpha': 0.5, 'pad': 5})
         
       
#X axis (bottom)
ax5.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax5.set_xlabel('Date', fontsize=fsize)
ax5.set_xlim(dt.date(1970,1,1),dt.date(2020,1,1))
ax5.tick_params(axis="x", labelsize=labsize) 
ticks=[dt.date(1970,1,1), dt.date(1975,1,1), 
       dt.date(1980,1,1),dt.date(1985,1,1),
       dt.date(1990,1,1),dt.date(1995,1,1),
       dt.date(2000,1,1),dt.date(2005,1,1),
       dt.date(2010,1,1),dt.date(2015,1,1),
       dt.date(2020,1,1)]
labels=['1970', '1975', '1980','1985','1990','1995','2000','2005','2010','2015','2020']
ax5.set_xticks(ticks) 
ax5.set_xticklabels(labels, fontsize=labsize)    
ax5.tick_params(direction='out', pad=6)

#X axis (top)
ax1twin = ax1.twiny()
ax1twin.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax1twin.set_xlim(dt.date(1970,1,1),dt.date(2020,1,1))
ax1twin.tick_params(axis="x", labelsize=labsize) 
ax1twin.set_xticks(ticks) 
ax1twin.set_xticklabels(labels, fontsize=labsize)    
ax1twin.tick_params(direction='out', pad=6)

#Add common legend
scatwidth1=10
legend_elements = [Line2D([0], [0], marker='o', color='w', label='ERS/ENVISAT', 
                         markerfacecolor=lakecol[0], markersize=scatwidth1),
                  Line2D([0], [0], marker='o', color='w', label='Sentinel-1', 
                         markerfacecolor=lakecol[1], markersize=scatwidth1),
                  Line2D([0], [0], marker='o', color='w', label='Landsat 1-8', 
                         markerfacecolor=lakecol[2], markersize=scatwidth1),
                  Line2D([0], [0], marker='o', color='w', label='Sentinel-2', 
                         markerfacecolor=lakecol[3], markersize=scatwidth1),
                  Line2D([0], [0], marker='o', color='w', label='Aerial imagery', 
                         markerfacecolor=lakecol[4], markersize=scatwidth1),
                  Line2D([0], [0], color=lakecol[5], ls='dashed', lw=lwidth, 
                         label='ADEM maximum'),
                  Line2D([], [], marker='None', linestyle='None', 
                         label=''),
#                  Line2D([0], [0], color='#D79311', label='Asiaq discharge peak', 
#                         ls='solid', alpha=0.5, lw=10),
                  Line2D([0], [0], marker='^', color='w', label='Carrivick inventory', 
                         markerfacecolor='#FF0000', markersize=scatwidth1)]

ax5.legend(handles=legend_elements, fontsize=legsize, bbox_to_anchor=(0.5, -0.85),
          loc='lower center', ncol=9, edgecolor='black')
     
plt.savefig(workspace + r'timeseries_validation.png', dpi=300)
plt.show()


#-----------------------------   Plotting   -----------------------------------

#Plot change in lake area through time
print('Plotting change in lake area through time 2...')

#Set plot feature sizes
lwidth=2
dashwidth=0.5
scatwidth1=25
scatwidth2=45
legloc=2
yloc1=[-0.05,0.25]
yloc2=[1.075,0.73]

#Set font sizes
fsize=12
labsize=10
legsize=12

#Set labels
label=['Unnamed lake (526)', 'Unnamed lake (1020)']    

#Set GLOF record for select lakes
glofs=[dop_526, dop_1020]
    
#Set colours
lakecol=['#1D0363','#7F5FF5','#4D7EE6','#78D1EB','#16CDA0','#13A825']

#Change number of data lakes
out5 = [out3[0],out3[3]]
out6 = [out4[0],out4[3]]

#Prime figure plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20,10), sharex=True)

for ax,b,c,l,g in zip([ax1,ax2], out5, out6, label, glofs):
    
    #Get lake time-series
    date1 = [i[0] for i in b]
    area1 = [i[1] for i in b]
    source1=[i[2] for i in b]
    date2 = [i[0] for i in c]
    area2 = [i[1] for i in c]    
#    average = calcMoving(area1, n=10)
    
    date1_2=[]
    area1_2=[]
    area_adem=[]
    colours=[]
    for s in range(len(source1)):
        if source1[s] in ['ERS','ENVISAT']:
            date1_2.append(date1[s])
            area1_2.append(area1[s])
            colours.append(lakecol[0])
        elif source1[s] in ['S1']:
            date1_2.append(date1[s])
            area1_2.append(area1[s])
            colours.append(lakecol[1])
        elif source1[s] in ['LANDSAT_1','LANDSAT_2','LANDSAT_3','LANDSAT_4',
                   'LANDSAT_5','LANDSAT_7','LANDSAT_8']:
            date1_2.append(date1[s])
            area1_2.append(area1[s])
            colours.append(lakecol[2])
        elif source1[s] in ['S2A','S2B','S2']:
            date1_2.append(date1[s])
            area1_2.append(area1[s])
            colours.append(lakecol[3])
        elif source1[s] in 'AERIAL':
            date1_2.append(date1[s])
            area1_2.append(area1[s])
            colours.append(lakecol[4]) 
        elif source1[s] in 'ArcticDEM':
            area_adem.append(area1[s])
        else:
            print(date1[s])
            print(area1[s])
            print(source1[s])

    ax.scatter(date1_2, area1_2, s=scatwidth1, c=colours, label='Time-series')
    ax.hlines(sum(area_adem), dt.date(1970,1,1), dt.date(2020,1,1), 
              colors=lakecol[5], linestyle='dashed', label='ADEM maximum')
    ax.scatter(date2, area2, s=scatwidth2, c='#FF0000', marker='^', label='Carrivick')
    ax.grid()
    ax.set_ylabel('Area (km' + r'$^2$'+')', fontsize=fsize, labelpad=5)
    
    if g is not None:
        print(g)
        dop_glof1=[date[0] for date in g]
        dop_glof2=[date[1] for date in g]
        for a,b in zip(dop_glof1, dop_glof2):
            ax.axvspan(a, b, alpha=0.5, color='#D79311')   

#Y axis range
ax1.set_ylim(0,8)
ax1.set_yticks([0,2,4,6,8]) 
ax1.set_yticklabels(['0.0','2.0','4.0','6.0','8.0'], fontsize=labsize) 
ax2.set_ylim(0,2)
ax2.set_yticks([0,0.5,1.0,1.5,2]) 
ax2.set_yticklabels(['0.0','0.5','1.0','1.5','2.0'], fontsize=labsize) 


#Labels
col='#C3EDF7'
ax1.text(dt.date(2005,3,1), 0.5, label[0], fontsize=labsize,
         bbox={'facecolor': col, 'alpha': 0.5, 'pad': 5})
ax2.text(dt.date(2005,3,1), 0.125, label[1],fontsize=labsize,
         bbox={'facecolor': col, 'alpha': 0.5, 'pad': 5})

        
       
#X axis (bottom)
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax2.set_xlabel('Date', fontsize=fsize)
ax2.set_xlim(dt.date(2005,1,1),dt.date(2020,1,1))
ax2.tick_params(axis="x", labelsize=labsize) 
ticks=[dt.date(2005,1,1), dt.date(2006,1,1),dt.date(2007,1,1),dt.date(2008,1,1),
       dt.date(2009,1,1),dt.date(2010,1,1),dt.date(2011,1,1),dt.date(2012,1,1),
       dt.date(2013,1,1),dt.date(2014,1,1),dt.date(2015,1,1),dt.date(2016,1,1),
       dt.date(2017,1,1),dt.date(2018,1,1),dt.date(2019,1,1),dt.date(2020,1,1)]
labels=['2005','','2007','','2009','','2011','','2013','',
        '2015','','2017','','2019','']
ax2.set_xticks(ticks) 
ax2.set_xticklabels(labels, fontsize=labsize)    
ax2.tick_params(direction='out', pad=6)

#X axis (top)
ax1twin = ax1.twiny()
ax1twin.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax1twin.set_xlim(dt.date(2005,1,1),dt.date(2020,1,1))
ax1twin.tick_params(axis="x", labelsize=labsize) 
ax1twin.set_xticks(ticks) 
ax1twin.set_xticklabels(labels, fontsize=labsize)    
ax1twin.tick_params(direction='out', pad=6)

#Add common legend
scatwidth1=10
legend_elements = [Line2D([0], [0], marker='o', color='w', label='ERS/ENVISAT', 
                         markerfacecolor=lakecol[0], markersize=scatwidth1),
                  Line2D([0], [0], marker='o', color='w', label='Sentinel-1', 
                         markerfacecolor=lakecol[1], markersize=scatwidth1),
                  Line2D([0], [0], marker='o', color='w', label='Landsat 1-8', 
                         markerfacecolor=lakecol[2], markersize=scatwidth1),
                  Line2D([0], [0], marker='o', color='w', label='Sentinel-2', 
                         markerfacecolor=lakecol[3], markersize=scatwidth1),
                  Line2D([0], [0], marker='o', color='w', label='Aerial imagery', 
                         markerfacecolor=lakecol[4], markersize=scatwidth1),
#                  Line2D([0], [0], marker='o', color='w', label='ADEM', 
#                         markerfacecolor=lakecol[5], markersize=scatwidth1),
                  Line2D([0], [0], color=lakecol[5], ls='dashed', lw=lwidth, 
                         label='ADEM maximum'),
                  Line2D([], [], marker='None', linestyle='None', 
                         label=''),
#                  Line2D([], [], marker='None', linestyle='None', 
#                         label='Validation datasets'),
                  Line2D([0], [0], color='#D79311', label='Asiaq discharge peak', 
                         ls='solid', alpha=0.5, lw=10),
                  Line2D([0], [0], marker='^', color='w', label='Carrivick inventory', 
                         markerfacecolor='#FF0000', markersize=scatwidth1)]

#ax1.legend(handles=legend_elements, bbox_to_anchor=(1.13, 1.03), fontsize=legsize)
##          loc='1', ncol=3)
ax1.legend(handles=legend_elements, fontsize=legsize, bbox_to_anchor=(0.5, -1.5),
          loc='lower center', ncol=9, edgecolor='black')
     
plt.savefig(workspace + r'HKM_lakes_validation.png', dpi=300)
plt.show()

#----------------------------   Plotting 2   ----------------------------------

#Plot change in lake area through time
print('Plotting inventory...')

#Set plot feature sizes
lwidth=0.75
scatwidth=60
tickpad=4
yloc1=[-0.07, 0.5]
yloc2=[1.11, 0.45]
yloc3=[-0.052, 0.45]
cols = ['#2D92BD','#D79311']

#Set font sizes
fsize=12
labsize=10
legsize=12

#Prime figure plot
fig = plt.figure(figsize=(10,10))
ax1 = plt.subplot2grid((12,1), (4,0), rowspan=8, colspan=1)
ax2 = plt.subplot2grid((12,1),(2,0), rowspan=2, colspan=1, sharex=ax1)
ax3 = plt.subplot2grid((12,1),(0,0), rowspan=2, colspan=1, sharex=ax1)

#Plot bars
ax1.bar(range(len(carr_iiml_date)), carr_iiml_freq, color=cols[0], width=lwidth)
ax1.bar([len(carr_iiml_date)], iiml_freq ,color=cols[1], width=lwidth)
ax1.tick_params(direction='out', pad=tickpad)
ax1.set_ylabel('Lake count', fontsize=fsize)
ax1.yaxis.set_label_coords(yloc1[0], yloc1[1])
ax1.set_ylim(0, 1000)
ax1.set_yticks([0,100,200,300,400,500,600,700,800,900,1000]) 
ax1.set_yticklabels(['0','','200','','400','','600','','800','','1000'], 
                    fontsize=labsize)

#Plot scatters on same axis
ax2twin = ax2.twinx()
ax2twin.scatter(range(len(carr_iiml_date)), carr_iiml_area, s=scatwidth, c=cols[0])
ax2twin.scatter([len(carr_iiml_date)], iiml_area, s=scatwidth, c=cols[1])
ax2twin.set_xlim(-1,6)
ax2twin.set_ylim(600, 1100)
ax2twin.set_yticks([600,750,900,1050,1200]) 
ax2twin.set_yticklabels(['600','','900','','1200'], fontsize=labsize)
ax2twin.set_ylabel('Total lake \narea (km' + r'$^2$'+')', fontsize=fsize, rotation=270)
ax2twin.tick_params(direction='out', pad=tickpad)
ax2twin.yaxis.set_label_coords(yloc2[0], yloc2[1])

#Plot scatters on twin axis
ax3.scatter(range(len(carr_iiml_date)), carr_iiml_aver, s=scatwidth, c=cols[0],
            marker='s')
ax3.scatter([len(carr_iiml_date)], iiml_aver, s=scatwidth, c=cols[1], marker='s')
ax3.set_xlim(-1,6)
ax3.set_ylim(1, 2)
ax3.set_yticks([1.0,1.25,1.5,1.75,2.0]) 
ax3.set_yticklabels(['1.0','','1.5','','2.0'], fontsize=labsize)
ax3.set_ylabel('Average lake\narea (km' + r'$^2$'+')', fontsize=fsize)
ax3.tick_params(direction='out', pad=tickpad)
ax3.yaxis.set_label_coords(yloc3[0], yloc3[1])

#Set primary x axis 
ax1.set_xlim(-0.5,5.5)
labels=['','1985-88\nWest inventory','1992-94\nWest inventory',
        '1999-2001\nWest inventory','2004-07\nWest inventory',
        '2009-11\nWest inventory','2017\n inventory subset']
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

#Save plot
plt.subplots_adjust(left=0.11, bottom=0.24, right=0.90, top=0.90, wspace=0.2, hspace=0)
plt.savefig(r'P:\B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland\B71-05 Product validation and user assessment\publication\figures\old\inventory_validation.png', dpi=300)
plt.show()