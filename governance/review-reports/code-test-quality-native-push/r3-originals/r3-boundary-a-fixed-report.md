severity: minor

本席找到 3 个静态测试质量问题，均不阻塞；因唯读沙盒禁止建立指定实验目录，产品 before/after 行为全部标为未判定，不把收集失败算产品红。

### Finding 1

severity: minor  
blocking: 否

新增的 orphan-failure 案例只验证任意 `rc=2`，没有确认失败确实由 orphan failure 触发；其他结构化拒绝路径也可能让测试假绿。

原文 引句:「self.assertEqual(rc, 2, report)」

- input：testsuite 内有正常 testcase，另有脱离 testcase 的 failure 节点。
- expected：明确断言 orphan failure 对应的 reason／错误分类。
- 判准出处：/tmp/lumos-r2-manual-lens.txt:38 的「现场成立」与防假绿要求。
- 佐证 file: `scripts/test_test_quality_cli.py:571`
- 佐证 file: `scripts/test_test_quality_cli.py:575`
- case_source：`280f76b71f8852bd172f2c7ff98301f2e9df0a7a7d7b86acc2b5c71a7f73cef8`
- before：方法不存在；没有旧版测试可执行，行为未判定。
- after：未执行；没有实际载入产品、cwd、rc 或行为结果。
- comparison/attribution：可归因于修后新增测试的断言粒度；不代表产品 orphan 检查失效。

### Finding 2

severity: minor  
blocking: 否

stale-bytecode 案例虽验证 stale cache 已存在、来源档已还原，但结果仍只要求任意结构化 invalid；其他拒绝原因也可能通过。

原文 引句:「self.assertEqual(run.returncode, 2, run.stdout)」

- input：同尺寸、同 mtime 的旧 `test_quality.pyc`，恢复新版源码后输入汇总计数与 testcase 不一致的 XML。
- expected：确认载入新版源码，并断言拒绝原因来自 suite-count validation。
- 判准出处：/tmp/lumos-r2-manual-lens.txt:38。
- 佐证 file: `scripts/test_test_quality_cli.py:637`
- 佐证 file: `scripts/test_test_quality_cli.py:651`
- 佐证 file: `scripts/test_test_quality_cli.py:686`
- case_source：`92e8f55bdfea5954ad862f4feb967f3e004b8b69f164621b92ff722a69d192be`
- before：方法不存在；没有旧版测试，行为未判定。
- after：未执行；产品实际载入来源及真实拒绝原因未判定。
- comparison/attribution：新增案例改善了 stale-cache 前置条件，但还不足以排除“因别的 invalid 原因通过”。

### Finding 3

severity: minor  
blocking: 否

rename 案例的本机 Git 调用没有 timeout，也没有关闭用户层 commit signing；受污染环境可能失败或等待签章输入。

原文 引句:「return subprocess.check_output(」

- input：用户 Git 配置启用 `commit.gpgSign`，或本机 Git 子程序停滞。
- expected：fixture 明确关闭 signing，并为每次 Git 调用设置有限 timeout。
- 判准出处：/tmp/lumos-r2-manual-lens.txt:5 宣称可信本机命令均有逾时。
- 佐证 file: `scripts/test_test_quality_cli.py:609`
- 佐证 file: `scripts/test_test_quality_cli.py:621`
- case_source：`6068294f2d9a9764b96dc72fc993571041541b3671e9fa709317a4ddbabb46d3`
- before：方法不存在。
- after：未执行；没有真实 rc 或行为结果。
- comparison/attribution：属于新增测试的环境隔离问题，不是 `_review_role_changed_files` 的产品结论。

### 静态正向覆盖

以下只确认测试设计，不升格为修复有效或无回归结论：

- PHP／Node variants：逐一输入 `Test.php`、`runner.cjs/mts/cts`，独立期望均为 impact seed；case_source `9a3f79c…`。佐证 file: `scripts/test_test_quality_cli.py:561`
- extensionless cache：先确认真实生成 owned bytecode，再同时检查 owned 被删、用户 bytecode 保留；case_source `c0c9ebec…`。佐证 file: `scripts/test_test_quality_cli.py:571`
- rename provenance：先以真实 `git diff -M` 确认 `R100`，再期望回传原始 `service.py` 与 before commit；case_source `6068294f…`。佐证 file: `scripts/test_test_quality_cli.py:602`

### 固定图谱镜头

- py-eventloop：静态一致；本席方法无 async/event-loop。
- py-parallel：静态一致；没有新增并行任务。
- py-external：不完全成立，见 Finding 3。
- py-memory：指向 `scripts/test_quality.py`，超出本席固定方法，未验。
- py-hotpath：静态一致；均为离线测试。
- 未触发的 1 题：镜头未给题目，未验。
- vendored 测试套件假红 Issue：未用于本席结论。
- lumos-cli-lifecycle：本席未改其约束路径，未验。
- lumos-deinit：cache-removal 测试静态相关；行为未执行。
- lumos-cli-read：超出本席方法，未验。
- bound-tests-gate：超出本席方法，未验。
- guard-kill 两条 invariant：超出本席方法，未验。
- 授权与归属两条 invariant：超出本席方法，未验。
- 测试假绿形态：直接适用，形成 Findings 1、2。
- pitfalls-code-loop、design-loop、reversibility-governance-ledger、loop-convergence-recording、doctor-irreversible-hint、lumos-refcheck、check-t-sentinel、check-r-guard、节点范围与索引守卫、cochange-guard、canary-audit、slim-get、slim-install、slim-uninstall、六份计划与其余新增节点：镜头只列名称，未据此下结论。

### 执行与范围记录

- 指定安全目录建立命令：`mkdir -p /tmp/lumos-seat-work/code-test-quality-native-push/boundary-a`
- cwd：`/tmp/lumos-readme-oct-audit`
- rc：1
- 实际行为：`Operation not permitted`
- 实际载入产品：无。因此所有 before/after 产品行为均未判定。
- binding：before `598e41b…`／tree `db550fc…`；after `03a46da…`／tree `8aeb81d…`；repair patch SHA-256 `f1060f6b…`。
- 已覆盖：`scripts/test_test_quality_cli.py` 的五个指定修后方法、共同 fixture、repair patch 对该文件的方法级 hunk。
- 未验：其他新增/移动方法、被移除的 timeout 测试、产品实现、完整三份巨型 patch、`archive_only`、r1/r2 报告、作者 intake、候选行为案例、Windows 原生路径。
- 实际工具可见阅读量：约 1,275 行，包含规则、固定原文、镜头、搜索及重读；被工具截断而未显示的内容不计为已读，低于 1,800 行上限。