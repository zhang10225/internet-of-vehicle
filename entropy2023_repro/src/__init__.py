"""Clean-room Entropy 2023 reproduction skeleton built on Charm-Crypto.

This package is a research baseline, not the authors' original code and not a
production-secure implementation. It uses Charm's pairing group and CP-ABE
scheme to provide a reproducible protocol flow with revocation hooks.
"""

from .ta import setup, keygen, attr_revoke, revoke_user
from .scheme import encrypt
from .rsu import rsu_transform
from .obu import final_decrypt
from .types import (
    Certificate,
    CharmUnavailableError,
    Ciphertext,
    FinalKey,
    IntegrityError,
    KeyBundle,
    MasterSecretKey,
    PolicyNotSatisfiedError,
    PublicParams,
    RevokedAttributeError,
    RevokedUserError,
    RevocationState,
    TransformKey,
    TransformedCiphertext,
    UserSecretKey,
)

__all__ = [
    'setup',
    'keygen',
    'encrypt',
    'rsu_transform',
    'final_decrypt',
    'attr_revoke',
    'revoke_user',
    'Certificate',
    'CharmUnavailableError',
    'Ciphertext',
    'FinalKey',
    'IntegrityError',
    'KeyBundle',
    'MasterSecretKey',
    'PolicyNotSatisfiedError',
    'PublicParams',
    'RevokedAttributeError',
    'RevokedUserError',
    'RevocationState',
    'TransformKey',
    'TransformedCiphertext',
    'UserSecretKey',
]
