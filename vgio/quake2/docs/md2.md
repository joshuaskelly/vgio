# Md2 File Format
The Md2 file contains model data for the video game Quake 2.

## Header

| Offset | Size |   Type  |      Description      |                   Notes                   |
|--------|------|---------|-----------------------|-------------------------------------------|
| 0x00   | 4    | char[4] | Identity              |  File identity. Should be 'IDP2'          |
| 0x04   | 4    | int     | Version               |  File version. Should be 8                |
| 0x08   | 4    | int     | Skin Width            |  Width of the skin in pixels              |
| 0x0C   | 4    | int     | Skin Height           |  Height of the skin in pixels             |
| 0x10   | 4    | int     | Frame Size            |  Size of the frame struct in bytes        |
| 0x14   | 4    | int     | Number of Skins       |  The number of skin                       |
| 0x18   | 4    | int     | Number of Vertexes    |  The number of vertexes                   |
| 0x1C   | 4    | int     | Number of ST Vertexes |  The number of ST Vertexes                |
| 0x20   | 4    | int     | Number of Triangles   |  The number of triangles                  |
| 0x24   | 4    | int     | Number of Gl Commands |  The number of Gl commands                |
| 0x28   | 4    | int     | Number of Frames      |  The number of frames                     |
| 0x2C   | 4    | int     | Skin Offset           |  Skin data offset from start of file      |
| 0x30   | 4    | int     | ST Vertex Offset      |  St Vertex data offset from start of file |
| 0x34   | 4    | int     | Triangle Offset       |  Triangle data offset from start of file  |
| 0x38   | 4    | int     | Frame Offset          |  Frame data offset from start of file     |
| 0x3C   | 4    | int     | Gl Command Offset     |  Gl Command offset from start of file     |
| 0x40   | 4    | int     | End Offset            |  Offset to end of file                    |

## Skin

| Offset | Size |   Type   | Description |            Notes            |
|--------|------|----------|-------------|-----------------------------|
| 0x00   | 64   | char[64] | Name        |  The path of the skin file. |

## TriVertex

| Offset | Size |      Type     |    Description     |                                       Notes                                       |
|--------|------|---------------|--------------------|-----------------------------------------------------------------------------------|
| 0x00   | 1    | unsigned char | X-Coordinate       |                                                                                   |
| 0x01   | 1    | unsigned char | Y-Coordinate       |                                                                                   |
| 0x02   | 1    | unsigned char | Z-Coordinate       |                                                                                   |
| 0x03   | 1    | unsigned char | Light Normal Index |  The index for the pre-calculated normal vector of this vertex used for lighting. |

## StVertex

| Offset | Size |  Type | Description  |                Notes                |
|--------|------|-------|--------------|-------------------------------------|
| 0x00   | 2    | short | S-Coordinate |  The x-coordinate on the skin image |
| 0x02   | 2    | short | T-Coordinate |  The y-coordinate on the skin image |

## Triangle

| Offset | Size |   Type   | Description |                                      Notes                                       |
|--------|------|----------|-------------|----------------------------------------------------------------------------------|
| 0x00   | 6    | short[3] | Vertexes    |  A triple of Vertex indices. XYZ data can be obtained by from the current Frame. |
| 0x06   | 6    | short[3] | ST Vertexes |  A triple of St Vertex indexes                                                   |

## Frame

| Offset | Size |   Type   | Description |       Notes       |
|--------|------|----------|-------------|-------------------|
| 0x00   | 12   | float[3] | Scale       |  The frame scale  |
| 0x0C   | 12   | float[3] | Translate   |  The frame offset |
| 0x18   | 16   | char[16] | Name        |  The frame name   |

## GlVertex

| Offset | Size |  Type | Description  | Notes |
|--------|------|-------|--------------|-------|
| 0x00   | 4    | float | S-Coordinate |       |
| 0x04   | 4    | float | T-Coordinate |       |
| 0x08   | 4    | int   | Vertex       |       |

## GlCommand

| Offset | Size |  Type       | Description    | Notes               |
|--------|------|-------------|----------------|---------------------|
| 0x00   | 4    | int         | GlVertex Count |                     |
| 0x04   | Cn   | GlVertex[n] | GlVertexes     | Consecutive sequence of GlVertexes where n is the count. |