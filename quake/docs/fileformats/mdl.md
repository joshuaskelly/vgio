# Mdl File Format
The Spr file contains 3D model data for the video game Quake.

## Standard Mdl File Layout
| Offset | Name                        |
|--------|-----------------------------|
| 0x00   | [Header](#header)           |
| 0x54   | [Skins](#skins)             |
|        | [ST Vertexes](#st-vertexes) |
|        | [Triangles](#triangles)     |
|        | [Frames](#frames)           |

## Header
| Offset | Size | Type     | Description           | Notes                                        |
|--------|------|----------|-----------------------|----------------------------------------------|
| 0x00   | 4    | char[4]  | Magic Number          | Identifies the Mdl format. Should be 'IDPO'  |
| 0x04   | 4    | int      | Version Number        | Version of the spr format. Should be 6       |
| 0x08   | 12   | float[3] | Scale                 |                                              |
| 0x14   | 12   | float[3] | Origin                |                                              |
| 0x20   | 4    | float    | Radius                |                                              |
| 0x24   | 12   | float[3] | Eye Position          | Offset for eye position.                     |
| 0x30   | 4    | int      | Skin Count            | The number of Skins or Skin Groups in the Skins chunk.  |
| 0x34   | 4    | float    | Skin Width            |                                              |
| 0x38   | 4    | int      | Skin Height           |                                              |
| 0x3C   | 4    | int      | Vertex Count          |                                              |
| 0x40   | 4    | int      | Triangle Count        |                                              |
| 0x44   | 4    | int      | Frame Count           |                                              |
| 0x48   | 4    | int      | Sync Type             |                                              |
| 0x4C   | 4    | int      | Flags                 |                                              |
| 0x50   | 4    | float    | Size                  | The average size of the triangles.           |

## Skins
The skins chunk is a consecutive sequence of [Skins](#skin) or [Skin Groups](#skin-group). The first byte must be read to determine the type of skin that follows.

### Skin
| Offset  | Size  | Type     | Description       | Notes                                    |
|---------|-------|----------|-------------------|------------------------------------------|
| 0x00    | 4     | int      | Skin Type         | Identifies the skin type. Should be 0    |
| 0x04    |       | char[n]  | Pixel Data        | A sequence of unstructured pixel data.   |

### Skin Group
| Offset  | Size  | Type     | Description       | Notes                                    |
|---------|-------|----------|-------------------|------------------------------------------|
| 0x00    | 4     | int      | Skin Type         | Identifies the skin type. Should be 1    |
| 0x04    | 4     | int      | Group Skin Count  | The number of skins inside this group.   |
|         | 4n    | float[n] | Intervals         | The number of intervals is given by the Group Skin Count. |
|         | m     | char[m]  | Pixel Data        | The size of the pixel data is given by `Skin Width * Skin Height * Group Skin Count` |

## ST Vertexes
| Offset  | Size  | Type     | Description       | Notes                                    |
|---------|-------|----------|-------------------|------------------------------------------|
| 0x00    | 4     | int      | On Seam           | Indicates if the ST Vertex lies on a skin boundary. 0 indicates not on boundary.|
| 0x04    | 4     | int      | S Coordinate      |     |
| 0x08    | 4     | int      | T Coordinate      |     |

## Triangles
| Offset  | Size  | Type     | Description       | Notes                                    |
|---------|-------|----------|-------------------|------------------------------------------|
| 0x00    | 4     | int      | Faces Front       | Indicates if the triangle face the front of the model. 0 indicates back-facing.    |
| 0x04    | 12    | int[3]   | Vertex Indices    |         |


## Frames
The frames chunk is a consecutive sequence of [Frames](#frame) or [Frame Groups](#frame-group).

## Tri Vertex
| Offset  | Size  | Type         | Description        | Notes       |
|---------|-------|--------------|--------------------|-------------|
| 0x00    | 12    | int[3]       | Vertex Indices     |             |
| 0x0C    | 4     | int          | Light Normal Index |             |

## Frame
| Offset  | Size  | Type         | Description       | Notes       |
|---------|-------|--------------|-------------------|-------------|
| 0x00    | 4     | int          | Frame Type        | Identifies the frame type. Should be 0 |
| 0x04    | 16    | TriVertex[3] | Bounding Box Min  |             |
| 0x14    | 16    | TriVertex[3] | Bounding Box Max  |             |
| 0x24    | 16    | char[16]     | Frame Name        |             |
| 0x34    |       | TriVertex[n] | Frame Vertexes    | Consecutive sequence of n Tri Vertexes where n is the Vertex Count. |


## Frame Group
| Offset  | Size  | Type         | Description       | Notes       |
|---------|-------|--------------|-------------------|-------------|
| 0x00    | 4     | int          | Frame Type        | Identifies the frame type. Should be 1 |
| 0x04    | 16    | TriVertex[3] | Bounding Box Min  |             |
| 0x14    | 16    | TriVertex[3] | Bounding Box Max  |             |
| 0x24    | 4     | int          | Group Frame Count | The number of frames inside this group.            |
| 0x28    | 4n    | float[n]     | Intervals         |             |
|         |       | Frame[n]     | Group Frame Count | A consecutive sequence of Frames where n is the Group Frame Count. |


