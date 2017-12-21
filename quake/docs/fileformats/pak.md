## Pak

| Offset  | Length | Type     | Description      | Notes           |
|---------|--------|----------|------------------|-----------------|
| 0x00    | 4      | string   | Magic Number     | Should be 'PACK'|
| 0x04    | 4      | int      | Directory Offset |                 |
| 0x08    | 4      | int      | Directory Size   |                 |
|         |        |          | Data             |                 |
|         |        |          | Directory        |                 |

### Directory Entry

| Offset  | Length | Type     | Description       | Notes |
|---------|--------|----------|-------------------|-------|
| 0x00    | 56     | string   | Filename          |       |
| 0x04    | 4      | int      | File Offset       |       |
| 0x08    | 4      | int      | File Size         |       |
