# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 09:22:05 2020

Script for searching through server folders to assess storage

@author: HOW
"""

import os, glob
import pandas as pd
import numpy as np
import argparse
import datetime as dt
from statistics import mode
import win32security
import ntpath

#------------------------------------------------------------------------------

# #Activate parser and parser arguments
# parser = argparse.ArgumentParser(description='A script to scan a drive for ' + 
#                                   'folder size and last accessed information.')

# parser.add_argument('--drive', required=True, type=str, help='Drive for ' +
#                     'scanning, e.g. "P:/"')

# parser.add_argument('--csv', default=None, type=str, 
#                     help='Folder location for .csv files to be outputted to, if '+
#                     'specified. Files will not be written if location is not ' +
#                     'given')
# parser.add_argument('--thr', default='20190101', type=str,
#                     help='Date threshold to determine if drive is deemed ' +
#                     'active or not, given as yyyymmdd. This defaults to ' +
#                     '20190101 if a date is not given')

# #Retrieve arguments
# args = parser.parse_args()

# #Retrieve variables
# src = args.drive
# out = args.csv
# thr = args.thr
# thr = dt.datetime.strptime(thr, '%Y%m%d')

src = 'P:/'
out = 'D:/python_workspace/'
thr = '20190101'
thr = dt.datetime.strptime(thr, '%Y%m%d')

#------------------------------------------------------------------------------
#File metadata retrieval functions

def getOwner(filename):
    sd = win32security.GetFileSecurity (filename, 
                                        win32security.OWNER_SECURITY_INFORMATION)
    owner_sid = sd.GetSecurityDescriptorOwner()
    name, domain, type = win32security.LookupAccountSid (None, owner_sid)
    
    return str(name)

def getFileSize(filename):
    return os.path.getsize(str(filename))/1e+9

def getFileLast(filename, typ='number'):
    filedate = dt.datetime.fromtimestamp(os.path.getatime(str(filename)))
    if typ == 'string':
        return str(filedate.strftime('%Y-%m-%d %H:%M:%S'))   
    else:
        return filedate
        
def getFileActive(filename, threshold):
    return dt.datetime.fromtimestamp(os.path.getatime(str(filename))) >  threshold
    
#------------------------------------------------------------------------------

#Retrieve drive information 
src1 = sorted(glob.glob(src+'*')[58:])
count1=1

for s in src1:    
    print('\n\n\n' + str(count1) + '. ' + str(s))
    df = pd.DataFrame()
    if os.path.isfile(s) is True:
        src2 = sorted(glob.glob(s+'*'))
    else:
         src2 = sorted(glob.glob(s+'/*'))   
         
    #Iterate through folders in drive
    for f in src2:
        print('\n\n' + str(f))
        
        #If item in topfolder is a file
        if os.path.isfile(str(f)) is True:
                       
            #Print information
            print('File size: ' + str(getFileSize(f)) + ' GB')
            print('File owner: ' + str(getOwner(f)))
            print('Last accessed: ' + str(getFileLast(f, typ='string')))
                
            #Append information to database
            row = {'Folder':f, 
                   'Size_GB':format(getFileSize(f),'.1f'), 
                   'Num_items': 1,
                   'All_owners': getOwner(f),
                   'Popular_owner': getOwner(f),               
                   'Last_modified': getFileLast(f),
                   'Active': getFileActive(f, thr), 
                   'Age': getFileLast(f, typ='string'),
                   'Largest_size':0, 
                   'Largest_name':'NA'}    
        
            df=df.append(row, ignore_index=True)
        
        #If item in topfolder is a folder
        else:
            name=[]
            size=[]
            acc=[]
            own=[]
            act=[]
            for path, subdirs, files in os.walk(str(f)):
                for fs in files:
                    name.append(os.path.join(path, fs))
                    try:
                        acc.append(getFileLast(os.path.join(path, fs), typ='number'))
                    except:
                        pass                    
                    try:                    
                        size.append(getFileSize(os.path.join(path, fs)))
                    except:
                        size.append(np.nan)                
                    try:
                        own.append(getOwner(os.path.join(path, fs)))
                    except:
                        own.append('Unknown')
    
            
            #Print information
            print('Folder size: ' + str(np.nansum(size)) + ' GB')
            print('Number of folder items: ' + str(len(name)))
            
            try:
                own1 = str(set(own))
                own2 = str(mode(own))
            except:
                own1='None'
                own2='None'
            print('File owners: ' + own1)
            print('Popular owner: ' + own2)
           
            try:
                large_name = name[size.index(np.nanmax(size))]
                large_size = np.nanmax(size)
            except:
                large_name = 'None'
                large_size = 0
            print('Largest file: ' + large_name + ' (' + str(large_size) + ' GB)')
                
            try:
                old = str(min(acc).strftime('%Y-%m-%d %H:%M:%S'))
                new = str(max(acc).strftime('%Y-%m-%d %H:%M:%S'))
                act = max(acc) >  thr
            except:
                old = 'NA'
                new = 'NA'
                act = False
            print('Oldest accessed file: ' + old)
            print('Newest accessed file: ' + new)   
            
            #Append information to database
            row = {'Folder': f, 
                   'Size_GB': format((np.nansum(size)), '.1f'), 
                   'Num_items': len(name), 
                   'All_owners': own1, 
                   'Popular_owner': own2,
                   'Last_modified': new,
                   'Active': act,
                   'Age': old, 
                   'Largest_size': format(large_size, '.1f'), 
                   'Largest_name': large_name}    
            df=df.append(row, ignore_index=True)
    
    if out is not None:
        try:
            print('Writing database to ' +str(out)+str(ntpath.basename(s))+'_scan.csv')
            df[['Folder','Size_GB','Num_items','Active','Last_modified','Popular_owner','All_owners','Age']].to_csv(str(out)+str(ntpath.basename(s))+'_scan.csv')    
        except:
            print(str(ntpath.basename(s))+'_scan.csv' + ' file not written')
            print('Likely cause: empty folder directory')
    count1=count1+1