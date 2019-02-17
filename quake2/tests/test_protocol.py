import io
import unittest

from tests.basecase import TestCase
from quake2 import protocol

significant_digits = 5
angle_resolution = 360 / 256


class TestProtocolReadWrite(TestCase):
    def test_bad_message(self):
        protocol.Bad.write(self.buff)
        self.buff.seek(0)
        protocol.Bad.read(self.buff)

    def test_muzzle_flash(self):
        entity = 0
        weapon = 4
        mf0 = protocol.MuzzleFlash(entity, weapon)

        protocol.MuzzleFlash.write(self.buff, mf0)
        self.buff.seek(0)

        mf1 = protocol.MuzzleFlash.read(self.buff)

        self.assertEqual(mf0.entity, mf1.entity, 'Entity should be equal')
        self.assertEqual(mf0.weapon, mf1.weapon, 'Weapon should be equal')

    def test_muzzle_flash2(self):
        entity = 128
        flash_number = 64
        mf0 = protocol.MuzzleFlash2(entity, flash_number)

        protocol.MuzzleFlash2.write(self.buff, mf0)
        self.buff.seek(0)

        mf1 = protocol.MuzzleFlash2.read(self.buff)

        self.assertEqual(mf0.entity, mf1.entity, 'Entity should be equal')
        self.assertEqual(mf0.flash_number, mf1.flash_number, 'Flash number should be equal')

    def test_temp_entity_particles(self):
        type = protocol.TE_BLOOD
        position = 0, 0, 0
        direction = 16

        te0 = protocol.TempEntity(type,
                                  position,
                                  direction)

        protocol.TempEntity.write(self.buff, te0)
        self.buff.seek(0)

        te1 = protocol.TempEntity.read(self.buff)

        self.assertEqual(te0.position, te1.position, 'Position should be equal')
        self.assertEqual(te0.direction, te1.direction, 'Direction should be equal')

    def test_temp_entity_splashes(self):
        type = protocol.TE_SPLASH
        count = 8
        position = -16, 255, 0
        direction = 16

        te0 = protocol.TempEntity(type,
                                  count,
                                  position,
                                  direction)

        protocol.TempEntity.write(self.buff, te0)
        self.buff.seek(0)

        te1 = protocol.TempEntity.read(self.buff)

        self.assertEqual(te0.count, te1.count, 'Count should be equal')
        self.assertEqual(te0.position, te1.position, 'Position should be equal')
        self.assertEqual(te0.direction, te1.direction, 'Direction should be equal')

    def test_temp_entity_blue_hyperblaster(self):
        type = protocol.TE_BLUEHYPERBLASTER
        position = 0, 0, 0
        direction = -0.5, 0.0, 0.75

        te0 = protocol.TempEntity(type,
                                  position,
                                  direction)

        protocol.TempEntity.write(self.buff, te0)
        self.buff.seek(0)

        te1 = protocol.TempEntity.read(self.buff)

        self.assertEqual(te0.position, te1.position, 'Position should be equal')
        self.assertEqual(te0.direction, te1.direction, 'Direction should be equal')

    def test_temp_entity_trails(self):
        type = protocol.TE_RAILTRAIL
        position = 0, 0, 0
        position2 = 16, -128, 255

        te0 = protocol.TempEntity(type,
                                  position,
                                  position2)

        protocol.TempEntity.write(self.buff, te0)
        self.buff.seek(0)

        te1 = protocol.TempEntity.read(self.buff)

        self.assertEqual(te0.position, te1.position, 'Position should be equal')
        self.assertEqual(te0.position2, te1.position2, 'Position2 should be equal')

    def test_temp_entity_explosions(self):
        type = protocol.TE_EXPLOSION1
        position = 0, 0, 0

        te0 = protocol.TempEntity(type, position)

        protocol.TempEntity.write(self.buff, te0)
        self.buff.seek(0)

        te1 = protocol.TempEntity.read(self.buff)

        self.assertEqual(te0.position, te1.position, 'Position should be equal')

    def test_temp_entity_raise(self):
        with self.assertRaises(TypeError, msg='Should raise if __init__ called with too few args'):
            protocol.TempEntity(protocol.TE_BLOOD)

        with self.assertRaises(TypeError, msg='Should raise if __init__ called with too many args'):
            position = 0, 0, 0
            bad_arg = 16
            protocol.TempEntity(protocol.TE_EXPLOSION1,
                                position,
                                bad_arg)

    def test_layout(self):
        text = 'xv 32 yv 8 picn help'
        l0 = protocol.Layout(text)

        protocol.Layout.write(self.buff, l0)
        self.buff.seek(0)

        l1 = protocol.Layout.read(self.buff)

        self.assertEqual(l0.text, l1.text, 'Text should be equal')

    def test_inventory(self):
        inventory = [i << 7 for i in range(256)]
        i0 = protocol.Inventory(inventory)

        protocol.Inventory.write(self.buff, i0)
        self.buff.seek(0)

        i1 = protocol.Inventory.read(self.buff)

        self.assertEqual(tuple(i0.inventory), tuple(i1.inventory), 'Inventories should be equal')

    def test_nop_message(self):
        protocol.Nop.write(self.buff)
        self.buff.seek(0)
        protocol.Nop.read(self.buff)

    def test_disconnect_message(self):
        protocol.Disconnect.write(self.buff)
        self.buff.seek(0)
        protocol.Disconnect.read(self.buff)

    def test_reconnect_message(self):
        protocol.Reconnect.write(self.buff)
        self.buff.seek(0)
        protocol.Reconnect.read(self.buff)

    def test_sound_no_optional_args(self):
        flags = 0
        sound_number = 64
        s0 = protocol.Sound(flags, sound_number)

        protocol.Sound.write(self.buff, s0)
        self.buff.seek(0)

        s1 = protocol.Sound.read(self.buff)

        self.assertEqual(s0.flags, s1.flags, 'Flags should be equal')
        self.assertEqual(s0.sound_number, s1.sound_number, 'Sound_number should be equal')
        self.assertEqual(s0.volume, s1.volume, 'Volume should be equal')
        self.assertEqual(s0.attenuation, s1.attenuation, 'Attenuation should be equal')
        self.assertEqual(s0.offset, s1.offset, 'Offset should be equal')
        self.assertEqual(s0.channel, s1.channel, 'Channel should be equal')
        self.assertEqual(s0.entity, s1.entity, 'Entity should be equal')
        self.assertEqual(s0.position, s1.position, 'Position should be equal')

    def test_sound_all_optional_args(self):
        flags = 31
        sound_number = 0
        volume = 127 / 255
        attenuation = 2
        offset = 0
        channel = 7
        entity = 127
        position = 128, -128, 0

        s0 = protocol.Sound(flags,
                            sound_number,
                            volume,
                            attenuation,
                            offset,
                            channel,
                            entity,
                            position)

        protocol.Sound.write(self.buff, s0)
        self.buff.seek(0)

        s1 = protocol.Sound.read(self.buff)

        self.assertEqual(s0.flags, s1.flags, 'Flags should be equal')
        self.assertEqual(s0.sound_number, s1.sound_number, 'Sound_number should be equal')
        self.assertAlmostEqual(s0.volume, s1.volume, significant_digits, 'Volume should be equal')
        self.assertEqual(s0.attenuation, s1.attenuation, 'Attenuation should be equal')
        self.assertEqual(s0.offset, s1.offset, 'Offset should be equal')
        self.assertEqual(s0.channel, s1.channel, 'Channel should be equal')
        self.assertEqual(s0.entity, s1.entity, 'Entity should be equal')
        self.assertEqual(s0.position, s1.position, 'Position should be equal')

    def test_print(self):
        level = 3
        text = 'This is a test message!'
        p0 = protocol.Print(level, text)

        protocol.Print.write(self.buff, p0)
        self.buff.seek(0)

        p1 = protocol.Print.read(self.buff)

        self.assertEqual(p0.level, p1.level, 'Level should be the same')
        self.assertEqual(p0.text, p1.text, 'Text should be the same')

    def test_stuff_text(self):
        text = '+forward'

        t0 = protocol.StuffText(text)
        protocol.StuffText.write(self.buff, t0)
        self.buff.seek(0)

        t1 = protocol.StuffText.read(self.buff)

        self.assertEqual(t0.text, t1.text, 'Text should be equal')

    def test_server_data(self):
        protocol_version = 25
        server_count = 1
        attract_loop = 0
        game_directory = ''
        player_number = 1
        map_name = 'base1.bsp'

        sd0 = protocol.ServerData(protocol_version,
                                  server_count,
                                  attract_loop,
                                  game_directory,
                                  player_number,
                                  map_name)

        protocol.ServerData.write(self.buff, sd0)
        self.buff.seek(0)

        sd1 = protocol.ServerData.read(self.buff)

        self.assertEqual(sd0.protocol_version, sd1.protocol_version, 'Protocol_version should be equal')
        self.assertEqual(sd0.server_count, sd1.server_count, 'Server_count should be equal')
        self.assertEqual(sd0.attract_loop, sd1.attract_loop, 'Attract_loop should be equal')
        self.assertEqual(sd0.game_directory, sd1.game_directory, 'Game_directory should be equal')
        self.assertEqual(sd0.player_number, sd1.player_number, 'Player_number should be equal')
        self.assertEqual(sd0.map_name, sd1.map_name, 'Map_name should be equal')

    def test_config_string(self):
        index = 0
        text = 'Test text'

        cs0 = protocol.ConfigString(index, text)

        protocol.ConfigString.write(self.buff, cs0)
        self.buff.seek(0)

        cs1 = protocol.ConfigString.read(self.buff)

        self.assertEqual(cs0.index, cs1.index, 'Index should be equal')
        self.assertEqual(cs0.text, cs1.text, 'Text should be equal')

    def test_spawn_baseline_no_optional_data(self):
        number = 16
        origin_x = 0.0
        origin_y = 22.5
        angle_y = -45.0
        angle_z = 12.125
        frame = 4
        event = 1

        sb0 = protocol.SpawnBaseline(number=number,
                                     origin_x=origin_x,
                                     origin_y=origin_y,
                                     angles_y=angle_y,
                                     angles_z=angle_z,
                                     frame=frame,
                                     event=event)

        protocol.SpawnBaseline.write(self.buff, sb0)
        self.buff.seek(0)

        sb1 = protocol.SpawnBaseline.read(self.buff)

        self.assertEqual(sb0.number, sb1.number, 'Number should be equal')
        self.assertEqual(sb0.origin, sb1.origin, 'origin_x should be equal')

        angle_error_y = abs(sb0.angles[1] - sb1.angles[1])
        self.assertLessEqual(angle_error_y, angle_resolution, 'Angles should be within %s degrees of error' % angle_resolution)

        angle_error_z = abs(sb0.angles[2] - sb1.angles[2])
        self.assertLessEqual(angle_error_z, angle_resolution, 'Angles should be within %s degrees of error' % angle_resolution)

        self.assertEqual(sb0.frame, sb1.frame, 'frame should be equal')
        self.assertEqual(sb0.event, sb1.event, 'event should be equal')

    def test_spawn_baseline_morebits1_optional_data(self):
        number = 300
        origin_z = 12.5
        angle_x = 6.25
        model_index = 1
        render_fx = 4
        effects = 2

        sb0 = protocol.SpawnBaseline(number=number,
                                     origin_z=origin_z,
                                     angles_x=angle_x,
                                     model_index=model_index,
                                     render_fx=render_fx,
                                     effects=effects)

        protocol.SpawnBaseline.write(self.buff, sb0)
        self.buff.seek(0)

        sb1 = protocol.SpawnBaseline.read(self.buff)

        self.assertEqual(sb0.number, sb1.number, 'Number should be equal')
        self.assertEqual(sb0.origin, sb1.origin, 'Origins should be equal')

        angle_error_x = abs(sb0.angles[0] - sb1.angles[0])
        self.assertLessEqual(angle_error_x, angle_resolution, 'Angles should be within %s degrees of error' % angle_resolution)

        self.assertEqual(sb0.model_index, sb1.model_index, 'Model indices should be equal')
        self.assertEqual(sb0.render_fx, sb1.render_fx, 'Render FX values should be equal')
        self.assertEqual(sb0.effects, sb1.effects, 'Effect values should be equal')

    def test_spawn_baseline_morebits2_optional_data(self):
        skin = 16
        frame = 276
        render_fx = 315
        model_index_2 = 1
        model_index_3 = 2
        model_index_4 = 4

        sb0 = protocol.SpawnBaseline(skin_number=skin,
                                     frame=frame,
                                     render_fx=render_fx,
                                     model_index_2=model_index_2,
                                     model_index_3=model_index_3,
                                     model_index_4=model_index_4)

        protocol.SpawnBaseline.write(self.buff, sb0)
        self.buff.seek(0)

        sb1 = protocol.SpawnBaseline.read(self.buff)

        self.assertEqual(sb0.skin_number, sb1.skin_number, 'Skin_number should be equal')
        self.assertEqual(sb0.frame, sb1.frame, 'Frame should be equal')
        self.assertEqual(sb0.render_fx, sb1.render_fx, 'Render_fx should be equal')
        self.assertEqual(sb0.model_index_2, sb1.model_index_2, 'Model_index_2 should be equal')
        self.assertEqual(sb0.model_index_3, sb1.model_index_3, 'Model_index_3 should be equal')
        self.assertEqual(sb0.model_index_4, sb1.model_index_4, 'Model_index_4 should be equal')

    def test_spawn_baseline_morebits3_optional_data(self):
        old_origin_x, old_origin_y, old_origin_z = 0.0, 12.25, -265
        skin = 315
        sound = 1
        solid = 9250

        sb0 = protocol.SpawnBaseline(old_origin_x=old_origin_x,
                                     old_origin_y=old_origin_y,
                                     old_origin_z=old_origin_z,
                                     skin_number=skin,
                                     sound=sound,
                                     solid=solid)

        protocol.SpawnBaseline.write(self.buff, sb0)
        self.buff.seek(0)

        sb1 = protocol.SpawnBaseline.read(self.buff)

        self.assertEqual(sb0.old_origin[0], sb1.old_origin[0], 'Old_origin_x should be equal')
        self.assertEqual(sb0.old_origin[1], sb1.old_origin[1], 'Old_origin_y should be equal')
        self.assertEqual(sb0.old_origin[2], sb1.old_origin[2], 'Old_origin_z should be equal')
        self.assertEqual(sb0.skin_number, sb1.skin_number, 'Skin should be equal')
        self.assertEqual(sb0.sound, sb1.sound, 'Sound should be equal')
        self.assertEqual(sb0.solid, sb1.solid, 'Solid should be equal')

    def test_centerprint(self):
        text = "Crouch here"

        cp0 = protocol.CenterPrint(text)
        protocol.CenterPrint.write(self.buff, cp0)
        self.buff.seek(0)
        cp1 = protocol.CenterPrint.read(self.buff)

        self.assertEqual(cp0.text, cp1.text, 'Text should be the same')

    def test_frame(self):
        server_frame = 100
        delta_frame = 2
        areas = [1, 2, 3, 4]

        f0 = protocol.Frame(server_frame,
                            delta_frame,
                            areas)

        protocol.Frame.write(self.buff, f0)
        self.buff.seek(0)
        f1 = protocol.Frame.read(self.buff)

        self.assertEqual(f0.server_frame, f1.server_frame, 'Server frame should be equal')
        self.assertEqual(f0.delta_frame, f1.delta_frame, 'Delta frame should be equal')
        self.assertEqual(f0.areas, f1.areas, 'Areas should be equal')


if __name__ == '__main__':
    unittest.main()
