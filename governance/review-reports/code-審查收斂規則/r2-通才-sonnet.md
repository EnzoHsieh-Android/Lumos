severity: major

我把主審差異和主程式改動讀完了,也在拋棄式 git repo 裡實測了 pitfalls 的殘留分級。以下 2 條 finding,其中 1 條 blocking。

severity: major
blocking: 是 — 殘留分級對縮排式測試方法靜默放行,既有的「改到殘留守的測試檔就升 high」被削弱
引句:「if ln.startswith(("+", "-", "@@")) and rx.search(ln):」
問題:這次修補把綁定測試所在的檔改成「diff 要碰到綁定測試名才算」(`_residual_diff_touches`)。它用 `git diff -U0` 的增刪行和 hunk 標頭找測試名。git 預設的 hunk 標頭只會抓行首就是字母的行,所以縮排的方法名進不了標頭。測試方法縮排在 class 裡的語言(Kotlin、Java、Swift、Dart、class 式 pytest),改方法本體時,增刪行不含方法名,標頭只顯示 `class FooTest {`,結果判成沒碰到。改前這支檔整檔都算命中,所以這是退步。
具體失敗情境:合約綁 `guardWorks`,[residual:] 已記,索引的 `tests` 是 `["guardWorks"]`。有人只把方法裡的 `assertEquals(1, a)` 改成 `assertEquals(9, a)` 來弱化測試,`_pitfall_tier` 不會升 high,推送不用過代碼審。
實測:一個 Kotlin 測試檔和一個 class 式 pytest 檔,索引都列了 `tests`。我只改方法本體再呼叫 `_residual_tier_hits("…","HEAD~1..HEAD")`,回傳 `{}`。同一段 diff 的 hunk 標頭是 `@@ -7 +7 @@ class FooTest {` 和 `@@ -4 +4 @@ class TestFoo:`,都沒有測試名。只有頂層 `def t_xxx` 的 test_lumos.py 不受影響,所以現有 138 個 residual 測試全綠,測不到這個洞。
佐證:``file: `scripts/lumos`(`_residual_diff_touches` 與 `_residual_tier_hits`,對應 patch 的 `_residual_diff_touches` 段)``

severity: minor
blocking: 否 — 被擋下的指令仍會改寫檔案,而且訊息不提
引句:「_residual_reindex_tail(env, "沒有這個標記")   # 上次寫一半(合約行已拿掉、索引沒更新)時,照提示重跑就補好」
問題:`guard residual --remove` 找不到標記時回 2「擋下…沒有東西可拿」,但先重寫了 `governance/residual-index.json`。「已經有了」那條路也一樣,回 0 前先重寫索引。輸入打錯字的指令因此在 git 工作樹留下未提交的索引改動,而且索引寫失敗的回傳值被丟掉。這個檔是 pitfalls 分級讀的,併發會談看到未預期的改動會困惑。
具體失敗情境:使用者 `--remove` 打錯指標,指令回 2。`git status` 多出一個沒要求的 `residual-index.json` 改動,可能夾進之後的提交。
佐證:``file: `scripts/lumos`(`_cmd_guard_residual_locked` 的 `--remove` 找不到標記分支)``

已讀,無 finding:
- guard audit 與 kill-add 改用 `_contract_locate`:`_kill_find_contract` 已先要求 INVARIANT_RE 命中,後面的 `.group(1)` 不會是 None。擋下訊息只多了 `_esc_clean` 和 200 字截斷。`-k kill_add` 與 `-k guard_audit` 共 95 個測試全綠。
- `discover_test_methods` 改用 `_strip_test_comments`:剝法逐字搬移,python 仍是 "none"。
- `_pq_decision_state` 抽出 `_pq_decision_target`:`#dN`、帶路徑、短名撞名、missing 四條路行為一致。
- `cmd_contracts` 的新增輸出行:`-k contracts` 24 個全綠,輸出只在有殘留時多一行。
- doctor 其他段落:只在殘留段多接一個回傳值。
- `_residual_tier_hits` 回傳型態從 list 改 dict:它唯一的呼叫端 `_pitfall_tier` 已同步改好。

最高等級 major,blocking 共 1 條。
