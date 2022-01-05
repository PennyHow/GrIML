# -*- coding: utf-8 -*-
"""
Created on Thu May 28 09:11:34 2020

@author: HOW
"""

"""
Created on Thu Sep 26 10:27:57 2019

Statistical analysis on ice-marginal lakes (ESA)

@author: Penelope How
"""

import os
import numpy as np
import geopandas as gp
import matplotlib.pyplot as plt

#-----------------------   Define inputs and outputs   ------------------------

#Define input file and location 
workspace1 = 'P:/B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland/B71-04 Essential Climate Variable production/final lake products/'
workspace2 = 'D:/python_workspace/ice_marginal_lakes/'
file1 = workspace1 + 'glacier_cci_lakes_20200819.shp'
file2 = workspace1 + 'other products/GL_basin_areas.shp'
file3 = workspace1 + 'other products/GL_basin_perimeters.shp'

#------------------------ Define counting function   --------------------------

def countSats(nsat, sat):
    '''Count satellite sources'''
    adem = 0
    S1 = 0
    S2 = 0
    ademS1 = 0
    ademS2 = 0
    S1S2 = 0
    allsats = 0
    for n,s in zip(nsat, sat):
        if n==1:
            if s in ['ArcticDEM']:
                adem=adem+1
            elif s in ['S1']:
                S1=S1+1
            elif s in ['S2']:
                S2=S2+1
        elif n==2:
            if s in ['ArcticDEM, S1', 'S1, ArcticDEM']:
                ademS1=ademS1+1
            elif s in ['ArcticDEM, S2', 'S2, ArcticDEM']:
                ademS2=ademS2+1
            elif s in ['S1, S2', 'S2, S1']:
                S1S2=S1S2+1
        elif n==3:
            allsats=allsats+1    
    print('Polygons detected from one source: ' + str(adem+S1+S2) + 
          ' ('+ str(adem) + ' ArcticDEM, ' + str(S1) + ' S1, ' + str(S2) + ' S2)')
    print('Polygons detected from two sources: ' + str(ademS1+ademS2+S1S2) +
          ' (' + str(ademS1) + ' ArcticDEM & S1, ' + str(ademS2) + 
          ' ArcticDEM & S2, ' + str(S1S2) + ' S1 & S2)')
    print('Polygons detected from three sources: ' + str(allsats))
    

def countCatch(drainageba, nsat, certainty):
    sw_cert=[]
    cw_cert=[]
    nw_cert=[]
    no_cert=[]
    ne_cert=[]
    se_cert=[]
    icecap_cert=[]    
    sw_sat=[]
    cw_sat=[]
    nw_sat=[]
    no_sat=[]
    ne_sat=[]
    se_sat=[]
    icecap_sat=[] 
    for d,n,c in zip(drainageba, nsat, certainty):
        if d in 'SW':
            sw_cert.append(c)
            sw_sat.append(n)
        elif d in 'CW':
            cw_cert.append(c)
            cw_sat.append(n)
        elif d in 'NW':
            nw_cert.append(c)
            nw_sat.append(n)
        elif d in 'NO':
            no_cert.append(c)
            no_sat.append(n)
        elif d in 'NE':
            ne_cert.append(c)
            ne_sat.append(n)
        elif d in 'SE':
            se_cert.append(c)
            se_sat.append(n)
        elif d in 'ICE_CAP':
            icecap_cert.append(c)    
            icecap_sat.append(n)   
    print('SW average certainty: ' + str(np.average(sw_cert)))
    print('CW average certainty: ' + str(np.average(cw_cert)))    
    print('NW average certainty: ' + str(np.average(nw_cert)))
    print('NO average certainty: ' + str(np.average(no_cert)))
    print('NE average certainty: ' + str(np.average(ne_cert)))
    print('SE average certainty: ' + str(np.average(se_cert)))
    print('ICECAP average certainty: ' + str(np.average(icecap_cert)) + '\n')

    print('SW: ' + str(sw_sat.count(1)) + ' (1 source, ' + 
          str((sw_sat.count(1)/len(sw_sat))*100) + '%), ' + str(sw_sat.count(2)) +
          ' (2 sources, ' + str((sw_sat.count(2)/len(sw_sat))*100) + '%), ' +
          str(sw_sat.count(3)) + ' (3 sources, ' + 
          str((sw_sat.count(3)/len(sw_sat))*100) + '%)')

    print('CW: ' + str(cw_sat.count(1)) + ' (1 source, ' + 
          str((cw_sat.count(1)/len(cw_sat))*100) + '%), ' + str(cw_sat.count(2)) +
          ' (2 sources, ' + str((cw_sat.count(2)/len(cw_sat))*100) + '%), ' +
          str(cw_sat.count(3)) + ' (3 sources, ' + 
          str((cw_sat.count(3)/len(cw_sat))*100) + '%)')

    print('NW: ' + str(nw_sat.count(1)) + ' (1 source, ' + 
          str((nw_sat.count(1)/len(nw_sat))*100) + '%), ' + str(nw_sat.count(2)) +
          ' (2 sources, ' + str((nw_sat.count(2)/len(nw_sat))*100) + '%), ' +
          str(nw_sat.count(3)) + ' (3 sources, ' + 
          str((nw_sat.count(3)/len(nw_sat))*100) + '%)')
        
    print('NO: ' + str(no_sat.count(1)) + ' (1 source, ' + 
          str((no_sat.count(1)/len(no_sat))*100) + '%), ' + str(no_sat.count(2)) +
          ' (2 sources, ' + str((no_sat.count(2)/len(no_sat))*100) + '%), ' +
          str(no_sat.count(3)) + ' (3 sources, ' + 
          str((no_sat.count(3)/len(no_sat))*100) + '%)')
        
    print('NE: ' + str(ne_sat.count(1)) + ' (1 source, ' + 
          str((ne_sat.count(1)/len(ne_sat))*100) + '%), ' + str(ne_sat.count(2)) +
          ' (2 sources, ' + str((ne_sat.count(2)/len(ne_sat))*100) + '%), ' +
          str(ne_sat.count(3)) + ' (3 sources, ' + 
          str((ne_sat.count(3)/len(ne_sat))*100) + '%)')
        
    print('SE: ' + str(se_sat.count(1)) + ' (1 source, ' + 
          str((se_sat.count(1)/len(se_sat))*100) + '%), ' + str(se_sat.count(2)) +
          ' (2 sources, ' + str((se_sat.count(2)/len(se_sat))*100) + '%), ' +
          str(se_sat.count(3)) + ' (3 sources, ' + 
          str((se_sat.count(3)/len(se_sat))*100) + '%)')
        
    print('ICECAP: ' + str(icecap_sat.count(1)) + ' (1 source, ' + 
          str((icecap_sat.count(1)/len(icecap_sat))*100) + '%), ' + str(icecap_sat.count(2)) +
          ' (2 sources, ' + str((icecap_sat.count(2)/len(icecap_sat))*100) + '%), ' +
          str(icecap_sat.count(3)) + ' (3 sources, ' + 
          str((icecap_sat.count(3)/len(icecap_sat))*100) + '%)') 


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


def getArea3(geofile, txtfile):
    numsat17 = geofile['NumOfSate'].tolist()
    source17 = geofile['Source'].tolist()
    id17 = geofile['LakeID'].tolist()
    geom17 = geofile['geometry'].tolist()
    area17 = geofile['Area'].tolist()

    #Open file    
    f = open(txtfile, 'w+')
    f.write('LakeID, ADEM, S1, S2, diff \n')

    id3=[]
    sou3=[]
    geom3=[]
    area3=[]
    areas=[]
    for i in range(len(numsat17)):
        if numsat17[i] == 2 or 3:
            id3.append(id17[i])
            sou3.append(source17[i])
            geom3.append(geom17[i])
            area3.append(area17[i])

    id3_unique = set(id3)
    for u in id3_unique:
        f.write(str(u) + ',')
        adem=[]
        S1=[]
        S2=[]
        for i in range(len(id3)):
            if id3[i] == u:
                if sou3[i] in ['ArcticDEM']:
                    adem.append(area3[i])
                elif sou3[i] in ['S1']:
                    S1.append(area3[i])
                elif sou3[i] in['S2']:
                    S2.append(area3[i])
                else:
                    print('Unidentified source: ' + str(sou3[i]))
        areas.append([sum(adem),sum(S1),sum(S2)])
        f.write(str(sum(adem)) + ',' + str(sum(S1)) + ',' + str(sum(S2)) + ',')       
        f.write(str(max(areas[-1])-min(areas[-1])) + '\n')
        
    f.close() 
    return areas
                
       
#-------------------------   Load as dataframe   ------------------------------

print('\nLoading geodataframes...')    

#Read file as geopandas index
geofile = gp.read_file(file1)
basinfile = gp.read_file(file2)
extfile = gp.read_file(file3)
agg_geofile = geofile.dissolve(by='LakeID')


#---------------   Get data from non-aggregated lake data  --------------------

print('\nRetrieving non-aggregated lake data...')

#Get data from columns
gfile_nsat = geofile['NumOfSate'].tolist()
gfile_sat = geofile['Satellites'].tolist()
gfile_cert = geofile['Certainty'].tolist()

print('Number of polygons in inventory: ' +str(len(geofile)))         
countSats(gfile_nsat, gfile_sat)

area3=getArea3(geofile, 'D:\python_workspace\ice_marginal_lakes\source_stats.csv')

#-----------------   Get data from aggregated lake data   ---------------------

print('\nRetrieving aggregated lake data...')

#Get data from columns
afile_nsat = agg_geofile['NumOfSate'].tolist()
afile_sat = agg_geofile['Satellites'].tolist()
afile_cert = agg_geofile['Certainty'].tolist()
afile_drain = agg_geofile['DrainageBa'].tolist()
afile_area = agg_geofile['Area'].tolist()
afile_area_sqkm = [a/1000000 for a in afile_area]
     
print('Number of unique lakes in inventory: ' +str(len(agg_geofile)))

countSats(afile_nsat, afile_sat)
countCatch(afile_drain, afile_nsat, afile_cert)

# bins=[0.00,0.06,0.07,0.08,0.09,0.10,0.20,0.30,0.40,0.50,1.0,10.00,200.00,250.00]
bins=[0.00,0.06,0.07,0.08,0.09,0.10,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,
      0.19,0.20,0.21,0.22,0.23,0.24,0.25,0.26,0.27,0.28,0.29,0.30,0.31,0.32,
      0.33,0.34,0.35,0.36,0.37,0.38,0.39,0.40,0.41,0.42,0.43,0.44,0.45,0.46,
      0.47,0.48,0.49,0.5,200.00,250.00]#0.51,0.52,0.53,0.54,0.55,0.56,0.57,0.58,0.59,0.60,200.00,250.00]
# bins=[0.00,0.15,0.25,0.35,0.45,0.55,0.65,0.75,0.85,0.95,1.05,200.00,250.00]
bincount = countArea(afile_area_sqkm, bins)

#----------------   Plot histogram of area distribution   ---------------------

#Plot change in lake area through time
print('Plotting inventory...')

#Set plot feature sizes
lwidth=0.1
scatwidth=60
tickpad=4
yloc1=[-0.07, 0.5]
yloc2=[1.11, 0.45]
yloc3=[-0.052, 0.45]
cols = ['#4E4E4E','#D79311']

#Set font sizes
fsize=13
labsize_x=6
labsize_y=10

# Prime figure plot
fig, (ax1) = plt.subplots(1, 1, figsize=(15,5), sharex=True)

# fig = plt.figure(figsize=(15,10))
# ax1 = plt.subplot2grid((6,1), (0,0), rowspan=2, colspan=1)
# ax2 = plt.subplot2grid((6,1),(2,0), rowspan=2, colspan=1)
# ax3 = plt.subplot2grid((6,1),(4,0), rowspan=2, colspan=1)

#Plot bars
barrange=[]
for a in range(len(bins)-1):
    barrange.append(a*(lwidth*1.0))


ax1.bar(barrange, bincount, color=cols[1], width=lwidth, edgecolor=cols[0])
ax1.tick_params(direction='out', pad=tickpad)
ax1.set_xlabel(r'Area bins (km$^2$)', fontsize=fsize)
ax1.set_ylabel('Count', fontsize=fsize)
# ax1.yaxis.set_label_coords(yloc1[0], yloc1[1])
ax1.set_ylim(0, 700)
ax1.set_yticks([0,100,200,300,400,500,600,700]) 
ax1.set_yticklabels(['0','100','200','300','400','500','600','700'], fontsize=labsize_y)

# #Set primary x axis 
ax1.set_xlim(barrange[1]-(lwidth/2), barrange[-1]+(lwidth/2))
ax1.set_xticks(barrange[1:]) 

labels=['0.05\n-0.06','0.06\n-0.07','0.07\n-0.08','0.08\n-0.09','0.09\n-0.10',
        '0.10\n-0.11','0.11\n-0.12','0.12\n-0.13','0.13\n-0.14','0.14\n-0.15','0.15\n-0.16','0.16\n-0.17','0.17\n-0.18','0.18\n-0.19','0.19\n-0.20',
        '0.20\n-0.21','0.21\n-0.22','0.22\n-0.23','0.23\n-0.24','0.24\n-0.25','0.25\n-0.26','0.26\n-0.27','0.27\n-0.28','0.28\n-0.29','0.29\n-0.30',
        '0.30\n-0.31','0.31\n-0.32','0.32\n-0.33','0.33\n-0.34','0.34\n-0.35','0.35\n-0.36','0.36\n-0.37','0.37\n-0.38','0.38\n-0.39','0.39\n-0.40',
        '0.40\n-0.41','0.41\n-0.42','0.42\n-0.43','0.43\n-0.44','0.44\n-0.45','0.45\n-0.46','0.46\n-0.47','0.47\n-0.48','0.48\n-0.49','0.49\n-0.50',
        '0.50<']
ax1.set_xticklabels(labels, fontsize=labsize_x, wrap=True)    

#Set plot grids
ax1.set_axisbelow(True)
ax1.yaxis.grid(True)

#Set x/y ticks off for other axes
ax1.tick_params(axis='y',which='both',right=True) 
# ax1.tick_params(axis='x',which='both',bottom=False,top=False,labelbottom=False) 
# ax1.spines['bottom'].set_visible(False)

#Save plot
plt.subplots_adjust(left=0.11, bottom=0.24, right=0.90, top=0.90, wspace=0.2, hspace=0)
plt.savefig(r'P:\B71_ESA_Inventory_of_Ice-Marginal_Lakes_in_Greenland\B71-05 Product validation and user assessment\publication\figures\old\area_histogram.png', dpi=300)
plt.show()