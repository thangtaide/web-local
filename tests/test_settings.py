import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from app.settings import load_settings, save_settings, SettingsError


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'data/settings.json'

    def test_missing_and_unicode_roundtrip(self):
        self.assertEqual(load_settings(self.path), '')
        save_settings(self.path, 'Truyện Đặc Biệt # % &')
        self.assertEqual(load_settings(self.path), 'Truyện Đặc Biệt # % &')

    def test_corrupt_file_is_reported_and_preserved(self):
        self.path.parent.mkdir()
        self.path.write_text('{bad', encoding='utf-8')
        with self.assertRaises(SettingsError):
            load_settings(self.path)
        self.assertEqual(self.path.read_text(), '{bad')

    def test_atomic_failure_preserves_old_settings(self):
        save_settings(self.path, 'old')
        with patch('app.storage.os.replace', side_effect=PermissionError('locked')):
            with self.assertRaises(PermissionError):
                save_settings(self.path, 'new')
        self.assertEqual(load_settings(self.path), 'old')
        self.assertEqual(list(self.path.parent.glob('*.tmp')), [])
