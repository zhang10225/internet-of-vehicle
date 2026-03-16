# Entropy 2023 clean-room reproduction

这不是论文作者原始代码，而是一套面向研究复现的 clean-room 最小工程。

## 当前包含的内容

- `Setup / KeyGen / Encrypt / RSUTransform / FinalDecrypt / AttrRevoke`
- 用户撤销、静态属性撤销、动态属性撤销的最小逻辑
- 基础正确性测试、撤销测试、完整性测试
- 第一版属性规模 benchmark 与画图脚本

## 当前不包含的内容

- 论文级双线性配对或 ECC 数学实现
- 作者原始参数、原始优化技巧和完整系统细节
- OMNeT++ / SUMO / Veins 网络仿真

## 在 Ubuntu 中建议的使用顺序

```bash
cd /home/zhang1022/research/iov/src/entropy2023_repro
pytest -q
python scripts/run_bench.py
python scripts/plot_figures.py
```

如果你后面要把它替换成 Charm 版本，优先替换：

1. `src/scheme.py` 中的加密与会话封装逻辑
2. `src/ta.py` 中的密钥生成逻辑
3. `src/rsu.py` / `src/obu.py` 中的变换与最终解密逻辑
