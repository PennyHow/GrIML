/* 
Author: Penelope How (pho@geus.dk)

This script shows how to derive surface lake temperature time-series over a series of points. 
Landsat surface water temperatures are derived from Landsat mission 4, 5, 7, 8 and 9 over 
Greenland in this example. Temperatures are determined from a series of points denoting the 
centroid position of an ice-marginal lake in the ESA CCI 2017 ice-marginal lake inventory 
(How et al., 2021).

This code is free and open. By using this code you agree to cite the following reference in 
any publications derived from them.

The deriving of surface temperature is based on the NASA Applied Remote Sensing Training 
(ARSET) program and the work of Sean McCartney (sean.mccartney@nasa.gov) on querying and 
charting Landsat surface temperature (ST) time series from Landsat missions 8 & 9 for a 
specified location (longitude/latitude). 

The correction for deriving surface water temperature is applied from Dyba et al. (2022)

//**** References ****

Dyba, K. et al. (2022) "Evaluation of Methods for Estimating Lake Surface Water Temperature 
Using Landsat 8" Remote Sensing 14, no. 15: 3839. https://doi.org/10.3390/rs14153839

How, P. et al. (2021) Greenland-wide inventory of ice marginal lakes using a multi-method 
approach. Scientific Reports 11, 4481. https://doi.org/10.1038/s41598-021-83509-1
*/

//****************** CLOUD MASK FUNCTION *****************//
function cloudMask(image) {
  var qa = image.select('QA_PIXEL');
  var mask = qa.bitwiseAnd(1 << 3)
    .or(qa.bitwiseAnd(1 << 4));
  return image.updateMask(mask.not());
}

//****************** GET IMAGERY FUNCTION *****************//
function getImages(aoi) {
  var L9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2') // Landsat 9 (entire collection)
  .select(['ST_B10', 'QA_PIXEL'], ['ST', 'QA_PIXEL'])
  .filterBounds(aoi)
  .filter(ee.Filter.lt('CLOUD_COVER', 20))
  .map(cloudMask);
  var L8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') // Landsat 8 (entire collection)
  .select(['ST_B10', 'QA_PIXEL'], ['ST', 'QA_PIXEL'])
  .filterBounds(aoi)
  .filter(ee.Filter.lt('CLOUD_COVER', 20))
  .map(cloudMask);
  var L7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2') // Landsat 7 (entire collection)
  .select(['ST_B6', 'QA_PIXEL'], ['ST', 'QA_PIXEL'])
  .filterBounds(aoi)
  .filter(ee.Filter.lt('CLOUD_COVER', 20))
  .map(cloudMask);
  var L5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2') // Landsat 5 (entire collection)
  .select(['ST_B6', 'QA_PIXEL'], ['ST', 'QA_PIXEL'])
  .filterBounds(aoi)
  .filter(ee.Filter.lt('CLOUD_COVER', 20))
  .map(cloudMask);
  var L4 = ee.ImageCollection('LANDSAT/LT04/C02/T1_L2') // Landsat 4 (entire collection)
  .select(['ST_B6', 'QA_PIXEL'], ['ST', 'QA_PIXEL'])
  .filterBounds(aoi)
  .filter(ee.Filter.lt('CLOUD_COVER', 20))
  .map(cloudMask);

  return L9.merge(L8).merge(L7).merge(L5).merge(L4);
}


//********* DERIVE ST FUNCTION ******************//
function applyWaterCorrection(image) {
  var waterBands = (image.select('ST').multiply(0.00341802).add(149.0)) // Scale factor
  .multiply(0.806).add(54.37) // Correction for water temperature
  .subtract(273.15); // Scale factor for degrees Celsius
  return image.addBands(waterBands, null, true);
}


//************ DERIVE AND EXPORT FUNCTION ******************//
function getST(feature, id) {

  var aoi = feature.geometry()
  var pt = aoi.buffer(30);

  var landsatWT = getImages(aoi).map(applyWaterCorrection);

  var values = landsatWT.map(function(image){
    return ee.Feature(null, image.reduceRegion(ee.Reducer.mean(), pt, 30))
                .set('lake_id', id)
                .set('system:time_start', image.get('system:time_start'))
                .set('system:index', image.get('system:index'))
                .set('date', ee.Date(image.get('system:time_start')).format('yyy-MM-dd'))
                .set('ST_max', image.reduceRegion(ee.Reducer.max(), pt, 30).values(['ST']))
                .set('ST_min', image.reduceRegion(ee.Reducer.min(), pt, 30).values(['ST']))    
                .set('ST_stddev', image.reduceRegion(ee.Reducer.stdDev(), pt, 30).values(['ST']))
                .set('ST_count', image.reduceRegion(ee.Reducer.count(), pt, 30).values(['ST']))
  });
  
  var name_file = id + '_lake_timeseries'
  Export.table.toDrive({
    collection: values, 
    description: name_file,
    folder: 'ST_IIML_poly', 
    fileFormat: 'CSV', 
    selectors: ['lake_id','system:time_start','date','system:index','ST','ST_max','ST_min','ST_stddev','ST_count','QA_PIXEL']
  });

}

//************ ITERATE OVER ALL PTS ******************//
print(table)

//var first = table.aggregate_array('LakeID').get(0);
//print(first);
//var t = table.filter(ee.Filter.eq('LakeID', first));
//getST(t, first);

table.sort('LakeID').aggregate_array('LakeID').evaluate(function (ids) {
  ids.map(function (id) {
    var t = table.filter(ee.Filter.eq('LakeID', id))
    getST(t, id)
  })
});

