"""Best-effort dimensions from small headers, without decoding image pixels."""
import struct


def image_size(stream):
    head = stream.read(32)
    try:
        size = None
        if head.startswith(b'\x89PNG\r\n\x1a\n') and head[12:16] == b'IHDR':
            size = struct.unpack('>II', head[16:24])
        elif head[:6] in (b'GIF87a', b'GIF89a'):
            size = struct.unpack('<HH', head[6:10])
        elif head[:2] == b'\xff\xd8':
            stream.seek(2)
            # Bound metadata traversal to avoid pathological/corrupt files.
            while stream.tell() < 262144:
                marker = stream.read(2)
                if len(marker) != 2 or marker[0] != 255:
                    break
                while marker[1] == 255:
                    marker = b'\xff' + stream.read(1)
                    if len(marker) != 2:
                        break
                if len(marker) != 2 or marker[1] in (0xda, 0xd9):
                    break
                if marker[1] == 1 or 0xd0 <= marker[1] <= 0xd8:
                    continue
                length = struct.unpack('>H', stream.read(2))[0]
                if length < 2:
                    break
                if marker[1] in (0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf):
                    height, width = struct.unpack('>HH', stream.read(5)[1:5])
                    size = width, height
                    break
                stream.seek(length - 2, 1)
        elif head[:4] == b'RIFF' and head[8:12] == b'WEBP':
            kind = head[12:16]
            if kind == b'VP8X':
                size = 1 + int.from_bytes(head[24:27], 'little'), 1 + int.from_bytes(head[27:30], 'little')
            elif kind == b'VP8 ' and head[23:26] == b'\x9d\x01\x2a':
                width, height = struct.unpack('<HH', head[26:30])
                size = width & 16383, height & 16383
            elif kind == b'VP8L' and head[20] == 0x2f:
                bits = int.from_bytes(head[21:25], 'little')
                size = (bits & 16383) + 1, ((bits >> 14) & 16383) + 1
        elif head[4:8] == b'ftyp' and (b'avif' in head or b'avis' in head):
            stream.seek(0)
            data = stream.read(262144)
            offset = data.find(b'ispe')
            if offset >= 4 and len(data) >= offset + 16 and int.from_bytes(data[offset-4:offset], 'big') >= 20:
                size = struct.unpack('>II', data[offset+8:offset+16])
        if size and all(0 < value <= 1000000 for value in size):
            return list(size)
    except (ValueError, IndexError, struct.error):
        pass
    return None
