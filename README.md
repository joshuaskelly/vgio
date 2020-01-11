# [![vgio](https://raw.githubusercontent.com/joshuaskelly/vgio/master/.media/logo.svg?sanitize=true)](https://github.com/JoshuaSkelly/vgio)

# vgio

[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)]() [![PyPI version](https://badge.fury.io/py/vgio.svg)](https://pypi.python.org/pypi/vgio) [![Build Status](https://travis-ci.org/joshuaskelly/vgio.svg?branch=master)](https://travis-ci.org/joshuaskelly/vgio) [![Documentation Status](https://readthedocs.org/projects/vgio/badge/?version=latest)](http://vgio.readthedocs.io/en/latest) [![Discord](https://img.shields.io/badge/discord-chat-7289DA.svg)](https://discord.gg/KvwmdXA)

vgio is a Python package for video game file I/O

## Mission

- *Pythonic:* Clean and well written Python.
- *Domain-specific:* The APIs and objects reflect the source code and community knowledge.
- *Complete:* Support as many file types as possible.
- *Robust:* The APIs and objects are thoroughly unit tested.

## Supported Games

- [Devil Daggers](./vgio/devildaggers)
- [Duke Nukem 3D](./vgio/duke3d)
- [Quake](./vgio/quake)
- [Quake II](./vgio/quake2)

## Installation
`$ pip install vgio`

## Usage
```python
from vgio.quake.bsp import Bsp

with Bsp.open('./maps/start.bsp') as bsp_file:
   """Do rad stuff with the BSP data structure!"""
```

## Tests
`$ python -m unittest discover`

## License
MIT

See the [license](./LICENSE) document for the full text.
