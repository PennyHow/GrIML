# Background

The **GrIML** processing package is for classifying water bodies from satellite imagery using a multi-sensor, multi-method remote sensing approach. This workflow is part of the [ESA GrIML project](https://eo4society.esa.int/projects/griml/) (Investigating Greenland's ice marginal lakes under a changing climate).

**Project aim:** To examine ice marginal lake changes across Greenland using a multi-method and multi-sensor remote sensing approach, refined with in situ validation.

## Motivation

<img src="https://media.springernature.com/full/springer-static/image/art%3A10.1038%2Fs41598-021-83509-1/MediaObjects/41598_2021_83509_Fig1_HTML.png?raw=true" align="right" width="400">

Sea level is predicted to rise drastically by 2100, with significant contribution from the melting of the Greenland Ice Sheet (GrIS). In these predictions, melt runoff is assumed to contribute directly to sea level change, with little consideration for meltwater storage at the terrestrial margin of the ice sheet; such as ice marginal lakes. 

In 2017, 3347 ice marginal lakes were identified in Greenland along the ice margin ([How et al., 2021](https://www.nature.com/articles/s41598-021-83509-1), see map figure for all mapped lakes). Globally, these ice marginal lakes hold up to 0.43 mm of sea level equivalent, which could have a marked impact on future predictions ([Shugar et al., 2021](https://www.nature.com/articles/s41558-020-0855-4)). Therefore, they need to be monitored to understand how changes in ice marginal lake water storage affect melt contribution, and how their dynamics evolve under a changing climate.

**GrIML** proposes to examine ice marginal lake changes across Greenland using a multi-sensor and multi-method remote sensing approach to better address their influence on sea level contribution forecasting.

1. Greenland-wide inventories of ice marginal lakes will be generated for selected years during the satellite era, building upon established classification methods in a unified cloud processing workflow

2. Detailed time-series analysis will be conducted on chosen ice marginal lakes to assess changes in their flooding dynamics; focusing on lakes with societal and scientific importance

3. The findings from this work will be validated against in situ observations - namely hydrological measurements and terrestrial time-lapse images - to evaluate whether the remote sensing workflow adequately captures ice marginal lake dynamics


## Methodology

<img src="https://github.com/PennyHow/pennyhow.github.io/blob/master/assets/images/griml_workflow.png?raw=true" alt="The GrIML workflow." width="1500" align="aligncenter" />

Ice marginal lakes are detected using a remote sensing approach, based on offline workflows developed within the [ESA Glaciers CCI](https://catalogue.ceda.ac.uk/uuid/7ea7540135f441369716ef867d217519") (Option 6, An Inventory of Ice-Marginal Lakes in Greenland) ([How et al., 2021](https://www.nature.com/articles/s41598-021-83509-1)). Lake extents are defined through a multi-sensor approach using:

- Multi-spectral indices classification from Sentinel-2 optical imagery
- Backscatter classification from Sentinel-1 SAR (synthetic aperture radar) imagery
- Sink detection from ArcticDEM digital elevation models 


## Reporting

Bi-monthly reports of GrIML's progress are available [here](https://github.com/PennyHow/GrIML/tree/main/other/reporting).


## Project links

- ESA [project outline](https://eo4society.esa.int/projects/griml/) and [fellow information](https://eo4society.esa.int/lpf/penelope-how/)

- Information about the [ESA Living Planet Fellowship](https://eo4society.esa.int/communities/scientists/living-planet-fellowship/)

- [GrIML project description](https://pennyhow.github.io/blog/investigating-griml/)

- 2017 ice marginal lake inventory [Scientific Reports paper](https://www.nature.com/articles/s41598-021-83509-1) and [dataset](https://catalogue.ceda.ac.uk/uuid/7ea7540135f441369716ef867d217519)
