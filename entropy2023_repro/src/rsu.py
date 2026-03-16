from __future__ import annotations

from .cert import get_valid_static_attrs
from .types import PolicyNotSatisfiedError, RevokedAttributeError, RevokedUserError, RevocationState, TransformKey, TransformedCiphertext, Ciphertext, Certificate, PublicParams
from .utils import derive_bytes, xor_bytes


def rsu_transform(
    pp: PublicParams,
    certificate: Certificate,
    transform_key: TransformKey,
    ciphertext: Ciphertext,
    revocation_state: RevocationState,
    context: set[str],
    at_time: int = 0,
) -> TransformedCiphertext:
    del pp
    if certificate.uid != transform_key.uid or certificate.cert_id != transform_key.cert_id:
        raise ValueError('certificate and transform key do not match')
    if certificate.uid in revocation_state.revoked_users:
        raise RevokedUserError(f'user revoked: {certificate.uid}')

    active_static_attrs = get_valid_static_attrs(certificate, at_time)
    active_static_attrs -= revocation_state.revoked_static_attrs.get(certificate.uid, set())
    if not ciphertext.static_policy.issubset(active_static_attrs):
        raise PolicyNotSatisfiedError('static policy is not satisfied')

    blocked_dynamic = revocation_state.revoked_dynamic_attrs.get(certificate.uid, set())
    if ciphertext.dynamic_policy.intersection(blocked_dynamic):
        raise RevokedAttributeError('dynamic attribute has been revoked')
    if not ciphertext.dynamic_policy.issubset(context):
        raise PolicyNotSatisfiedError('dynamic policy is not satisfied')

    transformed_mask = derive_bytes(
        transform_key.link_token,
        certificate.cert_id,
        ciphertext.tag,
        'transform-mask',
        length=len(ciphertext.session_blob),
    )
    transformed_session_blob = xor_bytes(ciphertext.session_blob, transformed_mask)
    return TransformedCiphertext(
        uid=certificate.uid,
        cert_id=certificate.cert_id,
        static_policy=ciphertext.static_policy,
        dynamic_policy=ciphertext.dynamic_policy,
        payload_nonce=ciphertext.payload_nonce,
        session_nonce=ciphertext.session_nonce,
        payload_ciphertext=ciphertext.payload_ciphertext,
        transformed_session_blob=transformed_session_blob,
        tag=ciphertext.tag,
        aad_digest=ciphertext.aad_digest,
        metadata={'context': sorted(context), 'at_time': at_time, **ciphertext.metadata},
    )
