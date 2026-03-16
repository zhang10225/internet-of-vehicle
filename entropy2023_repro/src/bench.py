from __future__ import annotations

from time import perf_counter

from .config import DEFAULT_ATTR_SCALE, DEFAULT_BENCH_ROUNDS, DEFAULT_DYNAMIC_ATTRS, DEFAULT_MESSAGE_SIZE
from .ta import setup, keygen
from .scheme import encrypt
from .rsu import rsu_transform
from .obu import final_decrypt
from .types import RevocationState


def _generate_attrs(count: int) -> list[str]:
    return [f'attr:{index}' for index in range(count)]


def benchmark_attr_scale(
    attr_counts: list[int] | None = None,
    rounds: int = DEFAULT_BENCH_ROUNDS,
) -> list[dict[str, float | int]]:
    rows: list[dict[str, float | int]] = []
    counts = attr_counts or DEFAULT_ATTR_SCALE
    for attr_count in counts:
        static_attrs = _generate_attrs(attr_count)
        dynamic_attrs = list(DEFAULT_DYNAMIC_ATTRS)
        context = set(DEFAULT_DYNAMIC_ATTRS)
        for round_id in range(rounds):
            pp, msk = setup()

            started = perf_counter()
            bundle = keygen(
                pp,
                msk,
                uid=f'user-{round_id}',
                static_attrs=static_attrs,
                dynamic_attrs=dynamic_attrs,
            )
            keygen_ms = (perf_counter() - started) * 1000

            started = perf_counter()
            ciphertext = encrypt(
                pp,
                message=b'x' * DEFAULT_MESSAGE_SIZE,
                static_policy=static_attrs,
                dynamic_policy=dynamic_attrs,
            )
            encrypt_ms = (perf_counter() - started) * 1000

            started = perf_counter()
            transformed = rsu_transform(
                pp,
                bundle.certificate,
                bundle.transform_key,
                ciphertext,
                RevocationState(),
                context=context,
            )
            transform_ms = (perf_counter() - started) * 1000

            started = perf_counter()
            final_decrypt(pp, bundle.final_key, transformed)
            final_decrypt_ms = (perf_counter() - started) * 1000

            rows.append(
                {
                    'attr_count': attr_count,
                    'round_id': round_id,
                    'keygen_ms': keygen_ms,
                    'encrypt_ms': encrypt_ms,
                    'transform_ms': transform_ms,
                    'final_decrypt_ms': final_decrypt_ms,
                }
            )
    return rows
