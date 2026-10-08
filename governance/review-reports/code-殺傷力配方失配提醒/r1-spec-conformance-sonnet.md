severity: minor

# 殺傷力配方失配提醒 代碼審 r1 — 實作是否照計劃條款(spec-conformance-sonnet)

做法:在 `git clone --shared` 的 clone 裡取 51f83721..bd637de7 的 diff,逐條對 S1–S7 與〈做法〉1–5;實跑 `t_guard_kill_add_warns_drifted_recipe`(21 過)、`t_doctor_kill_recipe_drift`(20 過)、`t_guard_kill_rm`(17 過)、`t_kill_recipe_check_matches_guard_kill`(49 過);另外用合成 repo 手跑 kill-add / kill-rm / doctor P2 的邊角。

逐條結論:
- S1/S2:提醒只在標準錯誤多一行、標準輸出與 rc 不變、判重擋下不印、只更新 covers 驗既有那條(`recipe = r`)、設定壞/平台不在/平台根找不到印「沒驗原文」。符合。
- S3/S4:P2 各狀態各列一條、`warn_soft` 不動 rc、`--ci` 才落 `check-p2`、`_KNOWN_GATES` 已登記、兩種「全對得上/沒有配方」字面正確、設定錯誤字面「設定檔讀不了:」與兜底「這一段算不出來」分開、平台根找不到只列一條。符合。
- S5:對照測試格子涵蓋計劃列的全部題目(含子模組、迴圈、經 `wt` 爬回、解析到 repo 頂),且每格獨立 repo,真跑 guard kill 對照全綠。
- S6:kill-rm 長度 8 以上十六進位(大小寫都收)、零條/多條不同身分 rc2、重複同身分一起移、移除前印每條完整內容與 kill-add 範本、`[kill:recipes]` 標記逐 KEY 行處理(實跑:同 KEY 兩條配方先移一條標記保留、移第二條標記拿掉)、移光整欄拿掉。符合。
- S7:diff 內沒有任何 hunk落在 `cmd_guard_kill` 本體(`def cmd_guard_kill(` 在 diff 裡 0 筆),符合。
- 範圍外改動:kill-add 判重擋下那句改指向 kill-rm(〈實作紀錄〉已申報)、`--file` 說明字串改(計劃〈誠實界線〉已列)、skill 三處落點與 HELP_WHEN。沒看到未申報的行為改動。
- 已申報偏離(HEAD 的 ls-tree、不設 40 次上限、斜線結尾判 missing、Check T 崩潰不處理等)我沒當 bug 報。

以下三條都只是字面/邊角不一致,沒有判斷錯誤、沒有誤報漏報。

## F1 kill-add 對「路徑以斜線結尾」的提醒字面跟實際 guard kill 結果矛盾
severity: minor
blocking: 否
引句:「msg = f"{f} 讀不到({res['detail']});guard kill 跑到它會判 drifted 或讀檔出錯。{fix}"」
佐證行:file: `scripts/lumos:13203`(`_kill_add_warn` 的 missing/undecodable 分支)
1. 重現:`lumos guard kill-add Systems/Limit 上限恆為5 --file prod.py/ --old "LIMIT = 5" --new y`,標準錯誤輸出:`⚠ 提醒:prod.py/ 讀不到(路徑以斜線結尾(guard kill 套得上壞法、還原會失敗,判 error));guard kill 跑到它會判 drifted 或讀檔出錯。修法:…`。
2. 括號裡說「判 error」,同一行後半又說「會判 drifted 或讀檔出錯」,而且「讀不到」本身也不符:檔其實讀得到。〈實作紀錄〉已申報這個狀態仍歸 missing、細節照實寫,但 S1 的字面是「照狀態」,套用到這格後前後兩句互相打架,讀的人會困惑。
3. 建議:`_kill_judge_file` 的斜線結尾格式獨立一個提醒字面(或讓 detail 自帶完整句,不再套 missing 模板)。

## F2 P2 對格式壞的配方顯示「::配方欄位格式不對」,「平台:file:細節」三欄裡前兩欄是空的
severity: minor
blocking: 否
引句:「st["items"].append(([stem], f"{rel} → {res['plat']}:{res['file']}:{detail}"」
佐證行:file: `scripts/lumos:13261`(`_kill_p2_one`)
1. 重現:note 的 `kill_recipes` 放 `[{"file":3}]`,跑 `lumos doctor`,P2 列出 `Systems/Limit.md → ::配方欄位格式不對(合約片段:;修法:lumos guard kill-rm Systems/Limit --id 684d6633cff7)`。
2. malformed 時 `plat`、`file` 都是空字串(`_kill_recipe_judge` 一開頭的預設值),所以套同一個格式印出 `::`、「合約片段:」後面也是空。計劃〈做法〉5 的格式是「節點 → 平台:file:狀態細節」,字面上沒錯,但 malformed 這格印出來是亂碼感。修法:malformed 時只印 `節點 → 配方欄位格式不對(…)`。

## F3 設定檔讀不了時,P2 的輸出取決於配方順序:前面已收集的條目會被整批丟掉,或根本不顯示「設定檔讀不了」
severity: minor
blocking: 否
引句:「return {"cfg_err": st["ctx"]["cfg_err"], "items": [], "total": st["total"]}」
佐證行:file: `scripts/lumos:13233`(`_kill_p2_scan`)
1. 重現(`.lumos/config.json` 寫 `{bad`):
   - 筆記只有一條格式壞的配方 → P2 列「有 1 條…::配方欄位格式不對」,完全沒提設定檔讀不了(因為 malformed 在 `_kill_recipe_judge` 檢查 cfg 之前就返回)。
   - 筆記是「格式壞配方 + 一條好配方」→ P2 只印「設定檔讀不了:…」,先前收集到的 malformed 條目與其他篇「解析不了」的條目被 `items: []` 丟掉。
2. 同一份壞設定,輸出因配方順序而不同。S4 的字面是設定錯誤時印「設定檔讀不了:<原因>」,上面第一種情形沒印;第二種情形則吞掉了 S3 說應各自列出的條目。不是誤報漏報(都是只提醒),所以只標 minor。建議:一律先判 cfg_err,有就整段只印那一句;或不丟已收集的 items。

最高等級:minor
