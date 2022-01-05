# -*- coding: utf-8 -*-
"""
Script for downloading Sentinel imagery in batch from SchiHub and unzipping to
a given destination in a structured folder system. Run in the 
command line by typing the following (making sure you have sentinelsat 
installed in your Python environment).

python getsentinel2.py --aoi "file.geojson"/tile-list --date1 "yyyymmdd"
--date2 "yyyymmdd"

@author: PENELOPE HOW, adapted from KIRSTY LANGLEY
"""

#Import packages needed
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from urllib.request import urlopen, HTTPError, URLError
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
import argparse
import requests
import zipfile
import shutil
import glob
import sys
import os

sys.path.append('.')

#------------------------------------------------------------------------------
#Activate parser and parser arguments
parser = argparse.ArgumentParser(description='A script to download Sentinel-2 ' 
                                 + 'scenes in batch based on an inputted AOI,'+
                                 ' and unzip them to a structured folder ' +
                                 'system')

parser.add_argument('--aoi', required=True, type=str, help='Filepath to ' +
                    'geojson polygon denoting the area of interest, or list' +
                    'of tile identifiers')

parser.add_argument('--date1', required=True, type=str, 
                    help='Start date for Sentinel scenes, yyyymmdd')

parser.add_argument('--date2', required=True, type=str,
                    help='End date for Sentinel scenes, yyyymmdd')

parser.add_argument('--loc1',  default=Path(__file__).parent.absolute(),
                    type=str,
                    help='Directory (folder location) for downloaded files')

parser.add_argument('--loc2',  default="G:/Satellitdata/S2", type=str,
                    help='Directory (folder location) for unzipped files')

parser.add_argument('--cloud', default=None, type=str, 
                    help='Cloud cover percentage range. E.g. (0,0.5) denotes ' +
                    'a percentage range of 0 to 50%')

parser.add_argument('--user', default="guest", type=str, 
                    help='SciHub username')

parser.add_argument('--pswrd', default="guest", type=str,
                    help='SciHub password')

parser.add_argument('--prod', default="S2MSI1C", type=str, 
                    help='Product type')

parser.add_argument('--over', default=False, type=bool, help='Flag denoting ' +
                    'if unzipped files will overwrite pre-existing files')

parser.add_argument('--offline', default=False, type=bool,
                    help='Flag denoting if offline products will be requested'+
                    ' from the Sentinel LTA archive')

#Retrieve arguments
args = parser.parse_args()

#Retrieve AOI file or tile identifier list    
if args.aoi[-7:] in ['geojson']:
    json = args.aoi
    tiles = None
else: 
    tiles = args.aoi
    tiles = tiles.split(',')
    json = None

#Retrieve cloud percentages as tuples if specified
cloud = args.cloud
if cloud is not None:
    cloud = tuple(cloud.split(','))
    
#Retrieve other variables
start = args.date1
end = args.date2
output1 = args.loc1
output2 = args.loc2
user = args.user
password = args.pswrd
product = args.prod
overwrite = args.over
offline = args.offline

#------------------------------------------------------------------------------

#Begin procedure
print('Commencing Sentinel product retrieval and download from SciHub \n\n')

#Log on to SciHub
print('Logging onto SchiHub...')
api = SentinelAPI(user, password, 'https://scihub.copernicus.eu/dhus')
print('Login successful\n\n')

#Gather products to download from aoi
if tiles is None:
    
    #Load geojson file
    print('Loading AOI from geojson file: ' + str(json))
    footprint = geojson_to_wkt(read_geojson(json))
    print('AOI loaded\n\n')
    
    print('Retrieving Sentinel products from geojson file ...')
    if cloud is not None:
        products = api.query(footprint, date=(start, end), platformname="Sentinel-2",
                             producttype= product, cloudcoverpercentage = cloud)
    else:
        print('Cloud cover percentage not specified')
        products = api.query(footprint, date=(start, end), platformname="Sentinel-2",
                             producttype= product)

#Gather products to download from tiles
elif json is None:
    print('Retrieving Sentinel products from tile identifiers: ' + str(tiles)) 
    products = OrderedDict()
    for t in tiles:
        if cloud is not None:
            p = api.query(tileid=t, date=(start, end), platformname="Sentinel-2",
                          producttype= product, cloudcoverpercentage = cloud)
        else:
            print('Cloud cover percentage not specified')
            p = api.query(tileid=t, date=(start, end), platformname="Sentinel-2",
                          producttype= product)
        products.update(p)
        

#Exit program if no products retrieved
if len((list(products.keys())))==0:
    sys.exit('No products retrieved. Check input parameters')

#Compile keys and file titles
keys = list(products.keys())
titles=[]
idx = list(products.values())
for i in idx:
    titles.append(i['title'])
print(str(len(titles)) + ' products retrieved')

#Iterate through products
count=1
for k,t in zip(keys, titles):
    print('\nProduct ' + str(count) + '. Preparing to download ' + str(t))
    
    #Check if product already exists if overwrite flag is false
    exists=False
    if overwrite is False:    
        info = str(t).split('_')  
        if info[0] in ['S2A', 'S2B']:
            fname=info[0]+'_'+info[1][-3:]+'_'+info[5]+'_'+info[4]+'_'+info[2][:8]+'_B01.jp2'
            if info[1] in ['MSIL1C']:
    
                pathout = Path(output2).joinpath('S2', info[5], info[4], 
                                                  str(info[2].split('T')[0]), 
                                                  fname)                    
            elif info[1] in ['MSIL2A']:
                pathout = Path(output2).joinpath('S2', info[5], info[4], 
                                                  str(info[2].split('T')[0]),
                                                  info[1][-3:], fname)                         
        elif info[0] in ['S1A', 'S1B']:
            fname = t
            pathout = Path(output2).joinpath('S1', info[1], info[2], 
                                              str(info[5].split('T')[0]), info[7],
                                              t) 
        if os.path.isfile(str(pathout)) is True: 
            exists=True

    if exists is False:
        print('Downloading to ' + str(output1))
        productinfo = api.get_product_odata(k, full=True)
        if productinfo['Online']:
            api.download(k, str(output1))
            t = str(t)+'.zip'
        else:
            print('Product is not online. Attempting to retrieve file from ' +
                  'Google Cloud repository...')

            #Construct URL and check if it is valid  
            t = str(t)+'.SAFE'
            url='http://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/' + str(info[5][1:3]) + '/' + str(info[5][3]) + '/' + str(info[5][-2:]) + '/' + str(t)
                
            #Retrieve manifest file from URL
            print('Retrieving product from ' + str(url))
            img = os.path.basename(url)
            target_path = os.path.join(str(output1), img)
            target_manifest = os.path.join(target_path, "manifest.safe")
            if not os.path.exists(target_path):
                os.makedirs(target_path)
                manifest_url = url + "/manifest.safe"
                try:
                    content = urlopen(manifest_url)
                except HTTPError as error:
                    print("Error downloading {} [{}]".format(url + 
                          rel_path, error))
                    continue   
                with open(target_manifest, 'wb') as f:
                    shutil.copyfileobj(content, f)
                    
                #Open manifest file and retrieve file URL list
                with open(target_manifest, 'r') as manifest_file:
                        manifest_lines = manifest_file.read().split()
                for line in manifest_lines:
                    if 'href' in line:
                        rel_path = line[7:line.find("><") - 2]
                        abs_path = os.path.join(target_path, 
                                                *rel_path.split('/')[1:])
                        if not os.path.exists(os.path.dirname(abs_path)):
                            os.makedirs(os.path.dirname(abs_path))
                            
                        #Download file from URL
                        try:
                            with requests.get(url+rel_path, stream=True) as r:
                                with open(abs_path, 'wb') as f:
                                    shutil.copyfileobj(r.raw, f) 
                        except HTTPError as error:
                            print("Error downloading {} [{}]".format(url + 
                                    rel_path, error))
                            continue                   
                
                #Populate image band files
                image_name = os.path.basename(target_path)
                tile = image_name.split("_")[5]
                list_dirs = os.listdir(os.path.join(target_path, 'GRANULE'))
                match = [x for x in list_dirs if x.find(tile) > 0][0]
                list_files = os.path.join(target_path, 'GRANULE', match, 'IMG_DATA')
                files = glob.glob(list_files + "/*.jp2")
                match_band = [x for x in files if x.find("B01") > 0][0]
                granule = os.path.dirname(os.path.dirname(match_band))
                
                #Add additional directory
                for extra_dir in ("AUX_DATA", "HTML"):
                    if not os.path.exists(os.path.join(target_path, extra_dir)):
                        os.makedirs(os.path.join(target_path, extra_dir))
                    if not os.path.exists(os.path.join(granule, extra_dir)):
                        os.makedirs(os.path.join(granule, extra_dir))
                if not manifest_lines:
                    print()
                                                    
    else:
        print('Files already exist at ' + str(pathout.parent))
        print('Moving to next Sentinel product')
        count=count+1
        continue
        
    count=count+1

        
#------------------------------------------------------------------------------
    
    #Re-format filepath to Path object
    truepath = Path(output1).joinpath(str(t))
         
    #Split filename to obtain useful info
    info = str(truepath.name).split('_')
    
    #If product is Sentinel-2A or 2B
    if info[0] in ['S2A', 'S2B']:
        print('Sentinel-2 file detected at ' + str(truepath.name))
        
        #Construct L1C output file path
        if info[1] in ['MSIL1C']:  
            pathout = Path(output2).joinpath('S2', info[5], info[4], 
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
                        continue
                    elif overwrite == True:
                        print('Proceeding to overwrite files')
        
        #Construct L2A output file path
        elif info[1] in ['MSIL2A']:
            pathout = Path(output2).joinpath('S2', info[5], info[4], 
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
        discrim = info[6].split('.zip')[0]
        discrim = discrim.split('.SAFE')[0]
        f.write('Product discriminator: ' +str(discrim))        
        f.close()

        #Print statement to check output
        print('Textfile saved to ' + str(pathout))

        #Get all elements if folder is zipped        
        if '.zip' in str(truepath.suffix):

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
            
        #Get all elements if folder is .SAFE
        elif '.SAFE' in str(truepath.suffix):            
            print(pathout) 
            other1=pathout.joinpath('ESA')
            os.mkdir(other1)                    
            allpaths = list(truepath.rglob('*'))                    

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


            #Print statement to check output
            print('Moved to: ' + str(pathout))   
            
        #Remove zip file
        print('Removing ' + str(truepath))
        try:
            os.remove(str(truepath))
            print('File successfully removed')  
        except:
            print('File could not be removed, check permissions')                      
        
#------------------------------------------------------------------------------
print('\n\nFinished getsentinel2.py')
