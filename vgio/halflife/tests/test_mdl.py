import unittest

from vgio.halflife.tests.basecase import TestCase
from vgio.halflife import mdl

significant_digits = 5


class TestMdlReadWrite(TestCase):
    def test_check_file_type(self):
        self.assertFalse(mdl.is_mdlfile('./test_data/test.bsp'))

    def test_header(self):
        h0 = mdl.Header(
            mdl.IDENTITY,
            mdl.VERSION,
            'valve/models/test.mdl',
            0,
            *(1, 2, 3),
            *(-64, -64, -64),
            *(64, 64, 64),
            *(-128, -128, -128),
            *(128, 128, 128),
            0,
            1,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            0,
            1,
            128,
            256,
            1,
            1,
            0,
            1,
            16,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0
        )

        mdl.Header.write(self.buff, h0)
        self.buff.seek(0)

        h1 = mdl.Header.read(self.buff)

        self.assertEqual(h0.identity, h1.identity, 'Identity should be equal')
        self.assertEqual(h0.version, h1.version, 'Version should be equal')
        self.assertEqual(h0.name, h1.name, 'Name should be equal')
        self.assertEqual(h0.filesize, h1.filesize, 'Filesize should be equal')
        self.assertEqual(h0.eye_position, h1.eye_position, 'Eye_position should be equal')
        self.assertEqual(h0.min, h1.min, 'Min should be equal')
        self.assertEqual(h0.max, h1.max, 'Max should be equal')
        self.assertEqual(h0.bounding_box_min, h1.bounding_box_min, 'Bounding_box_min should be equal')
        self.assertEqual(h0.bounding_box_max, h1.bounding_box_max, 'Bounding_box_max should be equal')
        self.assertEqual(h0.flags, h1.flags, 'Flags should be equal')
        self.assertEqual(h0.bone_count, h1.bone_count, 'Bone_count should be equal')
        self.assertEqual(h0.bone_offset, h1.bone_offset, 'Bone_offset should be equal')
        self.assertEqual(h0.bone_controller_count, h1.bone_controller_count, 'Bone_controller_count should be equal')
        self.assertEqual(h0.bone_controller_offset, h1.bone_controller_offset, 'Bone_controller_offset should be equal')
        self.assertEqual(h0.hitbox_count, h1.hitbox_count, 'Hitbox_count should be equal')
        self.assertEqual(h0.hitbox_offset, h1.hitbox_offset, 'Hitbox_offset should be equal')
        self.assertEqual(h0.sequence_count, h1.sequence_count, 'Sequence_count should be equal')
        self.assertEqual(h0.sequence_offset, h1.sequence_offset, 'Sequence_offset should be equal')
        self.assertEqual(h0.sequence_group_count, h1.sequence_group_count, 'Sequence_group_count should be equal')
        self.assertEqual(h0.sequence_group_offset, h1.sequence_group_offset, 'Sequence_group_offset should be equal')
        self.assertEqual(h0.texture_count, h1.texture_count, 'Texture_count should be equal')
        self.assertEqual(h0.texture_offset, h1.texture_offset, 'Texture_offset should be equal')
        self.assertEqual(h0.texture_data_offset, h1.texture_data_offset, 'Texture_data_offset should be equal')
        self.assertEqual(h0.skin_count, h1.skin_count, 'Skin_count should be equal')
        self.assertEqual(h0.skin_group_count, h1.skin_group_count, 'Skin_group_count should be equal')
        self.assertEqual(h0.skin_offset, h1.skin_offset, 'Skin_offset should be equal')
        self.assertEqual(h0.body_part_count, h1.body_part_count, 'Body_part_count should be equal')
        self.assertEqual(h0.body_part_offset, h1.body_part_offset, 'Body_part_offset should be equal')
        self.assertEqual(h0.attachment_count, h1.attachment_count, 'Attachment_count should be equal')
        self.assertEqual(h0.attachment_offset, h1.attachment_offset, 'Attachment_offset should be equal')
        self.assertEqual(h0.sound_table, h1.sound_table, 'Sound_table should be equal')
        self.assertEqual(h0.sound_index, h1.sound_index, 'Sound_index should be equal')
        self.assertEqual(h0.sound_groups, h1.sound_groups, 'Sound_groups should be equal')
        self.assertEqual(h0.sound_group_offset, h1.sound_group_offset, 'Sound_group_offset should be equal')
        self.assertEqual(h0.transition_count, h1.transition_count, 'Transition_count should be equal')
        self.assertEqual(h0.transition_offset, h1.transition_offset, 'Transition_offset should be equal')


if __name__ == '__main__':
    unittest.main()
