# Investigating Greenland's ice marginal lakes under a changing climate (GrIML)

[![PyPI version](https://badge.fury.io/py/griml.svg)](https://badge.fury.io/py/griml) [![DOI](https://zenodo.org/badge/444752900.svg)](https://zenodo.org/badge/latestdoi/444752900) [![Documentation Status](https://readthedocs.org/projects/griml/badge/?version=latest)](https://griml.readthedocs.io/en/latest/?badge=latest) [![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2FPennyHow%2FGrIML%2Fbadge%3Fref%3Dmain&style=flat)](https://actions-badge.atrox.dev/PennyHow/GrIML/goto?ref=main)

The **GrIML** processing package for classifying water bodies from satellite imagery using a multi-sensor, multi-method remote sensing approach. This workflow is part of the [ESA GrIML project](https://eo4society.esa.int/projects/griml/), and this repository also holds all project-related materials.

## Installation

The GrIML post-processing Python package can be installed using pip: 

```
$ pip install griml
```
Or cloned from the Github repository: 

```
$ git clone git@github.com:PennyHow/GrIML.git
$ cd GrIML
$ pip install .
```

## Workflow outline

<img src="https://github.com/PennyHow/GrIML/blob/main/other/reporting/figures/griml_workflow_with_gee.png?raw=true" alt="The GrIML workflow." width="1500" align="aligncenter" />

**GrIML** proposes to examine ice marginal lake changes across Greenland using a multi-sensor and multi-method remote sensing approach to better address their influence on sea level contribution forecasting.

Ice marginal lakes are detected using a remote sensing approach, based on offline workflows developed within the [ESA Glaciers CCI](https://catalogue.ceda.ac.uk/uuid/7ea7540135f441369716ef867d217519") (Option 6, An Inventory of Ice-Marginal Lakes in Greenland) ([How et al., 2021](https://www.nature.com/articles/s41598-021-83509-1)). Initial classifications are performed on Google Earth Engine with the scripts available [here](https://github.com/PennyHow/GrIML/tree/main/gee_scripts). Lake extents are defined through a multi-sensor approach using:

- Multi-spectral indices classification from Sentinel-2 optical imagery
- Backscatter classification from Sentinel-1 SAR (synthetic aperture radar) imagery
- Sink detection from ArcticDEM digital elevation models 

Post-processing of these classifications is performed using the GrIML post-processing Python package, including raster-to-vector conversion, filtering, merging, metadata population, and statistical analysis.

## Project links

- ESA [project outline](https://eo4society.esa.int/projects/griml/) and [fellow information](https://eo4society.esa.int/lpf/penelope-how/)

- Information about the [ESA Living Planet Fellowship](https://eo4society.esa.int/communities/scientists/living-planet-fellowship/)

- [GrIML project description](https://pennyhow.github.io/blog/investigating-griml/)

- 2017 ice marginal lake inventory [Scientific Reports paper](https://www.nature.com/articles/s41598-021-83509-1) and [dataset](https://catalogue.ceda.ac.uk/uuid/7ea7540135f441369716ef867d217519)
