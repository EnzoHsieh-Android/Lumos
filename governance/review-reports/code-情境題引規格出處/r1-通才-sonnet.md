severity: major

## t1 人裁條款換綁別的測試後仍被當既有行為,殺傷力證明對不上
severity: major
blocking: 是
引句:「(那一行的 _clause_body_of(keep_code=True) 轉 NFC 再算 sha256,同寫入時的算法)才算;條款改了字雜湊就對不上、回到一般條款的規矩。」
file: `scripts/lumos:14531-14551`、`scripts/lumos:75669-75672`
1. `_clause_body_of` 會先剝掉 `[test:...]`,所以條款雜湊不含綁的測試名。
2. 治理帳事件另外存了 `test_name`,`_spec_gate_ruled_ids` 只比 `plan`、`clause_id`、`clause_sha`,沒比測試名。
3. 殺傷力驗證只證明過寫回當下綁的那支測試咬得住。docstring 也這樣宣稱:「人裁的測試是寫回當下才綁上的,殺傷力驗證已證過它咬得住」。
4. 把 `[test:t_orig]` 改成 `[test:任何一支早就綠、從沒被殺過的測試]`,雜湊不變,規格閘照樣把這條當既有行為(同 keeps),不要求紅,也不要求預期值表。
5. 規格閘原本要擋的是「新行為條款綁了一支沒被證明會紅的測試」,這個洞讓它整個失效。
重現(臨時 repo 放治理帳一筆 situation-rule,`test_name` 是 `t_orig`):
```
text  = "# P\n\n## 驗收條款\n\n- [S1] 當 A 時 系統應 回 B [test:t_orig]\n"
orig            -> _spec_gate_ruled_ids(...) = {'S1'}
test 改成另一支 -> _spec_gate_ruled_ids(...) = {'S1'}   # 預期該是空集合
```
計劃規格範圍 5 與 S13 只寫了文字雜湊,所以這是規格本身的洞,不只是實作漏。比對端沒把帳上的 `test_name` 納入,這個保證就是假的。

## t2 `_situation_rule_clause_problem` 把合法條款文字擋掉
severity: minor
blocking: 否
引句:「_SITUATION_RULE_BAD = (("\n", "換行"), ("\r", "換行"), ("[S", "[S"), ("[test:", "[test:"),」
file: `scripts/lumos:75407-75425`
1. 比對時兩邊都轉小寫(`bad.lower() in low`),所以 `[s` 開頭的任何字樣都被擋。反引號裡的 Kotlin 程式碼 `items[size]` 就中,但規格閘只認 `[S<數字>]`。
2. 反引號裡的 `a || b` 因為禁用 `|` 也被擋。
實跑:
```
'當 `items[size]` 超過 5 時 系統應 回 錯誤' -> 條款文字不准有 [S(…)
'當 `a || b` 成立 時 系統應 回 錯誤'        -> 條款文字不准有 |(…)
```
這兩條在 Android 條款裡很常見,訊息講的又不是真正的原因。人裁指令因此寫不回,出口只剩改寫條款或段放行。

## t3 推送熱路徑上,每份計劃都先讀整本治理帳,才看門與生效日
severity: minor
blocking: 否
引句:「        new = new - _spec_gate_ruled_ids(_vault_repo_root(env), rel, text)   # 只扣掉、不併進 keeps:表裡有它那一列也不算錯(不講「標了 keeps」)」
file: `scripts/lumos:14557-14576`、呼叫端 `scripts/lumos:17254`
1. `_expected_requirement` 只要有一條沒標 keeps 的條款,就先算人裁集合,再判 `door != "high"` 與生效日。
2. 風險低、生效日前的計劃最後都回 None,卻每份都已讀完 22MB、12.5 萬行的 `docs/.governance-log.jsonl`。
3. 實測 `_gov_vc_gate_events('.', 'situation-rule')` 約 0.16 秒/次。推送前的 `_expected_push_one` 對每份候選計劃都呼叫它。
4. 把人裁集合移到門與日期檢查通過之後,就不用為會回 None 的計劃付這筆錢。

## t4 `_situation_rule_write` 重寫了專案已有的原子寫入
severity: minor
blocking: 否
引句:「整份正文原子寫(同 atomic_write_verify 的步驟):拒絕符號連結與多重硬連結 → 暫存檔 → 讀回比對 → 取代;回失敗原因或 None。」
file: `scripts/lumos:30466`(`_write_refusal_reason`)、`scripts/lumos:30533`(`_write_bytes_atomic`)、新碼 `scripts/lumos:75455`
1. `_write_bytes_atomic` 的 docstring 明寫「要位元組逐一相同的寫入直接用這支,不另寫一份原子寫入」。
2. 新函式自己開 `O_EXCL` 暫存檔、`copymode`、`os.replace`,是第三份拷貝。
3. 該改叫的是 `_write_refusal_reason(path)` 加 `_write_bytes_atomic(path, data)`。讀回比對可以放在寫完之後,不用重做暫存檔。
4. 維護風險:暫存檔命名、權限、例外清理哪天在共用處修了,這份不會跟著改。

## t5 人裁事件的 `recipe_id` 跟殺傷力帳本同一筆配方算出不同值
severity: minor
blocking: 否
引句:「"consent": consent, "kill_verdict": r0["verdict"], "recipe_id": _kill_recipe_key(prel, cid, nfc(file), old)}」
file: `scripts/lumos:75380-75480`(`_situation_rule_kill` 的 recipe)、`scripts/lumos:75672`
1. 跑殺傷力時傳的配方是 `{"invariant": cid0, "file": kfile, ...}`。`kfile` 是相對平台根的路徑,`cid0` 是試插時的號碼。殺傷力帳本的 `recipe_id` 用這兩個值算。
2. 治理帳事件的 `recipe_id` 改用鎖內重算的 `cid`,和使用者給的 `nfc(file)`(repo 相對路徑)。
3. 平台根不是 repo 根(例如 `android/`),或試插到寫入之間有別人加了條款,兩邊就對不上。計劃寫「配方身分」就是要拿它把兩本帳接起來,現在接不上。

## t6 全部答不適用的表態,不適用列填的壞出處不被核對
severity: minor
blocking: 否
引句:「形狀多驗出處兩欄;specs 給了(名單算得出來、這段沒有段放行)再核出處內容(_kt_sit_spec_problem),」
file: `scripts/lumos:74636-74645`(`_kt_sit_verdict_one` 算名單的條件)、`scripts/lumos:73821`(`_kt_sit_spec_shape` 的 docstring)
1. 對應計劃名單只在 `_kt_sit_has_applies` 為真時才算。作者全答不適用時 `specs=None`,不適用列填的 `spec` 只驗形狀,不查計劃或條款是否存在。
2. 同一份表態只要別列有一列答適用,名單算出來,這列的 `Projects/不存在#S9` 就被擋。
3. `_kt_sit_spec_shape` 的 docstring 寫「答不適用的列一樣驗(填了照樣核對)」,實作是否核對取決於別列。結果不穩,也跟文件不符。

## t7 situation-rule 開跑前的清殘骸會刪使用者用 `--keep-worktree` 留的現場
severity: minor
blocking: 否
引句:「sweep_repo=proot if recipes_override is not None else None) as _iw:」
file: `scripts/lumos:27515`、`scripts/lumos:27553`、`scripts/lumos:42529`
1. `_isolated_worktree_sweep` 會刪系統暫存裡所有 `lumos-kill-*`、超過一天(`_LINT_NEW_STALE_SEC=86400`)的資料夾,不分哪個 repo 或會談建的。
2. `guard kill --keep-worktree` 刻意保留的現場也是這個前綴。兩天後有人跑 `lumos situation-rule`,現場就被無聲刪掉。
3. 原本 `_isolated_worktree` 的 docstring 說 guard kill 不清;現在 recipes_override 一路開了清除,既有行為悄悄變了。

## 附:manifest 與圖譜鏡頭
**manifest(2 條,都是 `open(` 的資源類)**
- `scripts/lumos:75400`(`_tty_reachable`):誤報。它是 `os.open`,下一行就 `os.close(fd)`,失敗走 `except OSError` 回 False,沒有洩漏。
- `scripts/lumos:75466`(`_situation_rule_write`):誤報。`os.fdopen(fd,"wb")` 在 `with` 裡,例外分支會 `os.unlink(tmp)`。只剩 `fdopen` 本身丟例外時 fd 會漏,實際碰不到。

**圖譜鏡頭**
本案沒附固定席節點(鏡頭計算超時,派工詞說不必自己補算),我沒有逐條判節點合約。
我另外讀了 `_spec_gate_ruled_ids` 與規格閘的對應關係。計劃規格 S13、範圍 5 只要求文字雜湊,實作符合,但留下 t1 的洞。

最嚴重 severity: major,blocking 共 1 條。
