# Bsp File Format
The Wad file contains level data for the video game Quake.

## Standard Bsp File Layout
| Offset | Name                            |
|--------|---------------------------------|
| 0x00   | [Header](#header)               |
|        | [Entities](#entities)           |
|        | [Planes](#planes)               |
|        | [Mip Textures](#mip-textures)   |
|        | [Vertexes](#vertexes)           |
|        | [Visibilities](#visibilities)   |
|        | [Nodes](#nodes)                 |
|        | [Texture Infos](#texture-infos) |
|        | [Faces](#faces)                 |
|        | [Lighting](#lighting)           |
|        | [Clip Nodes](#clip-nodes)       |
|        | [Leafs](#leafs)                 |
|        | [Mark Surfaces](#mark-surfaces) |
|        | [Edges](#edges)                 |
|        | [Surf Edges](#surf-edges)       |
|        | [Models](#models)               |

## Header
| Offset | Size | Type     | Description           | Notes                                     |
|--------|------|----------|-----------------------|-------------------------------------------|
| 0x00   | 4    | int      | Version Number        | Version of the Bsp format. Should be 29   |
| 0x04   | 4    | int      | Entities Offset       | Offset from the start of the Wad file.    |
| 0x08   | 4    | int      | Entities Size         |                                           |
| 0x0C   | 4    | int      | Planes Offset         | Offset from the start of the Wad file.    |
| 0x10   | 4    | int      | Planes Size           |                                           |
| 0x14   | 4    | int      | Mip Textures Offset   | Offset from the start of the Wad file.    |
| 0x18   | 4    | int      | Mip Textures Size     |                                           |
| 0x1C   | 4    | int      | Vertexes Offset       | Offset from the start of the Wad file.    |
| 0x20   | 4    | int      | Vertexes Size         |                                           |
| 0x24   | 4    | int      | Visibilities Offset   | Offset from the start of the Wad file.    |
| 0x28   | 4    | int      | Visibilities Size     |                                           |
| 0x2C   | 4    | int      | Nodes Offset          | Offset from the start of the Wad file.    |
| 0x30   | 4    | int      | Nodes Size            |                                           |
| 0x34   | 4    | int      | Texture Infos Offset  | Offset from the start of the Wad file.    |
| 0x38   | 4    | int      | Texture Infos Size    |                                           |
| 0x3C   | 4    | int      | Faces Offset          | Offset from the start of the Wad file.    |
| 0x40   | 4    | int      | Faces Size            |                                           |
| 0x44   | 4    | int      | Lighting Offset       | Offset from the start of the Wad file.    |
| 0x48   | 4    | int      | Lighting Size         |                                           |
| 0x4C   | 4    | int      | Clip Nodes Offset     | Offset from the start of the Wad file.    |
| 0x50   | 4    | int      | Clip Nodes Size       |                                           |
| 0x54   | 4    | int      | Leafs Offset          | Offset from the start of the Wad file.    |
| 0x58   | 4    | int      | Leafs Size            |                                           |
| 0x5C   | 4    | int      | Mark Surfaces Offset  | Offset from the start of the Wad file.    |
| 0x60   | 4    | int      | Mark Surfaces Size    |                                           |
| 0x64   | 4    | int      | Edges Offset          | Offset from the start of the Wad file.    |
| 0x68   | 4    | int      | Edges Size            |                                           |
| 0x6C   | 4    | int      | Surf Edges Offset     | Offset from the start of the Wad file.    |
| 0x70   | 4    | int      | Surf Edges Size       |                                           |
| 0x74   | 4    | int      | Models Offset         | Offset from the start of the Wad file.    |
| 0x78   | 4    | int      | Models Size           |                                           |

## Entities
The entities chunk is a plain text string containing entity defintions. The syntax is the same as the map file.

## Planes
The planes chunk is a consecutive sequence of Planes.

## Plane
| Offset | Size | Type     | Description | Notes        |
|--------|------|----------|-------------|--------------|
| 0x00   | 12   | float[3] | Normal      |              |
| 0x0C   | 4    | float    | Distance    |              |
| 0x10   | 4    | int      | Type        |              |

## Mip Textures

## Mip Texture
| Offset | Size | Type     | Description           | Notes                                           |
|--------|------|----------|-----------------------|-------------------------------------------------|
| 0x00   | 16   | char[16] | Texture Name          | Name of the frame as a null-byte padded string. |
| 0x10   | 4    | int      | Width                 | Width of texture in pixels.                     |
| 0x14   | 4    | int      | Height                | Height of texture in pixels.                    |
| 0x18   | 16   | int[4]   | Offsets               | Offsets for each of the four mip levels.        |
| 0x28   |      |          | Pixel Data            | A sequence of unstructured pixel data.          |

## Vertexes

## Vertex
| Offset | Size | Type     | Description     | Notes        |
|--------|------|----------|-----------------|--------------|
| 0x00   | 12   | float[3] | XYZ Coordinates |              |


## Visibilities

## Nodes

## Node
| Offset | Size | Type     | Description       | Notes        |
|--------|------|----------|-------------------|--------------|
| 0x00   | 4    | int      | Plane Number      |              |
| 0x04   | 4    | int      | Children          |              |
| 0x08   | 12   | int[3]   | Bounding Box Min  |              |
| 0x14   | 12   | int[3]   | Bounding Box Min  |              |
| 0x20   | 2    | short    | First Face        |              |
| 0x22   | 2    | short    | Face Count        |              |

## Texture Infos

## Texture Info
| Offset | Size | Type     | Description        | Notes        |
|--------|------|----------|--------------------|--------------|
| 0x00   | 12   | float[3] | S Coordinate       |              |
| 0x0C   | 4    | float    | S Offset           |              |
| 0x10   | 12   | float[3] | T Coordinate       |              |
| 0x1C   | 4    | float    | T Offset           |              |
| 0x20   | 4    | int      | Mip Texture Number |              |
| 0x24   | 4    | int      | Flags              |              |

## Faces

## Face
| Offset | Size | Type     | Description        | Notes        |
|--------|------|----------|--------------------|--------------|
| 0x00   | 2    | short    | Plane Number       |              |
| 0x02   | 2    | short    | Side               |              |
| 0x04   | 4    | int      | First Edge         |              |
| 0x08   | 2    | short    | Edge Count         |              |
| 0x0A   | 2    | short    | Texture Info       |              |
| 0x0C   | 4    | char[4]  | Styles             |              |
| 0x10   | 4    | int      | Light Offset       |              |

## Lighting

## Clip Nodes

## Clip Node
| Offset | Size | Type     | Description        | Notes        |
|--------|------|----------|--------------------|--------------|
| 0x00   | 4    | int      | Plane Number       |              |
| 0x04   | 4    | short[2] | Children           |              |

## Leafs

## Mark Surfaces

## Edges

## Surf Edges

## Models

