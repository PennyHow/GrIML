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
import numpy as np
import geopandas as gp

from bokeh.plotting import figure, save, show
from bokeh.palettes import RdYlBu11 as palette
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper

#-------------------------  Operating Functions  ------------------------------

def getPolyCoords(row, geom, coord_type):
    """Returns the coordinates ('x' or 'y') of edges of a Polygon exterior"""

    # Parse the exterior of the coordinate
    exterior = row[geom].exterior
    if coord_type == 'x':
        # Get the x coordinates of the exterior
        return list( exterior.coords.xy[0] )
    elif coord_type == 'y':
        # Get the y coordinates of the exterior
        return list( exterior.coords.xy[1] )


def getPolyCoords2(df, geom):
    """Returns the coordinates ('x' or 'y') of edges of a Polygon exterior"""
     
    all_coords = []
    for b in df.geometry: # for first feature/row

#        print(b.boundary)
#        print(help(b))
        try:
            xycoords = list(b.boundary)
            print(xycoords)
            coords = np.dstack(b.boundary.xy).tolist()
            all_coords.append(xycoords)
            print('NEW FEATURE')    
        except:
            print('SHAPE NOT PASSED')                 
    
    return(all_coords)
    
    
def tilePicker():
    workspace = 'D:/python_workspace/arcticdem_download/'
    mosaic = gp.read_file(workspace + 'ArcticDEM_Tile_Index_Rel7/ArcticDEM_Tile_Index_GL.shp')
    ice = gp.read_file(workspace + 'ArcticDEM_GL_ice.shp')
    land = gp.read_file(workspace + 'ArcticDEM_GL_land.shp')

    mosaic['x'] = mosaic.apply(getPolyCoords, geom='geometry', coord_type='x', axis=1)
    mosaic['y'] = mosaic.apply(getPolyCoords, geom='geometry', coord_type='y', axis=1)

    icexy = getPolyCoords2(ice, geom='geometry')
    print(icexy)
    sys.exit(1)
#    ice['x'] = ice.apply(getPolyCoords2, geom='geometry', coord_type='x', axis=1)
#    ice['y'] = ice.apply(getPolyCoords2, geom='geometry', coord_type='y', axis=1)    
#
#    land['x'] = land.apply(getPolyCoords2, geom='geometry', coord_type='x', axis=1)
#    land['y'] = land.apply(getPolyCoords2, geom='geometry', coord_type='y', axis=1)   
    
    p_mosaic = mosaic.drop('geometry', axis=1).copy()
    ps_mosaic = ColumnDataSource(p_mosaic)
    
    p_ice = ice.drop('geometry', axis=1).copy()
    ps_ice = ColumnDataSource(p_ice)    

    p_land = land.drop('geometry', axis=1).copy()
    ps_land = ColumnDataSource(p_land)   


    #Initialize our figure
    p = figure(title="ArcticDEM mosaic tiles in Greenland")
    
    color_mapper = LogColorMapper(palette=palette)
    
    # Plot grid
#    p.patches('x', 'y', source=ps_mosaic,
#             fill_color={'field': 'pt_r_tt_ud', 'transform': color_mapper},
#             fill_alpha=1.0, line_color="black", line_width=0.05)
    
#    # Add metro on top of the same figure
#    p.multi_line('x', 'y', source=ps_ice, color="black", line_width=2)

    p.patches('x', 'y', source=ps_ice,
             fill_color={'field': 'pt_r_tt_ud', 'transform': color_mapper},
             fill_alpha=1.0, line_color="black", line_width=0.05)
    
#    # Add points on top (as black points)
#    p.multi_line('x', 'y', size=3, source=ps_land, color="black")

    p.patches('x', 'y', source=ps_land,
             fill_color={'field': 'pt_r_tt_ud', 'transform': color_mapper},
             fill_alpha=1.0, line_color="black", line_width=0.05)    
    
    show(p)
    # Save the figure
#    outfp = r"/home/geo/data/travel_time_map.html"
#    save(p, outfp)
    
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
                    outroot = Path(output2).joinpath('ArcticDEM','MOSAIC',vurl,tile,rurl)                    
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
                            wget.download(out, str(outfile), bar=bar_custom)
                            print('\nFile downloaded to ' + str(outfile))                            
                            extractTar(outroot, outfile, remove=True)
                            
                        except HTTPError as error:
                            print("\nError downloading {} [{}]".format(url, error))
                            continue 
                                    
                    else:
                        print('File already exists at ' + str(outroot))
                else:
                    print('URL not found: ' + str(u))
        count=count+1
                 

def extractTar(pathout1, pathout2, remove=True):    
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
        tilepath = root.joinpath('ArcticDEM', datatype, version, t, resolution)

        if tilepath.exists():
            
            #Get all directories in tile folder and append to output
            pathlist = tilepath.glob('*.tif')
            for i in pathlist:
                folders.append(i)
                        
        #Print statement if file directory to tiles not found
        else:
            print('Path not found: ' + str(tilepath))
     
    #Return list of folder directories with specified tiles
    return folders            
                
                
mrooturl='http://data.pgc.umn.edu/elev/dem/setsm/ArcticDEM/mosaic/'
trooturl='http://data.pgc.umn.edu/elev/dem/setsm/ArcticDEM/geocell/'

test_mrooturl='http://data.pgc.umn.edu/elev/dem/setsm/ArcticDEM/mosaic/v3.0/10m/15_29/'
test_srooturl='http://data.pgc.umn.edu/elev/dem/setsm/ArcticDEM/geocell/v3.0/2m/n62w101/SETSM_W2W2_20150626_1030010043A8A100_10300100443D3300_seg1_2m_v3.0.tar.gz'





download='D:/python_workspace/arcticdem_download/arctic_dem_test_download'
output='G:/Satellitdata/ArcticDEM/Ver_7_32m_Mosaic'
version='3.0'
resolution='32'

rowrange=list(range(11,26,1))
colrange = list(range(37,40,1))
tilelist=[]
for r in rowrange:
    for c in colrange:
        tilelist.append(str(r) + '_' + str(c))


downloadMosaic(version, resolution, tilelist, download, output)


files=getFolders(rootdirectory, 'mosaic', version, tilelist, resolution)
zone24=[]
zone1=[]
zone2=[]
zone3=[]












#arcticdem/ee_setsm_clip2aoi.py 
#optional arguments:
#  -h, --help       show this help message and exit
#  --source SOURCE  Choose location of your AOI shapefile
#  --target TARGET  Choose the location of the master ArcticDEM strip file
#  --output OUTPUT  Choose the location of the output shapefile based on your
#                   AOI
#def demaoi(source=None,target=None,output=None):
#    subprocess.call('ogr2ogr -f "ESRI Shapefile" -clipsrc '+source+" "+output+" "+target+" -skipfailures", shell=True)
#    print("Clip Completed")
#
#
##arcticdem/ee_setsm_clip2download.py 
#def pgcaoi(source=None,target=None,output=None,destination=None):
#    os.system('ogr2ogr -f "ESRI Shapefile" -clipsrc '+source+" "+output+" "+target+" -skipfailures")
#    print("Clip Completed")
#    target=infile
#    with fiona.open(infile) as input:
#        for pol in input:
#            reader= pol['properties']['fileurl']
#            print(reader)
#            url = reader
#            dest = destination
#            obj = SmartDL(url, dest)
#            obj.start()
#            path=obj.get_dest()
#
#
##arcticdem/ee_setsm_dfshp.py
##optional arguments:
##  -h, --help            show this help message and exit
##  --subset SUBSET       Choose the location of the output shapefile based on
##                        your AOI[You got this from demaoi tool]
##  --destination DESINATION
##                        Choose the destination where you want to download your
##                        files
#def demdownload(infile=None,destination=None):
#    with fiona.open(infile) as input:
#        for pol in input:
#            reader= pol['properties']['fileurl']
#            fname= os.path.basename(reader)
#            fpath=os.path.join(destination,fname)
#            if not os.path.exists(fpath):
#                url=reader
#                dest=destination
#                obj=SmartDL(url,dest, threads=3)
#                obj.start()
#                path=obj.get_dest()
#            else:
#                print('Skipping....' + str(fname))
#                # print("Skipping...."+str(fname), end='\r')
#        print("Download Completed")
#
#
#  
##arcticdem/ee_setsm_meta2file.py (meta parsing for GEE)
##optional arguments:
##  -h, --help           show this help message and exit
##  --folder FOLDER      Choose where you unzipped and extracted your DEM and
##                       metadata files
##  --metadata METADATA  Choose a path to the metadata file "example:
##                       users/desktop/metadata.csv"
##  --error ERROR        Choose a path to the errorlog file "example:
##                       users/desktop/errorlog.csv"
#def demmeta(folder,mfile,errorlog):
#    metasource = [y for x in os.walk(folder) for y in glob(os.path.join(x[0], '*.txt'))]
#    with open(mfile,'wb') as csvfile:
#        writer=csv.DictWriter(csvfile,fieldnames=["id_no", "system:time_start", "platform", "catId1","catId2", "noDataValue", "releaseVersion", "srcImg1","srcImg2","setsmVersion","resolution","bitdepth","acqDate","minelv","maxelv","units"], delimiter=',')
#        writer.writeheader()
#    with open(errorlog,'wb') as csvfile:
#        writer=csv.DictWriter(csvfile,fieldnames=["id_no"], delimiter=',')
#        writer.writeheader()
#    for files in metasource:
#        print(files)
#        with open(files,'r') as myfile:
#            a=myfile.readlines()
#            try:
#                demid=str(a).split('stripDemId = "')[1].split('v2.0";')[0]+"v20_dem"
#                platform=str(a).split('platform = "')[1].split('";')[0]
#                catId1 = str(a).split('catId1 = "')[1].split('";')[0]
#                catId2 = str(a).split('catId2 = "')[1].split('";')[0]
#                noDataValue = str(a).split('noDataValue = ')[1].split(';')[0]
#                date_time = str(a).split('stripCreationTime = ')[1].split('T')[0]
#                rls=str(a).split('releaseVersion = "')[1].split('";')[0]
#                sim=str(a).split('sourceImage1 = "')[1].split('";')[0]
#                sim2=str(a).split('sourceImage2 = "')[1].split('";')[0]
#                setv=str(a).split('setsmVersion = ')[1].split(';')[0]
#                rs=str(a).split('outputResolution = ')[1].split(';')[0]
#                bp=str(a).split('bitsPerPixel = ')[1].split(';')[0]
#                acq=str(a).split('acqDate = ')[1].split(';')[0]
#                minelv=str(a).split('minElevValue = ')[1].split(';')[0]
#                maxelv=str(a).split('maxElevValue = ')[1].split(';')[0]
#                units=str(a).split('horizontalCoordSysUnits = "')[1].split('";')[0]
#                pattern = '%Y-%m-%d'
#                epoch = int(time.mktime(time.strptime(date_time, pattern)))*1000
#                acqtime=int(time.mktime(time.strptime(acq, pattern)))*1000
#                print("DEM ID",demid)
#                print("Platform",platform)
#                print("Acquisition Time",acqtime)
#                print("Strip Creation Time",epoch)
#                print('CatID1',catId1)
#                print('CatID2',catId2)
#                print("noDataValue",noDataValue)
#                print("Release Version",rls)
#                print("SourceImage 1",sim)
#                print('SourceImage 2',sim2)
#                print('SETSM Version',setv)
#                print("BitsPerPixel",bp)
#                print("Unit",units)
#                print("Minimum Elevation",format(float(minelv),'.2f'))
#                print("Maximum Elevation",format(float(maxelv),'.2f'))
#                print("Output Resolution",format(float(rs),'.2f'))
#                with open(mfile,'a') as csvfile:
#                    writer=csv.writer(csvfile,delimiter=',',lineterminator='\n')
#                    writer.writerow([demid,epoch,platform,catId1,catId2,noDataValue,rls,sim,sim2,setv,format(float(rs),'.2f'),bp,acqtime,format(float(minelv),'.2f'),format(float(maxelv),'.2f'),units])
#                csvfile.close()
#            except Exception:
#                print(infilename)
#                with open(errorlog,'a') as csvfile:
#                    writer=csv.writer(csvfile,delimiter=',',lineterminator='\n')
#                    writer.writerow([infilename])
#                csvfile.close()
#                
#
##arcticdem/ee_targz_ext_extract.py
##optional arguments:
##  -h, --help            show this help message and exit
##  --folder FOLDER       Choose the download file where you downloaded your tar
##                        zipped files
##  --destination DESTINATION
##                        Choose the destination folder where you want your
##                        images and metadata files to be extracted
##  --action ACTION       Choose if you want your zipped files to be deleted
##                        post extraction "yes"|"no"
#def demextract(directory=None,destination=None,delete=None):
#    files=os.listdir(directory)
#    if not os.path.exists(destination):
#        os.makedirs(destination)
#        os.makedirs(os.path.join(destination,"pgcdem"))
#        os.makedirs(os.path.join(destination,"pgcmeta"))
#        os.makedirs(os.path.join(destination,"pgcmt"))
#    else:
#        if not os.path.exists(os.path.join(destination,"pgcdem")):
#            os.makedirs(os.path.join(destination,"pgcdem"))
#        if not os.path.exists(os.path.join(destination,"pgcmeta")):
#            os.makedirs(os.path.join(destination,"pgcmeta"))
#        if not os.path.exists(os.path.join(destination,"pgcmt")):
#            os.makedirs(os.path.join(destination,"pgcmt"))
#    filesdem = os.listdir(os.path.join(destination,"pgcdem"))
#    for fdem in filesdem:
#        #print(os.path.join(destination,"pgcdem",fdem))
#        os.remove(os.path.join(destination,"pgcdem",fdem))
#    filesmeta = os.listdir(os.path.join(destination,"pgcmeta"))
#    for fm in filesmeta:
#        #print(os.path.join(destination,"pgcmeta",fm))
#        os.remove(os.path.join(destination,"pgcmeta",fm))
#    filesmt = os.listdir(os.path.join(destination,"pgcmt"))
#    for fmt in filesmt:
#        #print(os.path.join(destination,"pgcmeta",fm))
#        os.remove(os.path.join(destination,"pgcmt",fmt))
#    for fname in files:
#        filepath=os.path.join(directory,fname)
#        if (filepath.endswith("tar.gz")):
#            tar = tarfile.open(filepath,'r:*')
#            tar.extractall(destination)
#            tar.close()
#            print("Extracted in Current Directory")
#        elif (filepath.endswith("tar")):
#            tar=tarfile.open(filepath,'r:*')
#            tar.extractall(destination)
#            tar.close()
#        else:
#            print("Not a tar.gz file: '%s '")
#    jp= [y for x in os.walk(destination) for y in glob(os.path.join(x[0], '*.tif'))]
#    mf= [y for x in os.walk(destination) for y in glob(os.path.join(x[0], '*.txt'))]
#    for mfd in mf:
#        if mfd.count("mdf")!=1:
#            os.unlink(mfd)
#    tifcount= [y for x in os.walk(destination) for y in glob(os.path.join(x[0], '*.tif'))]
#    mfcount= [y for x in os.walk(destination) for y in glob(os.path.join(x[0], '*.txt'))]
#    indexfold=os.path.join(destination,"index")
#    if os.path.exists(indexfold):
#        shutil.rmtree(indexfold)
#    for tifffile in tifcount:
#        if tifffile.endswith("dem.tif"):
#            basetif=os.path.basename(tifffile)
#            shutil.move(tifffile, os.path.join(destination,"pgcdem",basetif))
#    for tifffile in tifcount:
#        if tifffile.endswith("matchtag.tif"):
#            basetif=os.path.basename(tifffile)
#            shutil.move(tifffile, os.path.join(destination,"pgcmt",basetif))
#    for textfile in mfcount:
#        basemeta=os.path.basename(textfile)
#        shutil.move(textfile, os.path.join(destination,"pgcmeta",basemeta))
#    if delete=="yes":
#        tarcount=[y for x in os.walk(directory) for y in glob(os.path.join(x[0], '*.tar'))]+[y for x in os.walk(directory) for y in glob(os.path.join(x[0], '*.tar.gz'))]
#        for tar in tarcount:
#            os.unlink(tar)
#    else:
#        print("Extract Completed & Tar files not deleted")
#
#
##arcticdem/setsm_size.py
##optional arguments:
##  --infile INFILE  Choose the clipped aoi file you clipped from demaoi
##                   tool[This is the subset of the master ArcticDEM Strip]
##  --path PATH      Choose the destination folder where you want your dem files
##                   to be saved[This checks available disk space]
#def demsize(path, infile):
#    results = []
#    summation=0
#    spc=psutil.disk_usage(path).free
#    remain=float(spc)/1073741824
#    # now start downloading each file
#    try:
#        with fiona.open(infile) as input:
#            for pol in input:
#                reader= pol['properties']['fileurl']
#                download_url = reader
#                pool = PoolManager()
#                response = pool.request("GET", download_url, preload_content=False)
#                max_bytes = 100000000000
#                content_bytes = response.headers.get("Content-Length")
#                summary=float(content_bytes)/1073741824
#                summation=summation+summary
#                print(format(float(summation),'.2f'),"GB", end='\r')
#            else:
#                result = False
#    except KeyError:
#        print('Could not check size')
#
#        #print(remain,"MB")
#    print("Remaining Space in GB",format(float(remain),'.2f'))
#    print ("Total Download Size in GB",format(float(summation),'.2f'))
    
