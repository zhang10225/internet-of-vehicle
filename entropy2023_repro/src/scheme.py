from __future__ import annotations

import secrets
from typing import Sequence

from .charm_support import GT
from .types import Ciphertext, PublicParams
from .utils import (
    derive_mask_from_gt,
    digest_bytes,
    digest_charm_object,
    make_message_tag,
    policy_to_charm,
    symmetric_encrypt,
    xor_bytes,
)


def encrypt(
    pp: PublicParams,
    message: bytes,
    static_policy: str | Sequence[str],
    dynamic_policy: str | Sequence[str],
    associated_data: bytes | None = None,
    metadata: dict | None = None,
) -> Ciphertext:
    static_policy_str, static_policy_attrs = policy_to_charm(static_policy)
    dynamic_policy_str, dynamic_policy_attrs = policy_to_charm(dynamic_policy)

    session_key = secrets.token_bytes(32)
    payload_nonce = secrets.token_bytes(16)
    payload_ciphertext = symmetric_encrypt(session_key, message, payload_nonce)

    static_secret = pp.group.random(GT)
    dynamic_secret = pp.group.random(GT)
    static_ct = pp.static_abe.encrypt(pp.static_pk, static_secret, static_policy_str)
    dynamic_ct = pp.dynamic_abe.encrypt(pp.dynamic_pk, dynamic_secret, dynamic_policy_str)

    static_mask = derive_mask_from_gt(pp.group, static_secret, length=len(session_key))
    dynamic_mask = derive_mask_from_gt(pp.group, dynamic_secret, length=len(session_key))
    wrapped_session = xor_bytes(xor_bytes(session_key, static_mask), dynamic_mask)

    static_ct_digest = digest_charm_object(static_ct, pp.group)
    dynamic_ct_digest = digest_charm_object(dynamic_ct, pp.group)
    aad_digest = digest_bytes(associated_data)
    message_tag = make_message_tag(
        session_key,
        payload_nonce,
        payload_ciphertext,
        static_ct_digest,
        dynamic_ct_digest,
        aad_digest,
    )

    return Ciphertext(
        static_policy_str=static_policy_str,
        dynamic_policy_str=dynamic_policy_str,
        static_policy_attrs=static_policy_attrs,
        dynamic_policy_attrs=dynamic_policy_attrs,
        payload_nonce=payload_nonce,
        payload_ciphertext=payload_ciphertext,
        wrapped_session=wrapped_session,
        static_ct=static_ct,
        dynamic_ct=dynamic_ct,
        static_ct_digest=static_ct_digest,
        dynamic_ct_digest=dynamic_ct_digest,
        message_tag=message_tag,
        aad_digest=aad_digest,
        metadata=dict(metadata or {}),
    )
