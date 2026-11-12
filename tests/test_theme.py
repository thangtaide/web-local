"""Theme integration: native ttk states, copy/focus, and layouts at three DPI scales."""
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from app.manager import MangaManager
from app.paths import AppPaths
from app.theme import COLORS


class ManagerThemeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.manager = MangaManager(self.root, AppPaths(self.base, self.base / 'data', self.base / 'web'))
        self.addCleanup(self.manager.dispose)

    def test_dark_controls_copy_unicode_path_and_tab_order(self):
        manager = self.manager
        self.assertEqual(self.root.cget('background').upper(), COLORS['background'])
        self.assertEqual(manager.style.lookup('Path.Manga.TEntry', 'fieldbackground', ('readonly',)).upper(), COLORS['surface'])
        self.assertEqual(manager.style.lookup('Primary.Manga.TButton', 'background').upper(), COLORS['action'])
        self.assertEqual(manager.style.lookup('Primary.Manga.TButton', 'background', ('active',)).upper(), COLORS['accent_hover'])
        self.assertEqual(manager.style.lookup('Primary.Manga.TButton', 'foreground', ('disabled',)).upper(), COLORS['secondary'])
        value = 'Thư viện tiếng Việt # % & / Một câu chuyện'
        manager.folder.set(value)
        self.root.deiconify(); self.root.update()
        manager.path_entry.selection_range(0, 'end')
        # Exercise Tk's Copy binding against an interpreter-local clipboard stub.
        # Never replace the user's system clipboard while running tests.
        clipboard = []
        def local_clipboard(action, *args):
            if action == 'clear': clipboard.clear()
            elif action == 'append': clipboard.append(args[-1])
            return ''
        self.root.tk.call('rename', 'clipboard', 'manga_test_original_clipboard')
        self.root.tk.createcommand('clipboard', local_clipboard)
        try:
            manager.path_entry.event_generate('<<Copy>>')
            self.assertEqual(''.join(clipboard), value)
        finally:
            self.root.tk.deletecommand('clipboard')
            self.root.tk.call('rename', 'manga_test_original_clipboard', 'clipboard')
        self.assertEqual(str(manager.path_entry.tk_focusNext()), str(manager.choose_button))
        self.assertEqual(str(manager.choose_button.tk_focusNext()), str(manager.open_button))
        self.assertEqual(str(manager.open_button.tk_focusNext()), str(manager.path_entry))
        self.assertTrue(manager.path_entry.instate(['readonly']))

    def test_status_has_semantic_text_and_readable_colors(self):
        manager = self.manager
        for kind, color, text in [('Ready', 'accent_hover', 'Sẵn sàng.'), ('Scanning', 'warning', 'Đang quét thư viện…'),
                                  ('Success', 'success', 'Đã quét thành công.'), ('Error', 'error', 'Không hoàn tất. Hãy thử lại.')]:
            manager._set_status(text, kind)
            self.assertEqual(manager.status.get(), text)
            self.assertEqual(manager.status_dot.cget('style'), kind + '.Manga.TLabel')
            self.assertEqual(manager.style.lookup(manager.status_label.cget('style'), 'foreground').upper(), COLORS[color])

    def test_layout_fits_at_100_125_150_percent_scaling(self):
        # Tk point/pixel scaling is simulated; this does not change the user's monitor DPI.
        self.manager.dispose()
        for child in self.root.winfo_children(): child.destroy()
        for percent in (100, 125, 150):
            with self.subTest(percent=percent):
                self.root.tk.call('tk', 'scaling', 96 * percent / 100 / 72)
                manager = MangaManager(self.root, AppPaths(self.base, self.base / 'data', self.base / 'web'))
                try:
                    manager._set_status('Không hoàn tất. Có thể chọn lại thư mục và thử lại.', 'Error')
                    manager.stats.set('12 truyện · 345 tập · 67890 ảnh')
                    self.root.deiconify(); self.root.update()
                    minimum = self.root.minsize()
                    self.root.geometry(f'{minimum[0]}x{minimum[1]}')
                    self.root.update()
                    for widget in (manager.path_entry, manager.choose_button, manager.open_button, manager.status_label, manager.stats_label):
                        x = widget.winfo_rootx() - self.root.winfo_rootx()
                        y = widget.winfo_rooty() - self.root.winfo_rooty()
                        self.assertGreaterEqual(x, 0)
                        self.assertGreaterEqual(y, 0)
                        self.assertLessEqual(x + widget.winfo_width(), self.root.winfo_width() + 1)
                        self.assertLessEqual(y + widget.winfo_height(), self.root.winfo_height() + 1)
                        self.assertGreaterEqual(widget.winfo_height(), widget.winfo_reqheight())
                finally:
                    manager.dispose()
                    for child in self.root.winfo_children(): child.destroy()
