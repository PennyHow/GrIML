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

![An overview of the GrIML Python package workflow \label{fig:workflow}](https://github.com/PennyHow/GrIML/blob/joss-paper/other/reporting/figures/griml_workflow_without_gee.png?raw=true)

This package is part of the [ESA GrIML project](https://eo4society.esa.int/projects/griml/) (Investigating Greenland's ice marginal lakes under a changing climate), whose aim is to map and monitor ice marginal lakes across Greenland through a series of annual ice marginal lake inventories (2016-2023). This workflow was used to make the inventory series, and will continue to be used to generate inventories in the future.


# Statement of need

`GrIML` meets four main needs to users in the remote sensing and cryospheric science communities:

1. Provide a usable workflow for post-processing of rasterised water body classifications
2. Document the criteria for classifying an ice marginal lake
3. Showcase a transparent workflow that, in turn, produces an open and reproducible ice marginal lake dataset that adheres to the FAIR principles [@wilkinson_fair_2016]
4. Produce inventories that map the areal extent and frequency of ice marginal lakes across Greenland, which demonstrate ice marginal lake evolution under a changing cliamte


- Many different approaches to classifying ice marginal lakes [@shugar_rapid_2020;@rick_dam_2022]
- Previously this workflow was a closed method [@how_greenland-wide_2021]


Sea level is predicted to rise drastically by 2100, with significant contribution from the melting of the Greenland Ice Sheet (GrIS). In these predictions, melt runoff is assumed to contribute directly to sea level change, with little consideration for meltwater storage at the terrestrial margin of the ice sheet; such as ice marginal lakes. 

In 2017, 3347 ice marginal lakes were identified in Greenland along the ice margin ([How et al., 2021](https://www.nature.com/articles/s41598-021-83509-1), see map figure for all mapped lakes). Globally, these ice marginal lakes hold up to 0.43 mm of sea level equivalent, which could have a marked impact on future predictions ([Shugar et al., 2021](https://www.nature.com/articles/s41558-020-0855-4)). Therefore, they need to be monitored to understand how changes in ice marginal lake water storage affect melt contribution, and how their dynamics evolve under a changing climate.

`GrIML` proposes to examine ice marginal lake changes across Greenland using a multi-sensor and multi-method remote sensing approach to better address their influence on sea level contribution forecasting.

1. Greenland-wide inventories of ice marginal lakes will be generated for selected years during the satellite era, building upon established classification methods in a unified cloud processing workflow
2. Detailed time-series analysis will be conducted on chosen ice marginal lakes to assess changes in their flooding dynamics; focusing on lakes with societal and scientific importance
3. The findings from this work will be validated against in situ observations - namely hydrological measurements and terrestrial time-lapse images - to evaluate whether the remote sensing workflow adequately captures ice marginal lake dynamics


# Usage

![The GrIML workflow](https://github.com/PennyHow/pennyhow.github.io/blob/master/assets/images/griml_workflow.png?raw=true)

Ice marginal lakes are detected using a remote sensing approach, based on offline workflows developed within the [ESA Glaciers CCI](https://catalogue.ceda.ac.uk/uuid/7ea7540135f441369716ef867d217519") (Option 6, An Inventory of Ice-Marginal Lakes in Greenland) ([How et al., 2021](https://www.nature.com/articles/s41598-021-83509-1)). Lake extents are defined through a multi-sensor approach using:

- Multi-spectral indices classification from Sentinel-2 optical imagery
- Backscatter classification from Sentinel-1 SAR (synthetic aperture radar) imagery
- Sink detection from ArcticDEM digital elevation models 

# Acknowledgements

This work is funded by the ESA Living Planet Fellowship (4000136382/21/I-DT-lr) entitled 'Examining Greenland's Ice Marginal Lakes under a Changing Climate'. Further support was provided by PROMICE (Programme for Monitoring of the Greenland Ice Sheet), which is funded by the Geological Survey of Denmark and Greenland (GEUS) and the Danish Ministry of Climate, Energy and Utilities under the Danish Cooperation for Environment in the Arctic (DANCEA), conducted in collaboration with DTU Space (Technical University of Denmark) and Asiaq Greenland Survey.


# References

