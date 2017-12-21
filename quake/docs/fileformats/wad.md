## Wad

| Offset        | Length        | Type     | Description      | Notes           |
|---------------|---------------|----------|------------------|-----------------|
| 0x00          | 4             | string   | Magic Number     | Should be 'WAD2'|
| 0x04          | 4             | int      | File Entry Count |                 |
| 0x08          | 4             | int      | Directory Offset |                 |
|               |               |          | Data             |                 |
|               |               |          | Directory        |                 |

### Directory Entry

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
