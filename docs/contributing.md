# Contributing

## Bug reports and enhancement requests

Bug reports are essential to improving the stability and usability of the GrIML processing package. These should be raised on [GrIML’s issues forum](https://github.com/PennyHow/GrIML/issues). A complete and reproducible report is essential for bugs to be resolved easily, therefore bug reports must:

- Include a concise and self-contained Python snippet reproducing the problem
- Include a description of how your GrIML configuration is set up, such as from pip install or repository cloning/forking. If installed from pip or locally built, you can find the version of GrIML you are using with the following function

```python
from importlib import metadata
print(metadata.version('griml'))
```

- Explain why the current behaviour is wrong or not desired, and what you expect instead

```{important}
Before submitting an issue, please make sure that your installation is correct and working from either the pip installation or the main branch of the GrIML repository.
```

## Contributing to GrIML

You can work directly with GrIML’s development if you have a contribution, such as a solution to an issue or a suggestion for an enhancment.

### Forking

In order to contribute, you will need your own fork of the GrIML GitHub repository to work on the code. Go to the repo and choose the Fork option. This now creates a copy in your own GitHub space, which is connected to the upstream GrIML repository.

### Creating a development branch

From your forked space, make sure you have a Python Environment for running GrIML, as described in the [installation](https://griml.readthedocs.io/en/latest/installation.html). Then create and checkout a branch to make your developments on.

```
$ git checkout -b my-dev-branch
```

```{important}
Keep changes in this branch specific to one bug or enhancement, so it is clear how this branch contributes to GrIML
```

### Creating a pull request

To contribute your changes to GrIML, you need to make a pull request from your forked development branch to GrIML’s main branch. Before doing so, retrieve the most recent version of the main repository to keep this branch up to date with GrIML’s main branch.

```
$ git fetch
$ git merge upstream/main
```

And then open a pull request. Make sure to include the following in your pull request description:

1. The aim of your changes
2. Details of what these changes are
3. Any limitations or further development needed

Your pull request will be reviewed and hopefully accepted. Following this, you will be listed as a contributor to GrIML.
