---
title: 'pypromice: A Python package for processing automated weather station data'
tags:
  - Python
  - glaciology
  - climate
  - promice
  - gc-net
  - geus
  - greenland
  - kalaallit-nunaat
authors:
  - name: Penelope R. How
    orcid: 0000-0002-8088-8497
    corresponding: true # (This is how to denote the corresponding author)
    affiliation: 1
  - name: Patrick J. Wright
    orcid: 0000-0003-2999-9076
    affiliation: 1
  - name: Kenneth D. Mankoff
    orcid: 0000-0001-5453-2019
    affiliation: "1, 2, 3"
  - name: Baptiste Vandecrux
    orcid: 0000-0002-4169-8973
    affiliation: 1
  - name: Robert S. Fausto
    orcid: 0000-0003-1317-8185
    affiliation: 1
  - name: Andreas P. Ahlstrøm
    orcid: 0000-0001-8235-8070
    affiliation: 1
affiliations:
 - name: Department of Glaciology and Climate, Geological Survey of Denmark and Greenland (GEUS), Copenhagen, Denmark
   index: 1
 - name:  Autonomic Integra, New York, NY, USA
   index: 2
 - name: NASA Goddard Institute for Space Studies, New York, NY, USA
   index: 3

date: 03 March 2023
bibliography: paper.bib

---

# Summary

- GrIML post-processing toolbox description
- GrIML project aim and outline
- GrIML datasets
- Similar toolboxes

Citations to entries in paper.bib should be in [rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html) format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

Figures can be included like this:

![Caption for example figure.\label{fig:example}](https://raw.githubusercontent.com/PennyHow/GrIML/blob/main/other/reporting/figures/workflow_revised.jpg)

and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:

![Caption for example figure.](https://raw.githubusercontent.com/PennyHow/GrIML/blob/main/other/reporting/figures/workflow_revised.jpg){ width=20% }


# Statement of need

- Need for reproducibility and transparency
- Outlines criteria for ice marginal lake classification


# Usage

- Use in GrIML inventory series generation

 
# Acknowledgements

This work is funded by the ESA Living Planet Fellowship (4000136382/21/I-DT-lr) entitled "Examining Greenland's Ice Marginal Lakes under a Changing Climate". Further support is provided by [PROMICE](https://promice.org] (The Programme for Monitoring of the Greenland Ice Sheet), funded by the [Geological Survey of Denmark and Greenland (GEUS)](https://www.geus.dk/) and the Danish Ministry of Climate, Energy and Utilities under the Danish Cooperation for Environment in the Arctic (DANCEA).


# References

