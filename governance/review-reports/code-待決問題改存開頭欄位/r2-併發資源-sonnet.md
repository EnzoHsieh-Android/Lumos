severity: minor

這輪修補的主要目標(決策指令拿鎖)成立,但同一族的 `decision-reindex --all` 沒上鎖,文件卻寫成有。我在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r2-併發資源-sonnet/` 的臨時副本做了試驗,沒有改 repo。

1. **`decision-reindex --all` 沒拿鎖,文件卻寫成三支決策指令都拿了同一把。**
   - 派發處 `scripts/lumos:52965` 的 `--all` 分支直接呼叫 `cmd_decision_reindex(env, all_mode=True)`,內部逐篇讀—改—寫,全程沒有 `_vault_write_lock`。只有單節點分支走 `_decision_cmd_locked`。
   - 文件 `docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:114` 寫「decision-add/supersede/reindex … 都拿同一把」,沒有排除 `--all`。
   - 最小重現(race.py,在讀檔和寫檔之間讓另一個程序跑完 `question-add`):`question-add` 回傳 0 並印出 Q1,接著 `reindex --all` 也回傳 0,最後檔案裡沒有 `pending_questions`,Q1 被靜默蓋掉。
   - 修前(`ea9d1ca2`)結果相同,所以不是這次修補造成的。
   - 對照單節點走鎖的路徑:另一個程序等滿 60 秒,印「擋下:等了 60 秒還輪不到寫入…檔案沒動」並回傳 2,逾時訊息和回傳碼正確。
   引句:「寫入鎖 `_vault_write_lock`:set/append/remove、decision-add/supersede/reindex(2026-10-12 起,跟待決問題寫同一份開頭欄位)、question-add/set 都拿同一把」
   佐證:`scripts/lumos:52965`
   歸因:有證據的原有漏查
severity: minor
   blocking: 否

2. **其他仍沒上鎖、會整份重寫開頭欄位的指令,會蓋掉 `pending_questions`。**
   - 我用 grep 找寫 frontmatter 的 `cmd_*`,沒拿鎖的有 `cmd_decision_amend`、`cmd_dref_promote`、`_append_decision_ref`、`cmd_guard_bind`、`cmd_guard_audit`。
   - `_append_decision_ref` 由 rel-cascade confirm 對鄰居筆記呼叫。鄰居是靠 verified_by/plan_refs 連進來的,常是計劃,所以這條路徑會碰到有待決問題的計劃。
   - 最小重現(race2.py):在 `_append_decision_ref` 讀檔後、寫檔前插入一次 `question-add`,結果 `question-add` 回傳 0、`_append_decision_ref` 回傳 True,最後檔案只剩 `decision_refs_ai`,題目不見。修前修後結果相同。
   - `_write_lf` 的註解和文件都承認這些指令是後寫蓋先寫(accepted)。但 `pending_questions` 是這次新增的欄位,等於多了一種被靜默蓋掉的資料,而文件只寫「accepted」,沒寫回頭條件。
   引句:「question-add/set 由呼叫端上鎖(_vault_write_lock);其他寫入指令仍是 last-write-wins(單機 CLI,accepted)。」
   佐證:`scripts/lumos:21256`、`scripts/lumos:21553`、`scripts/lumos:41571`
   歸因:有證據的原有漏查
severity: minor
   blocking: 否

3. **決策指令現在也依賴寫入鎖,鎖被殘留時整支卡 60 秒。**
   - 鎖內除了寫檔,還做了重建整個圖譜 `Env`、`rel_cascade_create`、`cascade_surface` 和 `_drift_print_backrefs`。這 851 篇的圖譜,backrefs 約 0.4 秒、重建 Env 約 0.5 秒,持鎖時間延長有限。
   - 鎖內沒有子程序,也沒有再拿別把鎖,所以沒有死鎖。可重入只對同一程序有效,而這裡沒有跨程序呼叫,所以不成問題。
   - 殘留鎖(程序被 SIGKILL)現在也會讓 `decision-add`/`supersede`/`reindex` 卡 60 秒後回傳 2,以前這三支不受影響。鎖內還會對 stdout 印出內容,管線若被下游卡住,持鎖時間會跟著拉長。這是行為變化,不是錯誤。
   引句:「decision-supersede/add/reindex 單節點那一段:整段在寫入鎖裡;拿鎖逾時也走」
   佐證:`scripts/lumos:53008`
   歸因:有證據的修復回歸(可預期的代價,修前同命令沒有此現象)
severity: minor
   blocking: 否

4. **`_pq_git_read_many` 逾時和 git 失敗共用同一句訊息;其餘行為都正確。**
   - 逾時(`TimeoutExpired`)和非零回傳碼都回 `None`,使用者只看到「git cat-file 失敗」,看不出是逾時。逾時時提醒整批跳過,不會擋推送,影響低。
   - 我用 274 份計劃讀兩個版本(HEAD、HEAD~50),再加上不存在的路徑、含空格的路徑、目錄(tree)和不存在的 rev,共約 560 筆規格:耗時 0.32 秒,記憶體約 67MB,逐筆和 `git show` 抽樣比對(80 筆含全部特例)零錯位。missing 與 ambiguous 不會讓後面的規格讀錯;大小以位元組切片,解析正確。
   引句:「讀不到這次推送的計劃內容(git cat-file 失敗),待決問題的提醒跳過」
   佐證:`scripts/lumos:8053`
   歸因:未判定
severity: minor
   blocking: 否

5. **`t_qfm_decision_add_shares_lock` 只涵蓋 decision-add,不涵蓋 supersede、reindex 和 `--all`。**
   - 我把 `_decision_cmd_locked` 的鎖換成 `nullcontext` 當作拆鎖,連跑 3 次都翻紅(丟失 1 到 3 個回合,例如 `[(2,6,6)]`、`[(0,8,7),(1,7,8),(2,7,7)]`)。所以這支測試抓得到拆鎖,穩定度在這 3 次內是 3 比 3。
   - 還原後綠,耗時約 13.6 秒(它自己給的餘裕是 13 倍)。
   - 但三支指令共用同一個包裝函式,若有人把 supersede 或 reindex 拆出去,沒有測試會紅。`--all` 的缺口(第 1 條)正是這個死角。
   引句:「① 八個決策加八個題目同時寫(三回合):每回合全部都在」
   佐證:`scripts/test_lumos.py:56422`
   歸因:有證據的原有漏查
severity: minor
   blocking: 否

**三問**
- ① 原問題的行為證據:8 個 decision-add 加 8 個 question-add 同時跑 3 回合,修後全部保留。拆鎖後 3 次都有丟失,等於證明修補確實是在補這個洞。
- ② 相鄰呼叫路徑:鎖逾時走「擋下:」並回傳 2,成立。單節點 reindex/supersede/add 的輸出協議和回傳碼沒變。不成立的有兩處:`--all` 分支沒鎖(第 1 條),其他寫 frontmatter 的指令也沒鎖(第 2 條)。
- ③ 新發現的同一案例,修前與修後都是靜默丟題且回傳 0:`reindex --all` 與 `_append_decision_ref` 在修前(`ea9d1ca2`)和修後(`c0265db0`)結果相同。第 3 條在修前不卡,修後殘留鎖時卡 60 秒。

總結:這輪修補把決策指令的鎖補上了,沒有看到死鎖或持鎖過長,但 `--all` 沒鎖而文件說有,另有幾支會蓋掉 `pending_questions` 的指令沒鎖,都不阻擋合併。
