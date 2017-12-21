# Wad File Format
The Wad file is an archive used to store resource files for the video game Quake.

## Standard Wad File Layout
| Offset | Name |
|---|---|
| 0x00000000 | [Header](#header) |
| 0x0000000C | <br><br><br> Data <br><br><br><br> |
|            | [Directory](#directory) |

## Header
| Offset | Length | Type     | Description           | Notes                                                   |
|--------|--------|----------|------------------     |---------------------------------------------------------|
| 0x00   | 4      | char[4]  | Magic Number          | Identifies the WAD format. Should be 'WAD2'             |
| 0x04   | 4      | int      | Directory Entry Count | Number of directory entries.                            |
| 0x08   | 4      | int      | Directory Offset      | Offset of the directory from the start of the wad file. |

## Directory
The directory is a sequence of directory entries. The size of the directory is given by ```Number of Entries * 0x20```.

### Note
The directory is conventionally placed at the end of the pack file, but this is not a strict requirement.

## Directory Entry
| Offset        | Length        | Type     | Description       | Notes |
|-------------- |---------------|----------|-------------------|-------|
| 0x00          | 4             | int      | File Offset       |       |
| 0x04          | 4             | int      | Disk Size         |       |
| 0x08          | 4             | int      | File Size         |       |
| 0x0C          | 1             | char     | File Type         |       |
| 0x0D          | 1             | char     | File Compresssion |       |
| 0x0E          | 1             | char     | File Padding      |       |
| 0x0F          | 1             | char     | File Padding      |       |
| 0x10          | 16            | string   | File Name         |       |
