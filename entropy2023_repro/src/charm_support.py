from __future__ import annotations

try:
    from charm.core.engine.util import objectToBytes
    from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
    from charm.toolbox.pairinggroup import GT, PairingGroup
except ImportError as exc:  # pragma: no cover - depends on local Charm install
    CHARM_IMPORT_ERROR = exc
    objectToBytes = None
    CPabe_BSW07 = None
    GT = None
    PairingGroup = None
else:
    CHARM_IMPORT_ERROR = None


def ensure_charm_available() -> None:
    if CHARM_IMPORT_ERROR is not None:
        raise RuntimeError(
            'Charm-Crypto 不可用。请先在当前虚拟环境中安装 charm-crypto-framework，'
            '或确认源码版 Charm 已成功安装。'
        ) from CHARM_IMPORT_ERROR


__all__ = [
    'CPabe_BSW07',
    'GT',
    'PairingGroup',
    'objectToBytes',
    'ensure_charm_available',
]
