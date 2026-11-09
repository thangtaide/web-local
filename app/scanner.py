"""Read-only, deterministic library scanner. Any access/race error aborts the scan."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import unicodedata

from app.storage import atomic_write

IMAGE_EXTENSIONS = frozenset({'.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif'})


class ScanError(Exception):
    """An incomplete library must never replace a previously valid library."""


def io_path(path):
    """Extended Windows paths for IO only; public URIs keep standard drive/UNC syntax."""
    value = str(path)
    if os.name == 'nt' and not value.startswith('\\\\?\\'):
        if value.startswith('\\\\'):
            return Path('\\\\?\\UNC\\' + value[2:])
        if Path(value).is_absolute():
            return Path('\\\\?\\' + value)
    return Path(value)


def natural_key(value):
    original = str(value)
    normalized = unicodedata.normalize('NFKC', original).casefold()
    parts = tuple((1, int(part)) if part.isdecimal() else (0, part)
                  for part in re.split(r'(\d+)', normalized) if part)
    return parts, normalized, original


def stable_id(relative_path):
    return hashlib.sha256(str(relative_path).replace('\\', '/').encode('utf-8')).hexdigest()[:24]


def entries(path, directories):
    result = []
    with os.scandir(io_path(path)) as iterator:
        for entry in iterator:
            # stat errors (including a disappearing entry) propagate instead of silently skipping.
            info = entry.stat(follow_symlinks=False)
            relevant = stat.S_ISDIR(info.st_mode) if directories else Path(entry.name).suffix.lower() in IMAGE_EXTENSIONS
            if not relevant:
                continue
            if entry.is_symlink() or getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise ScanError(f'Không hỗ trợ liên kết/junction trong thư viện: {entry.path}')
            if directories or stat.S_ISREG(info.st_mode):
                result.append(Path(path) / entry.name)
    return sorted(result, key=lambda item: natural_key(item.name))


def scan_library(folder):
    root = Path(folder).expanduser().resolve()
    stories = []
    chapter_count = image_count = 0
    try:
        if not io_path(root).is_dir():
            raise ScanError('Thư mục thư viện không tồn tại hoặc không thể truy cập.')
        for story_dir in entries(root, True):
            chapters = []
            for chapter_dir in entries(story_dir, True):
                images = []
                for image in entries(chapter_dir, False):
                    # Verify readability, without decoding or changing the image.
                    with io_path(image).open('rb') as stream:
                        stream.read(1)
                    images.append(image.as_uri())
                if images:
                    chapters.append({'id': stable_id(chapter_dir.relative_to(root).as_posix()),
                                     'name': chapter_dir.name, 'images': images, 'image_count': len(images)})
                    image_count += len(images)
            if chapters:
                stories.append({'id': stable_id(story_dir.relative_to(root).as_posix()),
                                'name': story_dir.name, 'cover': chapters[0]['images'][0],
                                'chapters': chapters, 'chapter_count': len(chapters)})
                chapter_count += len(chapters)
    except OSError as exc:
        raise ScanError(f'Không đọc được đầy đủ thư viện. Kiểm tra quyền truy cập hoặc quét lại nếu file vừa thay đổi. Chi tiết: {exc}') from exc
    return {'schema_version': 1, 'source': {'name': root.name, 'uri': root.as_uri()},
            'scanned_at': datetime.now(timezone.utc).isoformat(),
            'stats': {'stories': len(stories), 'chapters': chapter_count, 'images': image_count},
            'stories': stories}


def write_library(path, library):
    if not isinstance(library, dict) or library.get('schema_version') != 1 or not isinstance(library.get('stories'), list):
        raise ValueError('Dữ liệu thư viện không hợp lệ.')
    serialized = json.dumps(library, ensure_ascii=True, allow_nan=False, separators=(',', ':'))
    serialized = serialized.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    atomic_write(path, 'window.MANGA_LIBRARY = ' + serialized + ';\n')
