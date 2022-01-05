# -*- coding: utf-8 -*-
'''

Script for unzipping satellite image files. The scripts finds zip files in a
given input directory and unzips them to a structured location based on the 
type of product. If a product already exists in an output directory then the 
overwrite flag denotes whether it will be overwritten or not (True = 
overwritten; False = not overwritten).

Sentinel-2 imagery:
File structure: S2 >> tile >> row >> date 
Notes: L1C products are stored in this file directory, with .jp2 files stored 
directly here and others contained in a folder called 'ESA'. L2A products are 
stored in an additional folder called 'L2A'. Each product is stored with a text 
file called 'INFO' that contains 
1. The original zip file location
2. The date and time it was unzipped
3. Who unzipped it
4. Image details - satellite, product level, acquisition date and time, 
   baseline number, relative orbit number, tile number, product discriminator

@author: Penelope How
'''

# Import libraries
import os
import tarfile
from datetime import datetime
from pathlib import Path


#------------------------------------------------------------------------------

# Set input directory
in_dir = 'C:/Users/how/Downloads'
#in_dir = 'P:/B35_Remote_Sensing/B35-19 SandRockflourMapping/feltarbejde/Sentinel-2'
out_dir = 'D:/data'
overwrite=False

#List all zip files
in_dir=Path(in_dir)
out_dir=Path(out_dir)

folders = list(in_dir.glob('L*.tar.gz'))
print('\n\nCommencing file extraction from ' + str(len(list(folders))) + 
      ' zip folders')

#File count
count = 1


#Iterate through products
count=1
for scene in folders:
    print('\nProduct ' + str(count) + '. Preparing to unzip ' + 
          str(scene))

    #Get product name and components
    info1 = str(scene.name).split('_')  
    fname = str(scene.name)
    
    #Define filepath for downloaded product and unzipped dataset
    pathout1 = Path(out_dir).joinpath('Landsat', info1[2][0:3], info1[2][3:], 
                  info1[3])
    pathout2 = Path(in_dir).joinpath(str(fname))
        
          
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
     
    count=count+1
    
    #Remove zip file
    print('Removing ' + str(pathout2))
    try:
        os.remove(str(pathout2))
        print('File successfully removed\n')  
    except:
        print('File could not be removed, check permissions\n')                      

#------------------------------------------------------------------------------