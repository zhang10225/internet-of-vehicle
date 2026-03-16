from __future__ import annotations

import hashlib
import re
from typing import Iterable, Sequence

from .charm_support import ensure_charm_available, objectToBytes

_BOOLEAN_TOKENS = {'and', 'or'}
_ATTR_PATTERN = re.compile(r'[A-Za-z0-9_:\.-]+')


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


def digest_bytes(data: bytes | None) -> str:
    return hashlib.sha256(data or b'').hexdigest()


def canonical_attr(attr_name: str) -> str:
    token = re.sub(r'[^A-Za-z0-9]+', '_', attr_name).strip('_').upper()
    if not token:
        raise ValueError(f'invalid attribute label: {attr_name!r}')
    if token[0].isdigit():
        token = f'ATTR_{token}'
    return token


def canonicalize_attrs(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted({canonical_attr(value) for value in values}))


def _extract_policy_tokens(policy: str) -> tuple[str, ...]:
    tokens: list[str] = []
    for match in _ATTR_PATTERN.findall(policy):
        if match.lower() in _BOOLEAN_TOKENS:
            continue
        tokens.append(match)
    return tuple(sorted(set(tokens)))


def policy_to_charm(policy: str | Sequence[str]) -> tuple[str, frozenset[str]]:
    if isinstance(policy, str):
        return policy, frozenset(_extract_policy_tokens(policy))
    attrs = canonicalize_attrs(policy)
    if not attrs:
        raise ValueError('policy must contain at least one attribute')
    if len(attrs) == 1:
        return attrs[0], frozenset(attrs)
    return '(' + ' and '.join(attrs) + ')', frozenset(attrs)


def digest_charm_object(obj: object, group: object) -> str:
    ensure_charm_available()
    return hashlib.sha256(objectToBytes(obj, group)).hexdigest()


def derive_mask_from_gt(group: object, gt_element: object, length: int = 32) -> bytes:
    ensure_charm_available()
    serialized = objectToBytes(gt_element, group)
    return derive_bytes(serialized, 'gt-mask', length=length)


def make_message_tag(
    session_key: bytes,
    payload_nonce: bytes,
    payload_ciphertext: bytes,
    static_ct_digest: str,
    dynamic_ct_digest: str,
    aad_digest: str,
) -> str:
    digest = hashlib.sha256()
    digest.update(session_key)
    digest.update(payload_nonce)
    digest.update(payload_ciphertext)
    digest.update(static_ct_digest.encode('ascii'))
    digest.update(dynamic_ct_digest.encode('ascii'))
    digest.update(aad_digest.encode('ascii'))
    return digest.hexdigest()
