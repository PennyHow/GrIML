# Tutorials

The following tutorial steps make up the full workflow for post-processing of raster classifications to a compiled, production-ready inventory of ice marginal lakes.


## Converting raster classifications to vectors

GrIML's convert module is used to convert binary raster classifications of water bodies to vectors; where values of 1 in the raster classification denote water has been classified, and zero values denote no water. We need the `convert` function to perform this. 

```python
from griml.convert import convert
```

Next we need to define some input variables - the projection, band information and date range of the input raster. If you have followed the [GEE script for classifying lakes](https://github.com/PennyHow/GrIML/blob/main/gee_scripts/lake_classification.js) available through the GrIMl repo, then each outputted raster band represents classifications using one of three approaches:

1. Multi-spectral classification from Sentinel-2
2. Backscatter threshold classification from Sentinel-1
3. Sink detection from ArcticDEM

And the default outputted projection is [Polar Stereographic](https://nsidc.org/data/user-resources/help-center/guide-nsidcs-polar-stereographic-projection). The start and end date should match the defined date range used for the raster classifications.

```python
# Define projection
proj = 'EPSG:3413'

# Define information from raster bands
band_info = [{'b_number':1, 'method':'VIS', 'source':'S2'}, 
             {'b_number':2, 'method':'SAR', 'source':'S1'},
             {'b_number':3, 'method':'DEM', 'source':'ARCTICDEM'}] 

# Define date range of classifications
start='20170701' 
end='20170831'
```

Next we need to define the location of our raster file. A test raster file is provided with GrIML, which can be located using the `os` module.

```python
import os
infile = os.path.join(os.path.dirname(griml.__file__),'test/test_north_greenland.tif')
```

And then the file can be converted from raster to vector classifications using the `convert` function and the input variables.

```python
vectors = convert([infile], proj, band_info, start, end) 
```

Note that a single raster file is wrapped as a list, as the `convert` function expects a list of rasters normally. We recommend using the `glob` module to generate a list of rasters from converting, if you wish to convert multiple classifications.

```python
# Generate list of all rasters
import glob
all_infiles = list(glob.glob("PATH/TO/RASTER_DIRECTORY/*.tif"))

# Define output directory to write converted vectors to
outdir = "PATH/TO/OUTPUT_DIRECTORY"

# Convert all rasters 
convert(all_infiles, proj, band_info, start, end, outdir) 
```

```{important}
If an output directory is not provided then converted vectors will not be written to file.
```


## Filtering vector classifications

Vector classifications can be filtered by size and proximity to an inputted mask. In our case, we remove water bodies below a size of 0.05 sq km and further than 1 km from the ice margin (as we want to retain larger ice marginal lakes).

GrIML is provided with a test vector file for filtering, and a test ice mask which is an ice margin polygon object with a 1 km buffer

```python
# Define input files
import os
infile1 = os.path.join(os.path.dirname(griml.__file__),'test/test_filter.shp') 
infile2 = os.path.join(os.path.dirname(griml.__file__),'test/test_icemask.shp')  

# Define output directory to write filtered vectors to
outdir = "PATH/TO/OUTPUT_DIRECTORY"    
```

GrIML's `filter_vectors` function can then be used to filter the vectors in the input file.
 
```python
from griml.filter import filter_vectors
filter_vectors([infile1], infile2, outdir)
```

The size threshold is 0.05 sq km by default, but can be altered with the optional `min_area` variable like so.

```python
filter_vectors([infile1], infile2, outdir, min_area=0.1)
```

The `filter_vectors` is typically used for filtering multiple vector files, inputted as a list.

```python
# Generate list of all rasters
import glob
all_infiles = list(glob.glob("PATH/TO/VECTOR_DIRECTORY/*.shp"))

# Convert all rasters 
filter_vectors(all_infiles, infile2, outdir)
```

## Merging

When covering large areas, the classifications are usually split into different files. At this stage, we will merge all files together, to form a complete inventory of ice marginal lake classifications. Test files are provided with GrIML to perform this.

```python
import os
infile1 = os.path.join(os.path.dirname(griml.__file__),'test/test_merge_1.shp')  
infile2 = os.path.join(os.path.dirname(griml.__file__),'test/test_merge_2.shp')                  
```

The `merge_vectors` function is used to merge all valid vectors within a list of files. In this case, we will merge all vectors from the two files defined previously. 

```python
from griml.merge import merge_vectors
i = merge_vectors([infile1,infile2]) 
```

An output file can be defined in order to write the merged vectors to file if needed.
 
```python
# Define output file path
outfile = "PATH/TO/OUTPUT_File.shp"

# Merge and save to file
merge_vectors([infile1,infile2], outfile) 
```

```{important}
If an output directory is not provided then the merged vectors will not be written to file. To retain the merged vectors in memory, make sure that an output variable is defined
```

## Adding metadata

Metadata can be added to the inventory with GrIML's `metadata` module. This includes:

- Adding a classification certainty value
- Assigning an identification number per lake
- Assigning a placename to each lake
- Assigning a region to each lake
- Assigning a list of all classification sources to each lake

Input files are needed for assigning a placename and a region to each lake. The placename file is a point vector file containing all placenames for a region. We use the placename database from [Oqaasileriffik](https://oqaasileriffik.gl/en/), the Language Secretariat of Greenland, for which there is an example data subset provided with GrIML. The region file is a polygon vector file containing all regions and their names. We use the Greenland Ice Sheet drainage basin regions as defined by [Mouginot and Rignot, (2019)](https://doi.org/10.7280/D1WT11), a dataset which is provided with GrIML. 

```python
import os

# Input test inventory for adding metadata to
infile1 = os.path.join(os.path.dirname(griml.__file__),'test/test_merge_2.shp') 

# Placenames file            
infile2 = os.path.join(os.path.dirname(griml.__file__),'test/test_placenames.shp')   

# Regions file           
infile3 = os.path.join(os.path.dirname(griml.__file__),'test/greenland_basins_polarstereo.shp') 
```

All metadata can be added with the `add_metadata` function.

```python
from griml.metadata.add_metadata import add_metadata
add_metadata(infile1, infile2, infile3)
```
