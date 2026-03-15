# 面向隐私保护车联网数据分发的 GLOBECOM 风格相关工作矩阵

## 文件用途

本文档是面向 IEEE GLOBECOM 投稿的中文理解版写作材料，目标轨道为
Communications and Information Systems Security (CISS)。它不是一份面面俱到的
综述，而是围绕以下三个核心贡献来筛选和组织文献：

1. 面向 IoV 消息分发的匿名且可追责认证，
2. 面向细粒度数据访问控制的双撤销机制，
3. 面向 OBU 的 RSU/边缘辅助轻量化处理。

这里也同步修正前一版规划中的两处引文问题：

- `TRE-DSP` 的已核对 DOI 为 `10.1016/j.vehcom.2024.100746`。
- `10.1016/j.procs.2023.09.020` 对应的是一篇通用 ABE 灵活撤销论文，而不是
  IoV 专属方案。它仍然适合作为撤销机制参考文献，但不应被表述为 IoV 直接 baseline。

## 与 GLOBECOM 的契合点

- GLOBECOM 的 CISS 方向明确覆盖 authentication、access control、privacy 和
  lightweight cryptography，因此本文应被表述为“通信安全系统论文”，而不是纯密码学论文 [G1]。
- 文稿需要紧凑、图表驱动。结合近年的 GLOBECOM 征稿页和作者说明，related work 更适合用于
  缺口定位，而不是铺陈过长的分类综述 [G2], [G3]。

## 精选相关工作矩阵

| 编号 | 论文 | 主要关注点 | 匿名认证 | 追踪 / 追责 | 用户撤销 | 属性撤销 | 策略隐藏 | 边缘 / 代理卸载 | 实验风格 | 我们如何使用 | 相对本文目标的关键不足 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [1] | BCPPA | 区块链辅助的 VANET 条件隐私认证 | 是 | 具备条件隐私和开启能力 | 否 | 否 | 否 | 有限 | 密码学开销 + 网络层讨论 | 认证线 baseline | 没有细粒度数据访问控制，也没有双撤销 |
| [2] | SE-CPPA | 轻量级 VANET 条件隐私认证 | 是 | 是，通过权威机构恢复身份 | 否 | 否 | 否 | 支持批验证 | 较完整的签名 / 验证开销测试 | 轻量认证主 baseline | 只解决认证，不保护业务数据访问 |
| [3] | Dynamic fine-grained access control scheme for VANETs | 动态访问控制与授权 | 否 | 弱 / 间接 | 是 | 不明确 | 否 | 有服务侧协助 | 访问控制时延与通信开销 | 用户撤销访问控制 baseline | 缺少匿名认证和可验证追责 |
| [4] | A Lightweight CP-ABE Scheme with Direct Attribute Revocation for Vehicular Ad Hoc Network | 面向 VANET 的 CP-ABE 与直接属性撤销 | 否 | 否 | 间接 / 有限 | 是 | 否 | 是，支持 RSU 两阶段解密 | OBU / RSU 拆分下的配对代价测试 | 属性撤销 baseline | 缺少匿名可追责认证，也缺少明确用户撤销 |
| [5] | Attribute-based Encryption with Flexible Revocation | 通用 ABE 灵活撤销机制 | 否 | 否 | 是 | 可通过更新机制支持 | 否 | 可扩展支持 | 密码学微基准实验 | 基础撤销机制参考 | 非 IoV 专属，不能解决车联网认证与追责 |
| [6] | TRE-DSP | 面向 IoV 的可追踪、可撤销、部分隐藏策略 CP-ABE 数据共享 | 否 | 数据共享层具备追踪能力 | 是 | 有限，非完整双撤销 | 部分支持 | 是 | 密码学开销 + 数据共享流程 | 最接近本文的数据共享 baseline | 没有把匿名网络认证与 ABE 保护分发真正打通 |

## 可直接写进论文的 related work 综合表述

### A. 条件隐私认证方向

条件隐私认证仍然是 VANET 和 IoV 信任建立中的主流设计模式。代表性方案如
BCPPA [1] 和 SE-CPPA [2]，能够在隐藏车辆长期身份的同时，对外提供可验证的消息合法性。
这类方案与车联网的网络约束较为匹配，因为它们通常重点优化签名、验证以及批验证过程。
然而，这些工作主要解决的是链路层或消息层认证问题，并不提供针对敏感业务数据的细粒度授权，
也不同时支持用户级与属性级的密文撤销。

### B. 细粒度访问控制与撤销方向

第二类工作将 ABE 引入车联网或边缘辅助数据共享。以 [3] 为代表的动态访问控制方案说明，
基于属性的授权机制非常适合处理车辆数据在动态服务环境中的访问控制需求。之后的研究进一步将
撤销机制和轻量化处理纳入设计。例如，[4] 把直接属性撤销与 RSU 辅助解密结合起来，以降低 OBU 负担；
[5] 则提供了一个适合作为用户撤销基础构件的通用 ABE 灵活撤销机制。更近期的 TRE-DSP [6]
已经在 IoV 数据共享中同时考虑了追踪、撤销和部分隐藏策略。但这一方向仍普遍把访问控制与车联网认证
作为相互分离的两层处理。

### C. 研究缺口定位

对于 GLOBECOM 风格论文来说，真正的缺口并不是“没有匿名认证”或“没有可撤销 ABE”本身，
而是缺少一个紧耦合的数据分发框架，能够同时做到：

1. 在匿名认证 IoV 发送者的同时提供可验证追责能力；
2. 面向业务数据而不是公开安全广播实现细粒度访问控制；
3. 在同一流程中同时支持用户撤销和属性撤销；
4. 通过 RSU / 边缘节点卸载重计算来降低 OBU 时延。

这应当成为论文中的核心定位。创新重点不是提出全新的密码原语，而是构造一个面向通信系统部署的组合框架，
弥合“隐私认证”和“可部署的数据平面访问控制”之间的实际断层。

## 实验中的 baseline 映射

| 评估维度 | 建议对比方案 | 原因 |
| --- | --- | --- |
| OBU 签名 / 验证时延 | [1], [2] | 认证方向最有代表性的 baseline |
| 批验证收益 | [2] | 实用性较强的条件隐私认证方案 |
| 访问控制时延 | [3], [4] | 与车联网数据授权最直接相关 |
| 属性撤销开销 | [4] | 最贴近车联网属性撤销的参考方案 |
| 用户撤销更新大小 / 时延 | [3], [5] | 一个车联网访问控制方案 + 一个通用撤销机制方案 |
| 追责时延 | [1], [2], [6] | 同时覆盖认证层和数据共享层的追责能力 |
| 边缘卸载收益 | [4], [6] | 最接近 RSU / 代理辅助处理的设计 |

## 最终写作建议

- 将 [1] 和 [2] 合并成一个短段，放在“面向认证的车联网隐私保护安全”小节中。
- 将 [3]、[4]、[5] 合并成一个短段，放在“基于 ABE 的访问控制与撤销”小节中。
- 单独用 [6] 来承接“最接近本文”的对比，并指出其仍未完成匿名认证与双撤销访问控制的一体化闭环。
- 用一句话结束该节，例如：
  “不同于现有工作仅分别优化匿名认证或可撤销访问控制，本文将可追责匿名认证 transcript 与边缘辅助双撤销
  CP-ABE 密文绑定，以支持低时延 IoV 业务数据分发。”

## 参考文献草稿

[1] M. A. Ferrag, O. Friha, L. Shu, and X. Yang, "BCPPA: A Blockchain-Based
Conditional Privacy-Preserving Authentication Protocol for Vehicular Ad Hoc
Networks," *IEEE Transactions on Intelligent Transportation Systems*, 2020.
DOI: https://doi.org/10.1109/TITS.2020.3002096

[2] "SE-CPPA: A Secure and Efficient Conditional Privacy-Preserving
Authentication Scheme in Vehicular Ad-Hoc Networks," *Sensors*, 2021.
URL: https://www.mdpi.com/1424-8220/21/24/8206

[3] "Dynamic fine-grained access control scheme for vehicular ad hoc networks,"
*Computer Networks*, 2021. DOI: https://doi.org/10.1016/j.comnet.2021.107872

[4] "A Lightweight CP-ABE Scheme with Direct Attribute Revocation for Vehicular
Ad Hoc Network," *Entropy*, 2023. DOI: https://doi.org/10.3390/e25070979

[5] "Attribute-based encryption with Flexible Revocation," *Procedia Computer
Science*, 2023. DOI: https://doi.org/10.1016/j.procs.2023.09.020

[6] "TRE-DSP: A traceable and revocable encryption and data sharing protocol
with partially hidden access policy for Internet of Vehicles,"
*Vehicular Communications*, 2024. DOI: https://doi.org/10.1016/j.vehcom.2024.100746

[G1] IEEE GLOBECOM 2025 CISS Symposium Page:
https://globecom2025.ieee-globecom.org/program/symposia/communications-and-information-systems-security-symposium

[G2] IEEE GLOBECOM 2025 Call for Symposium Papers:
https://globecom2025.ieee-globecom.org/call-symposium-papers

[G3] IEEE GLOBECOM 2026 CFP (IEEE China page):
https://cn.ieee.org/2026/01/27/call-for-paper-ieee-globecom-2026%E8%AE%BA%E6%96%87%E5%BE%81%E9%9B%86%E4%B8%AD/
