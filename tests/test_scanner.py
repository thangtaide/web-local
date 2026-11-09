import hashlib
import json
import shutil
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
import stat
from app.scanner import ScanError, scan_library, write_library, natural_key, io_path


class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='manga-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'Truyện dấu cách # % &'
        self.root.mkdir()

    def image(self, relative, content=b'fixture image'):
        path = self.root / relative
        io_path(path.parent).mkdir(parents=True, exist_ok=True)
        io_path(path).write_bytes(content)
        return path

    def test_valid_sort_formats_cover_unicode_and_source_unchanged(self):
        formats = ['1.JPG', '2.jpeg', '10.PNG', '11.WebP', '12.GIF', '13.AVIF']
        paths = [self.image('Truyện Đặc Biệt/Tập 2/' + name) for name in reversed(formats)]
        self.image('Truyện Đặc Biệt/Tập 10/1.jpg')
        (self.root / 'Truyện Đặc Biệt/Tập 1').mkdir()
        self.image('Truyện Đặc Biệt/Tập 2/ignore.txt')
        before = {p: (hashlib.sha256(p.read_bytes()).digest(), p.stat().st_mtime_ns) for p in paths}
        data = scan_library(self.root)
        self.assertEqual(data['stats'], {'stories': 1, 'chapters': 2, 'images': 7})
        story = data['stories'][0]
        self.assertEqual([c['name'] for c in story['chapters']], ['Tập 2', 'Tập 10'])
        self.assertEqual(story['chapters'][0]['images'], [(paths[0].parent / name).as_uri() for name in formats])
        self.assertEqual(story['cover'], (paths[0].parent / '1.JPG').as_uri())
        self.assertIn('%23', story['cover'])
        self.assertIn('%25', story['cover'])
        self.assertIn('%20', story['cover'])
        self.assertEqual(before, {p: (hashlib.sha256(p.read_bytes()).digest(), p.stat().st_mtime_ns) for p in paths})

    def test_empty_and_ignored_files(self):
        (self.root / 'Empty/Chapter').mkdir(parents=True)
        self.image('Empty/Chapter/a.pdf')
        self.assertEqual(scan_library(self.root)['stats'], {'stories': 0, 'chapters': 0, 'images': 0})

    def test_natural_sort_multiple_numbers_ties_unicode(self):
        names = ['Tập 10', 'Tập 2 phần 10', 'Tập 2 phần 2', 'Tập 1', 'tập 01', 'Tập 2']
        result = sorted(names, key=natural_key)
        self.assertLess(result.index('Tập 2'), result.index('Tập 10'))
        self.assertLess(result.index('Tập 2 phần 2'), result.index('Tập 2 phần 10'))
        self.assertEqual(result, sorted(reversed(names), key=natural_key))

    def test_ids_survive_relocation_and_insertion(self):
        self.image('Story/Chapter/1.jpg')
        first = scan_library(self.root)['stories'][0]
        new = self.root.parent / 'new root'
        shutil.copytree(self.root, new)
        self.image('AAA/Chapter/1.jpg')
        after = next(s for s in scan_library(self.root)['stories'] if s['name'] == 'Story')
        moved = scan_library(new)['stories'][0]
        self.assertEqual(first['id'], after['id'])
        self.assertEqual(first['id'], moved['id'])
        self.assertEqual(first['chapters'][0]['id'], moved['chapters'][0]['id'])

    def test_atomic_serialization_special_names_and_rollback(self):
        self.image("Tên ' quote &/Tập 1/1.jpg")
        path = self.root.parent / 'web/js/library.js'
        data = scan_library(self.root)
        data['stories'][0]['name'] += ' " </script> \\ \u2028'
        write_library(path, data)
        original = path.read_bytes()
        parsed = json.loads(original.decode()[len('window.MANGA_LIBRARY = '):-2])
        self.assertEqual(parsed, data)
        with patch('app.storage.os.replace', side_effect=PermissionError('locked')):
            with self.assertRaises(PermissionError):
                write_library(path, data)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(list(path.parent.glob('*.tmp')), [])
        data['bad'] = object()
        with self.assertRaises(TypeError):
            write_library(path, data)
        self.assertEqual(path.read_bytes(), original)

    def test_access_error_and_missing_image_abort(self):
        self.image('Story/Chapter/1.jpg')
        for error in [PermissionError('denied'), FileNotFoundError('deleted')]:
            with patch('app.scanner.entries', side_effect=error):
                with self.assertRaises(ScanError):
                    scan_library(self.root)
        with patch('pathlib.Path.open', side_effect=PermissionError('image denied')):
            with self.assertRaises(ScanError):
                scan_library(self.root)

    def test_missing_root(self):
        with self.assertRaises(ScanError):
            scan_library(self.root / 'missing')

    def test_outside_project_cross_drive_and_long_path(self):
        path = self.image(('Tên dài ' * 15).rstrip() + '/' + ('Chương ' * 15).rstrip() + '/1 # % &.jpg')
        self.addCleanup(io_path(path.parent).rmdir)
        self.addCleanup(io_path(path).unlink)
        data = scan_library(self.root)
        self.assertEqual(data['stories'][0]['cover'], path.as_uri())
        self.assertNotIn(str(Path(__file__).resolve().parent.parent), str(self.root))

    def test_ten_thousand_images(self):
        for number in range(10000):
            self.image(f'Story/Chapter/{number}.png', b'x')
        data = scan_library(self.root)
        self.assertEqual(data['stats']['images'], 10000)
        self.assertTrue(data['stories'][0]['chapters'][0]['images'][-1].endswith('/9999.png'))

    def test_symbolic_directory_is_reported_not_silently_skipped(self):
        entry = MagicMock()
        entry.stat.return_value.st_mode = stat.S_IFLNK
        entry.is_symlink.return_value = True
        entry.path = 'linked-folder'
        iterator = MagicMock()
        iterator.__enter__.return_value = [entry]
        with patch('app.scanner.os.scandir', return_value=iterator):
            with self.assertRaisesRegex(ScanError, 'junction'):
                scan_library(self.root)

    def test_extended_root_still_produces_standard_file_uri(self):
        image = self.image('Story/Chapter/1.jpg')
        result = scan_library(io_path(self.root))
        self.assertEqual(result['stories'][0]['cover'], image.as_uri())
