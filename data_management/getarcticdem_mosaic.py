# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 08:34:05 2020

Script for downloading ArcticDEM scenes

@author: PENNY HOW
"""
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import HTTPError
import sys, os
from datetime import datetime
import wget
import tarfile
import arcpy
from arcpy import env

#Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")
env.overwriteOutput = True

#-------------------------  Operating Functions  ------------------------------   
def checkURL(url):
    '''Check if URL exists'''
    try:
        result=urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

 
def bar_custom(current, total, width=80):
    '''Display download progress bar'''
    progress_message='Downloading : %d%% [%d / %d] bytes' % (current / total * 100, current, total)
    sys.stdout.write('\r'+ progress_message)
    sys.stdout.flush()  


def createINFO(filepath, pathout, product):
    '''Function to generate INFO.txt file for ArcticDEM data.
    
    Variables
    filepath (str):             Filepath to downloaded .tar.gz ArcticDEM file
    pathout (str):              Location for INFO.txt file
    '''
    #Change file directories to Path objects
    filepath=Path(filepath)
    pathout=Path(pathout)
    info = str(filepath.name).split('_')
    
    #Construct text file   
    f=open(pathout.joinpath('INFO.txt'), 'w')
    f.write('SCENE INFORMATION\n\n')
    f.write('Original file location: ' + str(filepath) + '\n')
    f.write('Unzipped on ' + str(datetime.now()) + ' by ' + str(os.getlogin()) 
            + '\n\n')  

    #Write appropriate info based on product type (mosaic or strip)  
    if product in 'mosaic':   
        meta1 = ['Tile identifier (100 km x 100 km): ', 
                 'Tile identifier (50 km x 50 km): ', 'Resolution: ', 
                 'Version: ']
        f.write('Data type: ArcticDEM mosaic \n')  
        if len(info)==6:        
            meta2 = [str(info[0])+'_'+str(info[1]), 
                           str(info[2])+'_'+str(info[3]), info[4], info[5]]
        else: 
            meta2 = [str(info[0])+'_'+str(info[1]), 'NA', info[2], info[3]]
        
        for m1,m2 in zip(meta1, meta2):
            f.write(m1 + m2 + '\n')
    
    elif product in 'strip': 
        meta1 = ['Tile identifier (100 km x 100 km): ', 
                 'Tile identifier (50 km x 50 km): ', 'Resolution: ',
                 'Version: ']
        f.write('Data type: ArcticDEM strip \n')  
       
        meta2 = [str(info[0])+'_'+str(info[1]), 
                           str(info[2])+'_'+str(info[3]), info[4], info[5]]

        
        for m1,m2 in zip(meta1, meta2):
            f.write(m1 + m2 + '\n')
               
    #Print statement to check output directory
    f.close()
    print('Textfile saved to ' + str(pathout))
    
     
def downloadMosaic(version, resolution, tileids, output1, output2, overwrite=False):
    '''Construct ArcticDEM mosaic tile URL from desired parameters and download
    if URL exists.
    
    Variables
    version (str):              DEM mosaic tile version (1, 2 or 3)
    resolution (str):           Resolution of DEM (2m, 10m, 32m, 100m, 500m or
                                1000 m)
    tileids (list):                List of tile identifiers (['XX_YY'])
    output1 (str):              Directory for downloaded zip files
    output2 (str):              Directory for ordered unzipped files
    overwrite (bool):           Flag denoting if files should be overwritten
                                (i.e. download will not occur and overwrite if 
                                files already exist in unzipped directory)
    '''
    mrooturl='http://data.pgc.umn.edu/elev/dem/setsm/ArcticDEM/mosaic/'
    print('Accessing ArcticDEM data from ' + str(mrooturl))
    
    #Create output directory if it doesn't exist
    #Check version compatibility
    if version in ['3','3.0','v3','v3.0']:
        vurl = 'v3.0'
    elif version in ['2','2.0','v2','v2.0']:
        vurl = 'v2.0'
    elif version in ['1','1.0','v1','v1.0']:
        vurl = 'v1.0'
    else:
        sys.exit('Requested mosaic version incorrect (input ' + str(version) 
                 +' not recognised)')

    #Check resolution compatibility
    if resolution in ['2','2m']:
        rurl = '2m'
    elif resolution in ['10','10m']:
        rurl = '10m'
    elif resolution in ['32','32m']:
        rurl = '32m'
    elif resolution in ['100','100m']:
        rurl = '100m'
    elif resolution in ['500','500m']:
        rurl = '500m'
    elif resolution in ['1000','1000m','1km']:
        rurl = '1km'
    else:
        sys.exit('Requested resolution incorrect (input ' + str(resolution) 
                 +' not recognised)')

    count=1
    for tile in tileids:
        
        #Construct url
        url = mrooturl + vurl + '/' + rurl + '/' + tile + '/'
        print('\n' + str(count) + '. Attempting to download files from ' + str(url))
        
        #Check if URL exists, and proceed to download if it does
        if checkURL(url) is False:
            sys.exit('URL does not exist. Amend input parameters and try again')
        else:
            url_list=[]
            if rurl in '2m':
                potential=['1_1','1_2','2_1','2_2']
                for p in potential:
                    out = url + tile + '_' + p + '_' + rurl + '_' + vurl + '.tar.gz'
                    url_list.append(out)
            else:
                out = url + tile + '_' + rurl + '_' + vurl + '.tar.gz'
                url_list.append(out)  
            
            for u in url_list:
                if checkURL(out) is True:
                    if rurl in '2m':
                        tileid = u.split('/')[-1]
                        tileid = tileid.split('_')[2:4]
                        outroot = Path(output2).joinpath('ArcticDEM','MOSAIC',
                                                          vurl,rurl,tile,
                                                          tileid[0]+'_'+tileid[1])
                    else:                         
                        outroot = Path(output2).joinpath('ArcticDEM','MOSAIC', 
                                                          vurl,rurl,tile)                    
                    exists=False
                    if overwrite is False:
                        name1 = u.split('/')[-1]
                        name2 = name1.split('.tar.gz')[0]
                        outroot_file = outroot.joinpath(name2 + '_reg_dem.tif')
                        if os.path.isfile(str(outroot_file)) is True:
                            exists=True
        
                    #Download files if they do not already exist                    
                    if exists is False:
                        print('Downloading file ' + name1)
                        outfile = Path(output1).joinpath(name1)
                        try:
                            wget.download(str(u), str(outfile), bar=bar_custom)
                            print('\nFile downloaded to ' + str(outfile))                            
                            extractTar(outroot, outfile, remove=False)
                            
                        except HTTPError as error:
                            print("\nError downloading {} [{}]".format(url, error))
                            continue 
                                    
                    else:
                        print('File already exists at ' + str(outroot))
                else:
                    print('URL not found: ' + str(u))
        count=count+1
                 

def extractTar(pathout1, pathout2, remove=False):    
    '''Extract all elements from a .tar.gz file to a given file directory. 
    Files are structured as the .tif file in the upper level of the directory,
    then all other files stored in a folder called "ADEM".
    
    Variables 
    pathout1 (str):             Folder path to intended location of extracted 
                                files
    pathout2 (str):             Filepath to zipped files
    remove (bool):              Flag denoting whether zipped filed should be
                                deleted after extraction is complete
    '''
    #Extract all elements from tar folder       
    if '.gz' in str(pathout2.suffix):
        tf=tarfile.open(pathout2, 'r')
        for member in tf.getmembers():
            pathname = Path(member.name)          
            if pathname.suffix=='.tif':
                tarpath = member.name
            else:
                tarpath = Path('ADEM').joinpath(str(member.name))            
            member.path = str(tarpath)           
            tf.extract(member, pathout1)       
        tf.close()
    
        #Print statement to check output
        print('Unzipped to ' + str(pathout1))    
              
    #Remove zip file
    if remove is True:
        print('Removing ' + str(pathout2))
        try:
            os.remove(str(pathout2))
            print('File successfully removed\n')  
        except:
            print('File could not be removed, check permissions\n')              


def getFolders(rootdirectory, datatype, version, tileids, resolution):
    '''Get scene folder directories, based on tile name.
    Args
    scenes (str):           Folder directory where scenes are located.
    
    Returns
    tiles (list):           List of folder directories with specified tiles
    '''
    #Create empty output
    folders=[]
    
    #Create path object from string
    root = Path(rootdirectory)
    
    #Reformat inputs if needed
    if datatype in ['mosaic', 'MOSAIC']:
        datatype='MOSAIC'
    elif datatype in ['strip', 'STRIP']:
        datatype='STRIP'
    else:
        sys.exit('Invalid datatype variable: ' + str(datatype))
    
    if version in ['3.0', '3', 'v3.0', 'v3']:
        version='v3.0'
    elif version in ['2.0', '2', 'v2.0', 'v2']:
        version='v2.0'
    elif version in ['1.0', '1', 'v1.0', 'v1']:
        version='v1.0'
    else:
        sys.exit('Invalid version variable: ' + str(version))

    if resolution in ['2','2m']:
        resolution = '2m'
    elif resolution in ['10','10m']:
        resolution = '10m'
    elif resolution in ['32','32m']:
        resolution = '32m'
    elif resolution in ['100','100m']:
        resolution = '100m'
    elif resolution in ['500','500m']:
        resolution = '500m'
    elif resolution in ['1000','1000m','1km']:
        resolution = '1km'
    else:
        sys.exit('Invalid resolution variable: ' + str(resolution))
        
    #Iterate through tile list
    for t in tileids:
        
        #Merge tile name with directory and check if it exists
        tilepath = root.joinpath('ArcticDEM', datatype, version, resolution, t)

        if tilepath.exists():
            
            #Get all directories in tile folder and append to output
            pathlist = tilepath.glob('*.tif')
            for i in pathlist:
                folders.append(str(i))
                        
        #Print statement if file directory to tiles not found
        else:
            print('Path not found: ' + str(tilepath))
     
    #Return list of folder directories with specified tiles
    return folders            

#---------------------  Input variables and running  --------------------------

#Directory to download to                
download='D:/python_workspace/arcticdem_download/arctic_dem_test_download'

#Directory to unzip files to
output='G:/Satellitdata/ArcticDEM/'
output_mosaic = output + 'ilulissat_mosaic_map_13052020'


#ArcticDEM mosaic version to retrieve
version='3.0'

#ArcticDEM mosaic resolution to retrieve
resolution='2'

#ArcticDEM tile identifier range
row_min = 17
row_max = 19
col_min = 38
col_max = 40

#ArcticDEM tile indentifier constructor
rowrange=list(range(row_min,row_max,1))
colrange = list(range(col_min,col_max,1))
tilelist=[]
for r in rowrange:
    for c in colrange:
        tilelist.append(str(r) + '_' + str(c))
print('Tile identifiers to download: ' + str(tilelist) + '\n')

#Download all ArcticDEM products based on inputs defined above
downloadMosaic(version, resolution, tilelist, download, output)

#Get all downloaded files
print('\nProceeding to merge downloaded files by zone')
files=getFolders(output, 'mosaic', version, tilelist, resolution)


##Sort downloaded files in zones for merging
#zone24=[]
#zone1=[]
#zone2=[]
#zone3=[]
#for f in files:
#    tile_id = str(Path(f).name).split('_')[0:2]
#    if tile_id[0] in ['20','21']:
#        zone24.append(f)
#    elif tile_id[0] in ['17','18','19']:
#        zone1.append(f)
#    elif tile_id[0] in ['14','15','16']:
#        zone2.append(f)    
#    elif tile_id[0] in ['11','12','13']:
#        zone3.append(f) 
#    else:    
#        print('Invalid tile id: ' + str(tile_id[0]) + '_' + str(tile_id[1]))
#zones = [zone24, zone1, zone2, zone3]
#zonenames = ['zone24', 'zone1', 'zone2', 'zone3']

##Merge downloaded files by zones
#if not os.path.exists(output_mosaic):
#    os.makedirs(output_mosaic)
#for z in files:
#    output_name = 'ilulissat_2m_mosaic_13052020.tif' 
#    arcpy.MosaicToNewRaster_management(z, str(output_mosaic), str(output_name), '',
#                                       '32_BIT_FLOAT', '32', '1')
##    'Float32'
##    'EPSG:3413 - WGS 84 / NSIDC Sea Ice Polar Stereographic North - Projected'
#    print('Merged mosaic saved at: ' + str(output_mosaic) + '\\' + str(output_name))