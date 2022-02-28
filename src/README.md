# GrIML workflow

This space is for storing and documenting GrIML's processing chain, primarily programmed in Python.

## Proposed workflow

GrIML will build upon existing workflows from the <a href="https://catalogue.ceda.ac.uk/uuid/7ea7540135f441369716ef867d217519">ESA Glaciers CCI</a> (Option 6, An Inventory of Ice-Marginal Lakes in Greenland), refined here to form a unified processing chain that will be shared openly on Github and pip.

<img src="https://github.com/PennyHow/pennyhow.github.io/blob/master/assets/images/griml_workflow.png?raw=true" alt="The proposed GrIML workflow." width="1500" align="aligncenter">

## Online processing

It is intended to perform the satellite data retrieval and basic binary classification of water bodies with cloud processing and/or in-memory processing. By doing so, the workflow will avoid the handling of heavy data downloads. 

Online processing strategies will include:

+ Using cloud processing APIs such as the <a href="https://developers.google.com/earth-engine/guides/python_install">Google Earth Engine Python API</a>
+ Utilising data retrieval from urls, using readily available functions like <a href="https://rasterio.readthedocs.io/en/latest/api/rasterio.html?highlight=URL#rasterio.open">this</a>

Subject to funding, add-on modules to the workflow will take advantage of the cloud processing capabilities provided by the <a href="https://sentinelhub-py.readthedocs.io/en/latest/">SentinelHub APIs</a>. SentinelHub is a cloud processing platform that can be used to retrieve and process data from many satellite products.

By having the option to retrieve data from URL or SentinelHub, I envisage that the workflow can be used by all regardless of whether they have a paid license for SentinelHub or not.

## Offline processing

Key Python packages that will be used in the offline components of the workflow:

+ [xarray](https://xarray.pydata.org/en/stable/) - for large data handling and parralel processing
+ [rasterio](https://rasterio.readthedocs.io/en/latest/) - for raster processing
+ [geopandas](https://geopandas.org/en/stable/) - for vector data handling
