"""Small sparse overwrite patches; all callers must verify whole-file SHA-256."""
import struct

MAGIC = b'LSP1'

def make_patch(original: bytes, target: bytes) -> bytes:
    chunks = []
    i = 0
    while i < len(target):
        if i < len(original) and original[i] == target[i]:
            i += 1
            continue
        start = i
        i += 1
        while i < len(target) and (i >= len(original) or original[i] != target[i]):
            i += 1
        chunks.append((start, target[start:i]))
    out = bytearray(MAGIC + struct.pack('<III', len(original), len(target), len(chunks)))
    for offset, data in chunks:
        out.extend(struct.pack('<II', offset, len(data)))
        out.extend(data)
    return bytes(out)

def apply_patch(original: bytes, patch: bytes) -> bytes:
    if len(patch) < 16 or patch[:4] != MAGIC:
        raise ValueError('Invalid patch header')
    original_size, target_size, count = struct.unpack_from('<III', patch, 4)
    if len(original) != original_size:
        raise ValueError('Original file length differs')
    out = bytearray(target_size)
    out[:min(original_size, target_size)] = original[:target_size]
    pos, end = 16, 0
    for _ in range(count):
        if pos + 8 > len(patch):
            raise ValueError('Truncated chunk header')
        offset, length = struct.unpack_from('<II', patch, pos)
        pos += 8
        if offset < end or offset + length > target_size or pos + length > len(patch):
            raise ValueError('Invalid chunk bounds')
        out[offset:offset + length] = patch[pos:pos + length]
        pos += length
        end = offset + length
    if pos != len(patch):
        raise ValueError('Trailing patch data')
    return bytes(out)
