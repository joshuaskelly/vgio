# Hxmesh

## Header

| Offset | Size |      Type     |     Description     |                      Notes                      |
|--------|------|---------------|---------------------|-------------------------------------------------|
| 0x00   | 4    | int           | index_count         |  The number of triangle indexes.                |
| 0x04   | 4    | int           | vertex_count        |  The number of vertices.                        |
| 0x08   | 1    | unsigned char | vertex_size         |  The size of each vertex. Should be 32          |
| 0x09   | 1    | unsigned char | mesh_partition_flag |  Indicates if a mesh contains a mesh partition? |

## Vertex

| Offset | Size |   Type   | Description |          Notes          |
|--------|------|----------|-------------|-------------------------|
| 0x00   | 12   | float[3] | position    |  Vertex position.       |
| 0x0C   | 12   | float[3] | normal      |  Vertex normal.         |
| 0x18   | 8    | float[2] | uv          |  Vertex UV coordinates. |
