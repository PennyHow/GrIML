print('Commencing script run');

//--------------------------------------------------------------------------
// DEFINE VARIABLES

var date1='2017-07-01';
var date2='2017-08-31';

// Bounds filter as rectangle
//var pos=[-49.5854, 70.7360, -55.5516, 59.9702];      
//var aoi = ee.Geometry.Rectangle([-50.30424, 66.10153, -52.50255, 65.21566]);    // SW Greenland
//var aoi = ee.Geometry.Rectangle([-10.0528, 83.8441, -61.8843, 59.9584]);

// Bounds as feature
var aoi = ee.FeatureCollection('users/pennyruthhow/greenland_coastline');

print('Searching for images... ','Date range', date1, date2, 'Cloud percentage', 20)

//--------------------------------------------------------------------------
// Sentinel-2 classification

// Function for masking clouds from mask image file
function maskS2clouds(image) {
  var qa = image.select('QA60');

  // Bits 10 and 11 are clouds and cirrus, respectively.
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;

  // Both flags should be set to zero, indicating clear conditions.
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
      .and(qa.bitwiseAnd(cirrusBitMask).eq(0));

  return image.updateMask(mask).divide(10000);
}

// Search for images
var dataset = ee.ImageCollection('COPERNICUS/S2')
                  .filterDate(date1, date2)
                  .filterBounds(aoi)
                  // Pre-filter to get less cloudy granules.
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                  .map(maskS2clouds);

var blue='B2';
var green='B3';
var red='B4';
var vnir='B8';
var swir1='B11';
var swir2='B12';
var image = dataset.select([blue, green, red, vnir, swir1, swir2]).reduce(ee.Reducer.mean());

var swir1='B11_mean';
var swir2='B12_mean';
print(image.bandNames())
var sw = image.select([swir1, swir2]).resample('bilinear').reproject({crs:'EPSG:4326', scale:10}).rename(['B11_mean_1','B12_mean_1']);

var blue='B2_mean';
var green='B3_mean';
var red='B4_mean';
var vnir='B8_mean';
var swir1='B11_mean_1';
var swir2='B12_mean_1';
var image = image.addBands(sw.select([swir1,swir2]));
print(image.bandNames());

var ndwi = image.normalizedDifference([green, vnir]);
var mndwi = image.normalizedDifference([green, swir1]);
var AWEIsh = image.expression('BLUE + 2.5 * GREEN - 1.5 * (VNIR + SWIR1) - 0.25 * SWIR2',
                                {'BLUE' : image.select(blue),
                                'GREEN' : image.select(green),
                                'SWIR1' : image.select(swir1),
                                'VNIR' : image.select(vnir),
                                'SWIR2' : image.select(swir2)});
var AWEInsh = image.expression('4.0 * (GREEN - SWIR1) - (0.25 * VNIR + 2.75 * SWIR2)',
                                {'GREEN' : image.select(green),
                                'SWIR1' : image.select(swir1),
                                'VNIR' : image.select(vnir),
                                'SWIR2' : image.select(swir2)});
var bright = image.expression('(RED + GREEN + BLUE) / 3',
                                {'BLUE' : image.select(blue),
                                'GREEN' : image.select(green),
                                'RED' : image.select(red)});
var s2_lakes = ee.Image().expression("(BRIGHT > 5000) ? 0 : (NDWI > 0.3) ? 1 : (MNDWI < 0.1) ? 0 : (AWEISH < 2000) ? 0 : (AWEISH > 5000) ? 0 : (AWEINSH < 4000) ? 0 : (AWEINSH > 6000) ? 0 : 1",
                                        {'NDWI' : ndwi,
                                        'MNDWI' : mndwi,
                                        'AWEISH' : AWEIsh,
                                        'AWEINSH' : AWEInsh,
                                        'BRIGHT' : bright}).rename('s2_lakes');
var s2_lakes = s2_lakes.toByte()
s2_lakes.updateMask(s2_lakes);

//Map.addLayer(s2_lakes.select(['s2_lakes']), {min:0, max:1, palette:['FF8000','0000FF']}, 'S2');

print('S2 scenes classified');

//--------------------------------------------------------------------------
// Sentinel-1 lakes classification

// Search for images
var dataset = ee.ImageCollection('COPERNICUS/S1_GRD')
                  .filterDate(date1, date2)
                  .filterBounds(aoi)
                  // Pre-filter to get less cloudy granules.
                  .filter(ee.Filter.listContains('transmitterReceiverPolarisation','HH'))
                  .filter(ee.Filter.eq('instrumentMode','IW'));

var aver = dataset.select('HH').mosaic();
var smooth = aver.select('HH').focal_median(50,'circle','meters');
var s1_lakes = smooth.lt(-20).rename('s1_lakes');
var s1_lakes = s1_lakes.toByte()
s1_lakes.updateMask(s1_lakes);

//Map.addLayer(s1_lakes.select(['s1_lakes']), {min:0, max:1, palette:['FF8000','0000FF']}, 'S1');

print('S1 scenes classified');

//--------------------------------------------------------------------------
// DEM lakes classification

var dem=ee.Image('UMN/PGC/ArcticDEM/V3/2m_mosaic').clip(aoi)
var elev = dem.select('elevation').focal_median(110, 'circle', 'meters')

var elev = elev.toInt64()
var fill = ee.Terrain.fillMinima(elev, 10, 50)
var diff = fill.subtract(elev)
var dem_lakes = diff.gt(0).rename('dem_lakes')

var dem_lakes = dem_lakes.select('dem_lakes').focal_median(50, 'circle', 'meters')
var dem_lakes = dem_lakes.toByte()
dem_lakes.updateMask(dem_lakes)

//Map.addLayer(dem_lakes.select(['dem_lakes']), {min:0, max:1, palette:['FF8000','0000FF']}, 'DEM');

print('DEM scenes classified')

//--------------------------------------------------------------------------

// EXPORT
var all_lakes = s2_lakes.addBands([s1_lakes.select('s1_lakes'), dem_lakes.select('dem_lakes')])
print('All lakes combined')
//print(all_lakes.bandNames())

// EXPORT ONE IMAGE
var clip_lakes = all_lakes.clip(featcol.first())
var clip_lakes = clip_lakes.reproject({
    crs: 'EPSG:3413',
    scale: 10
    });
var projection = clip_lakes.select('s2_lakes').projection().getInfo();
print('All lakes clipped and reprojected')
print(projection)

Export.image.toDrive({
    image: all_lakes,
    description: 'lakes',
    folder: 'out',
    region: featcol.first(),
    scale: 10,
    crs: projection.crs,
    crsTransform: projection.transform,
    maxPixels: 1e13
})

//--------------------------------------------------------------------------
print('Run finished');
