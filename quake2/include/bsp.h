struct Entities;

 // Class for representing a Bsp plane
struct Plane {
    // The normal vector to the plane.
    float normal[3];

    // The distance from world (0, 0, 0) to a point on the plane
    float distance;

    // Planes are classified as follows:
    //    0: Axial plane aligned to the x-axis.
    //    1: Axial plane aligned to the y-axis.
    //    2: Axial plane aligned to the z-axis.
    //    3: Non-axial plane roughly aligned to the x-axis.
    //    4: Non-axial plane roughly aligned to the y-axis.
    //    5: Non-axial plane roughly aligned to the z-axis.
    int type;
};

// Class for representing a Bsp Vertex
struct Vertex {
    // The x-coordinate
    float x;

    // The y-coordinate
    float y;

    // The z-coordinate
    float z;
};

struct Visibilities;

// Class for representing a node
//
// A Node is a data structure used to compose a bsp tree data structure. A
// child may be a Node or a Leaf.
struct Node {
    // The number of the plane that partitions the node.
    int plane_number;

    // A two-tuple of the two sub-spaces formed by the
    // partitioning plane.
    //
    // Note:
    //     Child 0 is the front sub-space, and child 1 is
    //     the back sub-space.
    //
    // Note:
    //     If bit 15 is set, the child is a leaf.
    int children[2];

    // The minimum coordinate of the bounding box containing
    // this node and all of its children.
    short bounding_box_min[3];

    // The maximum coordinate of the bounding box containing
    // this node and all of its children.
    short bounding_box_max[3];

    // The number of the first face in Bsp.mark_surfaces.
    unsigned short first_face;

    // The number of faces contained in the node. These are
    // stored in consecutive order in Bsp.mark_surfaces
    // starting at Node.first_face.
    unsigned short number_of_faces;
};

struct TextureInfo {
    float s[3];
    float s_offset;
    float t[3];
    float t_offset;
    int flags;
    int value;
    char texture_name[32];
    int next_texture_info;
};

struct Lump {
    int offset;
    int length;
};

struct Header {
    char identity[4];
    Lump lumps[19];
};