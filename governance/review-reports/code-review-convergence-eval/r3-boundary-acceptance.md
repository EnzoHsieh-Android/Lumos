severity: clean

本次只验收原 F1/F2；两项都已折好。没有重新扫描全案，也不构成第四轮或全案收敛保证。

## F1 — 产品边界

status: 已修复  
blocking: 否

`case_template` 现在复用 manifest identifier 的 `text_field` 校验，因此 128 字符可接受、129 字符会抛出 `DataError("case-loop")`。

引句:「if not text_field(loop) or not loop.startswith("code-"):」

file: `governance/eval/review_convergence.py:260`

128 字符上限来自同一 helper：

引句:「if not isinstance(value, str) or not value.strip() or len(value) > 128:」

file: `governance/eval/review_convergence.py:283`

实际 CLI 也直接调用该 helper，没有另留一套较宽松的判断：

引句:「out = case_template(args.loop)」

file: `governance/eval/review_convergence.py:561`

红绿证据：

- 修前，129 字符 helper 边界没有抛出 `DataError`。

  引句:「AssertionError: DataError not raised」

  file: `governance/review-reports/code-review-convergence-eval/r3-fixes-before.log:9`

- 修后，包含该案例的 25 项测试全部通过。

  引句:「Ran 25 tests in 0.430s」

  file: `governance/review-reports/code-review-convergence-eval/r3-fixes-after.log:3`

结论：原 F1 已折好。

## F2 — 测试守卫

status: 已修复  
blocking: 否

新增的 `test_template_loop_matches_manifest_identifier_boundary` 已覆盖原报告要求的四个部分：

1. 前置断言明确证明输入分别为 128 与 129 字符。

   引句:「self.assertEqual((len(accepted), len(rejected)), (128, 129))」

   file: `governance/eval/test_review_convergence.py:262`

2. 128 字符通过 helper。

   引句:「self.assertEqual(ev.case_template(accepted)["loop"], accepted)」

   file: `governance/eval/test_review_convergence.py:263`

3. 129 字符由 helper 拒绝。

   引句:「with self.assertRaises(ev.DataError):」

   file: `governance/eval/test_review_convergence.py:264`

4. 同一个 129 字符输入经过真实 CLI 时返回 rc=2。

   引句:「self.assertEqual(result.returncode, 2, result.stdout + result.stderr)」

   file: `governance/eval/test_review_convergence.py:268`

修前日志明确显示该新增守卫会翻红：

引句:「FAIL: test_template_loop_matches_manifest_identifier_boundary」

file: `governance/review-reports/code-review-convergence-eval/r3-fixes-before.log:3`

修后日志显示全套 25 案通过：

引句:「........................」

file: `governance/review-reports/code-review-convergence-eval/r3-fixes-after.log:1`

结论：原 F2 已折好；测试同时证明现场 helper 分支与真实 CLI 分支均可到达。

## 验收边界

本次只读取：

- `governance/eval/review_convergence.py`
- `governance/eval/test_review_convergence.py`
- `governance/review-reports/code-review-convergence-eval/r3-fixes-before.log`
- `governance/review-reports/code-review-convergence-eval/r3-fixes-after.log`

修前日志另有一个 JSON 数字等价性的失败，但它不属于本席 F1/F2，本次不作判断。没有读取其他席报告、没有写档，也没有重新审查其他功能。

最高等级：clean  
阻挡条数：0