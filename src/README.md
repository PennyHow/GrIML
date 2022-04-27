# The GrIML python package

[![PyPI version](https://badge.fury.io/py/griml.svg)](https://badge.fury.io/py/griml) [![DOI](https://zenodo.org/badge/444752900.svg)](https://zenodo.org/badge/latestdoi/444752900) [![Documentation Status](https://readthedocs.org/projects/griml/badge/?version=latest)](https://griml.readthedocs.io/en/latest/?badge=latest) 

A GrIML workflow for classifying water bodies from satellite imagery using a multi-sensor, multi-method approach. This workflow is part of the <a href="https://eo4society.esa.int/projects/griml/">ESA GrIML project</a>.


## Quickstart

The GrIML package can be installed using pip: 

```python
pip install griml
```
Or cloned from the Github repository: 

```python
git clone https://github.com/PennyHow/GrIML
```


## Workflow

GrIML builds on the existing workflows from the <a href="https://catalogue.ceda.ac.uk/uuid/7ea7540135f441369716ef867d217519">ESA Glaciers CCI</a> (Option 6, An Inventory of Ice-Marginal Lakes in Greenland), refined here to form a unified processing chain that is shared openly on Github and pip.

<img src="https://github.com/PennyHow/pennyhow.github.io/blob/master/assets/images/griml_workflow.png?raw=true" alt="The proposed GrIML workflow." width="1500" align="aligncenter">


## Cloud processing

Primary processing is performed using the <a href="https://developers.google.com/earth-engine/guides/python_install">Google Earth Engine Python API</a>, including satellite data retrieval and binary classification from multiple sensors. By doing so, the workflow avoids the handling of heavy data downloads and operations. 

Subject to funding, it is intended to include add-on modules to the workflow, which take advantage of the cloud processing capabilities provided by the <a href="https://sentinelhub-py.readthedocs.io/en/latest/">SentinelHub APIs</a>. SentinelHub is a cloud processing platform that can be used to retrieve and process data from many satellite products.


## Offline processing

Key Python packages that will be used in the offline components of the workflow:

+ [geopandas](https://geopandas.org/en/stable/) - for vector dataset handling
+ ['numpy'](https://numpy.org/) - for numerical operations
+ ['pandas'](https://pandas.pydata.org/) - for dataframe handling
+ ['scipy'](https://docs.scipy.org/doc/scipy/index.html) - for matrix operations
+ ['shapely'](https://shapely.readthedocs.io/en/stable/manual.html) - for geometric operations
