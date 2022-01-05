# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 13:46:52 2020

@author: Penelope How
"""

import shutil, os, time
from pathlib import Path

while True:
    paths = sorted(Path('C:/Users/how/Downloads').iterdir(), key=os.path.getmtime)
    outs = Path('D:/data/MOD35/')
    safepaths=[]
    for filename in paths:
        if str(filename.suffix) in ['.hdf']:
            safepaths.append(str(filename))
    
    for safe in safepaths[:-3]:
        print('Copying and deleting file: ' + str(safe))
        shutil.move(str(safe), outs.joinpath(Path(safe).name))
        # shutil.rmtree(safe)
    time.sleep(300)
