# vgio

[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)]() [![Discord](https://img.shields.io/badge/discord-chat-7289DA.svg)](https://discord.gg/KvwmdXA)

vgio is a Python package for video game file I/O.

## Mission

- *Pythonic:* Clean and well written Python.
- *Domain-specific:* The APIs and objects reflect the source code and community knowledge.
- *Complete:* Support as many file types as possible.
- *Robust:* The APIs and objects are thoroughly unit tested.

## Supported Game

- Duke Nukem 3D
- Quake
- Quake II

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
