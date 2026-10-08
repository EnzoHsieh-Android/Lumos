severity: minor

审查结论：原四个问题已修好，原先通过的 19 案全部保留；找到一个修前、修后都存在的 `template` 输入边界问题，不能归因于本轮修补。

## F1 — `template` 接受超过 manifest 上限的 loop

severity: minor  
blocking: 否

`template` 只检查 `code-` 前缀，会以 rc=0 输出 129 字符的 loop；但同一 loop 放进 manifest 时，`text_field` 的 128 字符上限必定拒收。模板因此可能产生无法直接补齐使用的骨架。

引句:「if not args.loop.startswith("code-"):」

file: `governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:728`

产品佐证：

- 前缀检查未套用 `text_field`。

  file: `governance/eval/review_convergence.py:538`

- manifest 的字符串上限为 128。

  file: `governance/eval/review_convergence.py:260`

- manifest 案例以该限制验证 loop。

  file: `governance/eval/review_convergence.py:306`

- 规格期望 template 产生待补案例骨架。

  file: `docs/lumos-toolchain-knowledge/Projects/審查回顧轉可比較eval_計劃.md:26`

同案例 input：`code-` 加 124 个 `x`，总长 129。

expected：拒收并返回 rc=2；至少不得输出一份已知 loop 字段不符合 manifest schema 的骨架。

case_source：现有 template 测试只使用 `code-x`。

file: `governance/eval/test_review_convergence.py:235`

修前实跑：

- command：`/opt/homebrew/opt/python@3.14/bin/python3.14 governance/eval/review_convergence.py template <code-+124*x>`
- cwd：`/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/review-eval-source-restore-d0_i6ykl/after`
- 载入 SHA：`f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
- 前提：Darwin、Python 3.14、无网络
- rc：0
- 原始输出：`input_length=129`，JSON 内保留完整 129 字符 loop。

修后实跑：

- command：同上
- cwd：`/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/review-eval-source-restore-d0_i6ykl/fixed_r2`
- 载入 SHA：`4b8a83ae7f2403a2a169e8c868a6059b40b705daafd62779cc87af53b9cf822e`
- 前提：同上
- rc：0
- 原始输出：与修前相同。

可比与归因界线：两端使用同案例、同命令，均返回 rc=0，故这是既存产品缺陷，不是 `cd0ae310` 新增的回归。

## F2 — template 测试守卫没有覆盖自身输入上限

severity: minor  
blocking: 否

这是测试守卫缺陷，与 F1 的产品行为分开计算。现有测试直接调用 `case_template("code-x")`，没有经过 CLI 的前缀检查，也没有覆盖 128/129 边界。

引句:「x = ev.case_template("code-x")」

file: `governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:991`

file: `governance/eval/test_review_convergence.py:234`

file: `governance/eval/review_convergence.py:538`

同案例、command、cwd、载入 SHA、前提、rc 与原始输出均同 F1。

建议新增 128 字符成功与 129 字符 rc=2 的 CLI 边界案例。

## 已验正向行为

共同 case_source：`cd0ae310ccf1609a56a2552374eab47b13c55882:governance/eval/test_review_convergence.py`，SHA 为 `03ebe1f115f30d7b30c6800f53a680fbf30b2d9a9047a81f37cbe1451dd27355`。

完整 argv、cwd、环境及输出指纹：

file: `governance/review-reports/code-review-convergence-eval/r3-paired-cases.json:2`

### 显示控制字符

input：ledger loop 含 C1、双向控制字符及 U+2028。

expected：stdout 不含原始控制字符，且 JSON round-trip 不改变数据。

实际结果：修前 FAIL、修后 ok。

引句:「self.assertNotIn(chr(point), result.stdout)」

file: `governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:962`

case_source：

file: `governance/eval/test_review_convergence.py:193`

### 十万笔短行放大

input：100001 行 `{}`。

expected：抛出 `DataError`，不得展开成完整记录集合。

实际结果：修前 FAIL、修后 ok。

引句:「if len(rows) >= 100000:」

file: `governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:314`

case_source：

file: `governance/eval/test_review_convergence.py:226`

### token 类型冲突

input：同 token 分别携带 `0/false`、`1/true`。

expected：标记冲突，成本保持未知，不把布尔值与数字视为同一原件。

实际结果：修前 FAIL、修后 ok。

引句:「self.assertTrue(x["conflicting_tokens"])」

file: `governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:973`

case_source：

file: `governance/eval/test_review_convergence.py:212`

### 129 字符真实 receipt 路径

input：真实存在的 129 字符 receipt 文件名。

expected：作为有效 trial 载入，不得套用识别字段的 128 字符限制。

实际结果：修前 FAIL、修后 ok。

引句:「self.assertTrue((root / name).is_file())」

file: `governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:1048`

case_source：

file: `governance/eval/test_review_convergence.py:285`

### Paired 原始结果

修前：

- command：固定 Python 3.14 loader，载入修前 module 与同一份修后测试来源。
- cwd：`/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/review-eval-source-restore-d0_i6ykl/after`
- module SHA：`f1e5df1ed7bdcb6a74af6dcf090e5228eb76428eb8a1923a3f0c610261bb933c`
- case_source SHA：`03ebe1f115f30d7b30c6800f53a680fbf30b2d9a9047a81f37cbe1451dd27355`
- rc：1
- executed：true
- 原始输出：`FAILED (failures=4)`。

file: `governance/review-reports/code-review-convergence-eval/r3-paired-before.log:65`

修后：

- command：同一固定 Python 3.14 loader 与同一测试来源。
- cwd：`/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/review-eval-source-restore-d0_i6ykl/fixed_r2`
- module SHA：`4b8a83ae7f2403a2a169e8c868a6059b40b705daafd62779cc87af53b9cf822e`
- case_source SHA：`03ebe1f115f30d7b30c6800f53a680fbf30b2d9a9047a81f37cbe1451dd27355`
- rc：0
- executed：true
- 原始输出：23 案全部通过，结尾为 `OK`。

file: `governance/review-reports/code-review-convergence-eval/r3-paired-after.log:27`

原正常案例保留：修前有 19 个 ok，修后有 23 个 ok；没有任何修前 ok 案在修后消失。

引句:「self.assertEqual(r.returncode, 0, r.stderr)」

file: `governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:946`

可比与归因界线：这是同一固定 23 案、同一 case source 下的两端执行，可证明原四个症状在该案例集内修复，并证明原 19 个正常案例在该案例集内保留；不能据此宣称其他输入家族或平台没有回归。

## 硬合约核对

- `py-eventloop na`：符合。工具为同步 CLI，未见事件循环。
- `py-parallel na`：符合。未见并行工作。
- `py-external na`：符合。产品入口未调用网络或数据库。
- `py-memory tension / chosen suggested`：维持原表态。16 MiB 输入与十万笔限制不是总 RAM 保证；实现仍会整份 decode、解析并保留 rows。依既定条件于 2026-10-21 重新核对实轮数据量与内存。
- `py-hotpath satisfied`：固定来源中的 comparison 案例均通过；没有另跑会写暂存数据的正式 runner。
- 测试假绿合约：描述符拒绝案例含 `rejected == 80` 前置断言，且 paired 两端均通过。

  file: `governance/eval/test_review_convergence.py:181`

- bound-tests、canary、guard-kill、slim-get/install/uninstall、lumos-cli-read 等间接合约未在本席重跑，不能冒充已验。
- Windows 原生验证依指示排除，未宣称 Windows 相容性通过。

## 来源闭包

r3 bundle 记录显示：

- 前置 commit：`ce4c30f98fe3573b4f8946653ccf1c2d4d6d75da`
- 空对象库无 alternates
- fetch rc：0
- 还原 commit：`cd0ae310ccf1609a56a2552374eab47b13c55882`
- 还原 tree：`e588725a66a969f9f019c70d5d36312c2e833894`

修前重生记录为 `ce4c30f9..c909bf98`，`exact_match=true`。这些资料只用于确认来源身份，不作为修补因果证据。

## 实读与未验范围

实读行数：1,397 行逐行正文、程序、测试与 log；另有 33 个定向匹配或 JSON 字段，合计 1,430。

未验范围：

- module 426–517
- tests 361–469
- 完整 repair/snapshot 的其余内容
- Windows 原生行为
- 模型实轮
- 其他 graph-lens 间接合约

单一边界家族视角不保证没有其他回归。

最高等级：minor  
阻挡条数：0