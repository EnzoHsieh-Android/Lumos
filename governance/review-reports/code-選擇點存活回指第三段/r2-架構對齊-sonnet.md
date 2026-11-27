severity: minor

三問答案如下。第 1 問和第 2 問沒有不對齊,第 3 問有 1 條 minor。

**問 1:分層與依賴方向。沒有不對齊。**
- `_kill_mtime_settle` 抽在 `_kill_revert` 旁邊,`_kill_revert` 後半與 `_KillCompile.restore` 的直寫路徑都呼叫它。依賴方向沒變,仍是同層 helper 被呼叫(`scripts/lumos:29937`、`scripts/lumos:29950`、`scripts/lumos:29647`)。`_kill_merge_restore` 沿用 `_kill_revert`,沒有另走一條。
- `_choice_layer_side` 與 `_choice_layer_side_write` 走既有的 `_NOTE_AUDIT_WORK_DIR/_CHOICE_LAYER_WORK` 工作夾和 `_write_lf`。雜湊用同檔既有的 `_choice_sha`(`scripts/lumos:80232`),沒有另寫雜湊。
- 判讀檔的 `cite` 欄跟著 `_choice_layer_write` 的 doc 一起存,跟既有 `_CHOICE_LAYER_TYPES` 那套帳欄位的做法同層。
- `_gov_choice_count_layer` 補的 `0 <= layer <= 4` 與讀側 `_choice_ledger_aux` 的判法一致(`scripts/lumos:80571`)。0 到 4 的字面量本來就散在好幾處,這次沒有新增第二套寫法。

**問 2:命名與錯誤處理。沒有不對齊。**
- `_choice_layer_reject` 與情境題盲判的拒收輸出逐項一致:前綴「擋下:」、最多列 10 條、其餘印「…另有 N 處」,rc 都是 2(盲判那段在 `scripts/lumos` 約 77815 至 77825 行)。
- `_choice_layer_load_result` 讀結果檔用 `utf-8-sig`,與同檔其他讀檔寫法一致(`scripts/lumos:1040`)。
- `_CHOICE_COMPILE_SOLO_MAX` 命名與既有 `_CHOICE_PROBE_SOLO_MAX` 同一族(`scripts/lumos:29582`)。
- 兩者上限的排序方式不同,一個依距離、一個依 seed 雜湊,但各自對應不同需求,不算做法分岔。

**問 3:第二種做法。有 1 條 minor。**

`_CHOICE_LAYER_NOT_BODY_RE` 自己註解寫「判法同 `_FOLD_AUDIT_RECORD_RE`」,實際不同。

- `_FOLD_AUDIT_RECORD_RE`(`scripts/lumos:69165`)的前綴只認 `§\d+\s+`。新正規式的前綴是 `(?:\S+\s+)?`,任何非空白詞都算。
- 同一批節名在既有程式裡還有第三種寫法:`_KT_SIT_ACCEPT_H2_RE`(`scripts/lumos:76215`)與 `_EXPECTED_H2_RE`(`scripts/lumos:14412`)都是嚴格相等 `^##\s+…\s*$`。
- 例如標題「驗收條款(補充)」會被判讀材料當成非正文而丟掉。但 `_KT_SIT_ACCEPT_H2_RE` 不把它當條款節,所以它兩邊都進不去。

結構上沒有跨層直呼,所以不到 major。

severity: minor
blocking: 否
引句:「_CHOICE_LAYER_NOT_BODY_RE = re.compile(r"^(?:\S+\s+)?(?:驗收條款|預期值表|審計修正紀錄)")」
建議:要嘛註解改成「比 `_FOLD_AUDIT_RECORD_RE` 寬」並說明為什麼要容 `T3` 這類代號,要嘛前綴縮成跟它同一個 `§\d+` 或把代號也納入共用的那一條。

不對齊共 1 條,其中 major 0 條
