from __future__ import annotations

import secrets
from typing import Iterable

from .types import Ciphertext, PublicParams
from .utils import derive_bytes, digest_bytes, normalize_attrs, symmetric_encrypt, xor_bytes, make_tag


def _policy_mask(
    pp: PublicParams,
    static_policy: Iterable[str],
    dynamic_policy: Iterable[str],
    session_nonce: bytes,
) -> bytes:
    return derive_bytes(
        pp.system_salt,
        session_nonce,
        normalize_attrs(static_policy),
        normalize_attrs(dynamic_policy),
        'policy-mask',
        length=32,
    )


def encrypt(
    pp: PublicParams,
    message: bytes,
    static_policy: Iterable[str],
    dynamic_policy: Iterable[str],
    associated_data: bytes | None = None,
    metadata: dict | None = None,
) -> Ciphertext:
    static_tuple = normalize_attrs(static_policy)
    dynamic_tuple = normalize_attrs(dynamic_policy)
    session_key = secrets.token_bytes(32)
    payload_nonce = secrets.token_bytes(16)
    session_nonce = secrets.token_bytes(16)
    payload_ciphertext = symmetric_encrypt(session_key, message, payload_nonce)
    session_blob = xor_bytes(session_key, _policy_mask(pp, static_tuple, dynamic_tuple, session_nonce))
    aad_digest = digest_bytes(associated_data)
    tag = make_tag(payload_nonce, session_nonce, payload_ciphertext, session_blob, aad_digest)
    return Ciphertext(
        static_policy=frozenset(static_tuple),
        dynamic_policy=frozenset(dynamic_tuple),
        payload_nonce=payload_nonce,
        session_nonce=session_nonce,
        payload_ciphertext=payload_ciphertext,
        session_blob=session_blob,
        tag=tag,
        aad_digest=aad_digest,
        metadata=dict(metadata or {}),
    )
