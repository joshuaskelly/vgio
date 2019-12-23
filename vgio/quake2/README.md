# QUAKE 2
A Python package for Quake 2 files.

[![Python 3](https://img.shields.io/badge/python-3-blue.svg)]() [![Discord](https://img.shields.io/badge/discord-chat-7289DA.svg)](https://discord.gg/hFct5VQ)

## Usage
```python
from quake2 import md2

with md2.Md2.open('player.md2') as md2_file:
   mesh = md2_file.mesh()
   skin = md2_file.image()
```

## Tests
```
>>> python -m unittest discover -s tests
```
