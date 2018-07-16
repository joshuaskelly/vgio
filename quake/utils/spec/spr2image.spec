# -*- mode: python -*-

block_cipher = None


a = Analysis(['../spr2image.py'],
             pathex=['/Users/Joshua/Repositories/game-tools/quake/utils'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[
                '_bz2',
                '_ctypes',
                '_codecs_hk',
                '_codecs_cn',
                '_codecs_jp',
                '_codecs_kr',
                '_codecs_tw',
                '_hashlib',
                '_pickle',
                '_lzma',
                '_socket',
                '_sha1',
                '_sha256',
                '_sha512',
                '_ssl'
             ],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='spr2image',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
