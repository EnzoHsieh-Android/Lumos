severity: major

F1：三支修補回歸測試缺少獨立前置斷言

severity: major  
blocking: 是

硬合約要求修 bug 的翻紅測試先證明目標情境確實成立；但下列測試都是執行產品後才斷言結果：

- 控制字元：產品命令在 governance/eval/test_review_convergence.py:199，第一個斷言在 :205。
- token 型別衝突：產品呼叫在 :217，第一個斷言在 :218。
- 十萬零一筆：:229 寫 fixture，:230 的 `assertRaises` 本身就是結果斷言，沒有先確認實際筆數或檔案大小。
- 129 字 receipt 測試有在產品呼叫前檢查長度及真實檔案，符合合約，見 :292、:293。

預期出處：governance/review-reports/code-review-convergence-eval/r3-graph-lens.txt:12。

完整快照引句：

- `self.assertNotIn(chr(point), result.stdout)` — governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:962
- `self.assertTrue(x["conflicting_tokens"])` — governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:973
- `def test_short_record_amplification_is_rejected(self):` — governance/review-reports/code-review-convergence-eval/r3-snapshot.patch:981

最小翻紅检查在 repo 根以 Python 3.14 AST 读取固定测试源，寻找产品调用前、且不是 `assertRaises` 的独立断言。原始输出：

```text
test_render_control_characters_without_changing_data: product_line=199 independent_precondition_assertions=[]
test_token_identity_keeps_json_types_and_ignores_key_order: product_line=217 independent_precondition_assertions=[]
test_short_record_amplification_is_rejected: product_line=231 independent_precondition_assertions=[]
missing_precondition=test_render_control_characters_without_changing_data,test_token_identity_keeps_json_types_and_ignores_key_order,test_short_record_amplification_is_rejected
RC=1
```

建议分别增加：

- 控制字元：执行 CLI 前验证磁碟 JSON 解码后确实含目标 C1／bidi 字元。
- token 型別：执行 `build_cohort` 前验证 `tokens` 两值型别不同。
- 十万零一笔：执行 `read_ledger` 前验证文件大小或实际为 100001 条记录。

配对证据与归因边界：

- case source：修后固定 `governance/eval/test_review_convergence.py`，SHA `03ebe1…27355`；检索来源见 r3-paired-cases.json:48。
- 修前 argv、cwd、执行状态及前提在 r3-paired-cases.json:6、:13、:15、:18；载入模块 SHA `f1e5df…933c`，见 r3-paired-before.log:1。rc=1；三案均 FAIL，见 :10、:12、:13。
- 修后 argv、cwd、执行状态及前提在 r3-paired-cases.json:28、:35、:37、:40；载入模块 SHA `4b8a83…822e`，见 r3-paired-after.log:1。rc=0；三案均 ok，见 :10、:12、:13。
- 环境两端相同：Python 3.14.6、Darwin、network=none，见 r3-paired-cases.json:19、:41。
- 来源闭包前提为 `ce4c30f9…`、无 alternates、修后 commit/tree 相符，见 r3-source-restore.json:3、:5、:7、:8。
- 配对结果证明产品修补是 fail→pass，但不能替代测试内的前置断言。token／短行测试是本次新增，测试守卫缺陷可归因本修补；控制字元测试是既有测试在本轮扩写，属于随修补带入但非全新产生的守卫债。未发现可归因本修补的产品回归。

修补三问：

1. 原问题已修好：四个固定案例由修前 FAIL 变为修后 ok，包括控制字元、短行放大、token 型别及 129 字路径；见 r3-paired-before.log:10、:12、:13、:24 与 r3-paired-after.log:10、:12、:13、:24。
2. 原正常案例保留：同一固定来源共 23 案，修前只有上述四案失败，修后 23 案全过；见 r3-paired-before.log:63、:65 与 r3-paired-after.log:27、:29。此结论仅限这一测试家族。
3. 新增问题：有一项测试守卫缺陷，即 F1；没有观察到同家族产品行为回归。

硬合约逐条状态：

1. 修 bug 翻红钉前置断言：违反，见 F1。
2. bound-tests gate 真跑及 rc：未执行 `lumos code-loop check`，未验。
3. canary record 持久化读回：未验。
4. canary second 不影响 gate：未验。
5. guard-kill rc 优先序：未验。
6. guard-kill JSON 纯度：未验。
7. 三支 PowerShell ASCII/BOM：Windows 原生能力不可得，跳过。
8. PowerShell `$Args` 保留名：Windows 原生能力不可得，跳过。
9. CLAUDE.md sentinel 外 byte-equal：未验。
10. 精简安装冪等：未验。
11. 完整区块 byte-level 备份：未验。
12. 安装 manifest 身分证：未验。
13. 安装三层目标守卫：未验。
14. `.cmd` 直译器选择：Windows 原生能力不可得，跳过。
15. `lumos`／`lumos.cmd` 碰撞侦测：Windows 原生能力不可得，跳过。
16. 卸载 bin 内容比对：未验。
17. 四项清理独立：未验。
18. skill 目录先备份：未验。
19. CLAUDE.md 精确还原：未验。
20. `.cmd` 独立移除：Windows 原生能力不可得，跳过。
21. 卸载 manifest 清理：未验。
22. search 默认排除 superseded、不排 stale：未验。

py-memory 表态：tension；chosen suggested。十六 MiB／十万笔只是输入约束，不是程序总 RAM 保证；文件也明确如此说明，见 governance/eval/review_convergence.md:28。回看日期：2026-10-21。

来源核对：bundle SHA 实测为 `b8aadb…6741`，与 r3-source-restore.json:2 相同；两端模块及固定测试源 SHA 与配对日志相同。还原目录是无 Git metadata 的普通完整快照，因此没有把其中 `git rev-parse HEAD` 的 harness 失败算产品失败。

最高等级：major  
阻挡条数：1  
实读：1651 行完整材料（AGENTS 97、CLAUDE 101、skills 327、graph lens 69、module 560、tests 469、docs 28），另仅定向抽取绑定字段与案例日志；未全文读取 r1/r2 报告、intake 或完整 repair patch。  
未验范围：Windows 原生行为、真实模型试轮、其他测试家族及上述未涉及合约；单一家族结果不保证无回归。