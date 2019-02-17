# Bsp File Format
The Bsp file contains level data for the video game Quake 2.

## Standard Bsp File Layout
| Offset | Name                            |
|--------|---------------------------------|
| 0x00   | [Header](#header)               |
|        | [Entities](#entities)           |
|        | [Planes](#planes)               |
|        | [Vertexes](#vertexes)           |
|        | [Visibilities](#visibilities)   |
|        | [Nodes](#nodes)                 |
|        | [Texture Infos](#texture-infos) |
|        | [Faces](#faces)                 |
|        | [Lighting](#lighting)           |
|        | [Leafs](#leafs)                 |
|        | [Leaf Faces](#leaf-faces)       |
|        | [Leaf Brushes](#leaf-brushes)   |
|        | [Edges](#edges)                 |
|        | [SurfEdges](#surfedges)         |
|        | [Models](#models)               |
|        | [Brushes](#brushes)             |
|        | [Brush Sides](#brush-sides)     |
|        | [Pop](#pop)                     |
|        | [Areas](#areas)                 |
|        | [Area Portals](#area-portals)   |

## Lump
| Offset | Size | Type | Description | Notes                                     |
|--------|------|------|-------------|-------------------------------------------|
| 0x00   | 4    | int  | Offset      | Offset from the start of the Bsp file.    |
| 0x04   | 4    | int  | Length      | Length of the data.                       |

## Header
| Offset | Size | Type | Description       | Notes                                       |
|--------|------|------|-------------------|---------------------------------------------|
| 0x00   | 4    | int  | Identity          | Identity of the Bsp file. Should be b'IBSP' |
| 0x04   | 4    | int  | Version Number    | Version of the Bsp file. Should be 29       |
| 0x10   | 8    | Lump | Entities Lump     |                                             |
| 0x18   | 8    | Lump | Planes Lump       |                                             |
| 0x20   | 8    | Lump | Vertexes Lump     |                                             |
| 0x28   | 8    | Lump | Visibilities Lump |                                             |
| 0x30   | 8    | Lump | Nodes Lump        |                                             |
| 0x38   | 8    | Lump | TextureInfos Lump |                                             |
| 0x40   | 8    | Lump | Faces Lump        |                                             |
| 0x48   | 8    | Lump | Lighting Lump     |                                             |
| 0x50   | 8    | Lump | Leafs Lump        |                                             |
| 0x58   | 8    | Lump | Leaf Faces Lump   |                                             |
| 0x60   | 8    | Lump | Leaf Brushes Lump |                                             |
| 0x68   | 8    | Lump | Edges Lump        |                                             |
| 0x70   | 8    | Lump | SurfEdges Lump    |                                             |
| 0x78   | 8    | Lump | Models Lump       |                                             |
| 0x80   | 8    | Lump | Brushes Lump      |                                             |
| 0x88   | 8    | Lump | Brush Sides Lump  |                                             |
| 0x90   | 8    | Lump | Pop Lump          |                                             |
| 0x98   | 8    | Lump | Areas Lump        |                                             |
| 0xA0   | 8    | Lump | Area Portals Lump |                                             |

## Entities
The entities lump is a plain text string containing entity defintions. The syntax is the same as the map file.

## Planes
The planes lump is a consecutive sequence of Planes.

## Plane
| Offset | Size | Type     | Description | Notes        |
|--------|------|----------|-------------|--------------|
| 0x00   | 12   | float[3] | Normal      |              |
| 0x0C   | 4    | float    | Distance    |              |
| 0x10   | 4    | int      | Type        |              |

## Vertexes
The vertexes lump is a consecutive sequence of Vertexes.

## Vertex
| Offset | Size | Type     | Description     | Notes        |
|--------|------|----------|-----------------|--------------|
| 0x00   | 12   | float[3] | XYZ Coordinates |              |


## Visibilities

## Nodes
The nodes lump is consecutive sequence of Nodes.

## Node
| Offset | Size | Type     | Description       | Notes        |
|--------|------|----------|-------------------|--------------|
| 0x00   | 4    | int      | Plane Number      |              |
| 0x04   | 4    | int      | Children          |              |
| 0x08   | 12   | int[3]   | Bounding Box Min  |              |
| 0x14   | 12   | int[3]   | Bounding Box Max  |              |
| 0x20   | 2    | short    | First Face        |              |
| 0x22   | 2    | short    | Face Count        |              |

## Texture Infos
The texture infos lump is consecutive sequence of Textures Infos.

## Texture Info
| Offset | Size | Type     | Description        | Notes        |
|--------|------|----------|--------------------|--------------|
| 0x00   | 12   | float[3] | S Coordinate       |              |
| 0x0C   | 4    | float    | S Offset           |              |
| 0x10   | 12   | float[3] | T Coordinate       |              |
| 0x1C   | 4    | float    | T Offset           |              |
| 0x20   | 4    | int      | Flags              |              |
| 0x24   | 4    | int      | Value              |              |
| 0x28   | 32   | char[32] | Texture Name       | Name of the texture info as a null-byte padded string. |
| 0x48   | 4    | int      | Next Texture Info  |              |

## Faces
The faces lump is consecutive sequence of Faces.

## Face
| Offset | Size | Type           | Description        | Notes        |
|--------|------|----------------|--------------------|--------------|
| 0x00   | 2    | unsigned short | Plane Number       |              |
| 0x02   | 2    | short          | Side               |              |
| 0x04   | 4    | int            | First Edge         |              |
| 0x08   | 2    | short          | Edge Count         |              |
| 0x0A   | 2    | short          | Texture Info       |              |
| 0x0C   | 4    | char[4]        | Styles             |              |
| 0x10   | 4    | int            | Light Offset       |              |

## Lighting

## Leafs
The leafs lump is consecutive sequence of Leafs.

## Leaf
| Offset | Size | Type           | Description        | Notes        |
|--------|------|----------------|--------------------|--------------|
| 0x00   | 4    | int            | Contents           |              |
| 0x04   | 2    | short          | Cluster            |              |
| 0x06   | 2    | short          | Area               |              |
| 0x08   | 6    | short[3]       | Bounding Box Min   |              |
| 0x0E   | 6    | short[3]       | Bounding Box Max   |              |
| 0x14   | 2    | unsigned short | First Leaf Face    |              |
| 0x16   | 2    | unsigned short | Leaf Face Count    |              |
| 0x18   | 2    | unsigned short | First Leaf Brush   |              |
| 0x1A   | 2    | unsigned short | Leaf Brush Count   |              |

## Leaf Faces
The leaf faces lump is a sequence of Face ids.

## Leaf Brushes
The leaf Brushes lump is a sequence of Brush ids.

## Edges

## Edge
| Offset | Size | Type           | Description        | Notes        |
|--------|------|----------------|--------------------|--------------|
| 0x00   | 2    | unsigned short | Vertex 0           |              |
| 0x02   | 2    | unsigned short | Vertex 1           |              |

## Surf Edges
The surf edges lump is a sequence of Edge ids.

## Models

## Model
| Offset | Size | Type           | Description        | Notes        |
|--------|------|----------------|--------------------|--------------|
| 0x00   | 12   | float[3]       | Bounding Box Min   |              |
| 0x0C   | 12   | float[3]       | Bounding Box Max   |              |
| 0x18   | 12   | float[3]       | Origin             |              |
| 0x24   | 16   | int[4]         | Head Node          |              |
| 0x34   | 4    | int            | First Face         |              |
| 0x38   | 4    | int            | Face Count         |              |

## Brushes
The brushes lump is a consecutive sequence of Brushes.

## Brush
| Offset | Size | Type | Description | Notes        |
|--------|------|------|-------------|--------------|
| 0x00   | 4    | int  | Fist Side   |              |
| 0x04   | 4    | int  | Side Count  |              |
| 0x08   | 4    | int  | Contents    |              |


## Brush Sides
The brush sides lump is a consecutive sequence of Brush Sides.

## Brush Side
| Offset | Size | Type           | Description        | Notes        |
|--------|------|----------------|--------------------|--------------|
| 0x00   | 2    | unsigned short | Plane Number       |              |
| 0x02   | 2    | short          | Texture Info       |              |

## Pop

## Areas
The areas lump is a consecutive sequence of Areas.

## Area
| Offset | Size | Type | Description        | Notes        |
|--------|------|------|--------------------|--------------|
| 0x00   | 4    | int  | Area Portal Count  |              |
| 0x04   | 4    | int  | First Area Portal  |              |

# Area Portals
The area portals lump is a consecutive sequence of Area Portals.

# Area Portal
| Offset | Size | Type | Description        | Notes        |
|--------|------|------|--------------------|--------------|
| 0x00   | 4    | int  | Portal Number      |              |
| 0x04   | 4    | int  | Other Area         |              |
