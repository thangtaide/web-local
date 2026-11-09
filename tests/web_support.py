"""Generate harmless PNG fixtures without imaging dependencies."""
from pathlib import Path
import struct
import zlib


def png(width=400, height=800, color=(112, 83, 155)):
    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data) & 0xffffffff)
    data = (b'\0' + bytes(color) * width) * height
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', width, height, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(data)) + chunk(b'IEND', b'')


def create_library(root, count=25):
    for number in range(count):
        name = 'Truyện Đặc Biệt' if number == 0 else f'Truyện {number}'
        for chapter in [10, 2, 1]:
            folder = Path(root) / name / f'Tập {chapter}'
            folder.mkdir(parents=True)
            for page in [1, 2, 10]:
                (folder / f'{page} # % &.PNG').write_bytes(png(color=(60 + number * 5, 70 + chapter * 4, 130 + page * 2)))
