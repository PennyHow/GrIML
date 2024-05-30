import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="griml",
    version="0.1.0",
    author="Penelope How",
    author_email="pho@geus.dk",
    description="A workflow for classifying lakes from satellite imagery and compiling lake inventories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PennyHow/GrIML",
    project_urls={
        "Bug Tracker": "https://github.com/PennyHow/GrIML/issues",
    },
    keywords="glaciology ice lake ESA",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    package_data={"griml.test": ["*"]},
    python_requires=">=3.8",
    install_requires=['geopandas', 'pandas', 'scipy', 'Shapely', 'rasterio'],
)
