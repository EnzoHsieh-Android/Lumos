severity: major

審查席:邊界-sonnet。我讀過整份 diff,並用 python3.14 載入 `scripts/lumos` 對兩條 major 實跑重現。

severity: major
blocking: 是
`scripts/lumos:29532`(`_KillCompile.apply_compile`,經 `scripts/lumos:29494` 的 `probe` 使用)
具體失敗場景:探針(帳上舊的無效候選重驗)在寫入後修改時間沒錯開(`ok` 為假),或 `mstate["unsure"]` 非空時,`apply_compile` 不跑編譯,直接回 `(0, "", False)`。`probe` 把 rc 0 當成「編譯全綠」,對 `ranges` 裡每一行記一筆 `cleared: true`。結果是一個根本沒編過的候選被記成補償,下一次 run 又會挑回它。真正的編譯結果若仍是編不過,下一次又記 invalid,補償與無效來回翻。docstring 只保證這個假綠「不記任何無效」,沒顧到補償這條路。
最小重現:建 `_KillCompile`,令 `c.mstate["unsure"]={"zzz"}`,把 `_kill_run` 換成一被呼叫就丟錯,再呼叫 `probe()`。結果 `on_invalid` 收到 `('g', True)`,而且沒有觸發「compile ran」錯誤,代表編譯沒跑。
引句:「got = self.compile() if ok and not c.mstate["unsure"] else (0, "", False)」

severity: major
blocking: 是
`scripts/lumos:81637`(`_situation_rule_point_target`)
具體失敗場景:新增的行狀態 `exhausted`(同一行全部候選都在跳過集合裡)沒有加進這支函式的訊息字典。對 exhausted 的行跑 `lumos situation-rule --point <檔>:<行>`,`x["status"] != "mutant"` 成立,接著用 `"exhausted"` 去查只有 `None/arid/none/not_unique` 四個鍵的字典,拋 `KeyError: 'exhausted'`。使用者看到 traceback,不是「計劃沒動」的說明。
最小重現:把 `_vault_repo_root`、`_lens_full_sha`、`_choice_range` 換成假的,再讓 `_choice_kill_scan` 回一行 `{"file":"A.kt","line":3,"status":"exhausted","mutant":None}`。呼叫 `_situation_rule_point_target(None,"A.kt:3",None,None)` 後得到 `KeyError 'exhausted'`。
引句:「what = {None: "不是這次範圍裡有選擇點的改到的行", "arid": "是乾節點", "none": "沒有壞法", "not_unique": "不唯一(帶不出唯一的 old)"}[」

severity: minor
blocking: 否
`scripts/lumos:29301`(`_choice_compile_cmd`)
具體失敗場景:規格範圍 1 寫「壞法跨模組就每個模組各一次」,實作只編測試所在模組那一個任務。壞法在測試模組不相依的另一個模組時,編譯錯誤根本不會出現,不記無效,到測試階段才記 no_result(編不過)。docstring 自己註明是刻意的失效開放,但跟條款字面不符。此條沒有重現,屬於規格對照。
引句:「只用測試所在模組那一個任務:壞法所在檔在測試模組不相依的模組時編不到它」

我另外檢查過這些極端輸入,都沒有找到失敗場景:
- `w:` 警告:正規式只收 `e:`,不受影響。
- 截斷、行號 0 或超過檔尾、相對路徑、Windows 路徑:這幾類都落到「對不回,不記無效」。
- 帶引號的 Gradle 任務:合批編譯與合併快篩兩邊都推不出指令而關閉,彼此一致。
- cleared 之後又 invalid:兩邊都取檔內最後一筆。
- 帳上 `blob` 型別不對:被型別檢查略過。

總結:最高等級是 major
