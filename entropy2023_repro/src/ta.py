from __future__ import annotations

from typing import Iterable

from .cert import issue_certificate
from .charm_support import CPabe_BSW07, PairingGroup, ensure_charm_available
from .config import DEFAULT_CERT_VALIDITY, DEFAULT_DYNAMIC_ATTRS, DEFAULT_SECURITY_PARAM
from .types import (
    CharmUnavailableError,
    FinalKey,
    KeyBundle,
    MasterSecretKey,
    PublicParams,
    RevocationState,
    TransformKey,
    UserSecretKey,
)
from .utils import canonical_attr, canonicalize_attrs


def setup(security_param: str = DEFAULT_SECURITY_PARAM) -> tuple[PublicParams, MasterSecretKey]:
    try:
        ensure_charm_available()
    except RuntimeError as exc:  # pragma: no cover - depends on local Charm install
        raise CharmUnavailableError(str(exc)) from exc

    group = PairingGroup(security_param)
    static_abe = CPabe_BSW07(group)
    dynamic_abe = CPabe_BSW07(group)
    static_pk, static_msk = static_abe.setup()
    dynamic_pk, dynamic_msk = dynamic_abe.setup()
    pp = PublicParams(
        security_param=security_param,
        group=group,
        static_abe=static_abe,
        dynamic_abe=dynamic_abe,
        static_pk=static_pk,
        dynamic_pk=dynamic_pk,
    )
    msk = MasterSecretKey(static_msk=static_msk, dynamic_msk=dynamic_msk)
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
    static_tuple = canonicalize_attrs(static_attrs)
    dynamic_tuple = canonicalize_attrs(dynamic_attrs or DEFAULT_DYNAMIC_ATTRS)
    certificate = issue_certificate(
        uid=uid,
        static_attrs=static_tuple,
        issued_at=issued_at,
        validity=DEFAULT_CERT_VALIDITY,
        attr_ttls=attr_ttls,
    )
    static_sk = pp.static_abe.keygen(pp.static_pk, msk.static_msk, list(static_tuple))
    dynamic_sk = pp.dynamic_abe.keygen(pp.dynamic_pk, msk.dynamic_msk, list(dynamic_tuple))
    user_secret_key = UserSecretKey(
        uid=uid,
        static_sk=static_sk,
        static_attrs=frozenset(static_tuple),
        dynamic_attrs=frozenset(dynamic_tuple),
    )
    transform_key = TransformKey(
        uid=uid,
        cert_id=certificate.cert_id,
        dynamic_sk=dynamic_sk,
        dynamic_attrs=frozenset(dynamic_tuple),
    )
    final_key = FinalKey(
        uid=uid,
        cert_id=certificate.cert_id,
        static_sk=static_sk,
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
    token = canonical_attr(attr_name)
    if revoke_type == 'static':
        revocation_state.revoked_static_attrs.setdefault(uid, set()).add(token)
        return revocation_state
    if revoke_type == 'dynamic':
        revocation_state.revoked_dynamic_attrs.setdefault(uid, set()).add(token)
        return revocation_state
    if revoke_type == 'user':
        return revoke_user(revocation_state, uid)
    raise ValueError(f'unsupported revoke_type: {revoke_type}')
