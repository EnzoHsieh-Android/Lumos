# 前置掃描:殺傷力配方修補體驗_計劃(只讀)

程式位置:`scripts/lumos`(`_kill_add_template` 約 13484、`cmd_guard_kill_rm` 約 13512、`cmd_guard_kill` 約 13735、argparse 約 40733)、`scripts/test_lumos.py`(`t_guard_kill_rm` 約 60522)。

## ① 未定義的詞
- 命中:「P2」。原句:「照 P2 列出的 10 條」「原文對得上的配方 P2 不列」。本篇沒說 P2 是 doctor 的哪一段(實為 `lumos doctor --verbose` 的 P2 段,定義在〈殺傷力配方失配提醒_計劃〉)。改法:首次出現處加一句「doctor 的 P2 段(逐條數失配配方)」。
- 命中:「S7 字面」。原句:「`t_kill_recipe_check_matches_guard_kill` 的 S7 字面」。S7 是別篇計劃的條款,本篇沒解釋。改法:改寫成「drifted/開檔失敗/逃逸三句說明字面」。
- 命中:「原文開頭」「完整內容」。原句:「逐條印一行『短身分(前 12 字元)、平台、檔、原文開頭、test』」。「原文開頭」取幾個字沒定;「完整內容」指 kill-rm 印的整條 JSON,沒解釋。改法:寫明截幾字(例:前 30 字,經 `_kill_show`),「完整內容」註明是 `要移除的配方(完整內容):` 那行。
- 命中:「第 2 條、第 3 條、1、4」(rtb 回報編號)只在〈依據〉有對照,〈範圍〉用「做 2、3」。可接受,但〈範圍〉建議直接寫功能名。
- 命中:「健康檢查」(指 doctor P2 還是別的?)。原句:「健康檢查列出真跑沒抓到的配方」。改法:改「doctor P2 段」。

## ② 壞引用
找得到:`_kill_add_template`、`_kill_recipe_id`、`_kill_show`、`cmd_guard_kill_rm`、`t_guard_kill_rm`、`t_kill_recipe_check_matches_guard_kill`、`t_guard_kill*`(`t_guard_kill`、`t_guard_kill_rc_precedence`、`t_guard_kill_json_purity`、`t_guard_kill_attribution`…)、`Systems/guard-kill`、`Projects/殺傷力配方失配提醒_計劃`、`Projects/漂移防治路線圖_計劃`。
- 壞引用:無。
- 還沒寫的 [test:](單獨列出,不算壞引用):`t_guard_kill_rm_lists_ids`、`t_guard_kill_prints_recipe_id`(grep 全 repo 零筆)。`t_guard_kill_rm` 存在。
- 外部引用(rtb 提交 c531ac7、rtb 的 `Issues/存量筆記漂移等工具修復`)不在本 repo,無法驗,屬〈依據〉出處,不算壞。
- 漏列:本計劃沒提要同步的文件——`Systems/guard-kill.md` 第 70 行(寫 `kill-rm <node> --id <短身分>`)與第 101 行(「範本(原文留給人照現在的程式填)」)、`skills/lumos-project-notes/commands/06-代碼審與推送.md` 第 24 行、`scripts/lumos` 約 40238 的 kill-rm 提示字串與 argparse help。lands_in 只寫 guard-kill;skill 檔不在內。

## ③ 範圍自相矛盾
- 未命中硬矛盾。檢查:〈範圍〉不做「guard kill 的判法、回傳碼、--json 內容」,〈做法〉只動人讀行,一致。
- 軟矛盾(命中):開頭「只做 2、3 兩件小事」,〈範圍〉「做」卻列三項(範本、kill-rm 列出、guard kill 行尾 id)。原句:「這份計劃只做 2、3 兩件小事」。改法:寫成「第 2 條(範本)與第 3 條(短身分,含 kill-rm 列出與 guard kill 行尾)」。
- 軟矛盾(命中):RETIRE-IF 稱「本計劃第二條(kill-rm 不帶 --id 列出)」,但〈做法〉第二項才是它、而〈範圍〉第二項是 kill-rm 列出,編號不明。改法:不用序號,直接寫功能名。

## ④ 機械宣稱驗語意
1. 「`_kill_add_template` 的 `--new` 一律印 `'<照新原文改寫的壞法>'`」前提「現在是抄舊壞法」:屬實。現況 `"--new", val("new", "'<壞法>'")`,舊配方 new 合法就原樣 shlex.quote 印出;`--old` 現況已是固定 `'<照現在的程式填原文>'`(PRIOR-ART 說「照 kill-rm 既有」成立)。
2. 「完整內容那一行仍應印出舊壞法」:屬實。`_kill_rm_show` 先印 `json.dumps(r)` 完整內容,再印範本;兩者同函式印。
3. 「`--id` 改成選填」:現況 argparse 是 `required=True`(約 40735),`dest=gkr_id`;`cmd_guard_kill_rm` 開頭 `re.fullmatch(...)` 對 None 會變 "" → 擋 rc2。實作要改三處:argparse、`cmd_guard_kill_rm` 開頭驗證要在 rid 為 None 時分流、並且分流必須在 `_vault_write_lock` 之外或另走唯讀路徑(計劃沒說列出時要不要拿寫入鎖;既有 kill-rm 讀—改—寫整段拿鎖,而列出是唯讀)。
4. 「整欄解析不了照既有擋下回 2」:屬實。`_guard_kill_rm_locked` 對 `load_raw_for_edit` 失敗與 `_kill_read_recipes` 回 None 都 `擋下 … return 2`。「找不到筆記回 2」也屬實(在 `--id` 驗證之後;不帶 id 時順序要重排)。
5. 「沒有配方就印一句…」:`_kill_read_recipes` 沒有 kill_recipes 欄回 `([], None)`,可分辨,屬實可行。
6. 「格式壞的配方也應列出且身分可直接拿去 --id 移除」:`_kill_recipe_id` 對格式壞的元素(非物件、invariant/file/old 非全字串)走 `sha256(["malformed", node, elem])`,kill-rm 現用同函式,屬實。但計劃〈做法〉沒說格式壞的元素列哪些欄(非 dict 沒有 平台/檔/原文)。改法:補一句「不是物件的元素印原樣 JSON 經 `_kill_show`」。
7. ★重大:「guard kill 結果行尾加 ` id=<短身分>`(同一支 `_kill_recipe_id`)」且「每筆結果本來就有完整 `recipe_id`」:後半屬實(蓋章迴圈對每筆 result 都寫 `recipe_id`,`--json` 已輸出)。但那個值是 `_kill_recipe_key(str(rel), res.get("invariant"), res.get("file"), res.get("old"))`,不是 `_kill_recipe_id`。`_kill_recipe_id` 只在 invariant/file/old 都是字串時才委派給 `_kill_recipe_key`;格式壞的配方(缺 old、file 為數字、invariant 缺…)兩者結果不同:key 把 None/數字直接進 json,id 走 "malformed" 雜湊。而且 result 是 `{**r, platform, verdict, …}`,事後無法從 result 還原原配方元素(多了欄位),所以行尾若用 `_kill_recipe_id(rel, result)` 也算不對。〈條款〉S3 的「該短身分拿去 kill-rm --id 應對得到那一條」對格式壞的配方會失敗(例:old 缺、被判 drifted 的配方,guard kill 仍會產出結果)。改法二擇一:(a) 在 `cmd_guard_kill` 建 results 時、`{**r…}` 之前用原配方 r 算 `_kill_recipe_id` 存旁路(不進 `--json`,參照 `_logged` 被濾掉的作法);(b) 條款限縮成「格式正常的配方」並明寫格式壞的不保證。另:`--json` 的 `recipe_id` 欄不要被改成 id,否則「`--json` 內容跟改動前相同」破功。
8. 「guard kill 的人讀輸出那行長怎樣」:現況 `f"{icon} {verdict:<9} {invariant[:30]} [{test}] {detail}"`(約 13990 一帶),`detail` 在行尾、可能很長或空;行尾附 ` id=` 在 detail 空時行尾是 `] ` + id,detail 含換行就 id 跟著斷。〈條款〉S3「每條結果行附」要說清楚 detail 後面還是前面。建議放 `[test]` 之後、detail 之前,避免 detail 吃掉。
9. 「`--json` 純度……只動人讀那支」:屬實,`as_json` 分支各自印,人讀在 else。
10. 既有測試比對:
   - 「`t_guard_kill_rm` 的『印出可照填的 kill-add 範本』斷言要改(不再找舊壞法在範本裡)」:★不精確★。②那條斷言是 `"lumos guard kill-add Systems/Limit" in r.stdout and "--covers java-concurrency" in r.stdout`,沒有任何斷言找舊壞法(`XX_BROKEN = 1` 在該測試區段 grep 零筆)。它不用改;要新增的是 S1 的反向斷言(範本不含 `XX_BROKEN`、完整內容仍含)。真正比對範本內容的只有 ②(`lumos guard kill-add Systems/Limit`、`--covers java-concurrency`)與 ⑥b(`note 含控制字元`),三者在改 `--new` 後都不受影響。②的「LIMIT = 5」「上限失守」在完整內容那行,也不受影響。
   - guard kill 結果行字面:測試只用 `in r.stdout` 子字串(`killed_unattributed`、`filter`、`咬得住`、`弱`、`逃逸`、`未提交變更`、`? timed_out_weak` 否定),沒有整行相等或 endswith;S7 的三句說明字面(`old 命中 0 次…`、`file 開不了:`、`file 路徑逃逸 worktree(圍欄擋下)`)是從 `--json` 的 detail 讀,不受人讀行影響。唯一要小心:`worktree 無殘留` 檢查 `r.stdout.strip().count("\n") == 0`(約 20445 一帶),人讀行要保持單行(含 id 後仍單行,OK)。計劃點名「t_guard_kill*」是對的,但實際不必改既有字面,風險比計劃寫的小。
   - 另有 `_` 文件守衛測試(約 25180)對 `cmd_guard_kill` 原始碼抽 `verdict` 值域:新增 id 變數若寫成 `verdict = …` 以外不影響;別在函式體內新增 `"verdict": "…"` 字面。
11. 回退節:「revert 之後 kill-rm 回到 --id 必填」屬實(現況 required=True)。
12. PRIOR-ART「列出時人寫的欄位照既有 `_kill_show` 跳脫」:`_kill_show` 會加 JSON 引號(`"…"`),完整內容那行用的是 `_kill_esc(json.dumps(...))`。兩者都能擋控制字元,計劃選 `_kill_show` 可,但輸出會帶引號,條款 S2 的測試要預期引號。

## 結論
硬傷 1 個:④-7(guard kill 行尾 id 與 `_kill_recipe_id` 對格式壞配方不一致,S3 後半句不成立)。不精確 1 個:④-10(t_guard_kill_rm 沒有斷言舊壞法)。補強:③ `--id` 選填要改 argparse、驗證順序、鎖;②同步 guard-kill.md 70/101 行與 skill 06 檔第 24 行。
