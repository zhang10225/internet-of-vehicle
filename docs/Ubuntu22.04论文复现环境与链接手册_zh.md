# Ubuntu 22.04 论文复现环境与论文 / 代码链接手册（中文）

## 1. 先说结论

如果你的主环境是 `Ubuntu 22.04`，我建议把复现工作分成三层：

1. `原生 Ubuntu 22.04`：用于复现 `Entropy 2023`、`SE-CPPA` 的 clean-room 原型，以及你自己的协议原型；
2. `Ubuntu 22.04 + OMNeT++/SUMO/Veins`：用于车联网网络级仿真；
3. `容器 / 老版本虚拟机`：只给 `BCPPA` 这种旧依赖论文用，因为它依赖 `ns-2.35 + JDK7 + VanetMobiSim`，不适合直接在现代系统上硬装。

也就是说：

- 你最先应该在 Ubuntu 22.04 上搭的是 `Python + Charm/OpenABE + PBC + Java` 这一套密码学原型环境；
- `OMNeT++ + SUMO + Veins` 放在第二阶段；
- `BCPPA` 放在第三阶段，而且最好放进容器或旧环境里复现。

## 2. Ubuntu 22.04 下推荐的总体环境结构

建议你在 Ubuntu 22.04 上准备 3 个独立环境：

### 环境 A：密码学原型环境

用于：

- `Entropy 2023` 属性撤销 CP-ABE 方案
- `Flexible Revocation for IoV`
- 你自己的双撤销 CP-ABE 原型
- `SE-CPPA` 的 clean-room 认证模块

推荐工具：

- Python 3.10
- venv
- Charm-Crypto
- OpenABE
- PBC
- OpenJDK 11

### 环境 B：网络仿真环境

用于：

- `SE-CPPA` 论文里的 OMNeT++ / Veins / SUMO 风格实验
- 你自己论文里的端到端 IoV 数据分发仿真

推荐工具：

- OMNeT++ 6.x
- SUMO 1.x
- Veins 5.2 / 5.3

### 环境 C：旧依赖兼容环境

用于：

- `BCPPA` 官方仓库

推荐方式：

- Docker / LXD / 独立 Ubuntu 18.04 虚拟机

不推荐直接在主系统上安装 `JDK7 + ns-2.35 + VanetMobiSim`，因为它们太旧，会把 Ubuntu 22.04 主环境弄得很脆弱。

## 3. Ubuntu 22.04 基础依赖安装

先安装通用工具链：

```bash
sudo apt update
sudo apt install -y \
  build-essential git curl wget unzip pkg-config cmake \
  autoconf automake libtool m4 bison flex gawk \
  python3 python3-dev python3-pip python3-venv \
  openjdk-11-jdk ant \
  libgmp-dev libssl-dev libffi-dev zlib1g-dev \
  libboost-all-dev libxml2-dev libexpat1-dev \
  libcairo2-dev qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools \
  libgl1-mesa-dev libxmu-dev
```

建议再顺手准备一个工作目录：

```bash
mkdir -p ~/research/iov/{src,venvs,data,logs}
cd ~/research/iov
```

## 4. Python 原型环境配置方法

建议为密码学实验单独建一个虚拟环境：

```bash
python3 -m venv ~/research/iov/venvs/iov-crypto
source ~/research/iov/venvs/iov-crypto/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

通用 Python 包可先装这些：

```bash
pip install pytest numpy pandas matplotlib scipy jupyter notebook
```

## 5. Charm-Crypto 安装方法

### 为什么推荐它

`Entropy 2023` 论文明确写到，实验代码基于 `charm-crypto framework` 和 `python 3.7`，实验系统为 `Ubuntu Linux 16.04.7`。在 Ubuntu 22.04 上，你不必完全复制旧系统，但建议保留 `Charm` 这一实现路径，用它做功能正确性和算法复现最合适。

来源：

- 论文页：<https://www.mdpi.com/1099-4300/25/7/979>
- 论文全文/PMC：<https://pmc.ncbi.nlm.nih.gov/articles/PMC10378673/>
- Charm 官方文档：<https://jhuisi.github.io/charm/>
- Charm 官方 GitHub：<https://github.com/JHUISI/charm>

### 安装建议

先试官方推荐的 pip 安装：

```bash
source ~/research/iov/venvs/iov-crypto/bin/activate
pip install charm-crypto-framework
```

Charm 官方文档说明，它支持直接通过 `pip install charm-crypto-framework` 安装，但系统里需要先有 `GMP`、`PBC`、`OpenSSL` 等底层库。

如果 pip 安装失败，再走源码：

```bash
cd ~/research/iov/src
git clone https://github.com/JHUISI/charm.git
cd charm
./configure.sh
make
sudo make install
make test
```

如果你要尽量贴近论文环境，我建议：

- 功能复现用 Ubuntu 22.04 + Python 3.10 + Charm；
- 论文中单独说明“原论文实验环境为 Ubuntu 16.04.7 + Python 3.7 + Charm”，而你采用了统一重实现环境。

## 6. PBC 安装方法

### 为什么要装它

即使你主要使用 Charm，很多 pairing-based 原型仍然会依赖 `PBC` 或其兼容接口。

官方来源：

- PBC 官网：<https://crypto.stanford.edu/pbc/>
- PBC 下载页：<https://crypto.stanford.edu/pbc/download.html>
- PBC GitHub 镜像：<https://github.com/blynn/pbc>

### 安装命令

```bash
cd ~/research/iov/src
git clone https://github.com/blynn/pbc.git
cd pbc
./configure
make -j$(nproc)
sudo make install
sudo ldconfig
```

如果 `./configure` 报 GMP 相关错误，先确认：

```bash
sudo apt install -y libgmp-dev
```

## 7. OpenABE 安装方法

### 为什么推荐它

如果你后面希望把 CP-ABE baseline 做得更“工程化”，`OpenABE` 比纯论文风格原型更稳。它也适合作为你自己协议后期的对照实现框架。

官方来源：

- OpenABE GitHub：<https://github.com/zeutro/openabe>

OpenABE 官方 README 写得很清楚：Ubuntu / Debian 下可以直接运行它自带的依赖安装脚本，再执行 `make` 和 `make test`。

### 安装命令

```bash
cd ~/research/iov/src
git clone https://github.com/zeutro/openabe.git
cd openabe
sudo -E ./deps/install_pkgs.sh
. ./env
make -j$(nproc)
make test
sudo -E make install
```

### 什么时候用 OpenABE，什么时候用 Charm

建议：

- `Charm`：用来快速重实现论文算法；
- `OpenABE`：用来做更稳定的 CP-ABE 基线、接口化封装和性能补测。

## 8. Java / JPBC 安装方法

### 是否一定需要 JPBC

不一定。

因为你目前最优先复现的 `Entropy 2023` 本身已经明确使用 `Charm + Python`，所以第一阶段没必要为了 JPBC 先折腾 Java pairing 框架。

但是，如果你后面需要：

- 跑历史 ABE 工程；
- 做 Java 版微基准；
- 或兼容旧仓库；

那就可以装它。

### 官方来源

- jPBC 官方 SourceForge：<https://sourceforge.net/projects/jpbc/>
- 直接下载：<https://sourceforge.net/projects/jpbc/files/jpbc_2_0_0/jpbc-2.0.0.zip/download>
- Arcanum 文档站：<https://adecaro.github.io/arcanum/>

### Java 环境

```bash
sudo apt install -y openjdk-11-jdk
java -version
javac -version
```

### JPBC 建议

- 第一阶段只下载留档，不优先投入；
- 真需要时再为它单独建一个 `~/research/iov/src/jpbc` 环境。

## 9. OMNeT++ / SUMO / Veins 在 Ubuntu 22.04 的配置方法

这套环境主要服务于 `SE-CPPA` 以及你后面自己的 GLOBECOM 网络级实验。

### 9.1 OMNeT++

官方来源：

- OMNeT++ 下载页：<https://omnetpp.org/download/>
- OMNeT++ GitHub：<https://github.com/omnetpp/omnetpp>
- `opp_env`：<https://pypi.org/project/opp-env/>

OMNeT++ 官方当前推荐使用 `opp_env` 安装，也支持下载 Linux 包后执行根目录下的 `install.sh`。

#### 方法 A：官方推荐的 opp_env

```bash
python3 -m pip install --user opp-env
mkdir -p ~/research/omnetpp-workspace
cd ~/research/omnetpp-workspace
opp_env init
opp_env install omnetpp-6.3.0
```

#### 方法 B：手工安装

1. 从官方页面下载 Linux 版本；
2. 解压后进入目录；
3. 运行：

```bash
./install.sh
source setenv
omnetpp
```

如果你只做命令行构建，不需要 GUI，也可以考虑 core 版本或 `install.sh --no-gui`。

### 9.2 SUMO

官方来源：

- SUMO 安装页：<https://sumo.dlr.de/docs/Installing/index.html>
- SUMO 下载页：<https://sumo.dlr.de/docs/Downloads.html>
- SUMO GitHub：<https://github.com/eclipse-sumo/sumo>

SUMO 官方文档说明，在 Debian / Ubuntu 上可以直接用 apt 安装：

```bash
sudo apt-get install sumo sumo-tools sumo-doc
```

如果你想要更高版本，可以先加官方 PPA：

```bash
sudo add-apt-repository ppa:sumo/stable
sudo apt-get update
sudo apt-get install sumo sumo-tools sumo-doc
```

安装后建议检查：

```bash
sumo --version
sumo-gui --version
```

### 9.3 Veins

官方来源：

- Veins 官网：<https://veins.car2x.org/>
- Veins 下载页：<https://veins.car2x.org/download/>
- Veins 官方 GitHub：<https://github.com/sommer/veins>
- OMNeT++ 的 Veins 页面：<https://omnetpp.org/download-items/Veins.html>

Veins 官方页面当前列出的最新版本是 `Veins 5.3.x`，OMNeT++ 页面还明确给出推荐安装方式：

```bash
opp_env install veins-latest
```

如果你采用手工安装：

```bash
cd ~/research/iov/src
git clone https://github.com/sommer/veins.git
```

然后再按其官网教程，将其与已安装好的 `OMNeT++` 和 `SUMO` 对接。

### 9.4 我给你的实际建议

如果你的目标是论文复现，不是长期做仿真平台维护，那么：

- `SE-CPPA` 的网络仿真优先用 `OMNeT++ + SUMO + Veins`；
- 不必追它论文里出现的 `GatcomSUMO` 这一旧工具链；
- 直接采用现代版 `OMNeT++ 6 + SUMO + Veins 5.2/5.3` 更现实。

## 10. BCPPA 的 Ubuntu 22.04 复现建议

### 10.1 先说为什么不建议原生硬装

BCPPA 官方仓库 README 里写得非常清楚，它的依赖包括：

- `ns 2.35`
- `JDK 7`
- `Ant`
- `VanetMobiSim`

官方仓库：

- GitHub：<https://github.com/colyn91/BCPPA>

这套依赖链明显偏老，尤其是 `JDK7` 和 `ns-2.35`，在 Ubuntu 22.04 上直接硬装往往会带来兼容性问题。

### 10.2 推荐复现方式

我建议用下面两种方式之一：

#### 方式 A：Docker / LXD 容器

建议专门建一个旧环境容器，例如 Ubuntu 18.04。

优点：

- 不污染主系统；
- 出问题容易重建；
- 便于记录旧实验环境。

#### 方式 B：独立虚拟机

例如：

- Ubuntu 18.04
- 或者更接近仓库年代的老发行版

### 10.3 不建议的做法

不建议：

- 在 Ubuntu 22.04 主系统里强行降级 Java；
- 直接混装多个古老仿真库；
- 为了复现一篇论文把主系统破坏掉。

### 10.4 BCPPA 对你真正有价值的部分

对你来说，BCPPA 更适合：

- 学习作者怎么组织车联网系统工程原型；
- 参考其 README 中的仿真流程和目录结构；
- 作为“系统对照样本”，而不是第一优先级复现对象。

## 11. 我建议你在 Ubuntu 22.04 上的实际复现顺序

### 第一阶段：先做密码学原型

顺序建议：

1. 安装基础依赖；
2. 安装 Python + venv；
3. 安装 Charm；
4. 安装 PBC；
5. 选做 OpenABE；
6. 先复现 `Entropy 2023`。

### 第二阶段：做认证原型

顺序建议：

1. clean-room 重实现 `SE-CPPA` 的认证接口；
2. 把 `Sign/Verify/Open/Judge` 这一组接口稳定下来；
3. 与你的 ABE 原型进行 transcript 绑定。

### 第三阶段：搭网络仿真

顺序建议：

1. 安装 OMNeT++；
2. 安装 SUMO；
3. 安装 Veins；
4. 把密码学测得的时延注入仿真；
5. 再做端到端图。

### 第四阶段：处理旧代码仓库

只在你有明确需要时，再投入 BCPPA。

## 12. 论文、全文、代码仓库汇总

| 对象 | 论文 / 项目链接 | 全文 / 开放版本 | 代码 / 仓库 | 备注 |
| --- | --- | --- | --- | --- |
| SE-CPPA | <https://doi.org/10.3390/s21248206> | MDPI: <https://www.mdpi.com/1424-8220/21/24/8206>；PubMed/PMC: <https://pubmed.ncbi.nlm.nih.gov/34960311/> | 我当前没有检索到作者官方代码仓库 | 论文声明 `Data sharing not applicable`，页面未给 GitHub 链接 |
| Entropy 2023 直接属性撤销 CP-ABE | <https://doi.org/10.3390/e25070979> | MDPI: <https://www.mdpi.com/1099-4300/25/7/979>；PMC: <https://pmc.ncbi.nlm.nih.gov/articles/PMC10378673/> | 我当前没有检索到作者官方代码仓库 | 论文声明 `Data Availability Statement: Not applicable`，页面未给 GitHub 链接 |
| Flexible Revocation for IoV | <https://doi.org/10.1016/j.procs.2023.09.020> | ScienceDirect: <https://www.sciencedirect.com/science/article/pii/S1877050923010670> | 我当前没有检索到作者官方代码仓库 | 适合机制级重实现 |
| Dynamic FGAC | <https://doi.org/10.1016/j.comnet.2021.107872> | ScienceDirect: <https://www.sciencedirect.com/science/article/abs/pii/S1389128621000402> | 我当前没有检索到作者官方代码仓库 | 更适合读思路，不建议先追原码 |
| BCPPA | <https://doi.org/10.1109/TITS.2020.3002096> | DOI 入口：<https://doi.org/10.1109/TITS.2020.3002096> | 官方 GitHub: <https://github.com/colyn91/BCPPA> | 仓库 README 明确依赖 `ns-2.35 + JDK7 + Ant + VanetMobiSim` |
| Charm-Crypto | 文档：<https://jhuisi.github.io/charm/> | GitHub: <https://github.com/JHUISI/charm> | GitHub 同左 | 适合论文算法 clean-room 重实现 |
| OpenABE | GitHub: <https://github.com/zeutro/openabe> | README 和文档在仓库内 | GitHub 同左 | 适合做 CP-ABE 工程化 baseline |
| PBC | 官网：<https://crypto.stanford.edu/pbc/> | 下载页：<https://crypto.stanford.edu/pbc/download.html> | GitHub: <https://github.com/blynn/pbc> | pairing 底层库 |
| jPBC | SourceForge: <https://sourceforge.net/projects/jpbc/> | 下载：<https://sourceforge.net/projects/jpbc/files/jpbc_2_0_0/jpbc-2.0.0.zip/download> | 官方以 SourceForge 为主 | 旧 Java pairing 工具，按需使用 |
| OMNeT++ | <https://omnetpp.org/download/> | 官方下载页同左 | GitHub: <https://github.com/omnetpp/omnetpp> | 官方推荐 `opp_env` |
| SUMO | 安装页：<https://sumo.dlr.de/docs/Installing/index.html> | 下载页：<https://sumo.dlr.de/docs/Downloads.html> | GitHub: <https://github.com/eclipse-sumo/sumo> | Ubuntu 22.04 可直接 apt 安装 |
| Veins | 官网：<https://veins.car2x.org/> | 下载页：<https://veins.car2x.org/download/> | GitHub: <https://github.com/sommer/veins> | 官方推荐与 OMNeT++/SUMO 联合使用 |

## 13. 对你最重要的建议

如果你现在就要开始做“可发表”的复现工作，我建议：

- 先不要碰 BCPPA 的旧环境；
- 先在 Ubuntu 22.04 上把 `Entropy 2023` 跑通；
- 然后 clean-room 重实现 `SE-CPPA` 的认证子模块；
- 最后再把二者合成你自己的协议原型。

这个路径最稳，也最符合你当前面向 GLOBECOM 的论文目标。

## 14. 说明

- 本文中的安装步骤是按 Ubuntu 22.04 的复现实践需求整理的；
- 我当前无法在你的 Ubuntu 主机上直接执行这些命令，因此这里给的是“可操作配置方案”，不是已在本机验证通过的日志；
- 对于没有给出官方代码仓库的论文，我只陈述“当前未检索到作者官方公开仓库”，不代表代码绝对不存在。
