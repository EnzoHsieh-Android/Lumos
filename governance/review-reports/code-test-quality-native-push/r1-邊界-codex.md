severity: major

ID: b1
severity: major
blocking: 是
引句:「from test_quality_semgrep import scan as semgrep_scan」
file: `scripts/test_quality_scan.py:20`
file: `scripts/test_quality.py:257`
file: `scripts/lumos:50231`
finding: 半套更新會讓 CLI 直接 traceback。若依序複製時中斷於 `test_quality_scan.py` 之後、`test_quality_semgrep.py` 之前，即使只跑 Python AST 掃描且未指定 `--semgrep`，頂層匯入仍拋出未捕捉的 `ModuleNotFoundError`，回 rc1，沒有回傳契約要求的 `complete:false`／rc2。現有測試只覆蓋 sidecar 全缺時舊 CLI 的 `--help`。

最小重現:
```sh
d=/tmp/lumos-seat-work/code-test-quality-native-push/boundary/partial-semgrep
mkdir -p "$d"
cp scripts/lumos scripts/test_quality.py scripts/test_quality_scan.py "$d/"
python3.14 "$d/lumos" test-quality scan scripts/test_test_quality_scan.py --json
rc=$?
test "$rc" -eq 2
```
目前輸出 `No module named 'test_quality_semgrep'` traceback、rc1，最後一行翻紅。

ID: b2
severity: minor
blocking: 否
引句:「scripts/test_quality.py", "scripts/test_quality_scan.py", "scripts/test_quality_semgrep.py」
file: `scripts/lumos:22125`
file: `scripts/lumos:21974`
finding: 新 sidecar 使任何 vendored CLI 呼叫在 `scripts/__pycache__/` 產生 bytecode，但 `deinit` 只刪白名單中的 `.py`，仍印「deinit 完成」並留下 Lumos bytecode及 `scripts/` 目錄。base 的 scripts/lumos --help 不產生本地 bytecode；HEAD 的相同命令立即產生 `scripts/__pycache__/test_quality.cpython-314.pyc`。既有 hook 模組執行後也可能留下 `scripts/hooks/claude/__pycache__`，所以 bytecode 清理類型並非全新；本次新增的具體退化是頂層 `scripts/__pycache__` 會由每次 CLI 建 parser 時的 sidecar 匯入產生，而且不在兩個 tree-dir 清理範圍內。真 `deinit --keep-graph` 已重現殘留。

PHP／Semgrep backend 的解析錯誤、未掃快照、缺工具與零候選處理：已讀,無 finding。

授權與歸屬固定席：三支新 vendored 檔均有 SPDX，授權檔未進移除白名單：已讀,無 finding。

圖譜 `test-quality-cli`、`test-quality-scan`、`test-quality-multilang`、`lumos-cli-lifecycle`：已逐條核對；除 b1、b2 外，無 finding。

總結: 最嚴重 severity major；blocking 1 條
