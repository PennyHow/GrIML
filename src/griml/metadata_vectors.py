#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GrIML processing module playground (experimental)

@author: Penelope How
"""
import glob
import geopandas as gpd
from pathlib import Path
from scipy.sparse.csgraph import connected_components


def assign_names(gdf, gdf_names, distance=500.0):
    '''Assign placenames to geodataframe geometries based on names in another 
    geodataframe point geometries'''  
    placenames = _compile_names(gdf_names)
                                    
    lakename=[]     
    for i,v in gdf.iterrows():  
        
        geom = v['geometry']
        
        polynames=[] 
        for pt in range(len(placenames)):
            if geom.contains(gdf_names['geometry'][pt]) == True:
                polynames.append(placenames[pt])  
                
        if len(polynames)==0:
            for pt in range(len(placenames)):  
                if gdf_names['geometry'][pt].distance(geom) < distance: 
                    polynames.append(placenames[pt]) 
            lakename.append(polynames)
            
        elif len(polynames)==1:  
            lakename.append(polynames)    
            
        else: 
            out=[]          
            for p in polynames:  
                out.append(p) 
            lakename.append(out) 
            
    lakeid = gdf['unique_id'].tolist()      
    lakename2 = []     
    
    for x in gdf.index:        
        indx = _get_indices(lakeid, x)                                         
        findname=[]
        for l in indx:
            if len(lakename[l])!=0: 
                findname.append(lakename[l])
        
        for i in range(len(indx)):  
            if len(findname)==0:
                lakename2.append('')
        
            else:                                           
                unique = set(findname[0])  
                unique = list(unique)  
                
                if len(unique)==1:
                    lakename2.append(findname[0][0]) 
                    
                else:
                    out2 = ', '
                    out2 = out2.join(unique) 
                    lakename2.append(out2) 
    gdf['placename'] = lakename2
    return gdf



def assign_certainty(gdf, search_names, scores, source='all_src'):
    '''Assign certainty score to geodataframe based on sources'''
    cert=[]
    srcs = list(gdf[source])

    for a in range(len(srcs)):
        if srcs[a].split(', ')==1:
            out = _get_score(srcs.split(', '))
            cert.append(out)    
        else:
            out=[]
            for b in srcs[a].split(', '):
                out.append(_get_score(b, search_names, scores))
            cert.append(sum(out))

    gdf['certainty'] = cert
    return gdf
    

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
    

def assign_id(gdf, col_name='unique_id'):
    '''Assign unique identification numbers to non-overlapping geometries in
    geodataframe'''
    # Find overlapping geometries
    geoms = gdf['geometry']
    geoms.reset_index(inplace=True, drop=True)        
    overlap_matrix = geoms.apply(lambda x: geoms.overlaps(x)).values.astype(int)
    
    # Get unique ids for non-overlapping geometries
    n, ids = connected_components(overlap_matrix)
    ids=ids+1
    
    # Assign ids and realign geoedataframe index 
    gdf[col_name]=ids
    gdf = gdf.sort_values(col_name)
    gdf.reset_index(inplace=True, drop=True) 
    return gdf
 
def _compile_names(gdf):
    '''Get preferred placenames from placename geodatabase'''  
    placenames=[]
    for i,v in gdf.iterrows():
        if v['Ny_grønla'] != None: 
            placenames.append(v['Ny_grønla'])
        else:
            if v['Dansk'] != None: 
                placenames.append(v['Dansk'])
            else:
                if v['Alternativ'] != None:
                    placenames.append(v['Alternativ'])
                else:
                    placenames.append(None)
    return placenames   

def _get_score(value, search_names, scores):
    '''Determine score from search string'''
    if search_names[0] in value:
        return scores[0]
    elif search_names[1] in value:
        return scores[1]
    elif search_names[2] == value:
        return scores[2]
    else:
        return None
 
    
def _get_indices(mylist, value):
    '''Get indices for value in list'''
    return[i for i, x in enumerate(mylist) if x==value]

if __name__ == "__main__": 
    indir = "/home/pho/python_workspace/GrIML/other/iml_2017/filtered_vectors/*.shp"
    
    infile_names = '/home/pho/python_workspace/GrIML/other/datasets/placenames/oqaasileriffik_placenames.shp'
    names = gpd.read_file(infile_names)

    count=1
    for infile in glob.glob(indir):
        print('\n'+str(count)+'. Populating metadata for '+str(Path(infile).stem))
        iml = gpd.read_file(infile)
        
        print('Assigning ID...')
        iml = assign_id(iml)
        
        print('Assigning sources...')
        iml = assign_sources(iml)
        
        print('Assigning certainty scores...')
        iml = assign_certainty(iml)
        
        print('Assigning placenames...')
        iml = assign_names(iml)
        
        print('Saving file...')
        iml.to_file("metadata_vectors/"+str(Path(infile).stem)+"_metadata.shp")
        print('Saved to '+str(Path(infile).stem)+"_metadata.shp")
        count=count+1