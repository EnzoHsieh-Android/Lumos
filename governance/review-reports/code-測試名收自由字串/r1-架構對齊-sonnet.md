severity: major

這份 diff 在三處另寫了測試名切法或字串掃描,和它自己宣稱的「全庫唯一切法」不一致。我只讀了 diff 和 base 的對照處,沒有跑 pitfalls。

## 1. 分層與依賴方向

大致對齊。新的 `_split_test_ref`、`_test_name_ok`、`_unwrap_backticks`、`_test_name_boundary_re` 放在 `resolve_test_refs` 旁邊,是同一層的純函式。呼叫方向由 guard、kill、spec-gate、歸檔等上層往下呼叫,沒有看到跨層直呼。

`_apply_test_overrides` 是從 `load_test_profile` 抽出來的,單平台和多平台都改走它,方向正確。

比較不對齊的一處是 `_run_cmd_expand` 加了 `name_filter` 參數。結構上沿用既有的 `{method}` 展開,不算跨層。

## 2. 命名與錯誤處理

擋下訊息和回傳碼大致和鄰居一致:

- `擋下:…` 開頭、rc 2、走 stderr,和鄰居相同。
- guard scaffold 的新訊息把可貼的指令獨立一行,並用 `_kill_cmd_arg` 包引號,符合「發生什麼→為何在意→指令」的形狀。

不一致的是同一句合法性規則被複製貼上三份。

severity: minor
blocking: 否
引句:「不能是空的、不能以減號開頭、不能含方括號或半形逗號、不能有控制字元)」
`_test_name_ok` 的白話規則在 `guard settle`、`guard kill` 和 `_kill_ev` 三處各寫一遍。diff 第 642、691、1411 行都有,措辭一致,但沒有共用常數。之後規則改了,三處會漂移。對照:既有的 `_CLAUSE_HANG_WHY` 這類字串表是集中放的。

另外,新增的 `_ns_wd_binding_norm` 沿用 `_test_name_of_match`、`_unwrap_backticks` 等底線私有命名。命名本身沒問題。

## 3. 第二種做法

severity: major
blocking: 是
引句:「m = re.match(r"([^:：]*)[:：]", body) if platforms else None」
`_split_test_ref` 的註解寫「切法全庫只有那一支,各處不另寫」,但 diff 裡還有另外兩處自己切平台前綴。

- 第一處是 `_kill_ev` 的新分支(diff 第 1406 行附近)。它重寫 `([^:：]*)[:：]`、又用 `_TEST_PLAT_LIKE_RE` 判前綴,最後才呼叫 `_split_test_ref`。這是在函式外複製了函式內的邏輯。
- 第二處是 `_ns_wd_binding_norm`(diff 第 1066–1070 行)。它保留舊的 `[^:：\s`\[\]]+` 前綴正規式,自己把前綴換成半形、拆反引號。
- 舊碼在 `_NS_TR_PREFIX_RE` 也有同樣做法,所以「去重與顯示」可以算沿襲。但 `_kill_ev` 那一處是這個 diff 新加的,算第二種做法。
- base 的對照:`_kill_ev` 舊版用 `body.split(":", 1)` 單一路徑。

severity: major
blocking: 否
引句:「_JS_STRIP_RE = re.compile(r"'(?:[^'\\\n]|\\.)*'?|\"(?:[^\"\\\n]|\\.)*\"?|`(?:[^`\\]|\\.)*`?|//[^\n]*|/\*(?:.*?\*/|.*\Z)", re.S)」
這是專案裡第三套認字串的詞法掃描,而且 `_strip_test_comments` 現在有三種剝法。

- 既有的是 `c-style` 兩段 `re.sub`,`c-style+strings` 把字串字面清空(都在 `_strip_test_comments`),以及 pitfalls 用的 `_strip_string_literals` / `_PITFALL_STRLIT_RE`(`scripts/lumos:30574`、`scripts/lumos:30744`,指 base 版)。
- 新的 `c-style-strings-kept` 是一趟式掃描,理由是「保留字串、同時剝註解」,既有的做不到,所以不是無由新增。
- 但它是在同一個派發函式裡加第三種模式,而不是修既有的 `c-style`。舊的 `c-style` 對 `http://`、`/*` 的錯誤,diff 註解自己承認。
- 判不準,標 ⚠ 交編排者:要不要讓 `dart`/`node-jest`/`playwright` 以外的 profile(`java`、`kotlin`、`swift`)也改走新模式。

## 結論

不對齊共 3 條,其中 major 2 條。上面另有一條 minor 訊息重複,這條不計入阻擋。

數字說明:major 兩條是 `_kill_ev` 另寫前綴切法、`_JS_STRIP_RE` 第三套字串掃描;minor 一條是合法性訊息三份複製。所以嚴格算是 3 條,major 2 條。

引句出處:diff 檔 `/Users/enzo/orca/workspaces/lumos-toolchain/web-gaps/governance/review-reports/code-測試名收自由字串/r1-lumos.patch`。審材外佐證:file: `scripts/lumos:30574`(`_strip_string_literals`,base 版)。
