#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def assign_certainty(gdf, search_names, scores, source='all_src'):
    '''Assign certainty score to geodataframe based on sources
    
    Parameters
    ----------
    gdf : pandas.GeoDataFrame
        Vectors to assign ncertainty to
    search_names : str
        Names of sources to count and determine certainty
    scores : list
        List of scores of certainty
    sources : str
        Column name of sources information
    '''
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
