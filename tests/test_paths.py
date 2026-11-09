from pathlib import Path
import os
import unittest
from unittest.mock import patch
from app.paths import get_paths


class PathsTests(unittest.TestCase):
    def test_source_paths_are_absolute(self):
        paths = get_paths()
        self.assertTrue(paths.resources.is_absolute())
        self.assertEqual(paths.library, paths.web / 'js/library.js')
        self.assertTrue((paths.resources / 'app').is_dir())

    def test_frozen_paths_use_user_data(self):
        with patch('sys.frozen', True, create=True), patch('sys._MEIPASS', str(Path.cwd()), create=True), patch.dict(os.environ, {'LOCALAPPDATA': str(Path.cwd() / 'test-user')}):
            paths = get_paths()
            self.assertEqual(paths.data.name, 'MangaReader')
            self.assertEqual(paths.web, paths.data / 'web')
