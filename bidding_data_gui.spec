import os
a = Analysis(['src\\bidding_data_gui.py'],
             pathex=[os.path.abspath('.')],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='bidding_data.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False , version='src\\version', icon='src\\icon.ico')
