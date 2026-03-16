from __future__ import annotations

from .scheme import _policy_mask
from .types import FinalKey, IntegrityError, PolicyNotSatisfiedError, PublicParams, TransformedCiphertext
from .utils import derive_bytes, make_tag, symmetric_decrypt, xor_bytes


def final_decrypt(
    pp: PublicParams,
    final_key: FinalKey,
    transformed_ciphertext: TransformedCiphertext,
) -> bytes:
    if final_key.uid != transformed_ciphertext.uid or final_key.cert_id != transformed_ciphertext.cert_id:
        raise ValueError('final key does not match transformed ciphertext')
    if not transformed_ciphertext.static_policy.issubset(final_key.issued_static_attrs):
        raise PolicyNotSatisfiedError('final key does not cover required static policy')

    transformed_mask = derive_bytes(
        final_key.link_token,
        transformed_ciphertext.cert_id,
        transformed_ciphertext.tag,
        'transform-mask',
        length=len(transformed_ciphertext.transformed_session_blob),
    )
    session_blob = xor_bytes(transformed_ciphertext.transformed_session_blob, transformed_mask)
    expected_tag = make_tag(
        transformed_ciphertext.payload_nonce,
        transformed_ciphertext.session_nonce,
        transformed_ciphertext.payload_ciphertext,
        session_blob,
        transformed_ciphertext.aad_digest,
    )
    if expected_tag != transformed_ciphertext.tag:
        raise IntegrityError('integrity verification failed')

    session_key = xor_bytes(
        session_blob,
        _policy_mask(
            pp,
            transformed_ciphertext.static_policy,
            transformed_ciphertext.dynamic_policy,
            transformed_ciphertext.session_nonce,
        ),
    )
    return symmetric_decrypt(
        session_key,
        transformed_ciphertext.payload_ciphertext,
        transformed_ciphertext.payload_nonce,
    )
