severity: major

審查席:通才-sonnet。範圍:`65c3520ca..cd73126da`,我讀完整份 diff,並到 `scripts/lumos` 對照呼叫端。鎖檔 `…1316.json.warming` 不存在,沒有動它。

白話先講:新功能讓「存活」的判定可以不重跑測試就沿用上次的紀錄。但原本防止「測試檔位置查不到時誤沿用」的那道保險,在新路徑上沒有補回來。

severity: major
blocking: 是
`scripts/lumos:79177-79180`(`_choice_kill_pick` 新增的 via cov 分支),同根因還有 `scripts/lumos:80101` 附近的 `_choice_reach_valid`。
引句:「+            if cov_sha_of is not None and evs[-1].get("cov_sha") == cov_sha_of(x):」
- 被改掉的行為:舊的 `disp == "survived" and evs[-1].get("tests_sha") == tests_sha and _CHOICE_TESTS_UNKNOWN not in str(tests_sha)` 明寫「雜湊帶不明標記就當成變了、survived 也重跑」(代碼審 r2 H1)。
- 新分支走 `cov_sha` 比對,沒有任何不明標記的判斷。`_choice_cov_sha` 把 `tests_sha`(尾端帶不明標記)與 `oids.get(file, 不明)` 直接雜湊進去,連兩次都是不明時值一模一樣。
- 場景:某支守的測試的所在檔找不到,或時限內沒查完,`_choice_tests_sha` 尾端就帶 `_CHOICE_TESTS_UNKNOWN`。第一次跑,某行被依覆蓋判成存活,事件帶 `cov_sha=X`。使用者補強測試後再跑,測試所在檔仍是不明,算出來還是 `X`,所以那一行被帶過去、不重跑,帳上仍是存活。
- 同樣的缺口讓 `_choice_ledger_status` 的 `_choice_reach_valid` 把這種過時的 reach 當有效,印出「經過 … 未判讀」。
- 最小重現(實跑,在臨時目錄用 python3.14 載入 `scripts/lumos`):
  - `_choice_kill_pick(res, {key:[{"verdict":"survived","via":"cov","cov_sha":"S","tests_sha":"cov:h"+U}]}, set(), set(), "h"+U, None, cov_sha_of=lambda x:"S")` 回傳的第二個值 `carried` 是 `{('a.kt','fp1'): 'survived'}`。
  - 同樣是 `h+U` 的舊路徑(`via` 是 run)回傳 `{}`,也就是會重跑。
  - 修法方向:carry 與 valid 兩處都加「`_CHOICE_TESTS_UNKNOWN in` 守的測試雜湊或所在檔 blob 就不算同」。
  - 測試缺口:`t_choice_cov_carry` 只比 cov_sha 相同與不同,沒有不明標記的案例。

severity: minor
blocking: 否
`scripts/lumos`,`_KillPrep._measure` 的 `todo = cb.cached()` 與 `_CHOICE_COV_ANALYZE`。未能重現(沒有真 Gradle)。
引句:「+        todo = cb.cached()」
- 場景:同一個 at_sha 中斷後再跑,所有測試的 exec 都在續跑快取裡,`todo` 為空,一支測試都不跑。
- guard-kill 每次都建新的隔離工作樹,這棵新樹沒有 `build/tmp/kotlin-classes`。分析腳本 `lumosCovAnalyze` 沒有 dependsOn 編譯,會讀不到任何類別檔。
- 結果是每個壞法行的 `total` 都是 0,全部落進 `nolines`,記成「這一行沒有指令紀錄」。這個原因不在 `_CHOICE_REACH_TEMP`,所以 `--reach-only` 不會重補。
- 這是 S6 續跑快取的主要用途,假 Gradle 看不出這個問題(測試只驗了「前 2 支取快取、第 3 支以後再量」的部分快取情況)。
- 建議:全部命中快取時先確認類別目錄存在,不然記暫時性原因;或讓分析任務依賴編譯。

severity: minor
blocking: 否
`scripts/lumos`,`_ChoiceKillRun.reach_done`,影響 `_choice_kill_report` 寫的 run 事件。
引句:「+        self.stats["survived"] += 1」
- 依覆蓋判存活時只加 `stats`,不加 `self.judged`。
- 規格閘的筆記白紙黑字寫「run 那筆多 merged、single(相加等於這次判定數)」,而 `ran = sum(kr.stats.values())`。
- 例如一次跑 3 個壞法,其中 1 個被 none 跳過:`ran=3`,`merged+single=2`。
- 讀者(gov)沒拿它們相加,所以不會壞,但筆記的不變式不再成立,`judged` 的分類也少了 cov 一種。

severity: minor
blocking: 否
`scripts/lumos`,`_choice_reach_cur`(choice-points 用)與 `_choice_kill_cov.cov_sha_of`(choice-kill 用)。
引句:「+    return {k: _choice_cov_sha(tsha, oids.get(k[0], _CHOICE_TESTS_UNKNOWN), v) for k, v in new_sha_of.items()}」
- 重用:兩處各自重算「守的測試雜湊、tree oids、cov_sha」,邏輯是複製的。choice-kill 與 choice-points 兩邊 `cov_sha` 一旦不同步,reach 就會被判成無效。
- 效率:`_choice_ledger_status` 只要 `reach_out is not None` 就先算 `_choice_reach_cur`,即使沒有任何存活行也先跑一次 `git grep`。`_choice_kill_cov` 在沒開覆蓋(`cov_plats` 為空)時仍呼叫 `_choice_tree_oids` 和 `_choice_tests_sha`,但規格寫「沒開覆蓋時行為同原本」。
- 建議:抽共用函式,並且只在有存活行、或確實開了覆蓋時才算。

severity: minor
blocking: 否
`scripts/test_lumos.py` 的 `_CKC_GRADLE`,對應 `scripts/lumos` 的 `_CHOICE_COV_INIT` 與 `_CHOICE_COV_ANALYZE`。
引句:「+_CKC_GRADLE = _CKM_GRADLE.replace("\nnote(\"start\")\n", "\n" + _CKC_JX + _CKC_ANALYZE + "\nnote(\"start\")\n" + _CKC_COV, 1)」
- 假 Gradle 完全不讀兩份 Groovy 腳本,只認 `--init-script` 的檔名與 `lumosCovAnalyze` 這個任務名。
- 把 `includeNoLocationClasses = true` 拿掉,或把分析腳本的行範圍寫錯一格,測試全綠;只有計劃裡的 S12、S18 真機實跑才會紅。
- 這是這個設計固有的限制,不是投稿的疏漏。但它保護的是「Robolectric 覆蓋不全 0」這個必要行為,審查結論上要記一筆。

沒找到會出錯的項目(逐項走過,供去重參考):
- 呼叫端:`_choice_kill_ledger` 多回一個 aux、`_choice_ledger_status` 與 `_choice_points_lines` 多參數,只有 `cmd_choice_kill` 與 `cmd_choice_points` 兩個呼叫端,都已同步。
- `_kill_merge_singles` 縮成一行呼叫共用函式後,`stop` 與 `remaining` 都有傳,原有行為都在。
- `--max-mutants` 預設改成 None 後,在 `cmd_choice_kill` 內補回預設值。
- `prep.run` 丟 `_KillHalt` 時,外層有 `except _KillHalt` 接住。
- `prep_only` 的 `continue` 不會破壞後面的結果蓋章。
- `_choice_ledger_status` 新增的 `_choice_test_blobs` 呼叫內部走 `_lens_git_dl`,不會多丟例外。

圖譜固定席判定:機器沒附固定席節點,我讀 `lens.txt` 與 `Systems/guard-kill.md`、`Systems/規格閘.md` 的 diff 對照。
- `guard-kill.md` 的兩條 INVARIANT(rc 優先序、`--json` 成功路徑 stdout 恰一行 JSON)沒被碰到:新碼的診斷訊息都走 stderr,`prep=None` 時控制流與原本相同。
- 兩篇筆記新增的 WHY、PITFALL 與 responsibility 與程式行為一致,只有上面「merged+single 相加等於判定數」那句在 cov 路徑下不成立(第三條 minor)。

總結:最高等級是 major(`_choice_kill_pick` 的 cov 帶過去分支漏了不明標記的守衛,已重現)。
