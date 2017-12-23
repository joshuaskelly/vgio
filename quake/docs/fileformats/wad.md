# Wad File Format
The Wad file is an archive used to store resource files for the video game Quake.

## Standard Wad File Layout
| Offset | Name                               |
|--------|------------------------------------|
| 0x00   | [Header](#header)                  |
| 0x0C   | <br><br><br> Data <br><br><br><br> |
|        | [Directory](#directory)            |

## Header
| Offset | Size | Type     | Description           | Notes                                                   |
|--------|------|----------|-----------------------|---------------------------------------------------------|
| 0x00   | 4    | char[4]  | Magic Number          | Identifies the WAD format. Should be 'WAD2'             |
| 0x04   | 4    | int      | Directory Entry Count | Number of directory entries.                            |
| 0x08   | 4    | int      | Directory Offset      | Offset of the directory from the start of the wad file. |

## Directory
The directory is a consecutive sequence of directory entries. The size of the directory is given by ```Number of Entries * 0x20```.

### Note
The directory is conventionally placed at the end of the pack file, but this is not a strict requirement.

## Directory Entry
| Offset  | Size  | Type     | Description       | Notes                                                     |
|---------|-------|----------|-------------------|-----------------------------------------------------------|
| 0x00    | 4     | int      | File Offset       | Offset of the local file from the start of the pack file. |
| 0x04    | 4     | int      | Disk Size         | Size of local file.                                       |
| 0x08    | 4     | int      | File Size         | Uncompressed size of the local file.                      |
| 0x0C    | 1     | char     | File Type         |                                                           |
| 0x0D    | 1     | char     | File Compression  |                                                           |
| 0x0E    | 1     | char     | File Padding      |                                                           |
| 0x0F    | 1     | char     | File Padding      |                                                           |
| 0x10    | 16    | char[16] | File Name         | Name of the file as a null-byte padded string.            |
