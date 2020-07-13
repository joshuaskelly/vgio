# Half-Life
A Python package for Half-Life files.

[![Python 3](https://img.shields.io/badge/python-3-blue.svg)]()

## Usage
```python
from halflife import wad

with wad.WadFile.open('halflife.wad') as wad_file:
   print(wad_file.file_list)
```

## Tests
```
>>> python -m unittest discover -s tests
```
