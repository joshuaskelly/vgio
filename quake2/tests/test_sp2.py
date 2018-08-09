import unittest

from tests.basecase import TestCase
from quake2 import sp2

significant_digits = 5


class TestSp2ReadWrite(TestCase):
    def test_sprite_frame(self):
        width = 16
        height = 16
        origin = -8, 8
        name = '/sprites/s_bubble.sp2'

        sf0 = sp2.SpriteFrame(width,
                              height,
                              *origin,
                              name)

        sp2.SpriteFrame.write(self.buff, sf0)
        self.buff.seek(0)

        sf1 = sp2.SpriteFrame.read(self.buff)

        self.assertEqual(sf0.width, sf1.width, 'Width should be equal')
        self.assertEqual(sf0.height, sf1.height, 'Height should be equal')
        self.assertEqual(sf0.origin, sf1.origin, 'Origin should be equal')
        self.assertEqual(sf0.name, sf1.name, 'Name should be equal')

    def test_sp2(self):
        identity = b'IDS2'
        version = 2
        number_of_frames = 2
        frame = sp2.SpriteFrame(16, 16, -8, 8, '/sprites/s_bubble.sp2')
        frames = frame, frame

        s0 = sp2.Sp2(identity,
                     version,
                     number_of_frames,
                     frames)

        sp2.Sp2.write(self.buff, s0)
        self.buff.seek(0)

        s1 = sp2.Sp2.read(self.buff)

        self.assertEqual(s0.identity, s1.identity, 'Identity should be equal')
        self.assertEqual(s0.version, s1.version, 'Version should be equal')
        self.assertEqual(s0.number_of_frames, s1.number_of_frames, 'Number_of_frames should be equal')

        for sf0, sf1 in zip(s0.frames, s1.frames):
            self.assertEqual(sf0.width, sf1.width, 'Width should be equal')
            self.assertEqual(sf0.height, sf1.height, 'Height should be equal')
            self.assertEqual(sf0.origin, sf1.origin, 'Origin should be equal')
            self.assertEqual(sf0.name, sf1.name, 'Name should be equal')

if __name__ == '__main__':
    unittest.main()