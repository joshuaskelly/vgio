# QUAKE
A Python package for Quake files.

[![Python 3](https://img.shields.io/badge/python-3-blue.svg)]() [![Discord](https://img.shields.io/badge/discord-chat-7289DA.svg)](https://discord.gg/hFct5VQ)

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
