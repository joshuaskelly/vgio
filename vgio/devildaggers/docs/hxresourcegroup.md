# HxResourceGroup File Format
The HxResourceGroup file is an archive used to store resource files for the video game Devil Daggers.

## Standard Hxmesh File Layout
| Offset | Name                        |
|--------|-----------------------------|
| 0x00   | [Header](#header)           |
| 0x0C   | [Directory](#directory)     |
|        | <br><br>Data<br><br><br>    |

## Header

| Offset | Size |   Type  |  Description   |                 Notes                 |
|--------|------|---------|----------------|---------------------------------------|
| 0x00   | 8    | char[8] | signature      |  File signature. Should be :hx:rg:\01 |
| 0x08   | 4    | int     | directory_size |  Size of directory.                   |

## Directory
The directory is a consecutive sequence of [Entries](#entry). 

#### Note
The end of the directory is terminated by a null byte.

### Entry

| Offset | Size |  Type | Description |                               Notes                                |
|--------|------|-------|-------------|--------------------------------------------------------------------|
| 0x00   | 2    | short | type        |  Resource type.                                                    |
| 0x02   | n    | char  | filename    |  Resource filename as a null terminated string of variable length. |
|        | 4    | int   | file_offset |  File offset.                                                      |
|        | 4    | int   | file_size   |  File size.                                                        |
|        | 4    | int   | date_time   |  Time last modified.                                               |
