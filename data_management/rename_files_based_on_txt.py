# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 09:43:48 2019

@author: HOW
"""

from pathlib import Path
import os

#in_dir = 'D:/data/S2'

#Get folder list
filelist = (list(Path(in_dir).glob('*/*/*')))
count = 1

#Iterate through list
for i in filelist:
    
    #Open info text file and get product level details
    txtpath = i.joinpath('INFO.txt')
    info = open(txtpath, 'r')
    lines = info.readlines()
    product = lines[6].split(' ')[2]
    product = product.split('\n')[0][-3:]
    print('\n' + str(count) + '. Found product level ' + str(product) + ' in folder ' +
          str(i))
    
    #Get all files for renaming
    jpfiles = list(i.glob('*.jp2'))
    for j in jpfiles:
        parent = j.parents[0]
        filename = j.name
        parts = str(filename).split('_')
        newname = parts[0] + '_' + str(product) + '_' + parts[1] + '_' + parts[2] + '_' + parts[3] + '_' + parts[4]
        newpath = parent.joinpath(newname)
        print('Renaming ' + str(filename) + ' to ' + str(newname))
        os.rename(j, newpath)
    
    count=count+1
    
