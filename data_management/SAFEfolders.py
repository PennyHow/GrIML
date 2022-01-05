# -*- coding: utf-8 -*-
'''

Script for moving and re-structuring SAFE files. The scripts finds SAFE files in a
given input directory, and moves them to a structured location based on the 
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
from datetime import datetime
from pathlib import Path
import shutil

#------------------------------------------------------------------------------

#Set input directory
in_dir = 'C:/Users/how/Downloads/S2A_MSIL1C_20160516T145922_N0202_R125_T22WEV_20160516T150205.SAFE'
out_dir = 'D:/data'
overwrite=False

#List all zip files
in_dir=Path(in_dir)
out_dir=Path(out_dir)

count=1
    
 
#Print statement to check input
print('\nSAFE file ' + str(count) + '. ' + str(in_dir.name))

#Split filename to obtain useful info
info = str(in_dir.name).split('_')

#Create path   
pathout = Path(out_dir).joinpath('S2', info[5], info[4], 
                                  str(info[2].split('T')[0]))             
#Create path if it doesn't exist
if not os.path.exists(pathout):
    os.makedirs(pathout)
    print('Making new directory: ' + str(pathout))
                
#Construct text file
f=open(pathout.joinpath('INFO.txt'), 'w')
f.write('SCENE INFORMATION\n\n')
f.write('Original file location: ' + str(in_dir) + '\n')
f.write('Unzipped on ' + str(datetime.now()) + ' by ' + str(os.getlogin()) + '\n\n')
f.write('Satellite: ' + str(info[0]) + '\n')
f.write('Product level: ' + str(info[1]) + '\n')
f.write('Acquisition date: ' + str(info[2].split('T')[0]) + '\n')
f.write('Acquisition time: ' + str(info[2].split('T')[1]) + '\n')
f.write('Baseline number: ' + str(info[3]) + '\n')
f.write('Relative orbit number: ' + str(info[4]) + '\n')
f.write('Tile number: ' + str(info[5]) + '\n')
discrim = info[6].split('.zip')[0]
discrim = discrim.split('.SAFE')[0]
f.write('Product discriminator: ' +str(discrim))        
f.close()

#Print statement to check output
print('Textfile saved to ' + str(pathout))

other1=pathout.joinpath('ESA')
os.mkdir(other1)                    
allpaths = list(in_dir.rglob('*'))                    

#Copy all directories
for a in allpaths:
    if a.is_dir():
        dirs = Path(str(a).split('SAFE')[-1]).parts[1:]
        other2=other1
        for d in dirs:
            other2 = other2.joinpath(d)
        os.mkdir(other2)

#Copy all files
for a in allpaths:
    if info[1] in ['MSIL1C']:
        if a.suffix == '.jp2':
            fname = 'S' + str(info[0][1:3]) + '_' + str(info[1][-3:]) + '_' + info[5] + '_' + info[4] + '_' + str(info[2].split('T')[0]) + '_' + str(a.name[-7:])
            fname_out = pathout.joinpath(str(fname))
            shutil.copyfile(str(a), str(fname_out)) 
        else: 
            if a.is_file():
                dirs = list(Path(str(a).split('SAFE')[-1]).parts[1:])
                other3=other1
                for d in dirs:
                    other3 = other3.joinpath(d) 
                shutil.copyfile(str(a), str(other3))            
  


#------------------------------------------------------------------------------

#Remove downloaded zip files
print('\n\nRemoving SAFE files from input directory...')

#File count
count = 1

#Iterate through zip files
for fold in folders:
    print('\nRemoving ' + str(fold))
    os.remove(str(fold))
    print('Zip file successfully removed')

#------------------------------------------------------------------------------