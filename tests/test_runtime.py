from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from app.paths import AppPaths, prepare_web, WEB_FILES


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.resources = self.base / 'bundle'
        for name in WEB_FILES:
            path = self.resources / 'web' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('source ' + name, encoding='utf-8')
        (self.resources / 'web/index.html').write_text('<link href="css/style.css"><script src="js/config.js"></script><script src="js/library.js"></script><script src="js/app.js"></script><script src="js/reader.js"></script>', encoding='utf-8')
        self.paths = AppPaths(self.resources, self.base / 'user', self.base / 'user/web')

    def test_versioned_deployment_preserves_data_and_user_files(self):
        self.paths.library.parent.mkdir(parents=True)
        self.paths.library.write_text('old library')
        user = self.paths.web / 'my-file.txt'
        user.write_text('user data')
        prepare_web(self.paths)
        index = (self.paths.web / 'index.html').read_text()
        self.assertIn('versions/', index)
        self.assertIn('src="js/library.js"', index)
        prepare_web(self.paths)
        self.assertEqual(len(list((self.paths.web / 'versions').iterdir())), 1)
        (self.resources / 'web/js/app.js').write_text('updated')
        prepare_web(self.paths)
        self.assertEqual(len(list((self.paths.web / 'versions').iterdir())), 2)
        self.assertEqual(self.paths.library.read_text(), 'old library')
        self.assertEqual(user.read_text(), 'user data')
        self.assertNotEqual((self.paths.web / 'index.html').read_text(), index)

    def test_failure_keeps_published_index(self):
        prepare_web(self.paths)
        index = (self.paths.web / 'index.html').read_bytes()
        (self.resources / 'web/js/app.js').write_text('updated')
        with patch('app.paths.atomic_write', side_effect=PermissionError('locked')):
            with self.assertRaises(PermissionError):
                prepare_web(self.paths)
        self.assertEqual((self.paths.web / 'index.html').read_bytes(), index)
