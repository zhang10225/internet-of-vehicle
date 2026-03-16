from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results' / 'benchmark_attr_scale.csv'
FIGURES = ROOT / 'results'


def main() -> None:
    if not RESULTS.exists():
        raise FileNotFoundError(f'benchmark results not found: {RESULTS}')
    dataframe = pd.read_csv(RESULTS)
    grouped = dataframe.groupby('attr_count', as_index=False)[
        ['encrypt_ms', 'transform_ms', 'final_decrypt_ms']
    ].mean()

    plt.figure(figsize=(8, 5))
    plt.plot(grouped['attr_count'], grouped['encrypt_ms'], marker='o', label='Encrypt')
    plt.plot(grouped['attr_count'], grouped['transform_ms'], marker='s', label='RSU Transform')
    plt.plot(grouped['attr_count'], grouped['final_decrypt_ms'], marker='^', label='OBU FinalDecrypt')
    plt.xlabel('Attribute Count')
    plt.ylabel('Time (ms)')
    plt.title('Entropy 2023 Clean-Room Baseline')
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend()
    FIGURES.mkdir(parents=True, exist_ok=True)
    output_path = FIGURES / 'benchmark_attr_scale.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    print(f'saved figure to {output_path}')


if __name__ == '__main__':
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    main()
