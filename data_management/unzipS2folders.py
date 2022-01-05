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
import zipfile
from datetime import datetime
from pathlib import Path


#------------------------------------------------------------------------------

# Set input directory
in_dir = 'D:/other/VG_articles/satellite_imgs'
#in_dir = 'P:/B35_Remote_Sensing/B35-19 SandRockflourMapping/feltarbejde/Sentinel-2'
out_dir = 'G:/Satellitdata/S2'
overwrite=False

#List all zip files
in_dir=Path(in_dir)
out_dir=Path(out_dir)

folders = list(in_dir.glob('S*.zip'))
print('\n\nCommencing file extraction from ' + str(len(list(folders))) + 
      ' zip folders')

#File count
count = 1

#Iterate through zip files
for fold in folders:
    
    #Re-format filepath to Path object
    truepath = Path(fold)
     
    #Print statement to check input
    print('\nZip file ' + str(count) + '. ' + str(truepath.name))
    
    #Split filename to obtain useful info
    info = str(truepath.name).split('_')
    
    #If product is Sentinel-2A or 2B
    if info[0] in ['S2A', 'S2B']:
        print('Sentinel-2 zip file detected')
        
        #Construct L1C output file path
        if info[1] in ['MSIL1C']:  
            pathout = Path(out_dir).joinpath('S2', info[5], info[4], 
                                              str(info[2].split('T')[0]))             
            #Create path if it doesn't exist
            if not os.path.exists(pathout):
                os.makedirs(pathout)
                print('Making new directory: ' + str(pathout))
                
            #If path exists, check which product exists
            else:
                if len(list(pathout.glob('*')))==1:
                    print('Product level 2A found in directory. Writing ' + 
                          'product level ' + str(info[1][-3:]) + ' to ' + 
                          str(pathout))                    
                else:                    
                    print(str(info[1][-3:]) + ' product already exists at ' + 
                          str(pathout))
                    if overwrite == False:
                        print('Original files will not be overwritten. ' +
                              'Moving to next zip file')  
                        count=count+1
                        continue
                    elif overwrite == True:
                        print('Proceeding to overwrite files')
        
        #Construct L2A output file path
        elif info[1] in ['MSIL2A']:
            pathout = Path(out_dir).joinpath('S2', info[5], info[4], 
                                              str(info[2].split('T')[0]),
                                              info[1][-3:])                     
            #Create path if it doesn't exist
            if not os.path.exists(pathout):
                os.makedirs(pathout)
                print('Making new directory: ' + str(pathout))
                
            #If path exists, overwrite if flag is true
            else:
                print(str(info[1][-3:]) + ' product already exists at ' + 
                      str(pathout))
                if overwrite == False:
                    print('Original files will not be overwritten. Moving ' + 
                          'to next zip file')
                    count=count+1
                    continue
                elif overwrite == True:
                    print('Proceeding to overwrite files')
        
        #If level is unrecognised
        else:
            print('Product level not recognised. Moving to next zip file')
            continue                    
                    
        #Construct text file
        f=open(pathout.joinpath('INFO.txt'), 'w')
        f.write('SCENE INFORMATION\n\n')
        f.write('Original file location: ' + str(truepath) + '\n')
        f.write('Unzipped on ' + str(datetime.now()) + ' by ' + str(os.getlogin()) + '\n\n')
        f.write('Satellite: ' + str(info[0]) + '\n')
        f.write('Product level: ' + str(info[1]) + '\n')
        f.write('Acquisition date: ' + str(info[2].split('T')[0]) + '\n')
        f.write('Acquisition time: ' + str(info[2].split('T')[1]) + '\n')
        f.write('Baseline number: ' + str(info[3]) + '\n')
        f.write('Relative orbit number: ' + str(info[4]) + '\n')
        f.write('Tile number: ' + str(info[5]) + '\n')
        f.write('Product discriminator: ' +str(info[6].split('.zip')[0]))        
        f.close()

        #Print statement to check output
        print('Textfile saved to ' + str(pathout))
        
        #Get all elements in zip folder
        zipdata = zipfile.ZipFile(truepath)
        

        #Iterate through each zipped item
        with zipdata as z:
            for i, f in enumerate(z.filelist): 
                pathname = Path(f.filename)
                               
                #If file name ends with .jp2 extension, unzip in folder
                if pathname.suffix == '.jp2':
                    if info[1] in ['MSIL1C']:  
                        zippath = '\S' + str(info[0][1:3]) + '_' + str(info[1][-3:]) + '_' + info[5] + '_' + info[4] + '_' + str(info[2].split('T')[0]) + '_' + str(pathname.name[-7:])
                    elif info[1] in ['MSIL2A']:
                        zippath = '\S' + str(info[0][1:3]) + '_' + str(info[1][-3:]) + '_' + info[5] + '_' + info[4] + '_' + str(info[2].split('T')[0]) + '_' + str(pathname.name[-11:])                    
                
                #Else, unzip file to ESA folder
                else:
                    zippath = '\ESA' + f.filename.split('.SAFE')[1].format(i)
                    
                #Redefine item directory in zip folder
                f.filename = str(zippath)
                
                #Extract item to output file path
                z.extract(f, pathout)  
            
            #Close zip folder
            z.close()        
        zipdata.close()
        
        #Print statement to check output
        print('Unzipped to: ' + str(pathout))    
         
        #Update file counter
        count=count+1

        
    #If product is Sentinel-1A or 1B
    elif info[0] in ['S1A', 'S1B']:
        print('Sentinel-1 zip file detected')     
      
        #Construct output file path
        pathout = Path(out_dir).joinpath('S1', info[1], info[2], str(info[5].split('T')[0]), info[7]) 

        if not os.path.exists(pathout):
            os.makedirs(pathout)
            print('Making new directory: ' + str(pathout))
        else:
            print(str(pathout) + ' already exists. Proceeding to overwrite')
    
        f=open(pathout.joinpath('INFO.txt'), 'w')
        f.write('SCENE INFORMATION\n\n')
        f.write('Original file location: ' + str(truepath) + '\n')
        f.write('Unzipped on ' + str(datetime.now()) + ' by ' + str(os.getlogin()) + '\n\n')
        f.write('Satellite: ' + str(info[0]) + '\n')
        f.write('Acquisition mode: ' + str(info[1]) + '\n')
        f.write('Product type: ' + str(info[2]) + '\n')
        f.write('Processing level: ' + str(info[4][0]))
        f.write('Product class: ' + str(info[4][1]))
        f.write('Polarisation: ' + str(info[4][2]))
        f.write('Acquisition start date: ' + str(info[5].split('T')[0]) + '\n')
        f.write('Acquisition start time: ' + str(info[5].split('T')[1]) + '\n')        
        f.write('Acquisition end date: ' + str(info[6].split('T')[0]) + '\n')
        f.write('Acquisition end time: ' + str(info[6].split('T')[1]) + '\n')         
        f.write('Absolute orbit number: ' + str(info[7]) + '\n')
        f.write('Mission Data Take ID: ' + str(info[8]) + '\n')
        f.write('Product Unique ID: ' +str(info[9].split('.zip')[0]))        
        f.close()

        # Print statement to check output
        print('Textfile saved to ' + str(pathout))
        
        # Get all elements in zip folder
        zipdata = zipfile.ZipFile(truepath)
        
        #Iterate through each zipped item
        with zipdata as z:
            for i, f in enumerate(z.filelist):
                
                #Redefine item directory in zip folder
                f.filename = f.filename.split('.SAFE')[1].format(i)
                
                #Extract item to output file path
                z.extract(f, pathout)    
            
            #Close zip folder
            z.close()
        
        zipdata.close()
        
        # Print statement to check output
        print('Unzipped to: ' + str(pathout))    
         
        # Update file counter
        count=count+1
       
    else:
        print('Formatting of file not recognised. Unable to unzip')
        continue

#------------------------------------------------------------------------------

#Remove downloaded zip files
print('\n\nRemoving downloaded zip files...')

#File count
count = 1

#Iterate through zip files
for fold in folders:
    print('\nRemoving ' + str(fold))
    os.remove(str(fold))
    print('Zip file successfully removed')

#------------------------------------------------------------------------------