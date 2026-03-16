from __future__ import annotations

import hashlib
from typing import Iterable


def _to_bytes(part: object) -> bytes:
    if isinstance(part, bytes):
        return part
    if isinstance(part, str):
        return part.encode('utf-8')
    if isinstance(part, int):
        return str(part).encode('ascii')
    if isinstance(part, (tuple, list, set, frozenset)):
        joined = '|'.join(str(item) for item in part)
        return joined.encode('utf-8')
    return str(part).encode('utf-8')


def derive_bytes(*parts: object, length: int = 32) -> bytes:
    output = bytearray()
    counter = 0
    while len(output) < length:
        digest = hashlib.blake2b(digest_size=32)
        digest.update(counter.to_bytes(4, 'big'))
        for part in parts:
            digest.update(_to_bytes(part))
            digest.update(b'\x00')
        output.extend(digest.digest())
        counter += 1
    return bytes(output[:length])


def xor_bytes(left: bytes, right: bytes) -> bytes:
    if len(left) != len(right):
        raise ValueError('xor inputs must have the same length')
    return bytes(a ^ b for a, b in zip(left, right))


def symmetric_encrypt(key: bytes, plaintext: bytes, nonce: bytes) -> bytes:
    stream = derive_bytes(key, nonce, 'stream', length=len(plaintext))
    return xor_bytes(plaintext, stream)


symmetric_decrypt = symmetric_encrypt


def make_tag(*parts: object) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(_to_bytes(part))
        digest.update(b'\x00')
    return digest.hexdigest()


def digest_bytes(data: bytes | None) -> str:
    return hashlib.sha256(data or b'').hexdigest()


def normalize_attrs(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted({value for value in values}))


def match_policy(required: Iterable[str], provided: Iterable[str]) -> bool:
    return set(required).issubset(set(provided))
