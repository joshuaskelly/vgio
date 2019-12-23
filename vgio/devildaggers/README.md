# Devil Daggers
A Python package for Devil Daggers files.

## Usage
```python
from vgio.devildaggers.hxresourcegroup import HxResourceGroupFile, ResourceType
from vgio.devildaggers.hxmesh import HxMesh

with HxResourceGroupFile('dd') as rg_file:
    for info in rg_file.file_list:
        if info.type == ResourceType.MESH:
            mesh = HxMesh.open(rg_file.open(info).read())
        
        if info.type == ResourceType.TEXTURE:
            """Do something with textures..."""
```

## Tests
```
>>> python -m unittest discover -s tests
```
