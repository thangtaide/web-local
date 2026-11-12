# Build only application-owned resources; never package generated library/settings.
from pathlib import Path

root = Path(SPECPATH).parent
web_files = ('index.html', 'css/style.css', 'js/config.js', 'js/app.js', 'js/reader.js')
datas = [(str(root / 'web' / name), str(Path('web') / Path(name).parent)) for name in web_files]
datas.append((str(root / 'assets/app.ico'), 'assets'))
a = Analysis([str(root / 'packaging/entry.py')], pathex=[str(root)], binaries=[],
             datas=datas, hiddenimports=[], hookspath=[], runtime_hooks=[],
             excludes=['playwright', 'pywinauto', 'PIL', 'numpy', 'pytest'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='MangaReader',
          debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
          console=False, icon=str(root / 'assets/app.ico'),
          version=str(root / 'packaging/version_info.txt'))
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='MangaReader')
