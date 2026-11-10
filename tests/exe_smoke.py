"""Explicit packaged Windows checks; NOT run automatically by unittest discovery.

Run: python -m unittest tests.exe_smoke -v
No shortcut is installed. Native GUI tests use an isolated LOCALAPPDATA.
"""
import ctypes
from ctypes import wintypes
import os
import json
import shutil
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch
from app.manager import MangaManager
from app.paths import AppPaths, prepare_web
from app.settings import save_settings
from app.scanner import scan_library, write_library
from tests.web_support import create_library
from tests.windows_capture import window_pixels

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
                    # Verify pixels rendered by the real binary, without foreground automation.
                    deadline = time.monotonic() + 5
                    while True:
                        _, _, pixels = window_pixels(windows[0])
                        if pixels.count(bytes.fromhex('ef5487')) > 500 or time.monotonic() > deadline:
                            break
                        time.sleep(.05)
                    self.assertGreater(pixels.count(bytes.fromhex('0b0909')), 10000, 'EXE thiếu nền AMOLED')
                    self.assertGreater(pixels.count(bytes.fromhex('ef5487')), 500, 'EXE thiếu nút tím mới')
                    self.assertGreater(pixels.count(bytes.fromhex('191414')), 1000, 'EXE thiếu ô đường dẫn tối')
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
            # Simulate an existing installation at the exact same permanent file URL.
            legacy = base / 'legacy-bundle'
            shutil.copytree(paths.resources / 'web', legacy / 'web')
            legacy_css = legacy / 'web/css/style.css'
            legacy_css.write_text(legacy_css.read_text(encoding='utf-8') + '\n:root { --bg-primary:#111217; }\n', encoding='utf-8')
            prepare_web(AppPaths(legacy, paths.data, paths.web))
            library = scan_library(folder)
            write_library(paths.library, library)
            save_settings(paths.settings, folder)
            settings_before = paths.settings.read_bytes()
            old_index = (paths.web / 'index.html').read_bytes()
            keep = paths.web / 'user-file.txt'
            keep.write_text('Không xóa dữ liệu riêng', encoding='utf-8')
            root = tk.Tk()
            root.withdraw()
            root.update_idletasks()
            opened = []
            manager = MangaManager(root, paths, opener=lambda url: opened.append(url) or True)
            try:
                with patch('app.manager.filedialog.askdirectory', return_value=str(folder)):
                    manager.choose_folder()
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch()
                    try:
                        page = browser.new_page()
                        stable_url = (paths.web / 'index.html').as_uri() + '#/library'
                        page.goto(stable_url)
                        page.wait_for_selector('.story-card')
                        page.wait_for_function("document.querySelector('.story-card img').naturalWidth > 0")
                        self.assertEqual(page.locator('html').evaluate('node=>getComputedStyle(node).backgroundColor'), 'rgb(17, 18, 23)')
                        old_css_url = page.locator('link[rel="stylesheet"]').get_attribute('href')
                        story, chapter = library['stories'][0], library['stories'][0]['chapters'][0]
                        progress = json.dumps({story['id']: {'chapterId': chapter['id'], 'time': 1, 'chapters': {chapter['id']: {'page': 1, 'ratio': .4, 'time': 1}}}})
                        page.evaluate('(value)=>{localStorage.setItem("manga-reader.progress.v1",value);localStorage.setItem("manga-reader.width.v1","1000")}', progress)
                        manager.open_web()
                        deadline = time.monotonic() + 15
                        while manager.controller.busy and time.monotonic() < deadline:
                            root.update(); time.sleep(.01)
                        self.assertFalse(manager.controller.busy)
                        self.assertEqual(opened, [stable_url])
                        self.assertIn('9 ảnh', manager.stats.get())
                        self.assertEqual(paths.settings.read_bytes(), settings_before)
                        self.assertEqual(keep.read_text(encoding='utf-8'), 'Không xóa dữ liệu riêng')
                        self.assertNotEqual((paths.web / 'index.html').read_bytes(), old_index)
                        page.reload()
                        page.wait_for_selector('.story-card')
                        self.assertEqual(page.locator('html').evaluate('node=>getComputedStyle(node).backgroundColor'), 'rgb(9, 9, 11)')
                        self.assertNotEqual(page.locator('link[rel="stylesheet"]').get_attribute('href'), old_css_url)
                        self.assertEqual(page.evaluate('localStorage.getItem("manga-reader.progress.v1")'), progress)
                        self.assertEqual(page.evaluate('localStorage.getItem("manga-reader.width.v1")'), '1000')
                        page.locator('.recent-continue').click()
                        page.wait_for_selector('.reader-stage[aria-busy="false"]')
                        self.assertEqual(page.locator('.reader-image').count(), 3)
                        self.assertEqual(page.locator('.width-label').inner_text(), '1000px')
                        restored = page.evaluate('(id)=>JSON.parse(localStorage.getItem("manga-reader.progress.v1"))[id]', story['id'])
                        self.assertEqual(restored['chapters'][chapter['id']]['page'], 1)
                        self.assertAlmostEqual(restored['chapters'][chapter['id']]['ratio'], .4, delta=.01)
                    finally:
                        browser.close()
            finally:
                manager.dispose(); root.destroy()
