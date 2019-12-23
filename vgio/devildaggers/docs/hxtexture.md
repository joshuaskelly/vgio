# HxTexture File Format
The HxTexture file contains miptexture data for the video game Devil Daggers.

## Standard HxTexture File Layout
| Offset | Name                                   |
|--------|----------------------------------------|
| 0x00   | [Header](#header)                      |
| 0x0E   | <br><br>[Pixels](#pixels)<br><br><br>  |

## Header

| Offset | Size |  Type |   Description   |                 Notes                  |
|--------|------|-------|-----------------|----------------------------------------|
| 0x00   | 2    | short | format          |  Texture format. Should be 0x4011      |
| 0x02   | 4    | int   | width           |  Width of the texture at mip level 0.  |
| 0x06   | 4    | int   | height          |  Height of the texture at mip level 0. |
| 0x0A   | 4    | int   | mip_level_count |  Number of mip levels.                 |

### Pixels
A sequence of unstructured indexed RGBA pixel data.
