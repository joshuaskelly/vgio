# Hxresourcegroup

## Header

| Offset | Size |   Type  |  Description   |                 Notes                 |
|--------|------|---------|----------------|---------------------------------------|
| 0x00   | 8    | char[8] | signature      |  File signature. Should be :hx:rg:\01 |
| 0x08   | 4    | int     | directory_size |  Size of directory.                   |

## Entry

| Offset | Size |  Type | Description |                               Notes                                |
|--------|------|-------|-------------|--------------------------------------------------------------------|
| 0x00   | 2    | short | type        |  Resource type.                                                    |
| 0x02   | n    | char  | filename    |  Resource filename as a null terminated string of variable length. |
|        | 4    | int   | file_offset |  File offset.                                                      |
|        | 4    | int   | file_size   |  File size.                                                        |
|        | 4    | int   | date_time   |  Time last modified.                                               |
