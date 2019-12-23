# HxShader File Format
The HxShader file contains GLSL shader data for the video game Devil Daggers.

## Standard HxShader File Layout
| Offset | Name                                |
|--------|-------------------------------------|
| 0x00   | [Header](#header)                   |
| 0x0C   | [Name](#name)                       |
|        | [Vertex Shader](#vertex-shader)     |
|        | [Fragment Shader](#fragment-shader) |

## Header

| Offset | Size | Type |    Description     |              Notes              |
|--------|------|------|--------------------|---------------------------------|
| 0x00   | 4    | int  | name_size          |  Length of shader name.         |
| 0x04   | 4    | int  | vertex_shader_size |  Length of the vertex shader.   |
| 0x08   | 4    | int  | frag_shader_size   |  Length of the fragment shader. |

### Name
The shader name.

### Vertex Shader
The vertex shader GLSL code.

### Fragment Shader
The fragment shader GLSL code.
