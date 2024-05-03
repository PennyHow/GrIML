# -*- coding: utf-8 -*-

import numpy as np
import geopandas as gp
from scipy import stats


def method_stats(infile1, infile2, outfile): 
    '''Calculate general statistics on a lake inventory file
    
    Parameters
    ----------
    infile1 : str
        File path to lake geodataframe
    infile2 : str
        File path to basin (as polygons) geodataframe
    outfile : str
        Outputted file name for general statistics
    '''

    print('\nLoading geodataframes...')    
    
    #Read file as geopandas index
    geofile = gp.read_file(infile1)
    basinfile = gp.read_file(infile2)
    agg_geofile = geofile.dissolve(by='unique_id')
   
    
    print('\nRetrieving basin area data...')
    
    #Get basin info        
    basinfile.sort_values('Subregion')
    basinfile['area'] = basinfile['geometry'].area/10**6                    
    basinfile_name = basinfile['Subregion'].tolist()
    

    print('\nAggregating lake data...')
    
    #Get data from columns
    agg_geofile['area'] = agg_geofile['geometry'].area
    agg_geofile['length'] = agg_geofile['geometry'].length
    agg_geofile.sort_values('drainageba')  
    aggfile_basin = agg_geofile['drainageba'].tolist()    #Get lake location
    aggfile_area = agg_geofile['area'].tolist()           #Get lake area
    aggfile_sat = agg_geofile['all_src'].tolist()      #Get lake source
    
    aggfile_areakm = []
    for i in aggfile_area:
        aggfile_areakm.append(i/10**6)
    
    #Get all lake data for basins
    aggfile_CW=[]
    aggfile_CE=[]
    aggfile_ICECAP=[]
    aggfile_NE=[]
    aggfile_NO=[]
    aggfile_NW=[]
    aggfile_SE=[]
    aggfile_SW=[]
    label=['CW', 'CE', 'IC', 'NE', 'NO', 'NW', 'SE', 'SW']
    aggfile_arealist=[aggfile_CW,aggfile_CE, aggfile_ICECAP,aggfile_NE,aggfile_NO,aggfile_NW,
                       aggfile_SE,aggfile_SW]
    for i in range(len(aggfile_basin)):
        for l in range(len(label)):
            if label[l] in aggfile_basin[i]:
                aggfile_arealist[l].append(aggfile_areakm[i])
    
    
    #Get all lake data for basins, rounded
    aggfiler_CW = [round(n, 2) for n in aggfile_CW]
    aggfiler_ICECAP = [round(n, 2) for n in aggfile_ICECAP]
    aggfiler_NE = [round(n, 2) for n in aggfile_NE]
    aggfiler_NO = [round(n, 2) for n in aggfile_NO]
    aggfiler_NW = [round(n, 2) for n in aggfile_NW]
    aggfiler_SE = [round(n, 2) for n in aggfile_SE]
    aggfiler_SW = [round(n, 2) for n in aggfile_SW]
    aggfile_arealist_round=[aggfiler_CW,aggfiler_ICECAP,aggfiler_NE,aggfiler_NO,aggfiler_NW,
                            aggfiler_SE,aggfiler_SW]            
                
    #Get all lake data for basins
    aggsat_CW=[]
    aggsat_CE=[]
    aggsat_ICECAP=[]
    aggsat_NE=[]
    aggsat_NO=[]
    aggsat_NW=[]
    aggsat_SE=[]
    aggsat_SW=[]
    aggfile_satlist=[aggsat_CW,aggsat_CE,aggsat_ICECAP,aggsat_NE,aggsat_NO,aggsat_NW,
                       aggsat_SE,aggsat_SW]
    for i in range(len(aggfile_sat)):
        for l in range(len(label)):
            if label[l] in aggfile_basin[i]:
                aggfile_satlist[l].append(aggfile_sat[i])
    
    
    print('Writing method stats to file...')
    
    #Open stats file    
    f = open(outfile, 'w+')
    
    f.write('Basin, Total no. lakes,Average lake area (km), Median lake area (km),'+
            'Mode lake area (w/ count),Standard deviation,Total lake area (km),S1, S1%, S2, S2%, ADEM, '+
            'ADEM%, S1 S2, S1 S2%, S1 ADEM, S1 ADEM%, S2 ADEM, S2 ADEM%, All, '+
            ' All%' + '\n')
    
    for i in range(len(basinfile_name)):
        f.write(str(basinfile_name[i]) + ',' +                                     #Basin name
                str(aggfile_basin.count(label[i])) + ',' +                         #Unique lakes
                str(np.average(aggfile_arealist[i])) + ',' +                       #Aver. lake area
                str(np.median(aggfile_arealist[i])) + ',' +                        #Median lake area
                str(stats.mode(aggfile_arealist_round[i]).mode[0]) + ' (' + 
                str(stats.mode(aggfile_arealist_round[i]).count[0]) + '),' +       #Mode lake area
                str(np.std(aggfile_arealist[i])) + ',' +                           #Standard deviation
                str(sum(aggfile_arealist[i])) + ',' +                              #Total lake area
                str(aggfile_satlist[i].count('S1')) + ',' + str(round((aggfile_satlist[i].count('S1')/aggfile_basin.count(label[i]))*100,2)) + '%,' +
                str(aggfile_satlist[i].count('S2')) + ',' + str(round((aggfile_satlist[i].count('S2')/aggfile_basin.count(label[i]))*100,2)) + '%,' +
                str(aggfile_satlist[i].count('ArcticDEM')) + ',' + str(round((aggfile_satlist[i].count('ArcticDEM')/aggfile_basin.count(label[i]))*100,2)) + '%,' +
                str(aggfile_satlist[i].count('S2, S1')) + ',' + str(round((aggfile_satlist[i].count('S2, S1')/aggfile_basin.count(label[i]))*100,2)) + '%,' +
                str(aggfile_satlist[i].count('ArcticDEM, S1')) + ',' + str(round((aggfile_satlist[i].count('ArcticDEM, S1')/aggfile_basin.count(label[i]))*100,2)) + '%,' +
                str(aggfile_satlist[i].count('S2, ArcticDEM')) + ',' + str(round((aggfile_satlist[i].count('S2, ArcticDEM')/aggfile_basin.count(label[i]))*100,2)) + '%,' +
                str(aggfile_satlist[i].count('S2, ArcticDEM, S1')) + ',' + str(round((aggfile_satlist[i].count('S2, ArcticDEM, S1')/aggfile_basin.count(label[i]))*100,2)) + '%\n')
    
    f.close()    


if __name__ == "__main__": 

    workspace1 = '/home/pho/python_workspace/GrIML/other/'
    file1 = workspace1 + 'iml_2017/metadata_vectors/griml_2017_inventory_final_first_intervention.shp'
    file2 = workspace1 + 'datasets/drainage_basins/Greenland_Basins_PS_merged_aru_v1.4.2.shp'
    outtxt = workspace1 + 'iml_2017/metadata_vectors/method_stats.csv'

    method_stats(file1, file2, outtxt)
