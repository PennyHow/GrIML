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

