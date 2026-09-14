severity: minor

## 檢查方法(先說怎麼查,結論見下)

把 `scripts/lumos` 複製到 `/tmp/dart-sarif-mutate.*` 臨時目錄,對 `cmd_dart_sarif` / `_dart_rel` / `_DART_LEVEL` 做四種拆壞實驗,再用複本模組跑 `t_dart_sarif_bridge` 的完整邏輯(monkeypatch `GRAPHCTL` 指向複本):

1. 把「讀不懂就 rc2、不寫檔」改回舊寫法(讀不懂就退回 `{"diagnostics": []}` 空結果)→ **5 條斷言真的翻紅**(rc2 系列 3 條 + stderr 說明 1 條 + 閘層 ok_bad 1 條),12 條中只剩 7 條過。
2. 把 `_dart_rel` 的 macOS 符號連結雙候選(`path` / `os.path.realpath(path)`)改回只比對單一 `os.getcwd()`(不做 realpath)→ **「絕對路徑轉成相對於執行目錄」翻紅**。這條路徑正規化本身也用真實 dart 3.13.3 + `python3 -c "os.getcwd()"` 驗證過:`tempfile.mkdtemp()` 在這台機器確實落在 `/var/folders/...`,子行程 `os.getcwd()` 確實回 `/private/var/folders/...`——雙候選是真的在解這個真實落差,不是防一個不存在的坑。
3. 把 `_DART_LEVEL` 的 ERROR/WARNING 互換 → **「嚴重度對到 SARIF level」翻紅**。
4. 把 `ruleId` 硬改成空字串 → **「lint-adapter 吃到 dart claim」與「真機:真的 dart analyze 接起來」都翻紅**。
5. 把 dart 從 PATH 拿掉重跑整支測試 → 11 條照過、真機那條印「⚠ 這台沒有 dart,真機端到端那段沒驗到」並跳過,不算失敗——與 pitfalls-lint-adapter.md 說的「CI 機器沒有 dart,那段真機端到端只在有 dart 的機器上跑」一致。

結論:**`t_dart_sarif_bridge` 不是假守衛**——它綁的核心合約(讀不懂就失敗不吐空結果、路徑正規化、嚴重度映射、規則名抽取)逐條都會因為對應實作被拆壞而真的翻紅,而且路徑正規化那條連同它聲稱要解的「macOS `/var`→`/private/var`」現象都用真 dart 3.13.3 驗證過,不是編出來的場景。也另外用 `dart analyze --format=json` 真跑過「沒裝」「給不存在的檔」兩種輸入,SARIF 形狀與 rc(64)都與 diag() 造的樣本、docstring 描述一致。

## F1 「給了不存在的檔會印用法說明」這個動機場景,在宣稱的正式管線裡其實到不了 dart-sarif

severity: minor
blocking: 否
引句:「給了不存在的檔印的是用法說明——照舊寫法會替一條根本沒跑的檢查報平安」
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md:121`(同一句話在 `scripts/lumos:20985` 的 docstring 又講一次)

診斷文字與 docstring 把「dart 沒裝時 stdout 是空的」和「給了不存在的檔印用法說明」並列成兩種會餵進 `lumos dart-sarif` stdin、逼出 rc2 設計的**動機場景**。但兩篇筆記自己宣告的正式管線是 `dart analyze --format=json {LINT_FILES} 2>/dev/null | python3 scripts/lumos dart-sarif --out {LINT_SARIF_OUT}`——帶 `2>/dev/null`。實測:

```
$ dart analyze --format=json lib/nope.dart >out.txt 2>err.txt
$ wc -c out.txt          # 0
$ cat err.txt
Directory or file doesn't exist: lib/nope.dart
Usage: dart analyze [arguments] ...
```

用法說明整段印在 stderr,stdout 是 0 bytes。也就是說在宣稱的正式管線下,「給了不存在的檔」這個案例送到 `lumos dart-sarif` stdin 的其實是**空字串**,和「dart 沒裝」是同一種輸入、同一條程式碼分支——不是測試裡另外造的那段 `"Directory or file doesn't exist: ...\n\nUsage: dart analyze"` 字面文字(那段文字只有在有人手滑漏掉 `2>/dev/null`、或直接把 dart 的合併輸出餵給 dart-sarif 時才會真的出現在 stdin)。另外追過 `_lint_new_verdict` 的呼叫路徑(`scripts/lumos:18216-18219`):每邊(`base`/`head`)只在 `f in files` 時才把該檔納入 `targets`,新增檔在 base 側直接被濾掉整條命令 `continue`,dart 根本不會被叫去分析一個不存在的路徑。所以這個「用法說明」分支目前只是防禦性寫法(不寫壞、不是假的),但拿「實跑量過」去背書它是正式管線會真的遇到的第二種獨立輸入,和管線自己宣告的 `2>/dev/null` 對不上,屬於同一批筆記/docstring 內部不一致。不影響功能:空輸入與用法說明文字兩種輸入現有程式碼走同一個 `isinstance` 判斷,結果一樣是 rc2、不寫檔。

## 固定席節點逐條判定

- `Systems/guard-kill.md`(guard kill rc 優先序 / --json 純淨)——diff 未觸碰任何 guard/kill 相關函式,`dart-sarif` 是全新獨立子命令,不影響。
- `Systems/授權與歸屬.md`(SPDX/MIT、LICENSE 白名單)——新函式加在既有已有 SPDX 檔頭的 `scripts/lumos` 內,沒有新增檔案進 vendored 清單,不影響。
- `Systems/lumos-cli-read.md`(search 排除 superseded 不排除 stale)——diff 未觸碰 `search`/濾網邏輯,不影響。
- `Systems/lumos-cli-lifecycle.md`(re-inject 只覆蓋 sentinel 內、外部 byte-equal)——AGENTS.md 改動的「73→74」那行位於 `<!-- LUMOS:GRAPH-DISCIPLINE:END -->` 之後,屬 sentinel 外的一般人工編輯,不是 `lumos update` 自動重灌覆蓋 sentinel 內容,不牴觸此不變量。
- `Systems/design-loop.md`(處置閘第五步時間戳/計劃格式判定)——diff 未觸碰 design-loop 相關程式碼,不影響。
- `Systems/pitfalls-code-loop.md`、`Systems/loop-convergence-recording.md`、`Systems/lumos-deinit.md`(★RISK★)——diff 未修改這三篇筆記本體、也未觸碰其牽連的 code-loop/deinit 邏輯,不影響。

另外機械查證:`python3 scripts/lumos --help` 實際列出 74 個頂層子命令(含 `dart-sarif`),與 AGENTS.md/ARCHITECTURE.md/reference.md 改後的「74」一致;跑 `scripts/test_lumos.py -k docs_command_count` 與 `-k dart_sarif` 在本機（含真 dart 3.13.3）全綠(12+5 之後補跑的 5 條)。

---
整份最高等級:minor。
