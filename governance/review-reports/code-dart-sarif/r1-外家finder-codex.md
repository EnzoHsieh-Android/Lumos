severity: major

## F1 快照缺少 Dart 套件解析環境，Flutter 閘會在錯誤語境下分析
severity: major
blocking: 是
引句:「| Dart / Flutter | `dart analyze`, piped through `lumos dart-sarif` (if the output can't be read, the gate reports "couldn't run" instead of "clean") |」
file: `scripts/lumos:17849`
新增告警快照既不帶 `.dart_tool/package_config.json`，也不帶未改動的相對 import；Dart analyzer 正靠 package config 解析 `package:` import（[官方說明](https://dart.dev/tools/pub/package-layout)），而新增測試只造了無依賴單檔。因此一般 Dart／Flutter 專案會吐可解析的假診斷，bridge 仍產合法 SARIF、runner 仍判成功，宣稱的 Flutter gate 沒有在真實依賴語境下執行。

重現：
```sh
tmp=$(mktemp -d)
cp -R /Users/enzo/.pub-cache/hosted/pub.dev/source_maps-0.10.13 "$tmp/probe"
cd "$tmp/probe"
test ! -e .dart_tool/package_config.json
raw=$(/opt/homebrew/bin/dart analyze --format=json lib/parser.dart)
dart_rc=$?
printf '%s' "$raw" | python3 -c 'import json,sys; d=json.load(sys.stdin)["diagnostics"][0]; print(f"{d[\"code\"]}: {d[\"problemMessage\"]}")'
printf 'dart_rc=%s\n' "$dart_rc"
```

輸出：
```text
uri_does_not_exist: Target of URI doesn't exist: 'package:source_span/source_span.dart'.
dart_rc=3
```

## F2 壞掉的 diagnostic 成員會被吞成乾淨結果
severity: major
blocking: 是
引句:「if not isinstance(data, dict) or not isinstance(data.get("diagnostics"), list):」
file: `scripts/lumos:21004`
程式只驗 `diagnostics` 是 list，非 dict 成員直接跳過，導致讀不懂的輸入仍以 rc0 輸出零結果 SARIF，正面違反本次「讀不懂就 rc2」的防假綠合約。

重現：
```sh
tmp=$(mktemp -d)
cd "$tmp"
printf '%s' '{"version":1,"diagnostics":[42]}' |
  python3 /Users/enzo/harness/lumos-toolchain/scripts/lumos dart-sarif
rc=$?
printf 'RC=%s\n' "$rc"
```

輸出：
```text
{"version": "2.1.0", "runs": [{"tool": {"driver": {"name": "dart"}}, "results": []}]}
RC=0
```

## F3 圖譜綁定的測試沒有走新增告警閘
severity: minor
blocking: 否
引句:「claims_real, ok_real = m._lint_run_and_parse(」
file: `scripts/test_lumos.py:11298`
圖譜宣稱此測試驗過基準版舊告警、目前版新增告警與移除 Dart 的自動放行，但函式只直接呼叫 `_lint_run_and_parse`，沒有 Git base/head、`_lint_new_verdict` 或 PATH 切換。因此 `[test:t_dart_sarif_bridge]` 是無法守住所述閘行為的假證據。

查證：
```sh
sed -n '11241,11303p' scripts/test_lumos.py |
  rg '_lint_new_verdict|_lint_run_and_parse|git init|git commit|PATH'
```

輸出：
```text
"""dart analyze --format=json → lumos dart-sarif → SARIF → _lint_run_and_parse(Dart/Flutter 進 lint-adapter)。
claims, ok = m._lint_run_and_parse(...)
claims_bad, ok_bad = m._lint_run_and_parse(...)
claims_real, ok_real = m._lint_run_and_parse(
```

## F4 兩篇圖譜筆記的更新日期仍停在舊狀態
severity: minor
blocking: 否
引句:「## Dart 橋接:讀不懂就失敗,不吐空結果（2026-09-14）」
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md:5`
兩篇筆記都新增 2026-09-14 的狀態，frontmatter 卻分別保留 2026-07-04 與 2026-09-13，令圖譜的更新日期與正文互相矛盾。

查證：
```sh
rg -n '^updated:|2026-09-14' \
  docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md \
  docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md
```

輸出：
```text
docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:5:updated: 2026-09-13
docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:68:...轉接器 2026-09-14 已進工具鏈...
docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md:5:updated: 2026-07-04
docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md:117:## Dart 橋接:讀不懂就失敗,不吐空結果（2026-09-14）
```

最高 severity：major
