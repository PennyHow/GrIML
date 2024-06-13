---
title: "GrIML: A Python package for investigating Greenland's ice marginal lakes under a changing climate"
tags:
  - python
  - glaciology
  - remote sensing
  - greenland
  - kalaallit nunaat
authors:
  - name: Penelope R. How
    orcid: 0000-0002-8088-8497
    corresponding: true
    affiliation: 1
affiliations:
 - name: Department of Glaciology and Climate, Geological Survey of Denmark and Greenland (GEUS), Nuuk, Greenland
   index: 1

date: 01 September 2024
bibliography: paper.bib

---


# Summary

The `GrIML` Python package is for the post-processing of classified water bodies from satellite imagery. Initial rasterised binary classifications denoting water bodies can be inputted to `GrIML` to convert, filter and merge into a cohesive ice marginal lake vector dataset, populated with useful metadata and analysed with relevant statistical information (\autoref{fig:workflow}).

![An overview of the GrIML Python package workflow \label{fig:workflow}](https://github.com/PennyHow/GrIML/blob/main/other/reporting/figures/griml_workflow_without_gee.png?raw=true)

This package is part of the [ESA GrIML project](https://eo4society.esa.int/projects/griml/) (Investigating Greenland's ice marginal lakes under a changing climate), whose aim is to map and monitor ice marginal lakes across Greenland through a series of annual ice marginal lake inventories (2016-2023). In 2017, 3347 ice marginal lakes were identified in Greenland along the ice margin [@how_greenland-wide_2021;wiesmann_2017_2021]. Globally, these ice marginal lakes hold up to 0.43 mm of sea level equivalent, which could have a marked impact on future predictions [@shugar_rapid_2020;@carrivick_ice-marginal_2022]. Therefore, they need to be monitored to understand how changes in ice marginal lake water storage affect melt contribution, and how their dynamics evolve under a changing climate. The GrIML workflow was used to make the 2017-2023 inventory series, and will continue to be used to generate inventories in the future.


# Statement of need

`GrIML` meets four main needs to users in the remote sensing and cryospheric science communities:

1. Provide a usable workflow for post-processing of rasterised water body classifications
2. Document the criteria for classifying an ice marginal lake
3. Showcase a transparent workflow that, in turn, produces an open and reproducible ice marginal lake dataset that adheres to the FAIR principles [@wilkinson_fair_2016]
4. Produce inventories that map the areal extent and frequency of ice marginal lakes across Greenland, which demonstrate ice marginal lake evolution under a changing cliamte

There have been many different approaches to classifying ice marginal lakes with remote sensing techniques [@shugar_rapid_2020;@rick_dam_2022]. Packages exist for handling satellite and spatial data, such as GrIML's two key dependencies, Geopandas [@kelsey_geopandas_2020] and Rasterio [@gillies_rasterio_2019], as well as others (e.g. SentinelHub, Google Earth Engine). Remote sensing object classification and post-processing routines are usually available in connection with scientific publications, however, few are available as open, deployable packages. The GrIML post-processing Python package addresses this gap, for the benefit of the future generation of ice marginal lake inventories and for others in the scientific community to adapt and use themselves.


# Usage


![The GrIML Python package structure \label{fig:workflow}](https://github.com/PennyHow/GrIML/blob/main/other/reporting/figures/griml_package_structure.png?raw=true)

- Installation overview
- Basic structure, steps put into separate modules, flexible data loading
- Analysis functionality


# Acknowledgements

This work is funded by the ESA Living Planet Fellowship (4000136382/21/I-DT-lr) entitled 'Examining Greenland's Ice Marginal Lakes under a Changing Climate'. Further support was provided by PROMICE (Programme for Monitoring of the Greenland Ice Sheet), which is funded by the Geological Survey of Denmark and Greenland (GEUS) and the Danish Ministry of Climate, Energy and Utilities under the Danish Cooperation for Environment in the Arctic (DANCEA), conducted in collaboration with DTU Space (Technical University of Denmark) and Asiaq Greenland Survey.


# References

