import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from app.manager import scan_and_publish
from app.paths import AppPaths
from app.scanner import ScanError


class PipelineTests(unittest.TestCase):
    def test_real_scan_publish_then_failure_preserves_data(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            paths = AppPaths(base, base / 'data', base / 'web')
            chapter = base / 'library/Story/Chapter'
            chapter.mkdir(parents=True)
            image = chapter / '1.jpg'
            image.write_bytes(b'sample')
            self.assertEqual(scan_and_publish(base / 'library', paths)['images'], 1)
            original = paths.library.read_bytes()
            with patch('app.scanner.entries', side_effect=PermissionError('denied')):
                with self.assertRaises(ScanError):
                    scan_and_publish(base / 'library', paths)
            self.assertEqual(paths.library.read_bytes(), original)
