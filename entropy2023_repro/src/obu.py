from __future__ import annotations

from .types import FinalKey, IntegrityError, PolicyNotSatisfiedError, PublicParams, TransformedCiphertext
from .utils import derive_mask_from_gt, digest_charm_object, make_message_tag, symmetric_decrypt, xor_bytes


def final_decrypt(
    pp: PublicParams,
    final_key: FinalKey,
    transformed_ciphertext: TransformedCiphertext,
) -> bytes:
    if final_key.uid != transformed_ciphertext.uid or final_key.cert_id != transformed_ciphertext.cert_id:
        raise ValueError('final key does not match transformed ciphertext')
    if not transformed_ciphertext.static_policy_attrs.issubset(final_key.issued_static_attrs):
        raise PolicyNotSatisfiedError('final key does not cover required static policy')
    if digest_charm_object(transformed_ciphertext.static_ct, pp.group) != transformed_ciphertext.static_ct_digest:
        raise IntegrityError('static ciphertext digest mismatch')

    recovered_static_secret = pp.static_abe.decrypt(
        pp.static_pk,
        final_key.static_sk,
        transformed_ciphertext.static_ct,
    )
    if not recovered_static_secret:
        raise PolicyNotSatisfiedError('static CP-ABE decryption failed')

    static_mask = derive_mask_from_gt(
        pp.group,
        recovered_static_secret,
        length=len(transformed_ciphertext.transformed_session_blob),
    )
    session_key = xor_bytes(transformed_ciphertext.transformed_session_blob, static_mask)

    expected_message_tag = make_message_tag(
        session_key,
        transformed_ciphertext.payload_nonce,
        transformed_ciphertext.payload_ciphertext,
        transformed_ciphertext.static_ct_digest,
        transformed_ciphertext.dynamic_ct_digest,
        transformed_ciphertext.aad_digest,
    )
    if expected_message_tag != transformed_ciphertext.message_tag:
        raise IntegrityError('integrity verification failed')

    return symmetric_decrypt(
        session_key,
        transformed_ciphertext.payload_ciphertext,
        transformed_ciphertext.payload_nonce,
    )
