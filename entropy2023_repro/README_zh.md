# Entropy 2023 clean-room reproduction（Charm 版）

这不是论文作者原始代码，而是一套面向研究复现的 clean-room 基线工程。

当前版本已经从最小 toy 逻辑切换为真正依赖 `Charm-Crypto` 的实现，核心采用：

- `PairingGroup('SS512')`
- `CPabe_BSW07`
- static / dynamic 双层 CP-ABE 封装
- `RSUTransform + FinalDecrypt` 两阶段恢复

## 当前包含的内容

- `Setup / KeyGen / Encrypt / RSUTransform / FinalDecrypt / AttrRevoke`
- 基于 Charm 的 static / dynamic 双层 CP-ABE 封装
- 用户撤销、静态属性撤销、动态属性撤销的最小逻辑
- 基础正确性测试、撤销测试、完整性测试
- 第一版属性规模 benchmark 与画图脚本

## 当前不包含的内容

- 论文作者原始 ECC 数学实现
- 完整 OMNeT++ / SUMO / Veins 网络仿真
- 论文所有证书字段、系统优化和部署细节

## Ubuntu 中建议的使用顺序

```bash
cd /home/zhang1022/research/iov/src/entropy2023_repro
pip install -r requirements.txt
pytest -q
python scripts/run_bench.py
python scripts/plot_figures.py
```

## 说明

这版实现的目标是：

1. 让你在 Ubuntu 22.04 上先跑通一个真正使用 Charm 的 baseline；
2. 给后续接入更严格的 CP-ABE / revocation 逻辑留接口；
3. 方便你继续扩展到自己的双撤销 IoV 协议。
