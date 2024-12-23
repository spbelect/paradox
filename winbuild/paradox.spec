# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew

block_cipher = None


a = Analysis(['Z:\\home\\z\\pproj\\paradox_dev\\main.py'],
             pathex=['Z:\\home\\z\\pproj\\paradox_dev\\winbuild'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='paradox',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe, Tree('Z:\\home\\z\\pproj\\paradox_dev\\', 
                         #prefix='paradox', 
                         excludes=['.git', '*.apk', '*.py', '*.orig', '*.pdf', '*.csv',
                                   '*.profile', '*.shelve','*.spec', '*.lock', '*.sqlite', 
                                   '*.xml', 'build', 'winbuild', 'recipes']),
               a.binaries,
               a.zipfiles,
               a.datas,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               strip=False,
               upx=True,
               name='paradox')

#coll = COLLECT(exe,
               #a.binaries,
               #a.zipfiles,
               #a.datas,
               #strip=False,
               #upx=True,
               #upx_exclude=[],
               #name='paradox')
