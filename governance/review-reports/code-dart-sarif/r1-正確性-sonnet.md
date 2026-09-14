severity: major

## F1 診斷清單裡混進非物件元素時,靜默吞掉、回報「零告警、rc0」——正是這支橋接自稱要防的假綠

severity: major
blocking: 是
引句:「if not isinstance(g, dict):」
file: `scripts/lumos:21004`

`cmd_dart_sarif` 對頂層做了「讀不懂就 rc2、不寫檔」的防呆(`isinstance(data.get("diagnostics"), list)`),但只驗證到「是不是 list」,沒驗證 list 裡的元素。實測輸入 `{"diagnostics": [1, "hello", null]}`——明顯不是 dart 真實輸出、也騙不過人眼——目前的處理是 `for g in data["diagnostics"]: if not isinstance(g, dict): continue`,三個元素全部跳過,`results` 變成空陣列,最終回 **rc0** 並寫出 `{"results": []}`。

重現:
```
$ echo '{"diagnostics": [1, "hello", null]}' | python3 scripts/lumos dart-sarif --out /tmp/o.sarif
$ echo $?
0
$ cat /tmp/o.sarif
{"version": "2.1.0", "runs": [{"tool": {"driver": {"name": "dart"}}, "results": []}]}
```

這正是這支橋接自己在文件與 docstring 裡點名要避免的假綠模式(「吐一份零條告警的 SARIF,等於替一條根本沒跑的檢查報平安」)。sqlfluff-sarif / stylelint-sarif 的舊行為被它拿來當反例,但它自己在「diagnostics 是 list、但元素形狀不對」這一種輸入下,掉進一模一樣的坑。新增告警閘拿到 rc0 + 空結果檔,會判「這次跑了、乾淨」而不是「跑不動」,等於把一次讀不懂的執行悄悄放行。測試 `t_dart_sarif_bridge` 沒有覆蓋「diagnostics 是 list 但元素非 dict」這個案例,所以沒抓到。

## F2 巢狀欄位型別不對時,`start.get(...)` 丟未捕捉的 AttributeError——不是文件宣稱的「rc2 講清楚為什麼」

severity: minor
blocking: 否
引句:「start.get("line", 0), "endLine": end.get("line", start.get("line", 0))」
file: `scripts/lumos:21014`

`loc.get("range") or {}`、`rng.get("start") or {}` 這種寫法只擋得住「缺欄位 / null」,擋不住「欄位在、但型別不對」。輸入 `{"diagnostics":[{"location":{"range":{"start":[1,2],"end":{"line":1,"column":1}}}}]}` 時,`start` 是 list,`start.get("line", 0)` 丟 `AttributeError: 'list' object has no attribute 'get'`,整支指令沒被任何 try/except 接住。

重現:
```
$ echo '{"version":1,"diagnostics":[{"code":"x","severity":"WARNING","location":{"file":"/tmp/a.dart","range":{"start":[1,2],"end":{"line":1,"column":1}}},"problemMessage":"boom"}]}' \
  | python3 scripts/lumos dart-sarif --out /tmp/o2.sarif
Traceback (most recent call last):
  ...
  File "scripts/lumos", line 21014, in cmd_dart_sarif
    "region": {"startLine": start.get("line", 0), "endLine": end.get("line", start.get("line", 0))},
AttributeError: 'list' object has no attribute 'get'
$ echo $?
1
$ ls /tmp/o2.sarif
ls: /tmp/o2.sarif: No such file or directory
```

不影響閘的安全性(檔案沒寫出來,`_lint_run_and_parse` 讀到空/不存在的暫存檔仍會判 `([], False)`=跑不動,不會誤判乾淨),但跟 docstring 自己宣稱的「★讀不懂就失敗(rc2、不寫結果檔)★」不符——這裡是 rc1、丟原始 traceback 到 stderr,不是設計要給的那句「擋下:…」說明。降級為 minor 是因為真實 `dart analyze --format=json` 的 schema 穩定,目前只有三種 severity、range 一定是物件,不會實際觸發;只有輸入被竄改或未來 schema 改版才會踩到。

## F3 圖譜筆記與 docstring 宣稱「給不存在的檔會印用法說明」,跟已宣告的實際管線行為對不上

severity: minor
blocking: 否
引句:「給了不存在的檔印的是用法說明」
file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md:184`

`.lumos/lint.json` 宣告的指令本身就帶 `2>/dev/null`(`dart analyze --format=json {LINT_FILES} 2>/dev/null | python3 scripts/lumos dart-sarif …`)。實測 dart 3.13.3 對不存在的檔案,「Directory or file doesn't exist…／Usage: dart analyze…」這段文字是印在 **stderr**,不是 stdout:

```
$ dart analyze --format=json /tmp/does-not-exist-xyz.dart 1>/tmp/o.txt 2>/tmp/e.txt; echo $?
64
$ wc -c /tmp/o.txt
0 /tmp/o.txt
$ head -1 /tmp/e.txt
Directory or file doesn't exist: /tmp/does-not-exist-xyz.dart
```

也就是說,照這篇筆記與 `cmd_dart_sarif` docstring 宣告的真實管線(`2>/dev/null`),「給了不存在的檔」這個情境下 `dart-sarif` 收到的 stdin 其實是**空字串**,會走「標準輸出是空的(dart 沒裝或沒跑起來?)」那條分支,而不是筆記與 `t_dart_sarif_bridge` 的「用法說明(給了不存在的檔)」案例所模擬、直接把用法說明文字塞進 stdin 的那條分支。兩條分支結果一樣(rc2、不寫檔),不影響閘的正確性,但「實跑量過」這句話所描述的因果跟宣告的管線對不上,屬於內部不一致,如實回報。

## 固定席逐條檢查

- **guard-kill.md ★INVARIANT★**(guard kill rc 優先序 / --json 純淨):本次 diff 未觸碰任何 guard kill 相關程式碼路徑,不影響。
- **授權與歸屬.md ★INVARIANT★**(SPDX / LICENSE 白名單):只在既有的 `scripts/lumos`(已有檔頭 SPDX)內新增函式與子指令,沒有新增檔案、沒有動 `_VENDORED_TOOLKIT` 清單,不影響。
- **lumos-cli-read.md ★INVARIANT★**(search 排除 superseded 不排除 stale):未觸碰 search/query 邏輯,不影響。
- **lumos-cli-lifecycle.md ★INVARIANT★**(re-inject 只覆蓋 sentinel 之間、外部 byte-equal):AGENTS.md 裡「73→74」那行改動在 `<!-- LUMOS:GRAPH-DISCIPLINE:END -->` 之後,屬於 sentinel 區塊**外**的人工維護內容,且本次 diff 完全沒動 `lumos update`/re-inject 的程式邏輯,不影響。
- **design-loop.md ★INVARIANT★**(處置閘第五步、審材必須是 .md):未觸碰 design-loop/loop 相關程式碼,不影響。
- **pitfalls-code-loop.md / loop-convergence-recording.md / lumos-deinit.md**(★RISK★,家含 scripts/lumos):三者都只是「牽連檔含 scripts/lumos」,本次改動是往同一支已受管檔案裡加一個獨立的新子指令(`dart-sarif`),不觸及 pitfalls tier 判定、loop 收斂記帳、deinit 白名單解除邏輯本身,不影響其宣稱行為。
- 其餘「超出上限,只列名」節點(含 `測試假綠形態.md`)未附 KEY/INVARIANT 內容,無法逐條核對;但提醒 F1 本質正是一種「假綠」,和 `測試假綠形態.md` 主題相關,建議之後補讀該節點確認是否已收錄同類模式。

最高等級:major,原因是 F1(diagnostics 元素型別不對時靜默產出假乾淨結果)已具體重現,且直接牴觸這支橋接存在的核心理由。
