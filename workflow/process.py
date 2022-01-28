"""
GrIML processing module playground (experimental)

@author: Penelope How
"""


# #Access Landsat 8 collection as list of images
# scenes = ee.ImageCollection(collection).filterDate(date1,
#                             date2).filterBounds(box)

# print(collection)
# # if cloud is not None:
# #     if collection.getInfo()['id'][0:7] in 'LANDSAT':
# # scenes = scenes.filter(ee.Filter.lte('CLOUD_COVER',cloud))       
#     # elif collection.getInfo()['id'][0:7] in 'COPERNI':            
# scenes = scenes.filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE',cloud))

# #Potentially an additional filter by tile coverage using the 'system:footprint'
# #attribute. It is a LinearRing geometry and could be converted to an area
# #and then filtered by footprint area

# #Retrieve metadata
# print('Collection retrieved from ' + str(collection))
# print('Total number of scenes: ', scenes.size().getInfo())
# print('Number of bands per scene: ' 
#       + str(len(scenes.first().bandNames().getInfo())))
# print('Band names: ' + str(scenes.first().bandNames().getInfo()))




# image_list = scenes.toList(scenes.size())
# print(scenes.size().getInfo())  

  
# #Iterate through image collection (as list)    
# for i in range(scenes.size().getInfo()):
    
#     #Get image object
#     scene = ee.Image(image_list.get(i))

#     #Print acquisition information
#     date = ee.Date(scene.get('system:time_start'))
#     time = date.getInfo()['value']/1000.

#     #Assign band information
#     if scene.getInfo()['id'][0:7] in 'LANDSAT':
#         blue='B2'
#         green='B3'
#         red='B4'
#         vnir='B5'
#         swir1='B6'
#         swir2='B7' 
#         print('Scene number ' + str(i) + ': LANDSAT ' + 
#               str(dt.datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')) 
#               + ' (' + str(scene.get('CLOUD_COVER').getInfo()) + 
#               '% cloud cover)') 
#     elif scene.getInfo()['id'][0:7] in 'COPERNI':
#         blue='B2'
#         green='B3'
#         red='B4'
#         vnir='B8'
#         swir1='B11'
#         swir2='B12'
#         print('Scene number ' + str(i) + ': SENTINEL ' + 
#               str(dt.datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')) 
#               + ' (' + str(scene.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()) + 
#               '% cloud cover)') 
#     # else:
#     #     sys.exit('Image collection type not valid')
              
#     #Create NDWI image
#     ndwi = scene.normalizedDifference([green,vnir])   
    
#     #Create MNDWI image
#     mndwi = scene.normalizedDifference([green,swir1])

#     #Create AWEIsh
#     AWEIsh = scene.expression('BLUE + 2.5 * GREEN - 1.5 * (VNIR + SWIR1) - 0.25 * SWIR2',
#                               {'BLUE' : scene.select(blue),
#                                'GREEN' : scene.select(green),
#                                'SWIR1' : scene.select(swir1),
#                                'VNIR' : scene.select(vnir),
#                                'SWIR2' : scene.select(swir2)})
    
#     #Create AWEInsh
#     AWEInsh = scene.expression('4.0 * (GREEN - SWIR1) - (0.25 * VNIR + 2.75 * SWIR2)',
#                                {'GREEN' : scene.select(green),
#                                 'SWIR1' : scene.select(swir1),
#                                 'VNIR' : scene.select(vnir),
#                                 'SWIR2' : scene.select(swir2)})
   
#     #Create BRIGHT
#     bright = scene.expression('(RED + GREEN + BLUE) / 3',
#                               {'BLUE' : scene.select(blue),
#                                'GREEN' : scene.select(green),
#                                'RED' : scene.select(red)})
    
#     #Decision tree (con, true, false)
#     # classif=Con(bright<0, bright, Con(cloud==1,11, Con(bright>5000,7, Con(HS==0,1, Con(slp>15,2, Con(ndwi>0.3,10, Con(mndwi<0.1,3, Con((aweish<2000)|(aweish>5000),4, Con((aweinsh<4000)|(aweinsh>6000), 5, Con(((ndwi>0.05)&(slp<10)),10,6)))))))))) 
#     merged = ndwi.lt(0) and mndwi.lt(0) and AWEIsh.lt(0) and AWEInsh.lt(0) #and bright.lt(5000)
#     merged = merged.lt(1) 
    
        


   
# # Separate ascending and descending orbit images into distinct collections.
# vvVhIwAsc = vvVhIw.filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))
# vvVhIwDesc = vvVhIw.filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))

# # Calculate temporal means for various observations to use for visualization.
# # Mean VH ascending.
# vhIwAscMean = vvVhIwAsc.select('VH').mean();
# # Mean VH descending.
# vhIwDescMean = vvVhIwDesc.select('VH').mean();
# # Mean VV for combined ascending and descending image collections.
# vvIwAscDescMean = vvVhIwAsc.merge(vvVhIwDesc).select('VV').mean();
# # Mean VH for combined ascending and descending image collections.
# vhIwAscDescMean = vvVhIwAsc.merge(vvVhIwDesc).select('VH').mean();

        



# task = ee.batch.Export.image.toDrive(image=merged, 
#                                       region=merged.getInfo()['coordinates'],
#                                       description='imagetoDriveEg',
#                                       )


# class Optical(object):
#     def __init__(self, im1, im2, im3, im4, im5, im6, proj, imtype):
#         self._red = im1                #S2 b4 
#         self._green = im2 		#S2 b3
#         self._blue = im3  		#S2 b2
#         self._nir = im4   		#S2 b8 (842 nm)
#         self._swir1 = im5 		#S2 b11 (1610 nm)
#         self._swir2 = im6 		#S2 b12 (2190 nm)
#         self._proj = proj
#         self._type = imtype
    
#     def checkProj(self, proj):
#         pass
    
#     def getNDWI(self):
#         g = self._green*1.0
#     	vnir = self._vnir*1.0
#     	ndwi = ((g-vnir)/(g+vnir))
#     	return ndwi
    
#     def getMNDWI(self):
#         g = self._green*1.0
#     	swir = self._swir1*1.0
#     	mndwi = ((g-swir)/(g+swir))
#     	return mndwi
    
#     def getBRIGHT(self):
#         bright = ((self._red + self._green + self._blue)/3)
# 	return bright
    
#     def getAWEIsh(self):
#         aweish = (self._blue + 2.5 * self._green - 1.5 * (self._vnir+self._swir1) - 0.25 * self._swir2)
#     	return aweish
    
#     def getAWEInsh(self):
#     	aweinsh = (4* (self._green-self._swir1)-(0.25 * self._vnir + 2.75 * self._swir2))
#     	return aweinsh
    
#     def getBinary(self):
#        #Decision tree (con, true, false). Convert arcpy to something else
#        #binary=Con(bright<0, bright, 
#         #           Con(cloud==1,11, 
#          #          Con(bright>5000,7, 
#           #         Con(HS==0,1, 
#            #        Con(slp>15,2, 
#             #       Con(ndwi>0.3,10, 
#              #      Con(mndwi<0.1,3, 
#               #     Con((aweish<2000)|(aweish>5000),4, 
#                #    Con((aweinsh<4000)|(aweinsh>6000), 5, 
#                 #   Con(((ndwi>0.05)&(slp<10)),10,6))))))))))
# 	binary = np.where(bright<0, bright, 
# 			  np.where(cloud==1, 11,
# 			  np.where(bright>5000, 7,
# 			  np.where(HS==0, 1,
# 			  np.where(slp>15, 2,
# 			  np.where(ndwi>0.3, 10,
# 			  np.where(mndwi<0.1, 3,
# 			  np.where(2000>aweish>5000, 4,
# 			  np.where(4000>aweinsh>6000, 5,
# 			  np.where(ndwi>0.05&slp<10, 10, 6))))))))))
        
#         binary = binary.astype('float32')
#         return binary

      
# class SAR(object):
#     def __init__(self, im, proj, imtype):
#         self._im = im
#         self._proj = proj
#         self._type = imtype

#     def checkProj(self, proj):
#         pass
    
#     def filterSpeckle(self):
#         pass
    
#     def getClass(self):
#         pass
    
#     def classify(self):
#         pass
        

# class DEM(object):
#     def __init__(self, dem, proj, demtype, ellipsoid):
#         self._dem = dem
#         self._proj = proj
#         self._type = demtype
#         self._ellip = ellipsoid

#     def checkProj(self, proj):
#         pass
    
#     def checkEllipsoid(self, ellip):
#         pass
    
#     def fillSinks(self, fillvalue):
#         pass
    
#     def subtractSinks(self):
#         pass
    
   
# def binToVector():
#     pass


# def filterBySize():
#     pass


# def filterByProximity():
#     pass


# def filterByMask():
#     pass


# def findDuplicates(geofile):
#     pass  


# def _getIdx(mylist, value):
#     #Function for finding indexes of certain values
#     return[i for i, x in enumerate(mylist) if x==value]

    
# def _listDuplicates(seq):
#     seen = set()
#     seen_add = seen.add
#     # adds all elements it doesn't know yet to seen and all other to seen_twice
#     seen_twice = set( x for x in seq if x in seen or seen_add(x) )
#     # turn the set into a list (as requested)
#     return list( seen_twice )


# def getAggregate():
#     pass


# def assignIDs():
#     pass


# def assignNames():
#     pass


# def assignSectors():
#     pass


# def getAreas():
#     pass
