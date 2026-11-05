severity: minor

**①分層與依賴方向**

`pitfalls` 輸出 JSON、掛鉤只讀欄位,這個方向跟既有做法一致。掛鉤現在就是用 `grep -q '"suite": *"docs"'` 這類寫法讀 `pf_json`,見 `scripts/hooks/pre-push:545`、`scripts/hooks/pre-push:546`、`scripts/hooks/pre-push:572`。沿用 `_note_reread_mainline_names` 也沒有重造主線判法。這一問只有一個小不一致。

severity: minor
blocking: 否(結構對,只是介面細節沒交代)
引句:「分支短名在 `_note_reread_mainline_names(root, tip)` 回的集合裡 → true」
- 位置:做法 1,`pitfalls` 的 `--pushed-ref` 與 `pushed_mainline` 判定。
- 問題:`_note_reread_mainline_names(root, tip, deadline)` 需要 `tip`,見 `scripts/lumos:53734`。唯一的既有呼叫端 `_note_reread_push_old` 傳的是 `scan["tip"]`,見 `scripts/lumos:53776`。`pitfalls` 只收 `--diff`,spec 沒說 `tip` 從哪來,例如從 `--diff` 右端解析,或不傳。
- 佐證:`scripts/lumos:53776`、`scripts/lumos:62304`。

**②命名與錯誤處理**

severity: minor
blocking: 否(命名慣例不一致,結構對)
引句:「只用來判主線,不改 `--diff` 的範圍;不需要遠端名」
- 位置:做法 1,單給 `--pushed-ref`、不給 `--push-remote`。
- 問題:專案其他命令都把兩個旗標綁在一起,缺一個就擋下並印「要一起給」。這包括 `room-guard`、`reread-prepare`、`reread-check`。掛鉤帶旗標時也總是成對。spec 讓 `pitfalls` 單獨接受 `--pushed-ref`,是旗標語意的第二種寫法。spec 沒有說明為什麼這裡可以不成對。
- 佐證:`scripts/lumos:49220`、`scripts/lumos:53490`、`scripts/hooks/pre-push:698`、`scripts/hooks/pre-push:700`。

severity: minor
blocking: 否(同一個詞在兩處語意相反)
引句:「被推的不是 `refs/heads/` 底下 → true」
- 位置:做法 1,`pushed_mainline` 對非分支 ref 的判定。
- 問題:既有的推主線判定 `_note_reread_push_old` 碰到非 `refs/heads/` 的 ref 就直接 return,視為不是主線。spec 的 `pushed_mainline` 對標籤回 true。這個方向偏安全,但同一個「是不是主線」的概念在兩處對標籤回答相反,spec 沒有點出這個差異。
- 佐證:`scripts/lumos:53772`。

severity: minor
blocking: 否(寫法細節)
引句:「用掛鉤既有的 `pp_q` 引號寫法」
- 位置:做法 2,掛鉤多帶 `--pushed-ref "$_rref"`。
- 問題:`pp_q` 是用來組字串的,例如 `_push_args="... --pushed-ref $(pp_q "$_rref")"`。掛鉤直接呼叫 `pitfalls` 時是用陣列式引號 `"$_rref"`,見 `scripts/hooks/pre-push:700`、`scripts/hooks/pre-push:540`。如果在直接呼叫裡再套 `pp_q`,ref 名會多出一層字面引號。spec 應該寫成直接呼叫的形式。
- 佐證:`scripts/hooks/pre-push:117`、`scripts/hooks/pre-push:698`。

**③第二種做法**

沒有發現 major 級的第二種做法。

severity: minor
blocking: 否(沿用同一組變數,但判 light 的條件變弱了)
引句:「降級刻意不受 `light_ok` 約束」
- 位置:做法 2,降成 light 的條件。
- 問題:現行 `scripts/hooks/pre-push:572` 只有一處把 `_suite_this` 從 full 降成 light,而且必須同時滿足 spec-gate 判 light 和 `light_ok`。註解寫明 `light_ok` 是為了不讓測試檔、skills 這類檔溜過去。spec 新增了第二個降級入口,條件只看 `pushed_mainline` 和 `suite_computed`。它沿用 `_SUITE_LIGHT` 和 `_SUITE_KEYS`,下游沒有分叉,所以不算新機制。但「什麼情況可以少跑全套」現在有兩套準則,spec 應明講這是刻意放寬。
- 另一個相關點:`suite_computed` 是新增的布林欄位,而現有的「算不出來」是用 `_test_suite_for_range` 回傳的 `reason` 字串表達。這是第二個傳遞管道。`--json` 輸出在 `scripts/lumos:61916` 與 `scripts/lumos:61983` 兩處各組一次,兩處都要加欄位,spec 沒提醒。
- 佐證:`scripts/hooks/pre-push:572`、`scripts/lumos:61712`、`scripts/lumos:61916`、`scripts/lumos:61983`。

**④落點**

已讀,無 finding。`lands_in` 指向 `Systems/bound-tests-gate` 與 `Systems/pitfalls-code-loop`,跟旗標與欄位的實際所在檔對得上。掛鉤是 `scripts/hooks/pre-push`,`pitfalls` 欄位在 `scripts/lumos` 的 `cmd_pitfalls`。

不對齊共 5 條,其中 major 0 條。整份最高是 minor,沒有會擋的問題。
