"""Reproducible geometric book icon, using only the standard library."""
from pathlib import Path
import struct
import zlib


def icon_png(size):
    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data) & 0xffffffff)
    pixels = bytearray()
    for row in range(size):
        pixels.append(0)
        y = (row + .5) / size
        for column in range(size):
            x = (column + .5) / size
            outside = ((max(.16-x, 0, x-.84))**2 + (max(.16-y, 0, y-.84))**2) > .14**2
            color = (0, 0, 0, 0) if outside else (44, 36, 64, 255)
            if .19 <= x <= .81 and .23 <= y <= .76:
                center = abs(x - .5)
                if y >= .23 + .12 * (1 - center/.31) and y <= .76 + .1 * (1 - center/.31):
                    color = (216, 198, 255, 255)
                    if .485 < x < .515:
                        color = (100, 79, 135, 255)
                    if (.27 < x < .42 or .58 < x < .73) and (.47 < y < .49 or .56 < y < .58 or .65 < y < .67):
                        color = (137, 115, 173, 255)
            pixels.extend(color)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', size, size, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(pixels)) + chunk(b'IEND', b'')


def main():
    sizes = [16, 32, 48, 64, 128, 256]
    images = [icon_png(size) for size in sizes]
    offset = 6 + 16 * len(sizes)
    entries = []
    for size, image in zip(sizes, images):
        entries.append(struct.pack('<4B2H2I', size % 256, size % 256, 0, 0, 1, 32, len(image), offset))
        offset += len(image)
    target = Path(__file__).resolve().parent.parent / 'assets/app.ico'
    target.parent.mkdir(exist_ok=True)
    target.write_bytes(struct.pack('<3H', 0, 1, len(sizes)) + b''.join(entries) + b''.join(images))


if __name__ == '__main__':
    main()
