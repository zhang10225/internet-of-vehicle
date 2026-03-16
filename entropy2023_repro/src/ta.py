from __future__ import annotations

import secrets
from typing import Iterable

from .cert import issue_certificate
from .config import DEFAULT_CERT_VALIDITY, DEFAULT_SECURITY_PARAM
from .types import FinalKey, KeyBundle, MasterSecretKey, PublicParams, RevocationState, TransformKey, UserSecretKey
from .utils import derive_bytes, normalize_attrs


def setup(security_param: str = DEFAULT_SECURITY_PARAM) -> tuple[PublicParams, MasterSecretKey]:
    pp = PublicParams(security_param=security_param, system_salt=secrets.token_bytes(32))
    msk = MasterSecretKey(root_secret=secrets.token_bytes(32))
    return pp, msk


def keygen(
    pp: PublicParams,
    msk: MasterSecretKey,
    uid: str,
    static_attrs: Iterable[str],
    dynamic_attrs: Iterable[str] | None = None,
    issued_at: int = 0,
    attr_ttls: dict[str, int] | None = None,
) -> KeyBundle:
    del pp
    static_tuple = normalize_attrs(static_attrs)
    dynamic_tuple = normalize_attrs(dynamic_attrs or [])
    certificate = issue_certificate(
        uid=uid,
        static_attrs=static_tuple,
        issued_at=issued_at,
        validity=DEFAULT_CERT_VALIDITY,
        attr_ttls=attr_ttls,
    )
    user_secret_key = UserSecretKey(
        uid=uid,
        secret_seed=derive_bytes(msk.root_secret, uid, 'user-secret', length=32),
        static_attrs=frozenset(static_tuple),
        dynamic_attrs=frozenset(dynamic_tuple),
    )
    link_token = derive_bytes(msk.root_secret, uid, certificate.cert_id, 'link-token', length=32)
    transform_key = TransformKey(uid=uid, cert_id=certificate.cert_id, link_token=link_token)
    final_key = FinalKey(
        uid=uid,
        cert_id=certificate.cert_id,
        link_token=link_token,
        issued_static_attrs=frozenset(static_tuple),
    )
    return KeyBundle(
        certificate=certificate,
        user_secret_key=user_secret_key,
        transform_key=transform_key,
        final_key=final_key,
    )


def revoke_user(revocation_state: RevocationState, uid: str) -> RevocationState:
    revocation_state.revoked_users.add(uid)
    return revocation_state


def attr_revoke(
    revocation_state: RevocationState,
    uid: str,
    attr_name: str,
    revoke_type: str = 'static',
) -> RevocationState:
    if revoke_type == 'static':
        revocation_state.revoked_static_attrs.setdefault(uid, set()).add(attr_name)
        return revocation_state
    if revoke_type == 'dynamic':
        revocation_state.revoked_dynamic_attrs.setdefault(uid, set()).add(attr_name)
        return revocation_state
    if revoke_type == 'user':
        return revoke_user(revocation_state, uid)
    raise ValueError(f'unsupported revoke_type: {revoke_type}')
