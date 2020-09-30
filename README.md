[![Documentation Status](https://readthedocs.org/projects/gdpys/badge/?version=latest)](https://gdpys.readthedocs.io/en/latest/?badge=latest)
# GDPyS 2
An object oriented rewrite of GDPyS.

## Why?
This rewrite will aim at resolving major architectural flaws of GDPyS. Firstly (as mentioned before) it will have a modular, object-oriented design. This will not only majorly improve code readability, it will allow for improved modification possibillities.
Secondly, it will be written in an asynchronous manner. This will allow multiple requests to be carried out simultaneously, increasing performance under load. Flask was not a suitable choice for a game server and this rewrite aims at resolving that.

## Docs

Visit our documentation [here](https://gdpys.readthedocs.io/en/latest/)