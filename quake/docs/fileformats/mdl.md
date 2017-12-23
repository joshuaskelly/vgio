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
| 0x30   | 4    | int      | Skin Count            |                                              |
| 0x34   | 4    | float    | Skin Width            |                                              |
| 0x38   | 4    | int      | Skin Height           |                                              |
| 0x3C   | 4    | int      | Vertex Count          |                                              |
| 0x40   | 4    | int      | Triangle Count        |                                              |
| 0x44   | 4    | int      | Frame Count           |                                              |
| 0x48   | 4    | int      | Sync Type             |                                              |
| 0x4C   | 4    | int      | Flags                 |                                              |
| 0x50   | 4    | float    | Size                  | The average size of the triangles.           |

## Skins

## ST Vertexes

## Triangles

## Frames
The frames chunk is a consecutive sequence of [Frames](#frame) or [Frame Groups](#frame-group).

## Frame
| Offset  | Size  | Type     | Description       | Notes       |
|---------|-------|----------|-------------------|-------------|
| 0x00    | 4     | int      |                   |             |


## Frame Group
| Offset  | Size  | Type     | Description       | Notes       |
|---------|-------|----------|-------------------|-------------|
| 0x00    | 4     | int      |                   |             |

