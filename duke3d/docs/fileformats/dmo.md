# Dmo File Format
The Dmo file contains demo data for the video game Duke Nukem 3D.

## Dmo Structure
| Offset | Size | Type              | Description | Notes                                 |
|--------|------|-------------------|-------------|---------------------------------------|
| 0x00   |      | [Header](#header) | Header      |                                       |
|        |      | [Data](#data)     | Data        | A sequence of LZW compressed records. |

## Header
| Offset | Size | Type         | Description       | Notes                                                                |
|--------|------|--------------|-------------------|----------------------------------------------------------------------|
| 0x000  | 4    | int          | Record Count      | Total number of records. Should be player count * total ticks        |
| 0x004  | 1    | char         | Version           | Version of the Dmo format. Should be 117                             |
| 0x005  | 1    | char         | Volume level      |                                                                      |
| 0x006  | 1    | char         | Level number      |                                                                      |
| 0x007  | 1    | char         | Player skill      |                                                                      |
| 0x008  | 1    | char         | Coop              |                                                                      |
| 0x009  | 1    | char         | FFire             |                                                                      |
| 0x00A  | 2    | short        | Multi Mode        |                                                                      |
| 0x00C  | 2    | short        | Monsters Off      |                                                                      |
| 0x00E  | 4    | int          | Respawn Monsters  |                                                                      |
| 0x012  | 4    | int          | Respawn Items     |                                                                      |
| 0x016  | 4    | int          | Respawn Inventory |                                                                      |
| 0x01A  | 4    | int          | Player AI         |                                                                      |
| 0x01E  | 512  | char[16][32] | Player Names      | A sequence of 16 player names as length 32 null-byte padded strings. |
| 0x21E  | 4    | int          | Dummy             |                                                                      |
| 0x222  | 128  | char[128]    | Map Filename      |                                                                      |
| 0x2A2  | n    | char[n]      | Player Aim Mode   |                                                                      |
| 0x2A3  | 2    | short        | leng              | Length of compressed data?                                                             |


## Data
| Offset | Size | Type     | Description    | Notes                                     |
|--------|------|----------|----------------|-------------------------------------------|
| 0x00   | 4    | int      | Version Number | Version of the Map format. Should be 7    |
