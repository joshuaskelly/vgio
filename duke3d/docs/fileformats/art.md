# Art File Format
The Art file is an archive used to store image files for the video game Duke Nukem 3D.

## Art Structure
| Offset | Size | Type              | Description | Notes            |
|--------|------|-------------------|-------------|------------------|
| 0x00   |      | [Header](#header) | Header      |                  |
|        |      | bytes             | Data        | The data is a sequence of images as unstructured pixel data in column major order. |


## Header
| Offset | Size | Type     | Description           | Notes                                                   |
|--------|------|----------|-----------------------|---------------------------------------------------------|
| 0x00   | 4    | int      | Version Number        | Version the Art format. Should be 1                     |
| 0x04   | 4    | int      | Tile Count            | Number of tile entries. Ken Silverman notes that this should not be relied upon. |
| 0x08   | 4    | int      | Local Tile Start      | The numeric id of first tile.                           |
| 0x0C   | 4    | int      | Local Tile End        | The numeric id of the last tile.                        |
| 0x10   | 2n   | short[n] | Tile x-dimensions     | A sequence of tile x-dimensions.                        |
|        | 2n   | short[n] | Tile y-dimensions     | A sequence of tile y-dimensions.                        |
|        | 4n   | int[n]   | Picanims              | A sequence of bitmasked tile attributes.                |
