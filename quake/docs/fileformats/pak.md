# Pak File Format
The Pak file is an uncompressed archive used to store resource files for the video game Quake.

## Standard Pak File Layout
| Offset | Name |
|---|---|
| 0x00000000 | [Header](#header) |
| 0x0000000C | <br><br><br> Data <br><br><br><br> |
|            | [Directory](#directory) |

## Header
| Offset | Length | Type    | Description      | Notes                                                    |
|--------|--------|---------|------------------|----------------------------------------------------------|
| 0x0000 | 4      | char[4] | Magic Number     | Identifies PAK format. Should be 'PACK'                  |
| 0x0004 | 4      | int     | Directory Offset | Offset of the directory from start of pack file.         |
| 0x0008 | 4      | int     | Directory Size   | Size of the directory. Equal to number of entries * 0x40 |

## Directory
The directory is a consecutive sequence of directory entries. The number of entries in this sequence is given by ```Size of Directory / 0x40```. The maximum number of entries supported is 2048.

### Note
The directory is conventionally placed at the end of the pack file, but this is not a strict requirement.

## Directory Entry
| Offset | Length  | Type     | Description | Notes                                                                          |
|--------|---------|----------|-------------|--------------------------------------------------------------------------------|
| 0x0000 | 56      | char[56] | File Name   | Name of the file as a null-byte padded string. Unix-style with file extension. |
| 0x0038 | 4       | int      | File Offset | Offset of the local file from the start of the pack file.                      |
| 0x003C | 4       | int      | File Size   | Size of the local file                                                       |
