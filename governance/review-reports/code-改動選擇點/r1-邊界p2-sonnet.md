severity: major

## b21 弱證據的 killed 也被當成「決定性結果」,同組其餘測試被略過
severity: major
blocking: 是(判準:違反 `on_row`/`stop_group_on` 自己宣告的合約「killed=沒有弱證據的 killed」,會讓壞法少跑本來能殺掉它的測試,判定從 killed 變 no_result)

引句:「key = "compile_error" if comp else ("killed" if res["verdict"] == "killed" and not why else res["verdict"])」
file: `scripts/lumos:28416`(`_KillHooks.flush`)

- 輸入:某個壞法的第一支守的測試紅了,但那條配方帶弱證據,例如 `_mtime_unsure` 或平台標 flaky,所以 `why` 非空。
- 執行路徑:`flush` 算 key,三元式兩個分支都回 `"killed"`。`verdict == "killed" and not why` 為假時走 `else res["verdict"]`,而 verdict 本來就是 `"killed"`。所以 key 恆為 `"killed"`,在 `_CHOICE_STOP_ON` 裡,`self.stopped.add(group)` 照加。
- 後續:`between()` 把同組其餘測試記成 `skipped`、不跑。`_ChoiceKillRun.on_row` 的 `decisive` 這時正確地把弱 killed 當不決定,不當場判。但略過的列也會進 `on_row`,`len(rows) >= len(order)` 成立後 `finish`。`_choice_kill_judge` 看到沒有強 killed、有 `killed` 弱證據,判 `no_result「killed(修改時間沒錯開…)」`。
- 預期:弱證據不該停組,下一支測試要照跑,可能得到強 killed。實際:後面的測試被略過,壞法在帳上變 no_result,推送閘不認 no_result。
- 重現(臨時副本 `/tmp/lumos-seat-work/code-改動選擇點/邊界p2-sonnet/repo`,腳本 `/tmp/lumos-seat-work/code-改動選擇點/邊界p2-sonnet/t1.py`):

```
python3.14 -I /tmp/lumos-seat-work/code-改動選擇點/邊界p2-sonnet/t1.py
→ weak= True group_stopped= {'A.kt:3'}
```

  餵一列 `verdict=killed`、`_mtime_unsure=True` 的結果給 `_KillHooks(_CHOICE_STOP_ON…).flush()`,`on_row` 收到 `weak=True`,`stopped` 卻含該組。
- 未端到端重現:沒有實際跑 Gradle。

## b22 兩個平台有同名的測試時,配方身分撞在一起,存活被記成「缺結果」
severity: major
blocking: 是(判準:`rid_map` 靜默丟掉一支測試的對應,判定資料損壞,存活的壞法被記成 no_result)

引句:「self.rid_map = {_kill_recipe_id(str(rel), r): (r["group"], (r["platform"], r["test"])) for r in self.recipes}」
file: `scripts/lumos:77797`(`_ChoiceKillRun`)、`scripts/lumos:_kill_recipe_key`(只雜湊 node、invariant、file、old)

- 輸入:計劃條款綁了兩個 kotlin-junit 平台的同名測試,例如 `android:FooTest.x` 與 `shared:FooTest.x`,檔在同一個 repo。
- 執行路徑:`_choice_guard` 以 `(plat, name)` 為鍵,兩支都留。`add()` 為每支組一條配方,`invariant` 是 `f"{loc}|{name}"`,`file`、`old` 也相同,只有 `platform` 不同。`_kill_recipe_id` 不含 platform,兩條 id 相同,`rid_map` 字典推導只剩後一個,`(android, FooTest.x)` 永遠收不到列。
- 預期:兩支各自有列,都 survived 就判 survived。實際:`len(rows) < len(order)`,`finish` 走「缺結果」,判 no_result。若 android 那支其實強殺掉,結果會被後一個映射蓋掉。這與 `_choice_bound_names` 刻意用「平台:名稱」區分同名測試的設計矛盾。
- 重現(腳本 `/tmp/lumos-seat-work/code-改動選擇點/邊界p2-sonnet/t2.py`):

```
python3.14 -I /tmp/lumos-seat-work/code-改動選擇點/邊界p2-sonnet/t2.py
→ recipes= 2 rid_map entries= 1 {…: ('app/A.kt:3', ('shared', 'FooTest.x'))}
→ ('no_result', None, '缺結果')
```

- 未端到端重現:只重現到 id 撞號與判定函式,沒有真的建兩平台設定跑 `choice-kill`。

## 審查範圍說明

- **patch 與 repo 不一致**:`r1-p2.patch` 與 repo 現況(`7826895c1`)不完全相同。後段已把 `killing_test` 改成「平台:名稱」,並加了 `_choice_killing_name` 與 `_choice_test_key`,`rid_map` 與 `flush` 的程式碼則和 patch 相同。上面兩條我都對 repo 現況跑過。
- **`guard kill` 預設路徑**:不傳 `source`、`stop_group_on`、`on_row`、`should_stop` 時,`_KillHooks` 全部短路(`self.on` 為假)。輸出與 rc 不變,兩條 ★INVARIANT★ 不受影響。`skipped` 只在傳了 `stop_group_on` 時才會出現。`_kill_log_rows` 的抽出沒有改欄位與順序。
- **圖譜固定席**:派工尾端的 `LUMOS-LENS` 寫明這次沒附固定席節點(鏡頭計算超時),我沒有自己補算。
- **機械檢查**:`ruff F821`(未定義名稱)對整支 `scripts/lumos` 沒有新增項。
- **沒有標 finding 的路徑**:`--max-seconds` 在配方之間停、Ctrl-C 兩段式、隔離工作樹登記與收掉、`lint-waive choice:` 的鍵換算、`situation-rule --point` 的冪等,我讀過沒找到能舉出具體輸入的錯誤。
- **殘留暫存**:臨時目錄 `/tmp/lumos-seat-work/code-改動選擇點/邊界p2-sonnet` 還在,依派工慣例由編排者收貨後刪。

最嚴重:major;blocking 共 2 條
