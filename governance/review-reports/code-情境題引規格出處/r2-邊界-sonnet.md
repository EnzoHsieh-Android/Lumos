severity: minor

## b1 同文、同測試的「已寫過」判斷只看 refs 含不含,綁兩支測試的舊條款會把人裁卡死
severity: minor
blocking: 否
歸因:有證據的修復回歸
引句:「and test in (r.get("refs") or [])」
file: `scripts/lumos:75505`(修後版 `_situation_rule_insert` 的 `same` 判斷)
1. 輸入:計劃已有 `- [S1] 當 A 時,X 應 回 B [test:t_a,t_b]`,人裁條款文字相同、`--test t_a`。
2. 走到 `same = next(...)`。`t_a` 在 refs 裡、指紋相同,所以回「計劃已寫過 S1(同一段條款文字、綁同一支 t_a)」並叫人補記帳。
3. 讀取端 `_spec_gate_ruled_ids` 要求 `got[1] == {e["test_name"]}`。S1 的 refs 是 `{t_a,t_b}`,補記的事件永遠不會被認。
4. 另一個副作用:S1 若是一般條款(從沒人裁過),訊息也叫人手補一筆 situation-rule 事件。殺傷力在這個分支之前就被擋掉,根本沒跑。
5. 查證(兩版載入 `_situation_rule_insert`,同一份計劃):
   - 修前 6ccb7a462 回 `S2 None`(照插)。
   - 修後 1d535b07b 回 `None 計劃已寫過 S1…`。
6. 修法:`same` 改成 `set(refs) == {test}`,與讀取端一致。

## b2 `_situation_rule_read` 只拒 CRLF,單獨的 CR 仍被整份改寫成 LF
severity: minor
blocking: 否
歸因:有證據的原有漏查
引句:「if b"\r\n" in raw:」
file: `scripts/lumos:5362`(`_note_lines` 把單獨的 `\r` 也當換行)
1. 輸入:行尾只有 `\r` 的計劃(沒有 `\n`)。
2. `_situation_rule_read` 放行。`_situation_rule_insert` 用 `_note_lines` 切行再 `"\n".join`,整份行尾變 LF。原檔結尾若是 `\r`,結尾換行也掉了(`text.endswith("\n")` 為假)。
3. 查證:實測插入結果是 `...[test:t_a]\n- [S2] ... [test:t_new]`,沒有結尾換行。修前版同樣行為(修前 nl 只看 `\r\n`),修補沒有解決,也沒有讓它變差。
4. 這正是修補想擋的「靜默改行尾、整份 diff 重寫」,只是漏了單獨 CR 這一種。

## b3 `--plan` 的大小寫在不分大小寫的檔案系統上不被擋,帳上記的路徑跟實際檔名對不上
severity: minor
blocking: 否
歸因:有證據的原有漏查
引句:「if real_rel is None or "Projects/" + str(real_rel).replace(os.sep, "/") != prel:」
file: `scripts/lumos:75605`(修前版 `_situation_rule_plan` 對應的 `prel`)
1. 輸入:實際檔 `Projects/Abc_計劃.md`,`--plan Projects/abc_計劃`。
2. 在 macOS 預設檔案系統上,`resolve()` 不修正大小寫,所以 `_situation_rule_plan` 回 `('Projects/abc_計劃','Projects/abc_計劃.md')`。`Projects/ABC_計劃.md` 也一樣放行。
3. 帳的 `plan` 與 `nodes` 因此記成錯誤大小寫,`_spec_gate_ruled_ids` 的 `nfc(e["plan"]) == nfc(str(rel))` 永遠對不上。
4. 結果是失敗方向安全(多認不到,不會少擋),但人裁已寫進計劃,規格閘不認,且訊息叫人「不要重跑」。
5. 查證:兩版實測(`Projects/./X`、`//`、符號連結、尾端斜線、`.md.md`、NUL 都被修後版拒絕),只有大小寫放行。修前版同樣放行。

## 附:三問、圖譜鏡頭
- 三問一,原問題的修復效果:實測以下輸入走到預期行。
  - `[S１]`(全形數字)被拒。
  - `[s9]` 放行。
  - 反引號外 `a|b` 被拒;反引號內 `` `a|b` ``、`` `a`|`b` `` 的外側管線也照預期處理。
  - 孤立代理字元 `\ud800` 被拒。
  - 縮排續行(空格、tab)之後才插入;純空白行不算續行;續行後緊接標題時插在續行後、標題前。
  - 同文同測試重跑被拒;NFC 與 NFD 的條款文字視為同文。
  - BOM 開頭的計劃,插入後 BOM 保留。
  - 測試名含 `::`、`.`、`:`、中文、NFD、全形數字,refs 都等於原字串。
  - `--plan` 的 `Projects/./X`、`Projects//X`、符號連結、尾端斜線都被拒。
- 三問二,修補處相鄰路徑:寫入端與讀取端共用 `_clause_sha`。上列各輸入(含 `\u2028`、`\x0b`、`\x85`、NFD)的 `_clause_sha(插入後那行)` 都等於 `_clause_sha("- [Sn] 條款 [test:T]")`。refs 與 `{test}` 的相等,只有 b1 這種預先存在的多測試條款不成立。`python3.14 scripts/test_lumos.py -k situation_rule` 結果 89 passed, 0 failed。
- 本案特定鏡頭,零寬字元與軟連字號:`[S\u200b1]`、`[te\u200bst:q]`、`<!\u200b--` 能通過 `_situation_rule_clause_problem` 並插入,clause_bindings 的 refs 仍只有 `[t_n]`。這只驗了 `clause_bindings`,規格閘其他讀取路徑(`_is_invisible` 之後的比對)未判定。
- 其他邊界:5000 位數字的 `[S99…9]` 定義行會讓 `clause_bindings` 因 Python 的整數字串長度上限丟 ValueError,`_situation_rule_insert` 沒接住。這段程式碼不在本次 diff 內,讀取端同樣會炸,未判定是否納入範圍,不列 finding。
- 圖譜鏡頭:派工詞說鏡頭計算超時、沒附固定席筆記,所以圖譜鏡頭未判定。
- 清理:已刪除自己建立的臨時目錄,指令用字面絕對路徑。

最嚴重 severity: minor;blocking 共 0 條。
