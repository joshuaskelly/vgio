// Class for representing a Md2 file header
struct Header {
    // File identity. Should be IDP2
    char identity[4];

    // File version. Should be 8
    int version;

    // Width of the skin in pixels
    int skin_width;

    // Height of the skin in pixels
    int skin_height;

    // Size of the frame struct in bytes
    int frame_size;

    // The number of skin
    int number_of_skins;

    // The number of vertexes
    int number_of_vertexes;

    // The number of ST Vertexes
    int number_of_st_vertexes;

    // The number of triangles
    int number_of_triangles;

    // The number of Gl commands
    int number_of_gl_commands;

    // The number of frames
    int number_of_frames;

    // Skin data offset from start of file
    int skin_offset;

    // St Vertex data offset from start of file
    int st_vertex_offset;

    // Triangle data offset from start of file
    int triangle_offset;

    // Frame data offset from start of file
    int frame_offset;

    // Gl Command offset from start of file
    int gl_command_offset;

    // Offset to end of file
    int end_offset;
};

// Class for representing a Skin
struct Skin {
    // The path of the skin file.
    char name[64];
};

/*
 * Class for representing a TriVertex
 *
 * A TriVertex is a set of XYZ coordinates and a light normal index.
 *
 * Note:
 *     The XYZ coordinates are packed into a (0, 0, 0) to (255, 255, 255)
 *     local space. The actual position can be calculated:
 *
 *     position = (packed_vertex * frame.scale) + frame.translate
 *
 * Note:
 *      The light normal index is an index into a set of pre-calculated normal
 *      vectors.
 */
struct TriVertex {
    // The x-coordinate
    unsigned char x;

    // The y-coordinate
    unsigned char y;

    // The z-coordinate
    unsigned char z;

    // The index for the pre-calculated normal vector of this vertex used for lighting.
    unsigned char light_normal_index;
};

/*
 * Class for representing an st vertex
 *
 * StVertices are similar to UV coordinates but are expressed in terms of
 * surface space and span (0,0) to (texture_width, texture_height).

 * Note:
 *     If an StVertex lies on a seam and belongs to a back facing triangle,
 *     the s-component must be incremented by half of the skin width.
 */
struct StVertex {
    // The x-coordinate on the skin image
    short s;

    // The y-coordinate on the skin image
    short t;
};

/*
 * Class for representing a triangle
 *
 *  Note:
 *      The triangle winding direction is clockwise.
 */
struct Triangle {
    // A triple of Vertex indexes. XYZ data can be obtained by from the current Frame.
    short vertexes[3];

    // A triple of St Vertex indexes
    short st_vertexes[3];
};

/*
 * Class for represting a Frame
 *
 * A Frame is an object that represents the state of the model at a single
 *  frame of animation.
 */
struct Frame {
    // The frame scale
    float scale[3];

    // The frame offset
    float translate[3];

    // The frame name
    char name[16];
};

struct GlVertex {
    float s;
    float t;
    int i;
};