import tempfile
from pathlib import Path
import threading
import time
import tkinter as tk
import unittest
from unittest.mock import patch
from app.manager import MangaManager, ScanController
from app.paths import AppPaths


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def wait_result(self, controller):
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            result = controller.poll()
            if result is not None:
                return result
            time.sleep(.005)
        self.fail('Worker did not finish')

    def test_validation(self):
        controller = ScanController(lambda _: {}, self.root / 'index.html')
        for folder in ['', str(self.root / 'missing')]:
            with self.assertRaises(ValueError):
                controller.start(folder)
        self.assertFalse(controller.busy)

    def test_worker_nonblocking_no_overlap_open_after_write_on_main_thread(self):
        gate = threading.Event()
        self.addCleanup(gate.set)
        events = []
        def job(_):
            gate.wait(2)
            events.append(('write', threading.get_ident()))
            return {'stories': 1}
        def opener(url):
            events.append(('open', threading.get_ident()))
            self.assertTrue(url.startswith('file:///'))
            return True
        controller = ScanController(job, self.root / 'index.html', opener)
        self.assertTrue(controller.start(str(self.root)))
        self.assertFalse(controller.start(str(self.root)))
        self.assertIsNone(controller.poll())
        self.assertEqual(events, [])
        gate.set()
        self.assertTrue(self.wait_result(controller)[0])
        self.assertEqual([e[0] for e in events], ['write', 'open'])
        self.assertNotEqual(events[0][1], threading.get_ident())
        self.assertEqual(events[1][1], threading.get_ident())
        self.assertFalse(controller.busy)

    def test_failure_does_not_open_and_can_retry(self):
        with patch('webbrowser.open') as opener:
            def fail(_):
                raise PermissionError('không đọc được')
            controller = ScanController(fail, self.root / 'index.html', opener)
            controller.start(str(self.root))
            self.assertEqual(self.wait_result(controller), (False, 'không đọc được'))
            opener.assert_not_called()
            self.assertTrue(controller.start(str(self.root)))
            self.wait_result(controller)


class GuiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.update_idletasks()
        self.addCleanup(self.root.destroy)
        self.paths = AppPaths(self.base, self.base / 'data', self.base / 'web')

    def test_choose_restore_cancel_and_missing(self):
        manager = MangaManager(self.root, self.paths)
        self.addCleanup(manager.dispose)
        with patch('app.manager.filedialog.askdirectory', return_value=str(self.base)):
            manager.choose_folder()
        self.assertEqual(manager.folder.get(), str(self.base))
        second = MangaManager(self.root, self.paths)
        self.addCleanup(second.dispose)
        self.assertEqual(second.folder.get(), str(self.base))
        with patch('app.manager.filedialog.askdirectory', return_value=''):
            manager.choose_folder()
        self.assertEqual(manager.folder.get(), str(self.base))

    def test_gui_heartbeat_while_scan_and_queue_result(self):
        gate = threading.Event()
        self.addCleanup(gate.set)
        def job(_):
            gate.wait(2)
            return {'stories': 1, 'chapters': 2, 'images': 3}
        opened = []
        manager = MangaManager(self.root, self.paths, job, lambda url: opened.append(url) or True)
        self.addCleanup(manager.dispose)
        manager.folder.set(str(self.base))
        manager.open_web()
        self.assertTrue(manager.open_button.instate(['disabled']))
        heartbeat = []
        self.root.after(5, lambda: heartbeat.append(True))
        deadline = time.monotonic() + .1
        while time.monotonic() < deadline:
            self.root.update()
            time.sleep(.005)
        self.assertEqual(heartbeat, [True])
        self.assertEqual(opened, [])
        gate.set()
        deadline = time.monotonic() + 3
        while manager.controller.busy and time.monotonic() < deadline:
            self.root.update()
            time.sleep(.005)
        self.assertEqual(len(opened), 1)
        self.assertIn('3 ảnh', manager.stats.get())
        self.assertFalse(manager.open_button.instate(['disabled']))
