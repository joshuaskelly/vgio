# Duke3D
A Python package for Duke Nukem 3D files.

[![Python 3](https://img.shields.io/badge/python-3-blue.svg)]() [![Discord](https://img.shields.io/badge/discord-chat-7289DA.svg)](https://discord.gg/KvwmdXA)

## Usage
```python
from duke3d import grp

with grp.GrpFile('./duke3d.grp') as grp_file:
   grp_file.extractall('./out')
```

## Tests
```
>>> python -m unittest discover -s tests
```
