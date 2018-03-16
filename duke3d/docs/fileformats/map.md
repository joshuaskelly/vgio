# Map File Format
The Map file contains level data for the video game Duke Nukem 3D.

## Standard Map Structure
| Offset | Size | Type                  | Description           | Notes   |
|--------|------|-----------------------|-----------------------|---------|
| 0x00   | 14   | [Header](#header)     | Header                |         |
| 0x14   | 2    | short                 | Sector Count          |         |
| 0x16   | 40n  | [Sector[n]](#sectors) | Sector Chunk          |         |
|        | 2    | short                 | Wall Count            |         |
|        | 32n  | [Wall[n]](#walls)     | Wall Chunk            |         |
|        | 2    | short                 | Sprite Count          |         |
|        | 44n  | [Sprite[n]](#sprites) | Sprite Chunk          |         |

## Header
| Offset | Size | Type     | Description           | Notes                                     |
|--------|------|----------|-----------------------|-------------------------------------------|
| 0x00   | 4    | int      | Version Number        | Version of the Map format. Should be 7    |
| 0x04   | 4    | int      | Position X            | Player starting position x-coordinate.    |
| 0x08   | 4    | int      | Position Y            | Player starting position y-coordinate.    |
| 0x0C   | 4    | int      | Position Z            | Player starting position z-coordinate.    |
| 0x10   | 2    | short    | Angle                 | Player staring angle.                     |
| 0x12   | 2    | short    | Current Sector Number | Staring sector number.                    |


## Sectors
The sectors chunk is a sequence of consecutive [Sectors](#sector). The first two bytes give the number of following sectors.

### Sector
| Offset | Size | Type     | Description           | Notes                                                   |
|--------|------|----------|-----------------------|---------------------------------------------------------|
| 0x00   | 2    | short    | Wall Pointer          | The index of the first wall of this sector.             |
| 0x02   | 2    | short    | Wall Number           | The total number of walls in this sector.               |
| 0x04   | 4    | int      | Ceiling Z             | The z-coordinate of the floor at the first point.       |
| 0x08   | 4    | int      | Floor Z               | The z-coordinate of the ceiling at the first point.     |
| 0x0C   | 2    | short    | Ceiling Stat          | The z-coordinate of the floor at the first point.       |
| 0x0E   | 2    | short    | Floor Stat            | The z-coordinate of the floor at the first point.       |
| 0x10   | 2    | short    | Ceiling Picnum        | Texture index into the Art file.                        |
| 0x12   | 2    | short    | Ceiling Heinum        | Ceiling slope value.                                    |
| 0x14   | 1    | char     | Ceiling Shade         | Shade offset.                                           |
| 0x15   | 1    | char     | Ceiling Palette       | Palette lookup number. The default palette is 0.        |
| 0x16   | 1    | char     | Ceiling X Panning     | Texture x alignment/panning value.                      |
| 0x17   | 1    | char     | Ceiling Y Panning     | Texture y alignment/panning value.                      |
| 0x18   | 2    | short    | Floor Picnum          | Texture index into the Art file.                        |
| 0x1A   | 2    | short    | Floor Heinum          | Ceiling slope value.                                    |
| 0x1C   | 1    | char     | Floor Shade           | Shade offset.                                           |
| 0x1D   | 1    | char     | Floor Palette         | Palette lookup number. The default palette is 0.        |
| 0x1E   | 1    | char     | Floor X Panning       | Texture x alignment/panning value.                      |
| 0x1F   | 1    | char     | Floor Y Panning       | Texture y alignment/panning value.                      |
| 0x20   | 1    | char     | Visibility            | Determines how fast shade changes relative to distance. |
| 0x21   | 1    | char     | Filler                | Padding byte.                                           |
| 0x22   | 2    | short    | Lotag                 | Game specific data.                                     |
| 0x24   | 2    | short    | Hitag                 | Game specific data.                                     |
| 0x26   | 2    | short    | Extra                 | Game specific data.                                     |


## Walls
The walls chunk is a sequence of consecutive [Walls](#wall). The first two bytes give the number of following walls.

### Wall
| Offset | Size | Type     | Description           | Notes                                              |
|--------|------|----------|-----------------------|----------------------------------------------------|
| 0x00   | 4    | int      | X                     | The x-coordinate of the left side of the wall.     |
| 0x04   | 4    | int      | Y                     | The y-coordinate of the left side of the wall.     |
| 0x08   | 2    | short    | Point2                | Index to the next wall on the right.               |
| 0x0A   | 2    | short    | Next Wall             | Index to the wall on the other side of the wall.   |
| 0x0C   | 2    | short    | Next Sector           | Index to the sector on the other side of the wall. |
| 0x0E   | 2    | short    | Cstat                 | A bitmasked field of attributes.                   |
| 0x10   | 2    | short    | Picnum                | Texture index into the Art file.                   |
| 0x12   | 2    | short    | Over Picnum           | Texture index into Art file for masked walls.      |
| 0x14   | 1    | char     | Shade                 | Shade offset of wall.                              |
| 0x15   | 1    | char     | Palette               | Palette lookup number. 0 is the standard palette.  |
| 0x16   | 1    | char     | X Repeat              | Used to stretch texture.                           |
| 0x17   | 1    | char     | Y Repeat              | Used to stretch texture.                           |
| 0x18   | 1    | char     | X Panning             | Texture x alignment/panning value.                 |
| 0x19   | 1    | char     | Y Panning             | Texture y alignment/panning value.                 |
| 0x1A   | 2    | short    | Lotag                 | Game specific data.                                |
| 0x1C   | 2    | short    | Hitag                 | Game specific data.                                |
| 0x1E   | 2    | short    | Extra                 | Game specific data.                                |


## Sprites
The sprites chunk is a sequence of consecutive [Sprites](#sprite). The first two bytes give the number of following sprites.

### Sprite
| Offset | Size | Type     | Description           | Notes                                              |
|--------|------|----------|-----------------------|----------------------------------------------------|
| 0x00   | 4    | int      | X                     | The x-coordinate of the sprite.                    |
| 0x04   | 4    | int      | Y                     | The y-coordinate of the sprite.                    |
| 0x08   | 4    | int      | Z                     | The z-coordinate of the sprite.                    |
| 0x0C   | 2    | short    | Cstat                 | A bitmasked field of attributes.                   |
| 0x0E   | 2    | short    | Picnum                | Texture index into the Art file.                   |
| 0x10   | 1    | char     | Shade                 | Shade offset of sprite.                            |
| 0x11   | 1    | char     | Palette               | Palette lookup number. 0 is the standard palette.  |
| 0x12   | 1    | char     | Clip Distance         | Size of the movement clipping square.              |
| 0x13   | 1    | char     | Filler                | Padding byte.                                      |
| 0x14   | 1    | char     | X Repeat              | Used to stretch texture.                           |
| 0x15   | 1    | char     | Y Repeat              | Used to stretch texture.                           |
| 0x16   | 1    | char     | X Offset              | Used to center texture.                            |
| 0x17   | 1    | char     | Y Offset              | Used to center texture.                            |
| 0x18   | 2    | short    | Sector Number         | Current sector number.                             |
| 0x1A   | 2    | short    | Status Number         | Current status of sprite.                          |
| 0x1C   | 2    | short    | Angle                 | Angle the sprite is facing.                        |
| 0x1E   | 2    | short    | Owner                 | Game specific data.                                |
| 0x20   | 2    | short    | X Velocity            | Game specific data.                                |
| 0x22   | 2    | short    | Y Velocity            | Game specific data.                                |
| 0x24   | 2    | short    | Z Velocity            | Game specific data.                                |
| 0x26   | 2    | short    | Lotag                 | Game specific data.                                |
| 0x28   | 2    | short    | Hitag                 | Game specific data.                                |
| 0x2A   | 2    | short    | Extra                 | Game specific data.                                |
