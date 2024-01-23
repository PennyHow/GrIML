#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GrIML metadata assignment

@author: Penelope How
"""

def assign_sources(gdf, col_names=['unique_id', 'source']):
    '''Assign source metadata to geodataframe, based on unique lake id and
    individual source information'''
    ids = gdf[col_names[0]].tolist()
    source = gdf[col_names[1]].tolist()
    satellites=[]
    
    # Construct source list
    for x in range(len(ids)):
        indx = _get_indices(ids, x)
        if len(indx) != 0:
            res = []
            if len(indx) == 1:
                res.append(source[indx[0]].split('/')[-1])
            else:
                unid=[]
                for dx in indx:
                    unid.append(source[dx].split('/')[-1])
                res.append(list(set(unid)))
            for z in range(len(indx)):
                if len(indx) == 1:
                    satellites.append(res)
                else:
                    satellites.append(res[0])
                    
    # Compile lists for appending
    satellites_names = [', '.join(i) for i in satellites]
    number = [len(i) for i in satellites]
    
    # Return updated geodataframe    
    gdf['all_src']=satellites_names
    gdf['num_src']=number
    return gdf


def _get_indices(mylist, value):
    '''Get indices for value in list'''
    return[i for i, x in enumerate(mylist) if x==value]