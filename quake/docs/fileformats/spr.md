# Spr File Format
The Spr file contains sprite model data for the video game Quake.

## Standard Spr File Layout
| Offset | Name |
|--------|----------|
| 0x00   | [Header](#header) |
| 0x24   | <br><br><br> [Frame Data](#frame-data) <br><br><br><br> |

## Header
| Offset | Size | Type     | Description           | Notes                                                   |
|--------|------|----------|-----------------------|---------------------------------------------------------|
| 0x00   | 4    | char[4]  | Magic Number          | Identifies the Spr format. Should be 'IDSP'             |
| 0x04   | 4    | int      | Version Number        | Version of the spr format. Should be 1                  |
| 0x08   | 4    | int      | Type                  | Type of the model. Determines orientation behavior.     |
| 0x0C   | 4    | float    | Bounding Radius       |                                                         |
| 0x10   | 4    | int      | Width                 | Width of the model.                                     |
| 0x14   | 4    | int      | Height                | Height of the model.                                    |
| 0x18   | 4    | int      | Frame Count           |                                                         |
| 0x1C   | 4    | float    | Beam Length           |                                                         |
| 0x20   | 4    | int      | Sync Type             |                                                         |

## Frame Data
The frame data chunk is a consecutive sequence of [Sprite Frames](#sprite-frame) or [Sprite Groups](#sprite-group). The first byte must be read to determine the type of frame that follows.

## Sprite Frame
| Offset  | Size  | Type     | Description       | Notes       |
|---------|-------|----------|-------------------|-------------|
| 0x00    | 4     | int      | Frame Type        | Identifies the frame type. Should be 0.   |
| 0x04    | 8     | int[2]   | Origin            |             |
| 0x0C    | 4     | int      | Width             | The width of the frame.            |
| 0x10    | 4     | char     | Height            | The height of the frame.            |
| 0x14    |       |          | Pixel Data        | A sequence of unstructured pixel data.            |

## Sprite Group
| Offset  | Size  | Type     | Description       | Notes       |
|---------|-------|----------|-------------------|-------------|
| 0x00    | 4     | int      | Frame Type        | Identifies the frame type. Should not be 0. |
| 0x04    | 8     | int      | Frame Count       |             |
| 0x08    | 4n    | float[n] | Intervals         | A sequence of n consecutive floats. |
|         |       |          | [Sprite Frames](#sprite-frame) | A sequence of n consecutive sprite frames. |
