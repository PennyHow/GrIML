# Installation

## Quickstart 

The GrIML package can be installed using pip: 

```
$ pip install griml
```

Or installed directly from the repository:

```
$ pip install --upgrade git+http://github.com/PennyHow/GrIML.git
```

```{important}
GrIML is tested for compatibility with Python 3.10, 3.11 and 3.12
```

GrIML comes with unit testing for ensuring that your installation is working. Once installed, run the following line to test GrIML's modules.

```
$ python -m unittest discover griml
```

## Developer install

The GrIML repo can be cloned and installed like so:

```
$ git clone git@github.com:PennyHow/GrIML.git
$ cd GrIML
$ pip install .
```
	
A conda environment `.yaml` file that includes all GrIML's dependencies is available for a straightforward conda set-up of the GrIML package:

```
$ git clone git@github.com:PennyHow/GrIML.git
$ cd GrIML
$ conda env create --file environment.yml
$ conda activate griml
$ pip install .
```
