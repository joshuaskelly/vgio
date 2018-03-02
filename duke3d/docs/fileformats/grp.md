# Grp File Format
The Grp file is an archive used to store resource files for the video game Duke Nukem 3D.

## Standard Grp File Layout
| Offset | Name                               |
|--------|------------------------------------|
| 0x00   | [Header](#header)                  |
| 0x10   | [Directory](#directory)            |
|        | <br><br><br> Data <br><br><br><br> |


## Header
| Offset | Size | Type     | Description           | Notes                                                   |
|--------|------|----------|-----------------------|---------------------------------------------------------|
| 0x00   | 12   | char[12] | Magic Number          | Identifies the GRP format. Should be 'KenSilverman'     |
| 0x0C   | 4    | int      | Group Entry Count     | Number of group entries.                                |

## Directory
The directory is a consecutive sequence of group entries. The size of the directory is given by ```Number of Entries * 0x10```.

## Directory Entry
| Offset  | Size  | Type     | Description       | Notes                                                     |
|---------|-------|----------|-------------------|-----------------------------------------------------------|
| 0x00    | 12    | char[12] | File Name         | Name of the file as a null-byte padded string.            |
| 0x0C    | 4     | int      | File Size         | Uncompressed size of the local file.                      |
