# -*- coding: utf-8 -*-

import numpy as np
import geopandas as gp


def general_stats(geofile, outfile): 
    '''Calculate general statistics on a lake inventory file
    
    Parameters
    ----------
    geofile : gpd.str
        File path to lake dataframe
    outfile : str
        Outputted file name for general statistics
    '''
    
    #Read file as geopandas index
    geofile = gp.read_file(file1)
    agg_geofile = geofile.dissolve(by='unique_id')

    print('\nRetrieving lake data...')
    
    #Get data from columns
    geofile = geofile.sort_values('drainageba')
    geofile_id = geofile['unique_id'].tolist()              #Get lake IDs
    geofile_uncertain = geofile['certainty'].tolist()       #Get lake uncertainty
    geofile_source = geofile['source'].tolist()             #Get lake source
    geofile_basin = geofile['drainageba'].tolist()          #Get lake location
    geofile['area'] = geofile['geometry'].area/10**6
    
    #Get unique values for basin area and satellite source 
    uniquebasin = list(set(geofile_basin))
    uniquesource = list(set(geofile_source))
    
    print('\nAggregating lake data...')
    
    #Get data from columns
    agg_geofile['area'] = geofile['geometry'].area
    agg_geofile['length'] = geofile['geometry'].length
    agg_geofile.sort_values('drainageba')  
    aggfile_basin = agg_geofile['drainageba'].tolist()    #Get lake location
    aggfile_area = agg_geofile['area'].tolist()           #Get lake area
    aggfile_areakm = []
    for i in aggfile_area:
        aggfile_areakm.append(i/10**6)
    
    label=['CW', 'CE', 'IC', 'NE', 'NO', 'NW', 'SE', 'SW']
               
    print('\nWriting general stats file...')
            
    #Open stats file    
    f = open(outtxt1, 'w+')
    
    #Total number of lakes in dataset and total number of unique lakes
    f.write('Total number of detected lakes , ' + str(len(geofile_id)) + '\n')
    f.write('Total number of unique lakes , ' + str(max(geofile_id)) + '\n\n')
    
    #Total lake count for each sector
    for i in range(len(label)):
        f.write(label[i] + ' total lake count , ' + str(geofile_basin.count(label[i])) + '\n')
    f.write('\n')
    
    #Unique lake count for each sector
    for i in range(len(label)):
        f.write(label[i] + ' unique lake count , ' + str(aggfile_basin.count(label[i])) + '\n')
    f.write('\n')
    
    #Source count
    for i in uniquesource:
        f.write('Lakes detected using ' + i + ',' + str(geofile_source.count(i)) + '\n')
    f.write('\n')
    
    #Min, max and average lake area
    f.write('Min. lake area (km), ' + str(min(aggfile_areakm)) + '\n')
    f.write('Max. lake area (km), ' + str(max(aggfile_areakm)) + '\n')
    f.write('Average lake area (km), ' + str(np.average(aggfile_areakm)) + '\n')
    f.write('\n')
    
    #Min, max and average uncertainty
    f.write('Min. uncertainty , ' + str(min(geofile_uncertain)) + '\n')
    f.write('Max. uncertainty , ' + str(max(geofile_uncertain)) + '\n')
    f.write('Average uncertainty , ' + str(np.average(geofile_uncertain)) + '\n\n')
    
    f.close()

if __name__ == "__main__": 
    
    #Define input file and location 
    workspace1 = '/home/pho/python_workspace/GrIML/other/'
    file1 = workspace1 + 'iml_2017/metadata_vectors/griml_2017_inventory_final_first_intervention.shp'
    outtxt1 = workspace1 + 'iml_2017/metadata_vectors/generalstats.csv'
    
    general_stats(file1, outtxt1)
