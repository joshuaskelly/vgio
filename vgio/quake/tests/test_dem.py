import io
import unittest

from vgio.quake.tests.basecase import TestCase
from vgio.quake import dem


class TestDemReadWrite(TestCase):
    def test_bad_message(self):
        dem.Bad.write(self.buff)
        self.buff.seek(0)
        dem.Bad.read(self.buff)

    def test_nop_message(self):
        dem.Nop.write(self.buff)
        self.buff.seek(0)
        dem.Nop.read(self.buff)

    def test_disconnect_message(self):
        dem.Disconnect.write(self.buff)
        self.buff.seek(0)
        dem.Disconnect.read(self.buff)

    def test_update_stat_message(self):
        u0 = dem.UpdateStat()
        u0.index = 0
        u0.value = 75

        dem.UpdateStat.write(self.buff, u0)
        self.buff.seek(0)

        u1 = dem.UpdateStat.read(self.buff)

        self.assertEqual(u0.index, u1.index, 'Update stat indexes should be equal')
        self.assertEqual(u0.value, u1.value, 'Update stat values should be equal')

    def test_version_message(self):
        v0 = dem.Version()
        v0.protocol_version = 15

        dem.Version.write(self.buff, v0)
        self.buff.seek(0)

        v1 = dem.Version.read(self.buff)

        self.assertEqual(v0.protocol_version, v1.protocol_version, 'Protocol versions should be equal')

    def test_set_view_message(self):
        s0 = dem.SetView()
        s0.entity = 16

        dem.SetView.write(self.buff, s0)
        self.buff.seek(0)

        s1 = dem.SetView.read(self.buff)

        self.assertEqual(s0.entity, s1.entity, 'Entities should be equal')

    def test_sound_message(self):
        # No optional arguments
        s0 = dem.Sound()
        s0.entity = 16
        s0.channel = 2
        s0.sound_number = 4
        s0.origin = -512, 256, 2048

        dem.Sound.write(self.buff, s0)
        self.buff.seek(0)

        s1 = dem.Sound.read(self.buff)

        self.assertEqual(s0.entity, s1.entity, 'Entity should be equal')
        self.assertEqual(s0.channel, s1.channel, 'Channel should be equal')
        self.assertEqual(s0.sound_number, s1.sound_number, 'Sound number should be equal')
        self.assertEqual(s0.origin, s1.origin, 'Origin should be equal')

        self.clear_buffer()

        # Both optional arguments
        s0 = dem.Sound()
        s0.entity = 16
        s0.channel = 2
        s0.sound_number = 4
        s0.origin = -512, 256, 2048
        s0.attenuation = 0.5
        s0.volume = 64
        s0.bit_mask |= dem.SND_ATTENUATION | dem.SND_VOLUME

        dem.Sound.write(self.buff, s0)
        self.buff.seek(0)

        s1 = dem.Sound.read(self.buff)

        self.assertEqual(s0.entity, s1.entity, 'Entities should be equal')
        self.assertEqual(s0.channel, s1.channel, 'Channels should be equal')
        self.assertEqual(s0.sound_number, s1.sound_number, 'Sound numbers should be equal')
        self.assertEqual(s0.origin, s1.origin, 'Origins should be equal')
        self.assertEqual(s0.attenuation, s1.attenuation, 'Attenuations should be equal')
        self.assertEqual(s0.volume, s1.volume, 'Volumes should be equal')

        dem.Sound.write(self.buff, s0)
        self.buff.seek(0)

    def test_time_message(self):
        t0 = dem.Time()
        t0.time = 4.125

        dem.Time.write(self.buff, t0)
        self.buff.seek(0)

        t1 = dem.Time.read(self.buff)

        self.assertEqual(t0.time, t1.time, 'Should be equal')

    def test_print_message(self):
        p0 = dem.Print()
        p0.text = "This hall selects EASY skill"

        dem.Print.write(self.buff, p0)
        self.buff.seek(0)

        p1 = dem.Print.read(self.buff)

        self.assertEqual(p0.text, p1.text, 'Text values should be equal')

    def test_stuff_text_message(self):
        s0 = dem.StuffText()
        s0.text = "This hall selects NORMAL skill"

        dem.StuffText.write(self.buff, s0)
        self.buff.seek(0)

        s1 = dem.StuffText.read(self.buff)

        self.assertEqual(s0.text, s1.text, 'Text values should be equal')

    def test_set_angle_message(self):
        s0 = dem.SetAngle()
        s0.angles = 0, -90, 22.5

        dem.SetAngle.write(self.buff, s0)
        self.buff.seek(0)

        s1 = dem.SetAngle.read(self.buff)

        self.assertEqual(s0.angles, s1.angles, 'Angles should be equal')

    def test_server_info_message(self):
        s0 = dem.ServerInfo()
        s0.protocol_version = 15
        s0.max_clients = 1
        s0.multi = 0
        s0.map_name = 'the Necropolis'
        s0.models = 'maps/e1m3.bsp', 'progs/player.mdl'
        s0.sounds = 'weapons/ric1.wav', 'weapons/ric2.wav'

        dem.ServerInfo.write(self.buff, s0)
        self.buff.seek(0)

        s1 = dem.ServerInfo.read(self.buff)

        self.assertEqual(s0.protocol_version, s1.protocol_version, 'Protocol versions should be equal')
        self.assertEqual(s0.max_clients, s1.max_clients, 'Max clients should be equal')
        self.assertEqual(s0.multi, s1.multi, 'Multi values should be equal')
        self.assertEqual(s0.map_name, s1.map_name, 'Map names Should be equal')
        self.assertEqual(s0.models, s1.models, 'Models should be equal')
        self.assertEqual(s0.sounds, s1.sounds, 'Sounds should be equal')

    def test_light_style_message(self):
        l0 = dem.LightStyle()
        l0.style = 15
        l0.string = 'azazaaazzz'

        dem.LightStyle.write(self.buff, l0)
        self.buff.seek(0)

        l1 = dem.LightStyle.read(self.buff)

        self.assertEqual(l0.style, l1.style, 'Styles should be equal')
        self.assertEqual(l0.string, l1.string, 'Strings should be equal')

    def test_update_name_message(self):
        u0 = dem.UpdateName()
        u0.player = 0
        u0.name = "Player"

        dem.UpdateName.write(self.buff, u0)
        self.buff.seek(0)

        u1 = dem.UpdateName.read(self.buff)

        self.assertEqual(u0.player, u1.player, 'Player values should be equal')
        self.assertEqual(u0.name, u1.name, 'Names should be equal')

    def test_update_frags_message(self):
        u0 = dem.UpdateFrags()
        u0.player = 1
        u0.frags = 100

        dem.UpdateFrags.write(self.buff, u0)
        self.buff.seek(0)

        u1 = dem.UpdateFrags.read(self.buff)

        self.assertEqual(u0.player, u1.player, 'Player values should be equal')
        self.assertEqual(u0.frags, u1.frags, 'Frags should be equal')

    def test_client_data_message(self):
        c0 = dem.ClientData()
        c0.on_ground = True
        c0.in_water = False
        c0.health = 75
        c0.active_ammo = 1
        c0.ammo = 25, 0, 0, 0
        c0.active_weapon = 16

        dem.ClientData.write(self.buff, c0)
        self.buff.seek(0)

        c1 = dem.ClientData.read(self.buff)

        self.assertEqual(c0.on_ground, c1.on_ground, 'On ground flags should be equal')
        self.assertEqual(c0.in_water, c1.in_water, 'In water flags should be equal')
        self.assertEqual(c0.health, c1.health, 'Health values should be equal')
        self.assertEqual(c0.active_ammo, c1.active_ammo, 'Active ammo values should be equal')
        self.assertEqual(c0.ammo, c1.ammo, 'Ammo counts should be equal')
        self.assertEqual(c0.active_weapon, c1.active_weapon, 'Active weapons should be equal')

        self.clear_buffer()

        c0 = dem.ClientData()
        c0.bit_mask = 0b0111111111111111

        c0.view_height = 18
        c0.ideal_pitch = 45
        c0.punch_angle = -22.5, 0, 90
        c0.velocity = 0, 16, -32
        c0.item_bit_mask = 0b01111111111111111111111111111111

        c0.on_ground = True
        c0.in_water = True
        c0.weapon_frame = 8
        c0.armor = 2
        c0.weapon = 32
        c0.health = 99
        c0.active_ammo = 1
        c0.ammo = 25, 0, 0, 0
        c0.active_weapon = 16

        dem.ClientData.write(self.buff, c0)
        self.buff.seek(0)

        c1 = dem.ClientData.read(self.buff)

        self.assertEqual(c0.bit_mask, c1.bit_mask, 'Bit masks should be equal')
        self.assertEqual(c0.view_height, c1.view_height, 'View heights should be equal')
        self.assertEqual(c0.ideal_pitch, c1.ideal_pitch, 'Ideal pitches should be equal')
        self.assertEqual(c0.punch_angle, c1.punch_angle, 'Punch angles should be equal')
        self.assertEqual(c0.velocity, c1.velocity, 'Velocities should be equal')
        self.assertEqual(c0.item_bit_mask, c1.item_bit_mask, 'Item bit masks should be equal')
        self.assertEqual(c0.on_ground, c1.on_ground, 'On ground flags should be equal')
        self.assertEqual(c0.in_water, c1.in_water, 'In water flags should be equal')
        self.assertEqual(c0.weapon_frame, c1.weapon_frame, 'Weapon frames should be equal')
        self.assertEqual(c0.armor, c1.armor, 'Armor values should be equal')
        self.assertEqual(c0.weapon, c1.weapon, 'Weapon values should be equal')
        self.assertEqual(c0.health, c1.health, 'Health values should be equal')
        self.assertEqual(c0.active_ammo, c1.active_ammo, 'Active ammo values should be equal')
        self.assertEqual(c0.ammo, c1.ammo, 'Ammo values should be equal')
        self.assertEqual(c0.active_weapon, c1.active_weapon, 'Active weapon values should be equal')

    def test_stop_sound_message(self):
        s0 = dem.StopSound()
        s0.channel = 2
        s0.entity = 64

        dem.StopSound.write(self.buff, s0)
        self.buff.seek(0)

        s1 = dem.StopSound.read(self.buff)

        self.assertEqual(s0.channel, s1.channel, 'Channels should be equal')
        self.assertEqual(s0.entity, s1.entity, 'Entities should be equal')

    def test_update_colors_message(self):
        u0 = dem.UpdateColors()
        u0.player = 1
        u0.colors = 0b00010001

        dem.UpdateColors.write(self.buff, u0)
        self.buff.seek(0)

        u1 = dem.UpdateColors.read(self.buff)

        self.assertEqual(u0.player, u1.player, 'Player values should be equal')
        self.assertEqual(u0.colors, u1.colors, 'Colors values should be equal')

    def test_particle_message(self):
        p0 = dem.Particle()
        p0.origin = 0, 16, -1024
        p0.direction = 0, 1, 2
        p0.count = 8
        p0.color = 73

        dem.Particle.write(self.buff, p0)
        self.buff.seek(0)

        p1 = dem.Particle.read(self.buff)

        self.assertEqual(p0.origin, p1.origin, 'Origin should be equal')
        self.assertEqual(p0.direction, p1.direction, 'Direction should be equal')
        self.assertEqual(p0.count, p1.count, 'Count should be equal')
        self.assertEqual(p0.color, p1.color, 'Color should be equal')

    def test_damage_message(self):
        d0 = dem.Damage()
        d0.armor = 8
        d0.blood = 4
        d0.origin = 0, 16, -512

        dem.Damage.write(self.buff, d0)
        self.buff.seek(0)

        d1 = dem.Damage.read(self.buff)

        self.assertEqual(d0.armor, d1.armor, 'Armor values should be equal')
        self.assertEqual(d0.blood, d1.blood, 'Blood values should be equal')
        self.assertEqual(d0.origin, d1.origin, 'Origins should be equal')

    def test_spawn_static_message(self):
        s0 = dem.SpawnStatic()
        s0.model_index = 127
        s0.frame = 8
        s0.color_map = 1
        s0.skin = 2
        s0.origin = 0, -32, 1600
        s0.angles = 22.5, 0, -45

        dem.SpawnStatic.write(self.buff, s0)
        self.buff.seek(0)

        s1 = dem.SpawnStatic.read(self.buff)

        self.assertEqual(s0.model_index, s1.model_index, 'Model indices should be equal')
        self.assertEqual(s0.frame, s1.frame, 'Frames should be equal')
        self.assertEqual(s0.color_map, s1.color_map, 'Color maps should be equal')
        self.assertEqual(s0.skin, s1.skin, 'Skins should be equal')
        self.assertEqual(s0.origin, s1.origin, 'Origins should be equal')
        self.assertEqual(s0.angles, s1.angles, 'Angles should be equal')

    def test_spawn_binary_message(self):
        with self.assertRaises(dem.BadDemFile):
            dem.SpawnBinary.write(self.buff)

        with self.assertRaises(dem.BadDemFile):
            dem.SpawnBinary.read(self.buff)

    def test_spawn_baseline_message(self):
        s0 = dem.SpawnBaseline()
        s0.entity = 10
        s0.model_index = 127
        s0.frame = 8
        s0.color_map = 1
        s0.skin = 2
        s0.origin = 0, -32, 1600
        s0.angles = 22.5, 0, -45

        dem.SpawnBaseline.write(self.buff, s0)
        self.buff.seek(0)

        s1 = dem.SpawnBaseline.read(self.buff)

        self.assertEqual(s0.entity, s1.entity, 'Entities should be equal')
        self.assertEqual(s0.model_index, s1.model_index, 'Model indices should be equal')
        self.assertEqual(s0.frame, s1.frame, 'Frames should be equal')
        self.assertEqual(s0.color_map, s1.color_map, 'Color maps should be equal')
        self.assertEqual(s0.skin, s1.skin, 'Skins should be equal')
        self.assertEqual(s0.origin, s1.origin, 'Origins should be equal')
        self.assertEqual(s0.angles, s1.angles, 'Angles should be equal')

    def test_temp_entity_message(self):
        t0 = dem.TempEntity()
        t0.type = dem.TE_WIZSPIKE
        t0.origin = 0, 128, -768

        dem.TempEntity.write(self.buff, t0)
        self.buff.seek(0)

        t1 = dem.TempEntity.read(self.buff)

        self.assertEqual(t0.type, t1.type, 'Types should be equal')
        self.assertEqual(t0.origin, t1.origin, 'Origins should be equal')

        self.clear_buffer()

        t0 = dem.TempEntity()
        t0.type = dem.TE_LIGHTNING1
        t0.entity = 8
        t0.start = 0, 0, 0
        t0.end = 16, -96, 2048

        dem.TempEntity.write(self.buff, t0)
        self.buff.seek(0)

        t1 = dem.TempEntity.read(self.buff)

        self.assertEqual(t0.type, t1.type, 'Types should be equal')
        self.assertEqual(t0.entity, t1.entity, 'Entity values should be equal')
        self.assertEqual(t0.start, t1.start, 'Start vectors should be equal')
        self.assertEqual(t0.end, t1.end, 'End vectors should be equal')

        self.clear_buffer()

        t0 = dem.TempEntity()
        t0.type = dem.TE_EXPLOSION2
        t0.origin = 0, 128, -768
        t0.color_start = 0
        t0.color_length = 16

        dem.TempEntity.write(self.buff, t0)
        self.buff.seek(0)

        t1 = dem.TempEntity.read(self.buff)

        self.assertEqual(t0.type, t1.type, 'Types should be equal')
        self.assertEqual(t0.origin, t1.origin, 'Origins should be equal')
        self.assertEqual(t0.color_start, t1.color_start, 'Color start values should be equal')
        self.assertEqual(t0.color_length, t1.color_length, 'Color length values should be equal')

        self.clear_buffer()

        with self.assertRaises(dem.BadDemFile):
            t0 = dem.TempEntity()
            t0.type = 14
            dem.TempEntity.write(self.buff, t0)

        self.clear_buffer()

        with self.assertRaises(dem.BadDemFile):
            self.buff.write(b'\x17\x0e')
            self.buff.seek(0)
            dem.TempEntity.read(self.buff)

    def test_set_pause_message(self):
        s0 = dem.SetPause()
        s0.paused = 1

        dem.SetPause.write(self.buff, s0)
        self.buff.seek(0)

        s1 = dem.SetPause.read(self.buff)

        self.assertEqual(s0.paused, s1.paused, 'Paused values should be equal')

    def test_sign_on_num_message(self):
        s0 = dem.SignOnNum()
        s0.sign_on = 1

        dem.SignOnNum.write(self.buff, s0)
        self.buff.seek(0)

        s1 = dem.SignOnNum.read(self.buff)

        self.assertEqual(s0.sign_on, s1.sign_on, 'Sign on values should be equal')

    def test_center_print_message(self):
        c0 = dem.CenterPrint()
        c0.text = 'This hall selects HARD skill'

        dem.CenterPrint.write(self.buff, c0)
        self.buff.seek(0)

        c1 = dem.CenterPrint.read(self.buff)

        self.assertEqual(c0.text, c1.text, 'Text values should be equal')

    def test_killed_monster_message(self):
        dem.KilledMonster.write(self.buff)
        self.buff.seek(0)
        dem.KilledMonster.read(self.buff)

    def test_found_secret_message(self):
        dem.FoundSecret.write(self.buff)
        self.buff.seek(0)
        dem.FoundSecret.read(self.buff)

    def test_spawn_static_sound_message(self):
        s0 = dem.SpawnStaticSound()
        s0.origin = 0, -32, 1096
        s0.sound_number = 2
        s0.volume = 0.5
        s0.attenuation = 0.25

        dem.SpawnStaticSound.write(self.buff, s0)
        self.buff.seek(0)

        s1 = dem.SpawnStaticSound.read(self.buff)

        self.assertEqual(s0.origin, s1.origin, 'Origins should be equal')
        self.assertEqual(s0.sound_number, s1.sound_number, 'Sound numbers should be equal')
        self.assertEqual(s0.volume, s1.volume, 'Volume values should be equal')
        self.assertEqual(s0.attenuation, s1.attenuation, 'Attenuation values should be equal')

    def test_intermission_message(self):
        dem.Intermission.write(self.buff)
        self.buff.seek(0)
        dem.Intermission.read(self.buff)

    def test_finale_message(self):
        f0 = dem.Finale()
        f0.text = 'Game Over'

        dem.Finale.write(self.buff, f0)
        self.buff.seek(0)

        f1 = dem.Finale.read(self.buff)

        self.assertEqual(f0.text, f1.text, 'Should be equal')

    def test_cd_track_message(self):
        c0 = dem.CdTrack()
        c0.from_track = 2
        c0.to_track = 3

        dem.CdTrack.write(self.buff, c0)
        self.buff.seek(0)

        c1 = dem.CdTrack.read(self.buff)

        self.assertEqual(c0.from_track, c1.from_track, 'From track values should be equal')
        self.assertEqual(c0.to_track, c1.to_track, 'To track should be equal')

    def test_sell_screen_message(self):
        dem.SellScreen.write(self.buff)
        self.buff.seek(0)
        dem.SellScreen.read(self.buff)

    def test_cut_scene_message(self):
        c0 = dem.CutScene()
        c0.text = 'Cut scene'

        dem.CutScene.write(self.buff, c0)
        self.buff.seek(0)

        c1 = dem.CutScene.read(self.buff)

        self.assertEqual(c0.text, c1.text, 'Text values should be equal')

    def test_update_entity_message(self):
        # Quick update
        u0 = dem.UpdateEntity()
        u0.bit_mask |= dem.U_ORIGIN1 | dem.U_ORIGIN2 | dem.U_ORIGIN3 | dem.U_ANGLE2 | dem.U_FRAME
        u0.entity = 4
        u0.origin = u0.origin = 128.5, 250, -980
        u0.angles = None, 90, None
        u0.frame = 1

        dem.UpdateEntity.write(self.buff, u0)
        self.buff.seek(0)

        u1 = dem.UpdateEntity.read(self.buff)

        self.assertEqual(u0.bit_mask, u1.bit_mask, 'Bit masks should be equal')
        self.assertEqual(u0.entity, u1.entity, 'Entities should be equal')
        self.assertEqual(u0.origin, u1.origin, 'Origins should be equal')
        self.assertEqual(u0.angles, u1.angles, 'Angles should be equal')
        self.assertEqual(u0.frame, u1.frame, 'Frames should be equal')

        self.clear_buffer()

        # Full update
        u0 = dem.UpdateEntity()
        u0.bit_mask |= 0x7F7F
        u0.entity = 4
        u0.model_index = 8
        u0.frame = 0
        u0.colormap = 1
        u0.skin = 2
        u0.effects = 3
        u0.origin = 128.5, 250, -980
        u0.angles = 22.5, 0, -90

        dem.UpdateEntity.write(self.buff, u0)
        self.buff.seek(0)

        u1 = dem.UpdateEntity.read(self.buff)

        self.assertEqual(u0.bit_mask, u1.bit_mask, 'Bit masks should be equal')
        self.assertEqual(u0.entity, u1.entity, 'Entities should be equal')
        self.assertEqual(u0.model_index, u1.model_index, 'Models should be equal')
        self.assertEqual(u0.frame, u1.frame, 'Frames should be equal')
        self.assertEqual(u0.colormap, u1.colormap, 'Colormaps should be equal')
        self.assertEqual(u0.skin, u1.skin, 'Skins should be equal')
        self.assertEqual(u0.effects, u1.effects, 'Effects should be equal')
        self.assertEqual(u0.origin, u1.origin, 'Origins should be equal')
        self.assertEqual(u0.angles, u1.angles, 'Angles should be equal')

    def test_dem(self):
        d0 = dem.Dem.open('./test_data/test.dem')
        d0.close()

        d0.save(self.buff)
        self.buff.seek(0)

        b = io.BufferedReader(self.buff)
        d1 = dem.Dem.open(b)

        self.assertEqual(d1.cd_track, '2', 'Cd track should be 2')
        self.assertEqual(len(d1.message_blocks), 168, 'The demo should have 168 message blocks')

        last_message_of_first_block = d1.message_blocks[0].messages[-1]

        self.assertTrue(isinstance(last_message_of_first_block, dem.SignOnNum), 'The last message of the first block should be a SignOnNum')
        self.assertEqual(last_message_of_first_block.sign_on, 1, 'Sign on value should be 1')
        self.assertTrue(isinstance(d1.message_blocks[-1].messages[0], dem.Disconnect), 'The last message should be a Disconnect')

        self.assertFalse(d1.fp.closed, 'File should be open')
        fp = d1.fp
        d1.close()
        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(d1.fp, 'File pointer should be cleaned up')

    def test_context_manager(self):
        with dem.Dem.open('./test_data/test.dem', 'a') as dem_file:
            self.assertFalse(dem_file.fp.closed, 'File should be open')
            self.assertEqual(dem_file.mode, 'a', 'File mode should be \'a\'')
            fp = dem_file.fp
            dem_file._did_modify = False
    
        self.assertTrue(fp.closed, 'File should be closed')
        self.assertIsNone(dem_file.fp, 'File pointer should be cleaned up')


if __name__ == '__main__':
    unittest.main()
