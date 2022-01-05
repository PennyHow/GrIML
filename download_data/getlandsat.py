# -*- coding: utf-8 -*-
"""
Script for downloading Landsat imagery (Landsat 5-8) in batch from 
EarthExplorer and unzipping to a given destination in a structured folder 
system. Run in the command line by typing the following (making sure you have 
landsatxplore installed in your Python environment).

python getlandsat.py --latlon "tile-list --date1 "yyyymmdd"
--date2 "yyyymmdd"

@author: PENELOPE HOW
"""

#Import packages needed
from landsatxplore.earthexplorer import EarthExplorer
import landsatxplore.api
from datetime import datetime
from pathlib import Path
import argparse
import tarfile
import sys
import os

sys.path.append('.')

#------------------------------------------------------------------------------
#Activate parser and parser arguments
parser = argparse.ArgumentParser(description='A script to download Landsat ' 
                                 + 'scenes in batch based on an inputted ' +
                                 'latitude and longitude and unzip them to a '+
                                 'structured folder system')

parser.add_argument('--latlon', required=True, type=str, help='Latitude and' +
                    ' Longitude')

parser.add_argument('--date1', required=True, type=str, 
                    help='Start date for Landsat scenes, yyyymmdd')

parser.add_argument('--date2', required=True, type=str,
                    help='End date for Landsat scenes, yyyymmdd')

parser.add_argument('--loc1',  default=Path(__file__).parent.absolute(),
                    type=str,
                    help='Directory (folder location) for downloaded files')

parser.add_argument('--loc2',  default="G:/Satellitdata/LandSat", type=str,
                    help='Directory (folder location) for unzipped files')

parser.add_argument('--cloud', default=None, type=tuple, 
                    help='Cloud cover percentage range. E.g. (0,5) denotes ' +
                    'a percentage range of 0 to 5%')

parser.add_argument('--user', default="USERNAME", type=str, 
                    help='EarthExplorer username')

parser.add_argument('--pswrd', default="PASSWORD", type=str,
                    help='EarthExplorer password')

parser.add_argument('--over', default=False, type=bool, help='Flag denoting ' +
                    'if unzipped files will overwrite pre-existing files')

parser.add_argument('--prodctrl', default=True, type=bool, help='Flag denoting ' +
                    'whether product control is implemented (i.e. OLI/TIRS ' +
                    'combined products will be downloaded only, and no ' +
                    'OLI-only and TIRS-only products will be downloaded)')

#Retrieve arguments
args = parser.parse_args()
   
#Retrieve argument variables
latlon = args.latlon
latlon = latlon.split(',')
start = args.date1
end = args.date2
output1 = args.loc1
output2 = args.loc2
cloud = args.cloud
user = args.user
password = args.pswrd
overwrite = args.over
productcontrol = args.prodctrl

#------------------------------------------------------------------------------

#Begin searching procedure
print('Commencing Landsat product retrieval and download from EarthExplorer \n\n')

#Log on to EarthExplorer API for searching
print('Logging onto EarthExplorer...')
api = landsatxplore.api.API(user, password)
print('Login successful\n\n')

#Request scenes based on search criteria
start = start[0:4] + '-' + start[4:6] + '-' + start[-2:]
end = end[0:4] + '-' + end[4:6] + '-' + end[-2:]
print('Retrieving Landsat products at ' + str(latlon[0]) + ',' + 
      str(latlon[1]) + ' from ' + str(start) + ' to ' + str(end))

product = ['LANDSAT_TM_C1', 'LANDSAT_ETM_C1', 'LANDSAT_8_C1']
total_scenes=[]
for p in product:
    if cloud is not None:
        print('Retrieving products with cloud cover specified at ' + str(cloud))
        scenes = api.search(dataset=str(p), latitude=float(latlon[0]), 
                            longitude=float(latlon[1]), start_date=start, 
                            end_date=end, max_cloud_cover=cloud)
    else:
        scenes = api.search(dataset=str(p), latitude=float(latlon[0]), 
                            longitude=float(latlon[1]), start_date=start, 
                            end_date=end)
    print(str(len(scenes)) +' products retrieved from ' + str(p) + ' dataset')
    if len(scenes)!=0:
        total_scenes.append(scenes)

#Quit download script if no products found
total_scenes_flat = [item for sublist in total_scenes for item in sublist]
if len(total_scenes_flat)==0:
    api.logout()
    sys.exit('No products retrieved. Check input parameters') 

#Print statement for number of products found to download
print('{} total products retrieved\n\n'.format(len(total_scenes_flat)))
api.logout()

#Log on to EarthExplorer for downloading
ee = EarthExplorer(user, password)

#Iterate through products
count=1
for scene in total_scenes_flat:
    print('\nProduct ' + str(count) + '. Preparing to download ' + 
          str(scene['displayId']))

    #Get product name and components
    info1 = str(scene['displayId']).split('_')  
    fname = str(scene['displayId'])

    #Move to next product if sensor type is invalid
    if productcontrol is True:
        if info1[0][2:] in '08':
            if info1[0][1] in ['O','T']:
                print('OLI-only product found. Only OLI/TIRS-combined ' +
                      'products will be downloaded. Moving to next product')
                continue
            elif info1[0][1] in ['T']:
                print('TIRS-only product found. Only OLI/TIRS-combined '+
                      'products will be downloaded. Moving to next product')
                continue
            else:
                print('OLI/TIRS-combined product detected. Proceeding to ' +
                      'download protocol')
    
    #Define filepath for downloaded product and unzipped dataset
    pathout1 = Path(output2).joinpath('Landsat', info1[2][0:3], info1[2][3:], 
                  info1[3])
    pathout2 = Path(output1).joinpath(str(fname)+'.tar.gz')
        
    #Check if file has already been downloaded
    exists=False
    if overwrite is False:    
        pathout1_test = Path(pathout1).joinpath(fname+'_B1.tif')
        if os.path.isfile(str(pathout1_test)) is True: 
            exists=True
    
    #Download product if local file does not exist    
    if exists is False:        
        if os.path.exists(str(pathout2)) is True:
            print('Downloaded product found at ' + str(pathout2) + '. ' +
                  'Preparing to unzip')
        else:            
            print('Downloading to ' + str(pathout2))
            ee.download(scene_id=scene['entityId'], output_dir=output1)
        count=count+1
    
    #Move to next product if local version already exists
    else:
        print('Files already exist at ' + str(pathout1))
        print('Moving to next Landsat product')
        count=count+1
        continue        
     
    #Split filename to obtain useful info
    info2 = fname.split('_')    
            
    #Create path if it doesn't exist
    if not os.path.exists(pathout1):
        os.makedirs(pathout1)
        print('\nMaking new directory: ' + str(pathout1))
                
    #If path exists, check which product exists
    else:
        if overwrite == False:
            print('\nOriginal files will not be overwritten. ' +
                  'Moving to next zip file')  
            continue
        elif overwrite == True:
            print('\nProceeding to overwrite files')
        
    #Construct text file
    f=open(pathout1.joinpath('INFO.txt'), 'w')
    f.write('SCENE INFORMATION\n\n')
    f.write('Original file location: ' + str(pathout2) + '\n')
    f.write('Unzipped on ' + str(datetime.now()) + ' by ' + str(os.getlogin()) 
            + '\n\n')
    f.write('Satellite: Landsat ' + str(info2[0][2:]) + '\n')          
    if 'C' in info2[0][1]:
        f.write('Sensor: OLI/TRS combined \n')
    elif 'O' in info2[0][1]:
        f.write('Sensor: OLI-only \n')
    elif 'T' in info2[0][1]:
        f.write('Sensor: TIRS-only \n')
    elif 'E' in info2[0][1]:
        f.write('Sensor: ETM+ \n')
    elif 'M' in info2[0][1]:
        f.write('Sensor: MSS \n')
    else:
        f.write('Sensor: Unknown identifier')        
    f.write('Processing correction level: ' + str(info2[1]) + '\n')    
    f.write('Acquisition date: ' + str(info2[3]) + '\n')
    f.write('Processing date: ' + str(info2[4]) + '\n')    
    f.write('WRS path number: ' + str(info2[2][0:3]) + '\n')
    f.write('WRS row number: ' + str(info2[2][3:]) + '\n')    
    f.write('Collection number: ' + str(info2[5]) + '\n')
    if 'RT' in info2[6]:
        f.write('Collection category: Real-Time \n')
    elif 'T1' in info2[6]:
        f.write('Collection category: Tier 1 \n')
    elif 'T2' in info2[6]:
        f.write('Collection category: Tier 2 \n')               
    f.close()
    
    #Print statement to check output
    print('Textfile saved to ' + str(pathout1))
    
    #Extract all elements from tar folder       
    if '.gz' in str(pathout2.suffix):
        tf=tarfile.open(pathout2, 'r')
        for member in tf.getmembers():
            pathname = Path(member.name)            
            if pathname.suffix=='.TIF':
                tarpath = member.name
            else:
                tarpath = Path('LS').joinpath(str(member.name))            
            member.path = str(tarpath)           
            tf.extract(member, pathout1)       
        tf.close()
    
        #Print statement to check output
        print('Unzipped to ' + str(pathout1))    
              
    #Remove zip file
    print('Removing ' + str(pathout2))
    try:
        os.remove(str(pathout2))
        print('File successfully removed\n')  
    except:
        print('File could not be removed, check permissions\n')                      
        

#Log out of EarthExplorer
ee.logout()

#------------------------------------------------------------------------------
print('\n\nFinished getlandsat.py')
