from __future__ import annotations

from .cert import get_valid_static_attrs
from .types import (
    Certificate,
    Ciphertext,
    IntegrityError,
    PolicyNotSatisfiedError,
    PublicParams,
    RevocationState,
    RevokedAttributeError,
    RevokedUserError,
    TransformKey,
    TransformedCiphertext,
)
from .utils import canonicalize_attrs, derive_mask_from_gt, digest_charm_object, xor_bytes


def rsu_transform(
    pp: PublicParams,
    certificate: Certificate,
    transform_key: TransformKey,
    ciphertext: Ciphertext,
    revocation_state: RevocationState,
    context: set[str],
    at_time: int = 0,
) -> TransformedCiphertext:
    if certificate.uid != transform_key.uid or certificate.cert_id != transform_key.cert_id:
        raise ValueError('certificate and transform key do not match')
    if certificate.uid in revocation_state.revoked_users:
        raise RevokedUserError(f'user revoked: {certificate.uid}')

    if digest_charm_object(ciphertext.static_ct, pp.group) != ciphertext.static_ct_digest:
        raise IntegrityError('static ciphertext digest mismatch')
    if digest_charm_object(ciphertext.dynamic_ct, pp.group) != ciphertext.dynamic_ct_digest:
        raise IntegrityError('dynamic ciphertext digest mismatch')

    active_static_attrs = get_valid_static_attrs(certificate, at_time)
    active_static_attrs -= revocation_state.revoked_static_attrs.get(certificate.uid, set())
    if not ciphertext.static_policy_attrs.issubset(active_static_attrs):
        raise PolicyNotSatisfiedError('static policy is not satisfied')

    context_tokens = set(canonicalize_attrs(context))
    blocked_dynamic = revocation_state.revoked_dynamic_attrs.get(certificate.uid, set())
    if ciphertext.dynamic_policy_attrs.intersection(blocked_dynamic):
        raise RevokedAttributeError('dynamic attribute has been revoked')
    if not ciphertext.dynamic_policy_attrs.issubset(context_tokens):
        raise PolicyNotSatisfiedError('dynamic policy is not satisfied')
    if not ciphertext.dynamic_policy_attrs.issubset(transform_key.dynamic_attrs):
        raise PolicyNotSatisfiedError('transform key does not cover required dynamic policy')

    recovered_dynamic_secret = pp.dynamic_abe.decrypt(pp.dynamic_pk, transform_key.dynamic_sk, ciphertext.dynamic_ct)
    if not recovered_dynamic_secret:
        raise PolicyNotSatisfiedError('dynamic CP-ABE decryption failed')

    dynamic_mask = derive_mask_from_gt(pp.group, recovered_dynamic_secret, length=len(ciphertext.wrapped_session))
    transformed_session_blob = xor_bytes(ciphertext.wrapped_session, dynamic_mask)

    return TransformedCiphertext(
        uid=certificate.uid,
        cert_id=certificate.cert_id,
        static_policy_str=ciphertext.static_policy_str,
        dynamic_policy_str=ciphertext.dynamic_policy_str,
        static_policy_attrs=ciphertext.static_policy_attrs,
        dynamic_policy_attrs=ciphertext.dynamic_policy_attrs,
        payload_nonce=ciphertext.payload_nonce,
        payload_ciphertext=ciphertext.payload_ciphertext,
        transformed_session_blob=transformed_session_blob,
        static_ct=ciphertext.static_ct,
        static_ct_digest=ciphertext.static_ct_digest,
        dynamic_ct_digest=ciphertext.dynamic_ct_digest,
        message_tag=ciphertext.message_tag,
        aad_digest=ciphertext.aad_digest,
        metadata={'context': sorted(context_tokens), 'at_time': at_time, **ciphertext.metadata},
    )
