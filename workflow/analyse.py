"""
GrIML ice marginal lake data analysis module

@author: Penelope How
"""

import fiona
from shapely.geometry import shape


def getSectorInfo():
	pass


def findIntersection(poly_file, line_file):
    polygons = fiona.open(poly_file)
    line = fiona.open(line_file)
    
    geom_p1 = [ shape(feat["geometry"]) for feat in polygons ]
    sline = [ shape(feat["geometry"]) for feat in line ]
    sline = sline[0]
    
    intersect=[]
    
    for j, g8 in enumerate(geom_p1):
        if sline.intersects(g8):
            try:
                i = sline.intersection(g8)
                intersect.append(i.length)
            except:
                print('Invalid geometry!')
    
    inter_sum = sum(intersect)
    print(f'Intersecting line length: {inter_sum}')
    print(f'Total ice margin length: {sline.length}')
    print(f'% of intersection: {(inter_sum/sline.length)*100}%')
    

