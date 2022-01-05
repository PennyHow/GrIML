# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:47:53 2020

Script for deriving cloud products from MODIS MOD35/MYD35 imagery, modelled 
from the processing chain created by Jordi Cristóbal Rosselló 
(CreaNuvolsMOD035_01).

@author: PENELOPE HOW
"""

import sys
import os
import getpass
import datetime as dt


from pymodis import downmodis
from pymodis import convertmodis_gdal

import satpy
from satpy import Scene
import pyresample
from pyresample import gradient
from pathlib import Path

#------------------------------------------------------------------------------
def getMOD35(tilelist, date1, date2, out, flagtype='MOD35', user='PenelopeHow', 
             password='CoreyFeldman1', delta=10):
    
    #Set other variables
    #ftp='https://e4ftl01.cr.usgs.gov'           #FTP server url
    ftp='ftp://n4ftl01u.ecs.nasa.gov'           #Other FTP server
    path='SAN/'                                 #FTP directory
    debugFlag=True                              #Download debugging flag
    jpgFlag=True
    emptyFlag=True
    
    if flagtype == 'MOD35':
        path=path+'MOLT'
        prod='MOD35_L2.006'
    else:
        path=path+'MOLA'
        prod='MYD35_L2.006'
    
    #Set modis object
    modisOgg = downmodis.downModis(url=ftp, user=user,
                                   password=password,
                                   destinationFolder=out,
                                   tiles=tilelist, path=path,
                                   product=prod, today=date1,
                                   enddate=date2, jpg=jpgFlag,
                                   delta=int(10), debug=debugFlag)
    #Connect to ftp
    modisOgg.connect()
    if modisOgg.nconnection <= 20:
        
        #Download data
        modisOgg.downloadsAllDay(clean=emptyFlag, allDays=True)
    else:
        print("A problem with the connection occured") 
        pass      

#------------------------------------------------------------------------------
# def mosaicMOD35(inputfile, outputfile, subset, resolution, wkt, epsg=32624,
#                  resample='NEAREST_NEIGHBOUR', outtype='GTiff', vrt=False):
    
#     modisConver = convertmodis_gdal.convertModisGDAL(inputfile, outputfile,
#                                                      subset, resolution,
#                                                      outtype, epsg, wkt, 
#                                                      resample, vrt)
#     modisConver.run()

#------------------------------------------------------------------------------
def convertMOD35(inputfile, outputfile, subset, resolution, wkt, epsg=32624,
                 resample='NEAREST_NEIGHBOUR', outtype='GTiff', vrt=False):
    
    modisConver = convertmodis_gdal.convertModisGDAL(inputfile, outputfile,
                                                     subset, resolution,
                                                     outtype, epsg, wkt, 
                                                     resample, vrt)
    modisConver.run()
    

    
#------------------------------------------------------------------------------
# tiles=['h16v2','h17v0']
# dates=['2019-06-01', '2019-06-02']
# output='D:/python_workspace/modis_cloud_remotebasis/test_data'
# getMOD35(tiles, dates[0], dates[1], output)

#------------------------------------------------------------------------------
# print(satpy.available_readers())

inDirectory = 'D:/python_workspace/modis_cloud_remotebasis/test_data/laads/individual_hdf/'
outDirectory = 'D:/python_workspace/modis_cloud_remotebasis/test_output/'

inFiles = list(Path(inDirectory).glob('*.hdf'))
print(inFiles)
print('Proceeding to extract cloud files from ' + str(len(inFiles)) + ' files\n')

#Create date index for files
index=[]
for i in inFiles:
    index.append(str(Path(i).name)[10:22])
uindex=set(index)

myfiles = satpy.find_files_and_readers(base_dir=inDirectory,
                                       sensor="modis",
                                       start_time=dt.datetime(2019, 3, 30, 11, 40),
                                       end_time=dt.datetime(2020, 6, 30, 12, 5),
                                       reader='modis_l2')
scn = Scene(filenames=myfiles)
print(scn.available_dataset_names())

scn.load(['cloud_mask'], resolution=250)
scn.save_dataset('cloud_mask', outDirectory+'test.tif'), 


# #Iterate through date index
# count=1
# for i in uindex:
#     date=dt.datetime.strptime(str(i), '%Y%j.%H%M')
#     print(str(count) + '. MODIS files acquired on ' + str(date))
#     tifs=[]
#     for f in range(len(inFiles)):
#         if str(Path(inFiles[f]).name)[10:22] in i:
#             tifs.append(inFiles[f])
#     print('Found ' + str(len(tifs)) + ' associated tif files\n')
    
#     for t in tifs:
#         hdf = Scene(reader='modis_l2', filenames=str(t))

#     count=count+1