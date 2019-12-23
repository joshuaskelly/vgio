# Sp2 File Format
The Sp2 file contains sprite model data for the video game Quake 2.

#### Note:
The Sp2 file does not contain pixel data.

## Sp2 File Layout
| Offset | Name              |
|--------|-------------------|
| 0x00   | [Header](#header) |
| 0x0C   | <br><br><br> [SpriteFrames](#spriteframe) <br><br><br><br> |

## Header

| Offset | Size |   Type  |   Description    |             Notes                |
|--------|------|---------|------------------|----------------------------------|
| 0x00   | 4    | char[4] | Identity         |  File identity. Should be 'IDS2' |
| 0x04   | 4    | int     | Version          |  File version. Should be 2       |
| 0x08   | 4    | int     | Number of Frames |  The number of sprite frames.    |

## SpriteFrame

| Offset | Size |   Type   | Description |                      Notes                      |
|--------|------|----------|-------------|-------------------------------------------------|
| 0x00   | 4    | int      | Width       |  Width of the frame.                            |
| 0x04   | 4    | int      | Height      |  Height of the frame                            |
| 0x08   | 8    | int[2]   | Origin      |  The offset of the frame                        |
| 0x10   | 64   | char[64] | Name        |  The name of the pcx file to use for the frame. |
