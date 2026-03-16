from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, FrozenSet


class SchemeError(Exception):
    """Base class for scheme-level errors."""


class PolicyNotSatisfiedError(SchemeError):
    """Raised when static or dynamic policy checks fail."""


class RevokedUserError(SchemeError):
    """Raised when a revoked user requests service."""


class RevokedAttributeError(SchemeError):
    """Raised when an attribute has been revoked."""


class IntegrityError(SchemeError):
    """Raised when integrity verification fails."""


class CertificateError(SchemeError):
    """Raised when a certificate is malformed or expired."""


@dataclass(slots=True)
class PublicParams:
    security_param: str
    system_salt: bytes


@dataclass(slots=True)
class MasterSecretKey:
    root_secret: bytes


@dataclass(slots=True)
class Certificate:
    cert_id: str
    uid: str
    static_attrs: dict[str, int | None]
    issued_at: int
    valid_until: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class UserSecretKey:
    uid: str
    secret_seed: bytes
    static_attrs: FrozenSet[str]
    dynamic_attrs: FrozenSet[str]


@dataclass(slots=True)
class TransformKey:
    uid: str
    cert_id: str
    link_token: bytes


@dataclass(slots=True)
class FinalKey:
    uid: str
    cert_id: str
    link_token: bytes
    issued_static_attrs: FrozenSet[str]


@dataclass(slots=True)
class KeyBundle:
    certificate: Certificate
    user_secret_key: UserSecretKey
    transform_key: TransformKey
    final_key: FinalKey


@dataclass(slots=True)
class Ciphertext:
    static_policy: FrozenSet[str]
    dynamic_policy: FrozenSet[str]
    payload_nonce: bytes
    session_nonce: bytes
    payload_ciphertext: bytes
    session_blob: bytes
    tag: str
    aad_digest: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TransformedCiphertext:
    uid: str
    cert_id: str
    static_policy: FrozenSet[str]
    dynamic_policy: FrozenSet[str]
    payload_nonce: bytes
    session_nonce: bytes
    payload_ciphertext: bytes
    transformed_session_blob: bytes
    tag: str
    aad_digest: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RevocationState:
    revoked_users: set[str] = field(default_factory=set)
    revoked_static_attrs: dict[str, set[str]] = field(default_factory=dict)
    revoked_dynamic_attrs: dict[str, set[str]] = field(default_factory=dict)
