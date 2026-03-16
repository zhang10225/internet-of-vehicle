"""Clean-room Entropy 2023 reproduction skeleton.

This package reproduces the protocol flow, revocation hooks, and
benchmarking surfaces needed for a research baseline. It is not a
paper-exact or production-secure cryptographic implementation.
"""

from .ta import setup, keygen, attr_revoke, revoke_user
from .scheme import encrypt
from .rsu import rsu_transform
from .obu import final_decrypt
from .types import (
    Certificate,
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
