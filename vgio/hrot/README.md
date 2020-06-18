# HROT
A Python package for HROT files.

[![Python 3](https://img.shields.io/badge/python-3-blue.svg)]() [![Discord](https://img.shields.io/badge/discord-chat-7289DA.svg)](https://discord.gg/hFct5VQ)

## Usage
```python
from vgio.hrot import pak

with pak.PakFile('HROT.PAK') as pak_file:
   pak_file.extractall('path/to/extract/to')
```

## Tests
```
>>> python -m unittest discover -s tests
```
