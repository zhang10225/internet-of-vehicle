from __future__ import annotations

import secrets
from typing import Iterable

from .types import Certificate, CertificateError


def issue_certificate(
    uid: str,
    static_attrs: Iterable[str],
    issued_at: int = 0,
    validity: int | None = None,
    attr_ttls: dict[str, int] | None = None,
    metadata: dict | None = None,
) -> Certificate:
    attr_map: dict[str, int | None] = {}
    for attr in set(static_attrs):
        ttl = None if attr_ttls is None else attr_ttls.get(attr)
        attr_map[attr] = None if ttl is None else issued_at + ttl
    valid_until = None if validity is None else issued_at + validity
    return Certificate(
        cert_id=secrets.token_hex(8),
        uid=uid,
        static_attrs=attr_map,
        issued_at=issued_at,
        valid_until=valid_until,
        metadata=dict(metadata or {}),
    )


def is_certificate_valid(certificate: Certificate, at_time: int) -> bool:
    if certificate.valid_until is None:
        return True
    return at_time < certificate.valid_until


def get_valid_static_attrs(certificate: Certificate, at_time: int) -> set[str]:
    if not is_certificate_valid(certificate, at_time):
        raise CertificateError('certificate has expired')
    valid_attrs: set[str] = set()
    for attr, expiry in certificate.static_attrs.items():
        if expiry is None or at_time < expiry:
            valid_attrs.add(attr)
    return valid_attrs


def revoke_static_attr(certificate: Certificate, attr_name: str) -> None:
    certificate.static_attrs.pop(attr_name, None)


def expire_static_attr(certificate: Certificate, attr_name: str, expired_at: int) -> None:
    if attr_name not in certificate.static_attrs:
        raise CertificateError(f'attribute not found in certificate: {attr_name}')
    certificate.static_attrs[attr_name] = expired_at
