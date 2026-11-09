"""Explicit packaged Windows checks; NOT run automatically by unittest discovery.

Run: python -m unittest tests.exe_smoke -v
No shortcut is installed. Native GUI tests use an isolated LOCALAPPDATA.
"""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch
from app.manager import MangaManager
from app.paths import AppPaths
from app.settings import save_settings
from tests.web_support import create_library

ROOT = Path(__file__).resolve().parent.parent
EXE = ROOT / 'dist/MangaReader/MangaReader.exe'


@unittest.skipUnless(os.name == 'nt' and EXE.exists(), 'Build Windows trước khi chạy EXE smoke')
class ExeSmokeTests(unittest.TestCase):
    def test_native_exe_starts_closes_and_restarts_with_isolated_settings(self):
        user32 = ctypes.windll.user32
        with tempfile.TemporaryDirectory(prefix='manga-exe-smoke-') as temp:
            base = Path(temp)
            folder = base / 'library'
            folder.mkdir()
            settings = base / 'MangaReader/settings.json'
            save_settings(settings, folder)
            original = settings.read_bytes()
            env = dict(os.environ, LOCALAPPDATA=str(base), PATH=str(base))
            for _ in range(2):
                process = subprocess.Popen([str(EXE)], cwd=base, env=env)
                try:
                    windows = []
                    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
                    def callback(handle, _):
                        pid = wintypes.DWORD()
                        user32.GetWindowThreadProcessId(handle, ctypes.byref(pid))
                        if pid.value == process.pid:
                            title = ctypes.create_unicode_buffer(256)
                            user32.GetWindowTextW(handle, title, 256)
                            if title.value == 'Manga Reader': windows.append(handle)
                        return True
                    deadline = time.monotonic() + 15
                    while time.monotonic() < deadline and not windows and process.poll() is None:
                        user32.EnumWindows(callback, 0)
                        time.sleep(.05)
                    self.assertTrue(windows, 'Không tìm thấy cửa sổ Manga Reader trong process EXE')
                    self.assertIsNone(process.poll())
                    user32.PostMessageW(windows[0], 0x0010, 0, 0)  # WM_CLOSE
                    self.assertEqual(process.wait(timeout=10), 0)
                    self.assertEqual(settings.read_bytes(), original)
                finally:
                    if process.poll() is None:
                        process.terminate(); process.wait(timeout=10)

    def test_packaged_assets_manager_pipeline_and_runtime_file_browser(self):
        import tkinter as tk
        from playwright.sync_api import sync_playwright
        with tempfile.TemporaryDirectory(prefix='manga-bundle-web-') as temp:
            base = Path(temp)
            folder = base / 'Truyện đặc biệt # % &'
            create_library(folder, 1)
            paths = AppPaths(EXE.parent / '_internal', base / 'user', base / 'user/web')
            root = tk.Tk()
            root.withdraw()
            root.update_idletasks()
            opened = []
            manager = MangaManager(root, paths, opener=lambda url: opened.append(url) or True)
            try:
                with patch('app.manager.filedialog.askdirectory', return_value=str(folder)):
                    manager.choose_folder()
                manager.open_web()
                deadline = time.monotonic() + 15
                while manager.controller.busy and time.monotonic() < deadline:
                    root.update(); time.sleep(.01)
                self.assertFalse(manager.controller.busy)
                self.assertEqual(len(opened), 1)
                self.assertEqual(paths.settings.read_text(encoding='utf-8').count('library_folder'), 1)
                self.assertIn('9 ảnh', manager.stats.get())
                self.assertTrue(opened[0].startswith(paths.web.as_uri()))
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch()
                    try:
                        page = browser.new_page()
                        page.goto(opened[0])
                        page.wait_for_selector('.story-card')
                        page.wait_for_function("document.querySelector('.story-card img').naturalWidth > 0")
                        page.locator('.story-card').click()
                        page.get_by_role('link', name='Đọc tiếp', exact=False).click()
                        page.wait_for_selector('.reader-stage[aria-busy="false"]')
                        self.assertEqual(page.locator('.reader-image').count(), 3)
                    finally:
                        browser.close()
            finally:
                manager.dispose(); root.destroy()
