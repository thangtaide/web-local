"""Shortcut scripts run against a temporary APPDATA, never the real Start Menu."""
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(os.name == 'nt', 'Shortcut COM chỉ có trên Windows')
class ShortcutTests(unittest.TestCase):
    def test_install_idempotent_target_working_directory_and_safe_uninstall(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            fake_exe = base / 'Ứng dụng có dấu/MangaReader.exe'
            fake_exe.parent.mkdir()
            shutil.copyfile(sys.executable, fake_exe)
            env = dict(os.environ, APPDATA=str(base / 'appdata'))
            def run(script, *args):
                return subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(ROOT / 'scripts' / script), *args], env=env, capture_output=True, check=True)
            run('install_shortcut.ps1', '-ExePath', str(fake_exe))
            run('install_shortcut.ps1', '-ExePath', str(fake_exe))
            programs = Path(env['APPDATA']) / 'Microsoft/Windows/Start Menu/Programs'
            self.assertEqual(len(list(programs.glob('*.lnk'))), 1)
            env['MANGA_SHORTCUT_HELPER'] = str(ROOT / 'scripts/shortcut_native.ps1')
            command = "[Console]::OutputEncoding=[Text.UTF8Encoding]::new(); . $env:MANGA_SHORTCUT_HELPER; $s=[MangaShortcut]::Read((Join-Path $env:APPDATA 'Microsoft\\Windows\\Start Menu\\Programs\\Manga Reader.lnk')); @{target=$s[0];cwd=$s[1];icon=$s[2]}|ConvertTo-Json -Compress"
            result = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', command], env=env, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', errors='replace'))
            data = json.loads(result.stdout.decode('utf-8-sig'))
            self.assertEqual(Path(data['target']), fake_exe)
            self.assertEqual(Path(data['cwd']), fake_exe.parent)
            self.assertIn('MangaReader.exe,0', data['icon'])
            keep = programs / 'keep.txt'
            keep.write_text('unrelated')
            run('uninstall_shortcut.ps1')
            run('uninstall_shortcut.ps1')
            self.assertFalse((programs / 'Manga Reader.lnk').exists())
            self.assertTrue(keep.exists())
            self.assertTrue(fake_exe.exists())

    def test_missing_executable_does_not_register(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(ROOT / 'scripts/install_shortcut.ps1'), '-ExePath', str(Path(temp) / 'missing.exe')], env=dict(os.environ, APPDATA=temp), capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(Path(temp).rglob('*.lnk')), [])
