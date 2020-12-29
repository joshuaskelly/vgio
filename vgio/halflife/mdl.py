"""This module provides file I/O for Half-Life MDL model files.

Example:
    mdl_file = mdl.Mdl.open('gordon.mdl')

References:
    FTE QuakeWorld Source
    - James Brown
    - https://sourceforge.net/p/fteqw/code/HEAD/tree/trunk/engine/gl/model_hl.h

    studiomdl
    - Christian Petersen
    - https://github.com/fnky/studiomdl/blob/master/src/studio.h
"""

import io
import struct

from vgio._core import ReadWriteFile

VERSION = 10
IDENTITY = b'IDST'


def _check_mdlfile(fp):
    fp.seek(0)
    data = fp.read(struct.calcsize('<4s'))

    return data == IDENTITY


def is_mdlfile(filename):
    """Quickly see if a file is a mdl file by checking the magic number.

    The filename argument may be a file for file-like object.

    Args:
        filename: File to check as string or file-like object.

    Returns:
        True if given file's magic number is correct.
    """
    try:
        if hasattr(filename, 'read'):
            return _check_mdlfile(fp=filename)
        else:
            with open(filename, 'rb') as fp:
                return _check_mdlfile(fp)

    except Exception:
        return False


class Header:
    """ Class for representing a Mdl file header

    Attributes:
        identity:  File identity. Should be IDST

        version:  File version. Should be 10

        name:  The model name.

        filesize:

        eye_position:

        min:

        max:

        bounding_box_min:

        bounding_box_max:

        flags:

        bone_count:

        bone_offset:

        bone_controller_count:

        bone_controller_offset:

        hitbox_count:

        hitbox_offset:

        sequence_count:

        sequence_offset:

        sequence_group_count:

        sequence_group_offset:

        texture_count:

        texture_offset:

        texture_data_offset:

        skin_count:

        skin_group_count:

        skin_offset:

        body_part_count:

        body_part_offset:

        attachment_count:

        attachment_offset:

        sound_table:

        sound_index:

        sound_groups:

        sound_group_offset:

        transition_count:

        transition_offset:
    """

    format = '<4si64si15f27i'
    size = struct.calcsize(format)

    __slots__ = (
        'identity',
        'version',
        'name',
        'filesize',
        'eye_position',
        'min',
        'max',
        'bounding_box_min',
        'bounding_box_max',
        'flags',
        'bone_count',
        'bone_offset',
        'bone_controller_count',
        'bone_controller_offset',
        'hitbox_count',
        'hitbox_offset',
        'sequence_count',
        'sequence_offset',
        'sequence_group_count',
        'sequence_group_offset',
        'texture_count',
        'texture_offset',
        'texture_data_offset',
        'skin_count',
        'skin_group_count',
        'skin_offset',
        'body_part_count',
        'body_part_offset',
        'attachment_count',
        'attachment_offset',
        'sound_table',
        'sound_index',
        'sound_groups',
        'sound_group_offset',
        'transition_count',
        'transition_offset'
    )

    def __init__(self,
                 identity,
                 version,
                 name,
                 filesize,
                 eye_position_0,
                 eye_position_1,
                 eye_position_2,
                 min_0,
                 min_1,
                 min_2,
                 max_0,
                 max_1,
                 max_2,
                 bounding_box_min_0,
                 bounding_box_min_1,
                 bounding_box_min_2,
                 bounding_box_max_0,
                 bounding_box_max_1,
                 bounding_box_max_2,
                 flags,
                 bone_count,
                 bone_offset,
                 bone_controller_count,
                 bone_controller_offset,
                 hitbox_count,
                 hitbox_offset,
                 sequence_count,
                 sequence_offset,
                 sequence_group_count,
                 sequence_group_offset,
                 texture_count,
                 texture_offset,
                 texture_data_offset,
                 skin_count,
                 skin_group_count,
                 skin_offset,
                 body_part_count,
                 body_part_offset,
                 attachment_count,
                 attachment_offset,
                 sound_table,
                 sound_index,
                 sound_groups,
                 sound_group_offset,
                 transition_count,
                 transition_offset):
        self.identity = identity.split(b'\x00')[0].decode('ascii') if type(identity) is bytes else identity
        self.version = version
        self.name = name.split(b'\x00')[0].decode('ascii') if type(name) is bytes else name
        self.filesize = filesize
        self.eye_position = eye_position_0, eye_position_1, eye_position_2
        self.min = min_0, min_1, min_2
        self.max = max_0, max_1, max_2
        self.bounding_box_min = bounding_box_min_0, bounding_box_min_1, bounding_box_min_2
        self.bounding_box_max = bounding_box_max_0, bounding_box_max_1, bounding_box_max_2
        self.flags = flags
        self.bone_count = bone_count
        self.bone_offset = bone_offset
        self.bone_controller_count = bone_controller_count
        self.bone_controller_offset = bone_controller_offset
        self.hitbox_count = hitbox_count
        self.hitbox_offset = hitbox_offset
        self.sequence_count = sequence_count
        self.sequence_offset = sequence_offset
        self.sequence_group_count = sequence_group_count
        self.sequence_group_offset = sequence_group_offset
        self.texture_count = texture_count
        self.texture_offset = texture_offset
        self.texture_data_offset = texture_data_offset
        self.skin_count = skin_count
        self.skin_group_count = skin_group_count
        self.skin_offset = skin_offset
        self.body_part_count = body_part_count
        self.body_part_offset = body_part_offset
        self.attachment_count = attachment_count
        self.attachment_offset = attachment_offset
        self.sound_table = sound_table
        self.sound_index = sound_index
        self.sound_groups = sound_groups
        self.sound_group_offset = sound_group_offset
        self.transition_count = transition_count
        self.transition_offset = transition_offset

    @classmethod
    def write(cls, file, header):
        header_data = struct.pack(
            cls.format,
            header.identity.encode('ascii'),
            header.version,
            header.name.encode('ascii'),
            header.filesize,
            *header.eye_position,
            *header.min,
            *header.max,
            *header.bounding_box_min,
            *header.bounding_box_max,
            header.flags,
            header.bone_count,
            header.bone_offset,
            header.bone_controller_count,
            header.bone_controller_offset,
            header.hitbox_count,
            header.hitbox_offset,
            header.sequence_count,
            header.sequence_offset,
            header.sequence_group_count,
            header.sequence_group_offset,
            header.texture_count,
            header.texture_offset,
            header.texture_data_offset,
            header.skin_count,
            header.skin_group_count,
            header.skin_offset,
            header.body_part_count,
            header.body_part_offset,
            header.attachment_count,
            header.attachment_offset,
            header.sound_table,
            header.sound_index,
            header.sound_groups,
            header.sound_group_offset,
            header.transition_count,
            header.transition_offset
        )

        file.write(header_data)

    @classmethod
    def read(cls, file):
        header_data = file.read(cls.size)
        header_struct = struct.unpack(cls.format, header_data)

        return Header(*header_struct)


class Bone:
    """

    Attributes:
        name:

        parent:  Parent bone

        flags:

        bone_controller:

        value:

        scale:
    """

    format = '<32s8i12f'
    size = struct.calcsize(format)

    __slots__ = (
        'name',
        'parent',
        'flags',
        'bone_controller',
        'value',
        'scale'
    )

    def __init__(self,
                 name,
                 parent,
                 flags,
                 bone_controller_0,
                 bone_controller_1,
                 bone_controller_2,
                 bone_controller_3,
                 bone_controller_4,
                 bone_controller_5,
                 value_0,
                 value_1,
                 value_2,
                 value_3,
                 value_4,
                 value_5,
                 scale_0,
                 scale_1,
                 scale_2,
                 scale_3,
                 scale_4,
                 scale_5):
        self.name = name.split(b'\x00')[0].decode('ascii') if type(name) is bytes else name
        self.parent = parent
        self.flags = flags
        self.bone_controller = bone_controller_0, bone_controller_1, bone_controller_2, bone_controller_3, bone_controller_4, bone_controller_5
        self.value = value_0, value_1, value_2, value_3, value_4, value_5
        self.scale = scale_0, scale_1, scale_2, scale_3, scale_4, scale_5

    @classmethod
    def write(cls, file, bone):
        bone_data = struct.pack(
            cls.format,
            bone.name.encode('ascii'),
            bone.parent,
            bone.flags,
            *bone.bone_controller,
            *bone.value,
            *bone.scale
        )

        file.write(bone_data)

    @classmethod
    def read(cls, file):
        bone_data = file.read(cls.size)
        bone_struct = struct.unpack(cls.format, bone_data)

        return Bone(*bone_struct)


class BoneController:
    """

    Attributes:
        bone:

        type:

        start:

        end:

        rest:

        index:
    """

    format = '<2i2f2i'
    size = struct.calcsize(format)

    __slots__ = (
        'bone',
        'type',
        'start',
        'end',
        'rest',
        'index'
    )

    def __init__(self,
                 bone,
                 type_,
                 start,
                 end,
                 rest,
                 index):
        self.bone = bone
        self.type = type_
        self.start = start
        self.end = end
        self.rest = rest
        self.index = index

    @classmethod
    def write(cls, file, bonecontroller):
        bonecontroller_data = struct.pack(
            cls.format,
            bonecontroller.bone,
            bonecontroller.type,
            bonecontroller.start,
            bonecontroller.end,
            bonecontroller.rest,
            bonecontroller.index
        )

        file.write(bonecontroller_data)

    @classmethod
    def read(cls, file):
        bonecontroller_data = file.read(cls.size)
        bonecontroller_struct = struct.unpack(cls.format, bonecontroller_data)

        return BoneController(*bonecontroller_struct)


class HitBox:
    """

    Attributes:
        bone:

        group:

        bounding_box_min:

        bounding_box_max:
    """

    format = '<2i6f'
    size = struct.calcsize(format)

    __slots__ = (
        'bone',
        'group',
        'bounding_box_min',
        'bounding_box_max'
    )

    def __init__(self,
                 bone,
                 group,
                 bounding_box_min_0,
                 bounding_box_min_1,
                 bounding_box_min_2,
                 bounding_box_max_0,
                 bounding_box_max_1,
                 bounding_box_max_2):
        self.bone = bone
        self.group = group
        self.bounding_box_min = bounding_box_min_0, bounding_box_min_1, bounding_box_min_2
        self.bounding_box_max = bounding_box_max_0, bounding_box_max_1, bounding_box_max_2

    @classmethod
    def write(cls, file, hitbox):
        hitbox_data = struct.pack(
            cls.format,
            hitbox.bone,
            hitbox.group,
            *hitbox.bounding_box_min,
            *hitbox.bounding_box_max
        )

        file.write(hitbox_data)

    @classmethod
    def read(cls, file):
        hitbox_data = file.read(cls.size)
        hitbox_struct = struct.unpack(cls.format, hitbox_data)

        return HitBox(*hitbox_struct)


class Sequence:
    """

    Attributes:
        identity:

        version:

        name:

        length:
    """

    format = '<4si64si'
    size = struct.calcsize(format)

    __slots__ = (
        'identity',
        'version',
        'name',
        'length'
    )

    def __init__(self,
                 identity,
                 version,
                 name,
                 length):
        self.identity = identity.split(b'\x00')[0].decode('ascii') if type(identity) is bytes else identity
        self.version = version
        self.name = name.split(b'\x00')[0].decode('ascii') if type(name) is bytes else name
        self.length = length

    @classmethod
    def write(cls, file, sequence):
        sequence_data = struct.pack(
            cls.format,
            sequence.identity.encode('ascii'),
            sequence.version,
            sequence.name.encode('ascii'),
            sequence.length
        )

        file.write(sequence_data)

    @classmethod
    def read(cls, file):
        sequence_data = file.read(cls.size)
        sequence_struct = struct.unpack(cls.format, sequence_data)

        return Sequence(*sequence_struct)


class SequenceGroup:
    """

    Attributes:
        label:

        name:

        cache:

        data:
    """

    format = '<32s64sIi'
    size = struct.calcsize(format)

    __slots__ = (
        'label',
        'name',
        'cache',
        'data'
    )

    def __init__(self,
                 label,
                 name,
                 cache,
                 data):
        self.label = label.split(b'\x00')[0].decode('ascii') if type(label) is bytes else label
        self.name = name.split(b'\x00')[0].decode('ascii') if type(name) is bytes else name
        self.cache = cache
        self.data = data

    @classmethod
    def write(cls, file, sequencegroup):
        sequencegroup_data = struct.pack(
            cls.format,
            sequencegroup.label.encode('ascii'),
            sequencegroup.name.encode('ascii'),
            sequencegroup.cache,
            sequencegroup.data
        )

        file.write(sequencegroup_data)

    @classmethod
    def read(cls, file):
        sequencegroup_data = file.read(cls.size)
        sequencegroup_struct = struct.unpack(cls.format, sequencegroup_data)

        return SequenceGroup(*sequencegroup_struct)


class Texture:
    """

    Attributes:
        name:

        flags:

        width:

        height:

        index:
    """

    format = '<64s4i'
    size = struct.calcsize(format)

    __slots__ = (
        'name',
        'flags',
        'width',
        'height',
        'index'
    )

    def __init__(self,
                 name,
                 flags,
                 width,
                 height,
                 index):
        self.name = name.split(b'\x00')[0].decode('ascii') if type(name) is bytes else name
        self.flags = flags
        self.width = width
        self.height = height
        self.index = index

    @classmethod
    def write(cls, file, texture):
        texture_data = struct.pack(
            cls.format,
            texture.name.encode('ascii'),
            texture.flags,
            texture.width,
            texture.height,
            texture.index
        )

        file.write(texture_data)

    @classmethod
    def read(cls, file):
        texture_data = file.read(cls.size)
        texture_struct = struct.unpack(cls.format, texture_data)

        return Texture(*texture_struct)


class BodyPart:
    """

    Attributes:
        name:

        model_count:

        base:

        model_offset:
    """

    format = '<64s3i'
    size = struct.calcsize(format)

    __slots__ = (
        'name',
        'model_count',
        'base',
        'model_offset',
        'models'
    )

    def __init__(self,
                 name,
                 model_count,
                 base,
                 model_offset):
        self.name = name.split(b'\x00')[0].decode('ascii') if type(name) is bytes else name
        self.model_count = model_count
        self.base = base
        self.model_offset = model_offset

    @classmethod
    def write(cls, file, bodypart):
        bodypart_data = struct.pack(
            cls.format,
            bodypart.name.encode('ascii'),
            bodypart.model_count,
            bodypart.base,
            bodypart.model_offset
        )

        file.write(bodypart_data)

    @classmethod
    def read(cls, file):
        bodypart_data = file.read(cls.size)
        bodypart_struct = struct.unpack(cls.format, bodypart_data)

        bp = BodyPart(*bodypart_struct)

        offset = file.tell()

        file.seek(bp.model_offset)
        bp.models = tuple(Model.read(file) for _ in range(bp.model_count))

        file.seek(offset)

        return bp


class Model:
    """

    Attributes:
        name:

        type:

        radius:

        mesh_count:

        mesh_offset:

        vertex_count:

        vertex_info_offset:

        vertex_offset:

        normal_count:

        normal_info_offset:

        normal_offset:

        group_count:

        group_offset:
    """

    format = '<64sif10i'
    size = struct.calcsize(format)

    __slots__ = (
        'name',
        'type',
        'radius',
        'mesh_count',
        'mesh_offset',
        'vertex_count',
        'vertex_info_offset',
        'vertex_offset',
        'normal_count',
        'normal_info_offset',
        'normal_offset',
        'group_count',
        'group_offset',
        'vertexes',
        'normals',
        'meshes'
    )

    def __init__(self,
                 name,
                 type_,
                 radius,
                 mesh_count,
                 mesh_offset,
                 vertex_count,
                 vertex_info_offset,
                 vertex_offset,
                 normal_count,
                 normal_info_offset,
                 normal_offset,
                 group_count,
                 group_offset):
        self.name = name.split(b'\x00')[0].decode('ascii') if type(name) is bytes else name
        self.type = type_
        self.radius = radius
        self.mesh_count = mesh_count
        self.mesh_offset = mesh_offset
        self.vertex_count = vertex_count
        self.vertex_info_offset = vertex_info_offset
        self.vertex_offset = vertex_offset
        self.normal_count = normal_count
        self.normal_info_offset = normal_info_offset
        self.normal_offset = normal_offset
        self.group_count = group_count
        self.group_offset = group_offset

    @classmethod
    def write(cls, file, model):
        model_data = struct.pack(
            cls.format,
            model.name.encode('ascii'),
            model.type,
            model.radius,
            model.mesh_count,
            model.mesh_offset,
            model.vertex_count,
            model.vertex_info_offset,
            model.vertex_offset,
            model.normal_count,
            model.normal_info_offset,
            model.normal_offset,
            model.group_count,
            model.group_offset
        )

        file.write(model_data)

    @classmethod
    def read(cls, file):
        model_data = file.read(cls.size)
        model_struct = struct.unpack(cls.format, model_data)

        m = Model(*model_struct)

        offset = file.tell()

        file.seek(m.mesh_offset)
        m.meshes = tuple(Mesh.read(file) for _ in range(m.mesh_count))

        file.seek(m.vertex_offset)
        format = '<fff'
        size = struct.calcsize(format)

        m.vertexes = tuple(struct.unpack(format, file.read(size)) for _ in range(m.vertex_count))

        file.seek(m.normal_offset)
        m.normals = tuple(struct.unpack(format, file.read(size)) for _ in range(m.normal_count))

        file.seek(offset)

        return m


class Mesh:
    """

    Attributes:
        triangle_count:

        triangle_offset:

        skin_index:

        normal_count:

        normal_offset:
    """

    format = '<5i'
    size = struct.calcsize(format)

    __slots__ = (
        'triangle_count',
        'triangle_offset',
        'skin_index',
        'normal_count',
        'normal_offset',
        'triangles',
        'normals'
    )

    def __init__(self,
                 triangle_count,
                 triangle_offset,
                 skin_index,
                 normal_count,
                 normal_offset):
        self.triangle_count = triangle_count
        self.triangle_offset = triangle_offset
        self.skin_index = skin_index
        self.normal_count = normal_count
        self.normal_offset = normal_offset

    @classmethod
    def write(cls, file, mesh):
        mesh_data = struct.pack(
            cls.format,
            mesh.triangle_count,
            mesh.triangle_offset,
            mesh.skin_index,
            mesh.normal_count,
            mesh.normal_offset
        )

        file.write(mesh_data)

    @classmethod
    def read(cls, file):
        mesh_data = file.read(cls.size)
        mesh_struct = struct.unpack(cls.format, mesh_data)

        m = Mesh(*mesh_struct)

        offset = file.tell()

        file.seek(m.triangle_offset)
        m.triangles = tuple(TriVertex.read(file) for _ in range(m.triangle_count))

        file.seek(m.normal_offset)
        #format = '<fff'
        #size = struct.calcsize(format)
        #m.normals = tuple(struct.unpack(format, file.read(size)) for _ in range(m.normal_count))

        file.seek(offset)

        return m


class TriVertex:
    """

    Attributes:
        vertex_index:

        normal_index:

        s:

        t:
    """

    format = '<4h'
    size = struct.calcsize(format)

    __slots__ = (
        'vertex_index',
        'normal_index',
        's',
        't'
    )

    def __init__(self,
                 vertex_index,
                 normal_index,
                 s,
                 t):
        self.vertex_index = vertex_index
        self.normal_index = normal_index
        self.s = s
        self.t = t

    @classmethod
    def write(cls, file, trivertex):
        trivertex_data = struct.pack(
            cls.format,
            trivertex.vertex_index,
            trivertex.normal_index,
            trivertex.s,
            trivertex.t
        )

        file.write(trivertex_data)

    @classmethod
    def read(cls, file):
        trivertex_data = file.read(cls.size)
        trivertex_struct = struct.unpack(cls.format, trivertex_data)

        return TriVertex(*trivertex_struct)


class Attachment:
    """

    Attributes:
        name:

        type:

        bone:

        origin:

        vector_0:

        vector_1:

        vector_2:
    """

    format = '<32s2i12f'
    size = struct.calcsize(format)

    __slots__ = (
        'name',
        'type',
        'bone',
        'origin',
        'vector_0',
        'vector_1',
        'vector_2'
    )

    def __init__(self,
                 name,
                 type_,
                 bone,
                 origin_0,
                 origin_1,
                 origin_2,
                 vector_0_0,
                 vector_0_1,
                 vector_0_2,
                 vector_1_0,
                 vector_1_1,
                 vector_1_2,
                 vector_2_0,
                 vector_2_1,
                 vector_2_2):
        self.name = name.split(b'\x00')[0].decode('ascii') if type(name) is bytes else name
        self.type = type_
        self.bone = bone
        self.origin = origin_0, origin_1, origin_2
        self.vector_0 = vector_0_0, vector_0_1, vector_0_2
        self.vector_1 = vector_1_0, vector_1_1, vector_1_2
        self.vector_2 = vector_2_0, vector_2_1, vector_2_2

    @classmethod
    def write(cls, file, attachment):
        attachment_data = struct.pack(
            cls.format,
            attachment.name.encode('ascii'),
            attachment.type,
            attachment.bone,
            *attachment.origin,
            *attachment.vector_0,
            *attachment.vector_1,
            *attachment.vector_2
        )

        file.write(attachment_data)

    @classmethod
    def read(cls, file):
        attachment_data = file.read(cls.size)
        attachment_struct = struct.unpack(cls.format, attachment_data)

        return Attachment(*attachment_struct)


class Mdl(ReadWriteFile):
    def __init__(self):
        super().__init__()

        self.identity = IDENTITY
        self.version = VERSION

        self.bones = []
        self.bone_controllers = []
        self.hit_boxes = []
        self.sequences = []
        self.sequence_groups = []
        self.textures = []
        self.body_parts = []
        self.attachments = []

    @classmethod
    def _read_file(cls, file, mode):
        def _read_chunk(class_, offset, count):
            file.seek(offset)

            return tuple(class_.read(file) for _ in range(count))

        mdl = cls()
        header = Header.read(file)

        mdl.bones = _read_chunk(Bone, header.bone_offset, header.bone_count)
        mdl.bone_controllers = _read_chunk(BoneController, header.bone_controller_offset, header.bone_controller_count)
        mdl.hit_boxes = _read_chunk(HitBox, header.hitbox_offset, header.hitbox_count)
        mdl.sequences = _read_chunk(Sequence, header.sequence_offset, header.sequence_count)
        mdl.sequence_groups = _read_chunk(SequenceGroup, header.sequence_group_offset, header.sequence_group_count)
        mdl.textures = _read_chunk(Texture, header.texture_offset, header.texture_count)
        mdl.body_parts = _read_chunk(BodyPart, header.body_part_offset, header.body_part_count)
        mdl.attachments = _read_chunk(Attachment, header.attachment_offset, header.attachment_count)

        return mdl
