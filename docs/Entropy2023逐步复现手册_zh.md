# Entropy 2023 逐步复现手册（中文）

## 1. 适用前提

这份手册默认你已经在 Ubuntu 22.04 上完成了基础环境配置，并且工作目录位于：

```bash
/home/zhang1022/research/iov/src/
```

默认你已经至少具备下面这些条件：

- `python3` 可用；
- 已创建并激活 Python 虚拟环境；
- `Charm-Crypto` 已安装成功；
- `git`、`pytest`、`numpy`、`matplotlib`、`pandas` 可用；
- 你当前优先复现的对象是 `Entropy 2023`：
  `A Lightweight CP-ABE Scheme with Direct Attribute Revocation for Vehicular Ad Hoc Network`。

论文原文：

- MDPI 页面：<https://www.mdpi.com/1099-4300/25/7/979>
- PDF：<https://www.mdpi.com/1099-4300/25/7/979/pdf>
- PMC：<https://pmc.ncbi.nlm.nih.gov/articles/PMC10378673/>

这份手册的目标不是一次性重现整篇论文，而是带你按研究上最稳的顺序，完成：

1. 读懂论文骨架；
2. 搭出 clean-room 代码结构；
3. 跑通最小正确性闭环；
4. 实现撤销；
5. 跑出第一组时间图；
6. 为你后续自己的论文做基线准备。

## 2. 先明确复现目标

你这一轮不要把目标定成“完全 1:1 复刻作者全部代码和原始毫秒数”。

更合理的目标是：

1. 正确重现论文的功能逻辑；
2. 重现主要算法接口；
3. 重现主要性能趋势；
4. 把 OBU/RSU 计算拆分和直接撤销机制讲清楚；
5. 生成你自己可控、可扩展的 baseline 代码。

这篇论文最核心的三个研究点是：

1. `CP-ABE` 风格的细粒度访问控制；
2. `直接属性撤销`；
3. `RSU 外包解密 + OBU 轻量终解密`。

所以你的第一阶段只要把下面 6 个接口跑通，就已经很成功：

- `Setup`
- `KeyGen`
- `Encrypt`
- `RSUTransform`
- `FinalDecrypt`
- `AttrRevoke`

## 3. 第一步：准备专门的复现工程目录

进入你的工作目录：

```bash
cd /home/zhang1022/research/iov/src/
```

新建一个专门工程：

```bash
mkdir -p entropy2023_repro/{src,tests,scripts,results,logs}
cd entropy2023_repro
```

建议目录结构如下：

```text
entropy2023_repro/
  src/
    __init__.py
    config.py
    types.py
    utils.py
    cert.py
    ta.py
    rsu.py
    obu.py
    scheme.py
    bench.py
  tests/
    test_correctness.py
    test_revocation.py
    test_integrity.py
  scripts/
    run_bench.py
    plot_figures.py
  results/
  logs/
```

接下来不要急着写复杂实现，先把这些空文件建出来：

```bash
touch src/__init__.py src/config.py src/types.py src/utils.py \
      src/cert.py src/ta.py src/rsu.py src/obu.py src/scheme.py src/bench.py \
      tests/test_correctness.py tests/test_revocation.py tests/test_integrity.py \
      scripts/run_bench.py scripts/plot_figures.py
```

做到这一步，你的工程骨架就建立好了。

## 4. 第二步：先把论文读成“可实现接口”

这一步很重要。你先不要写代码，先把论文内容转成你自己的接口语言。

建议你读论文时只做一件事：建立“算法表”。

你要从论文里提取出下面这些对象。

### 4.1 系统参与方

你需要在笔记里写清：

- `TA`：负责初始化、发证、属性管理；
- `RSU`：承担动态属性相关控制与外包解密；
- `OBU`：车辆端用户，负责最终轻量解密；
- `Sender / Service Provider`：按策略加密消息；
- `Revocation List / Certificate Logic`：负责撤销判断。

### 4.2 关键数据对象

你需要整理出下面这些对象在你代码里分别长什么样：

- `PublicParams`
- `MasterSecretKey`
- `UserSecretKey`
- `TransformKey`
- `FinalKey`
- `Certificate`
- `Ciphertext`
- `TransformedCiphertext`
- `RevocationState`

### 4.3 6 个核心接口

先在纸上或 Markdown 里写出这些函数的输入输出：

```python
def setup(security_param):
    ...

def keygen(pp, msk, uid, static_attrs, dynamic_attrs):
    ...

def encrypt(pp, message, static_policy, dynamic_policy):
    ...

def rsu_transform(pp, cert, transform_key, ciphertext, revocation_state, context):
    ...

def final_decrypt(pp, final_key, transformed_ciphertext):
    ...

def attr_revoke(revocation_state, uid, attr_name, revoke_type):
    ...
```

这一步的目标是：

你还没开始写实现，但你已经知道每个模块该接收什么、输出什么。

## 5. 第三步：先做“最小可运行版本”，别急着追撤销

真正开始编码时，不要第一天就把“直接撤销”塞进来。

正确顺序是：

1. 先让一个合法用户成功解密；
2. 再把 RSU 外包解密加进去；
3. 最后再加撤销。

### 5.1 先做一个最简配置文件

在 `src/config.py` 里先放最少量的配置概念：

- 安全参数；
- 默认属性全集；
- 默认静态属性；
- 默认动态属性；
- 默认测试消息；
- 默认模拟时间戳和区域。

例如你后面至少会需要这些概念：

```python
SECURITY_PARAM = "SS512"
DEFAULT_STATIC_ATTRS = ["role:ambulance", "dept:traffic"]
DEFAULT_DYNAMIC_ATTRS = ["region:r1", "timeslot:t1"]
DEFAULT_MESSAGE = b"vehicular data payload"
```

这里的 `SS512` 是为了尽量贴近论文中“160-bit 椭圆曲线群 + 512-bit 有限域”的描述。严格说这是基于 Charm 参数集的合理映射，不是论文逐字给出的字符串。

### 5.2 定义类型对象

在 `src/types.py` 中，先不要追求完美抽象，先定义清楚数据结构。

建议先用 `dataclass`：

- `Certificate`
- `Ciphertext`
- `TransformedCiphertext`
- `RevocationState`

你至少要让这些对象能清楚表达：

- 用户是谁；
- 有哪些静态属性；
- 当前动态上下文是什么；
- 哪些属性过期；
- 当前是否被撤销。

## 6. 第四步：实现不带撤销的正确性闭环

这一阶段只做一件事：

让 `Encrypt -> RSUTransform -> FinalDecrypt` 走通。

### 6.1 在 `src/ta.py` 中实现 `setup` 和 `keygen`

你先让 `setup` 完成：

1. 初始化配对群或论文所需群参数；
2. 生成公共参数；
3. 生成主密钥；
4. 返回 `(pp, msk)`。

然后让 `keygen` 完成：

1. 绑定用户 `uid`；
2. 为静态属性生成私钥材料；
3. 生成 OBU 使用的最终解密材料；
4. 生成 RSU 使用的变换密钥；
5. 同时生成证书对象 `Certificate`。

这个阶段不用追求“论文所有字段都齐”，但一定要让你后面能传下去。

### 6.2 在 `src/scheme.py` 中实现 `encrypt`

`encrypt` 的第一版建议这样做：

1. 输入 `message`、`static_policy`、`dynamic_policy`；
2. 先生成一个随机会话密钥 `K`；
3. 用 `K` 对消息做对称加密；
4. 再把 `K` 用“静态策略 + 动态策略”包装成 ABE 风格密文头；
5. 输出 `Ciphertext`。

注意：

第一版你可以先把静态策略和动态策略都写成很简单的 `AND` 结构，例如：

- 静态策略：`role:ambulance AND dept:traffic`
- 动态策略：`region:r1 AND timeslot:t1`

先别上来就实现复杂的 LSSS 语法树。

### 6.3 在 `src/rsu.py` 中实现 `rsu_transform`

第一版 `RSUTransform` 的目标不是“完全论文级优化”，而是：

1. 验证证书是否存在；
2. 检查动态策略是否满足；
3. 检查当前上下文是否匹配，比如区域和时隙；
4. 如果满足，则产出 `TransformedCiphertext`；
5. 如果不满足，则抛出失败。

你要特别注意：

这里应该体现“RSU 只做重计算，但不直接暴露明文”的结构。

### 6.4 在 `src/obu.py` 中实现 `final_decrypt`

OBU 的第一版只需要做：

1. 接收 `TransformedCiphertext`；
2. 用自己的最终密钥恢复会话密钥或其剩余部分；
3. 解开对称密文；
4. 检查消息标签或完整性标记。

只要这个步骤跑通，你就完成了论文最重要的一半：

OBU 确实没有承担完整解密，而是只做最终轻量恢复。

## 7. 第五步：先写 3 个最小测试

在这一阶段，你不要先跑 benchmark。

先用 `pytest` 验证逻辑正确性。

### 7.1 测试 1：合法用户成功解密

在 `tests/test_correctness.py` 中写第一个测试：

1. 初始化系统；
2. 生成一个合法用户；
3. 用满足其静态和动态属性的策略加密；
4. 经过 `RSUTransform`；
5. `FinalDecrypt` 成功恢复明文；
6. 断言解密结果等于原消息。

运行：

```bash
pytest -q tests/test_correctness.py
```

预期结果：

- 至少有 1 个测试通过。

### 7.2 测试 2：动态策略不满足时失败

第二个测试检查：

- 用户虽然有合法静态属性；
- 但当前区域或时隙不匹配；
- `RSUTransform` 应该失败。

例如：

- 用户在 `region:r1`
- 密文要求 `region:r2`

预期结果：

- 测试捕获异常或得到明确失败返回。

### 7.3 测试 3：静态策略不满足时失败

第三个测试检查：

- 用户缺少某个必要静态属性；
- 即使 RSU 侧通过了上下文检查；
- 最终仍无法正确解密。

做到这 3 个测试都通过后，你再进入撤销阶段。

## 8. 第六步：加入撤销机制

这一阶段才开始实现论文的“直接撤销”思想。

你不要把它误写成复杂的全局重密钥系统。

根据论文结构，更合适的 clean-room 复现顺序是：

1. 先实现用户撤销；
2. 再实现动态属性撤销；
3. 最后实现静态属性撤销。

### 8.1 用户撤销

这是最简单的一步。

在 `RevocationState` 中维护一个集合：

- `revoked_users = set()`

然后在 `rsu_transform` 中最先检查：

- 证书所属用户是否在撤销列表；
- 若在，则直接拒绝转换。

你要写一个测试：

1. 正常用户最初能解密；
2. 把该用户加入 `revoked_users`；
3. 同样的请求再次发送；
4. RSU 直接拒绝。

### 8.2 动态属性撤销

论文中这一部分和 RSU 场景关联非常紧。

最容易复现的方法是：

- 把动态属性理解为“当前区域 / 当前时隙 / 当前 RSU 侧状态”；
- 如果用户离开覆盖区域，或者当前时隙不再匹配，则不再允许转换。

也就是说，动态属性撤销可以先通过“上下文失效”来模拟。

这一步你要写测试：

1. 用户最初在 `region:r1`；
2. 密文策略要求 `region:r1`；
3. 后来把上下文改成 `region:r2`；
4. 再次请求时 `RSUTransform` 失败。

### 8.3 静态属性撤销

这一步建议通过证书完成。

也就是在 `Certificate` 里维护：

- `static_attrs`
- `attr_expiry`

然后支持两种撤销方式：

1. 从 `static_attrs` 中删除该属性；
2. 或把它的有效期改成已过期。

接着在 `rsu_transform` 或 `final_decrypt` 前做检查：

- 只有当前仍有效的静态属性才能参与解密。

这里你至少要写两个测试：

1. 删除属性后解密失败；
2. 属性过期后解密失败。

## 9. 第七步：加入完整性校验

如果你只做“能解出来”，还不够。

你还需要复现论文里“外包后 OBU 仍可验证正确性”的思路。

最简单可行的做法是：

1. 加密时为消息生成 `tag`；
2. `TransformedCiphertext` 中带上必要校验材料；
3. OBU 在 `FinalDecrypt` 后校验 `tag`；
4. 若密文被改动，则校验失败。

你要加一个测试：

- 故意篡改 `TransformedCiphertext` 中一个字段；
- `FinalDecrypt` 不应返回合法消息。

## 10. 第八步：开始做 benchmark

只有在前面的正确性测试都通过后，才开始计时。

### 10.1 先定义你要测哪些函数

第一轮 benchmark 只测这 4 类：

1. `KeyGen`
2. `Encrypt`
3. `RSUTransform`
4. `FinalDecrypt`

如果你一开始就把 `AttrRevoke` 也混进去，数据会比较乱。

### 10.2 定义实验变量

你第一轮只改变一个变量：属性数。

建议参数：

- `5`
- `10`
- `20`
- `30`
- `50`

每个点跑 `30` 次，记录平均值。

### 10.3 写 `scripts/run_bench.py`

这个脚本最少要完成：

1. 循环属性数；
2. 为每个属性规模随机生成测试策略；
3. 重复运行指定次数；
4. 记录耗时到 CSV；
5. 把结果保存到 `results/benchmark_attr_scale.csv`。

建议 CSV 字段：

- `attr_count`
- `round_id`
- `keygen_ms`
- `encrypt_ms`
- `transform_ms`
- `final_decrypt_ms`

### 10.4 运行基准测试

示例命令：

```bash
python scripts/run_bench.py
```

运行完成后，你应该确认两件事：

1. `results/benchmark_attr_scale.csv` 已生成；
2. 数值整体随属性规模增长而上升，并且没有明显异常值失控。

## 11. 第九步：画第一张图

在 `scripts/plot_figures.py` 中先做最简单的一张图：

- 横轴：属性数；
- 纵轴：时间（ms）；
- 曲线：`Encrypt`、`RSUTransform`、`FinalDecrypt`。

运行：

```bash
python scripts/plot_figures.py
```

你希望看到的不是“绝对数值和论文一模一样”，而是：

- `FinalDecrypt` 明显轻于完整重计算；
- `RSUTransform` 承担了更多计算；
- 属性数增加时，总体时间上升合理。

## 12. 第十步：写复现日志

这一步非常值得做，因为你后面写论文、写 rebuttal、写实验节都会用到。

建议你在工程根目录写一个 `REPRO_LOG.md`，每天按下面格式记录：

```text
日期：
完成内容：
当前通过的测试：
当前失败的测试：
性能结果简述：
和论文不一致的地方：
下一步：
```

例如：

```text
日期：2026-03-16
完成内容：实现 Setup/KeyGen/Encrypt/RSUTransform/FinalDecrypt 的最小闭环
当前通过的测试：合法解密、动态策略失败、静态策略失败
当前失败的测试：静态属性过期逻辑
性能结果简述：属性数从 5 增长到 30 时，Encrypt 和 Transform 上升明显
和论文不一致的地方：当前未实现论文的全部证书字段与完整撤销逻辑
下一步：加入 static attr expiry 和 integrity check
```

## 13. 第十一步：什么时候算“第一阶段复现成功”

满足下面 5 条，就可以认为你已经完成了第一阶段：

1. 论文 6 个核心接口已有 clean-room 实现；
2. 正确性测试全部通过；
3. 用户撤销、动态撤销、静态撤销至少各有 1 个测试；
4. 生成了至少 1 组属性规模 benchmark 数据；
5. 画出了至少 1 张可解释的图。

这时你就不再是“只读论文”，而是已经真正拥有了一个可继续扩展的 baseline。

## 14. 第十二步：接下来怎么衔接你的论文方案

当 `Entropy 2023` 第一阶段复现成功后，后面就进入你自己的论文构建阶段。

推荐顺序是：

1. 保持这个工程不动，作为 `属性撤销 + OBU/RSU 轻量化` baseline；
2. 新开 `SE-CPPA` 子工程，复现 `Sign/Verify/Open/Judge`；
3. 再设计你自己的组合方案：
   - 用匿名认证提供 `sigma`；
   - 用 CP-ABE 提供细粒度访问控制；
   - 用用户撤销 + 属性撤销做双撤销；
   - 用 transcript 绑定把认证和访问控制闭环起来。

## 15. 你现在立刻该做什么

如果你已经确认环境都装好了，那么就按下面这个最小顺序执行：

1. 进入 `/home/zhang1022/research/iov/src/`；
2. 创建 `entropy2023_repro` 工程骨架；
3. 定义 6 个核心接口的输入输出；
4. 先实现不带撤销的 `Encrypt -> RSUTransform -> FinalDecrypt`；
5. 写 3 个最小正确性测试；
6. 再逐步加用户撤销、动态属性撤销、静态属性撤销；
7. 最后做 benchmark 和画图。

如果你愿意，下一步我可以直接继续给你两样最实用的东西之一：

1. `Entropy 2023` 这 6 个接口的中文伪代码版；
2. 一套可以直接拷到 Ubuntu 里开始写的 `Python/Charm` 代码骨架。
