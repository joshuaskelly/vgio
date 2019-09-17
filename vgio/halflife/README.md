# Half-Life
A Python package for Half-Life files.

[![Python 3](https://img.shields.io/badge/python-3.6-blue.svg)]() [![Discord](https://img.shields.io/badge/discord-chat-7289DA.svg)](https://discord.gg/hFct5VQ)

## Usage
```python
from vgio.halflife import mdl

with mdl.Mdl.open('./models/player/gordon/gordon.mdl') as mdl_file:
   """Do something fun with the model!"""
```

## Tests
```
>>> python -m unittest discover -s tests
```
