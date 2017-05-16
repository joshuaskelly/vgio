# QUAKE
Python module for Quake files.

[![Python 3](https://img.shields.io/badge/python-3-blue.svg)]()

## Usage
```python
from quake import mdl

with mdl.Mdl.open('./progs/player.mdl') as mdl_file:
   mesh = mdl_file.mesh()
   skin = mdl_file.image()
```

## Tests
```
>>> python -m unittest discover -s tests
```
