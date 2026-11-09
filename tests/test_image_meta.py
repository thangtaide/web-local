import io
import struct
import unittest
from app.image_meta import image_size
from tests.web_support import png


class ImageMetaTests(unittest.TestCase):
    def test_png_gif_jpeg_webp_avif_headers(self):
        fixtures = [
            png(400, 800),
            b'GIF89a' + struct.pack('<HH', 400, 800) + bytes(22),
            b'\xff\xd8\xff\xc0' + struct.pack('>H', 17) + b'\x08' + struct.pack('>HH', 800, 400) + bytes(10),
            b'RIFF' + bytes(4) + b'WEBPVP8X' + bytes(8) + (399).to_bytes(3, 'little') + (799).to_bytes(3, 'little') + bytes(2),
            struct.pack('>I', 24) + b'ftypavif' + bytes(12) + struct.pack('>I', 20) + b'ispe' + bytes(4) + struct.pack('>II', 400, 800)
        ]
        for data in fixtures:
            with self.subTest(header=data[:16]):
                self.assertEqual(image_size(io.BytesIO(data)), [400, 800])

    def test_corrupt_unknown_header(self):
        for data in [b'', b'bad', b'\xff\xd8\xff', b'GIF89a', b'RIFF0000WEBP']:
            self.assertIsNone(image_size(io.BytesIO(data)))
