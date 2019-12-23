# Wal File Format
The Wal file contains miptexture data for the video game Quake 2.

## Wal File Layout
| Offset | Name              |
|--------|-------------------|
| 0x00   | [Header](#header) |
| 0x64   | <br><br><br> [Pixels](#pixels) <br><br><br><br> |

## Header

| Offset | Size |       Type      |  Description   | Notes |
|--------|------|-----------------|----------------|-------|
| 0x00   | 32   | char[32]        | name           |       |
| 0x20   | 4    | unsigned int    | width          |       |
| 0x24   | 4    | unsigned int    | height         |       |
| 0x28   | 16   | unsigned int[4] | offsets        |       |
| 0x38   | 32   | char[32]        | animation_name |       |
| 0x58   | 4    | int             | flags          |       |
| 0x5C   | 4    | int             | contents       |       |
| 0x60   | 4    | int             | value          |       |

## Pixels
A sequence of unstructured indexed pixel data represented as chars. A palette must be used to obtain RGB data.

#### Note: 
This is the pixel data for all four mip levels. The size is
calculated using the simplified form of the geometric series where
r = 1/4 and n = 4.

`size of pixel data = width * height * 85 / 64`