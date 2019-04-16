# Hxtexture

## Header

| Offset | Size |  Type |   Description   |                 Notes                  |
|--------|------|-------|-----------------|----------------------------------------|
| 0x00   | 2    | short | format          |  Texture format. Should be 0x4011      |
| 0x02   | 4    | int   | width           |  Width of the texture at mip level 0.  |
| 0x06   | 4    | int   | height          |  Height of the texture at mip level 0. |
| 0x0A   | 4    | int   | mip_level_count |  Number of mip levels.                 |
