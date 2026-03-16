from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.bench import benchmark_attr_scale


def main() -> None:
    rows = benchmark_attr_scale()
    results_dir = ROOT / 'results'
    results_dir.mkdir(parents=True, exist_ok=True)
    output_path = results_dir / 'benchmark_attr_scale.csv'
    with output_path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=['attr_count', 'round_id', 'keygen_ms', 'encrypt_ms', 'transform_ms', 'final_decrypt_ms'],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f'saved benchmark results to {output_path}')


if __name__ == '__main__':
    main()
