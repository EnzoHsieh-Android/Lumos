severity: major

## z1 殺傷力驗證只處理 Ctrl-C,SIGTERM 和 SIGHUP 會留下孤兒測試程序
severity: major
blocking: 是
引句:「測試開在自己的 session(start_new_session),終端的 Ctrl-C 送不到它:收掉整個程序群組再往上丟」
file: `scripts/lumos:27580`(`_kill_run`),`scripts/lumos:41414`(整支 lumos 只有 lint 的工作樹在別處裝了 SIGTERM 處理,`situation-rule` 這條路徑沒有)
file: `docs/lumos-toolchain-knowledge/Projects/情境題答案要引規格出處與回寫循環_計劃.md:93`(規格自己寫「超過對話裡跑指令的上限」)

失敗場景:
1. 在對話裡跑 `lumos situation-rule`。規格第 93 行說 Android 的 Gradle 基準加壞法要十幾分鐘,會超過對話裡跑指令的上限。
2. 對話工具逾時,或終端關閉,對 lumos 送的是 SIGTERM 或 SIGHUP,不是 SIGINT。Python 預設直接結束,不會丟 `KeyboardInterrupt`。
3. 新加的 `except KeyboardInterrupt` 走不到,`_kill_proc_group` 沒被呼叫。測試程序在自己的 session,所以不受影響,繼續跑。
4. `_isolated_worktree` 的 finally 也沒跑。隔離工作樹留在 `$TMPDIR/lumos-kill-*`,要等下次 `sweep_repo` 清,門檻是 `_LINT_NEW_STALE_SEC`(一天)。
5. 結果是 Gradle 這類十幾分鐘的測試在背景繼續吃 CPU 和記憶體,使用者看不到。

最小重現:在乾淨 clone 裡用 `SourceFileLoader` 載入 `scripts/lumos`,啟動 `m._kill_run("sleep 4242", "/tmp", 600)`,6 秒後送訊號。
- 送 SIGINT:輸出 `KI`,`pgrep -fl "sleep 4242"` 沒有殘留,補丁在這個路徑有效。
- 送 SIGTERM:`pgrep` 仍列出 `75815 sleep 4242`,測試程序成了孤兒。

測試只覆蓋 Ctrl-C,抓不到這個缺口(`r1-tests.patch:1189-1234`)。

## z2 規格閘每份計劃都整本重讀治理帳,沒有沿用既有的 ctx 快取
severity: minor
blocking: 否
引句:「new = new - _spec_gate_ruled_ids(_vault_repo_root(env), rel, text)」
file: `scripts/lumos:14563`(呼叫處),`scripts/lumos:23524`(`_gov_vc_gate_events` 用 `limit=None` 整檔讀入再切行)
file: `scripts/lumos:17254`、`scripts/lumos:17291`(`_expected_push_one` 逐份計劃呼叫 `_expected_requirement`,而 `signoff` 帳在同一處已用 `ctx["exp_gov"]` 只讀一次)

失敗場景:
1. 推送範圍帶出 N 份有「新行為條款」的計劃,例如範圍大時 `_spec_gate_push_candidates` 一次回幾十份。
2. 每份都走到 `_expected_requirement` 的 `if new:`,再整本讀一次 `docs/.governance-log.jsonl`,連一筆 `situation-rule` 都沒有也一樣讀。
3. 實測此 repo 的治理帳是 22 MB、125,521 行,一次呼叫 0.42 秒,尖峰記憶體約 50 MB。
4. 10 次連續呼叫共 4.2 秒。50 份計劃約 21 秒,全花在讀同一本沒變的帳上,而且是在推送前掛鉤的路徑上。
5. 單份計劃跑 `spec-gate` 本身只讀兩次(`16222` 和 `16258`),約 0.8 秒,可以接受。

不是會壞的行為,是在大範圍推送時多出的時間。

## 附:manifest 與圖譜鏡頭

manifest 兩條都判誤報:
- 第 75400 行 `fd = os.open(..."/dev/tty"...)`(`_tty_reachable`):下一行就是 `os.close(fd)`,中間沒有可能丟例外的敘述,確定關閉。誤報。
- 第 75466 行 `fd = os.open(str(tmp), ...)`(`_situation_rule_write`):緊接著 `os.fdopen(fd, "wb")` 放進 `with`,離開時確定關閉。`except BaseException` 會 `os.unlink` 暫存檔,連 `KeyboardInterrupt` 也涵蓋。唯一漏洞是 `fdopen` 自己失敗,實務上不會發生。誤報。

圖譜固定席:鏡頭計算逾時,這次沒有附固定席筆記,也沒有「圖譜沒有釘到節點」的備援段,所以不逐條答。我只確認了一件相關的事:`_impact_home_map` 對記憶體圖譜多帶 env 的記憶化,是獨立的分支,磁碟圖譜的鍵沒變,沒有改變熱路徑的行為。

本案特定鏡頭,逐項實測或讀碼結果:
- **名單只算一次**:`_kt_sit_verdict_one` 兩處呼叫 `_kt_sit_spec_names`,第二次命中 `cache["spec_names"]`。失敗也快取,不會重試。
- **盲判指令各算一次**:`_kt_bj_specs` 的 cache 是新的 `{}`,模板和寫入驗證各自重算一次。這是每個指令一次,不是每份核對多次。
- **名單耗時**:此 repo 範圍 `HEAD~15..HEAD` 算出 201 份計劃、1,112 條條款,共 145,177 字,耗時 2.5 秒,峰值 46 MB。超過 80,000 字,所以縮減路徑在真資料上會走到。
- **deadline 已用完仍能算出**:樹圖建構的 deadline 被 `max(1, …)` 墊成 1 秒,但 1,037 篇筆記的 `_drift_cat` 只要 0.08 秒,餘裕足夠。
- **gov --stats**:對 125k 行的帳跑 3 秒。補丁的新增部分是對已載入的 rows 做線性掃描,不另外讀檔。
- **`_kill_run` 的 Ctrl-C 處理對其他呼叫端**:合約測試閘(`73114`)在執行緒池裡,`KeyboardInterrupt` 只會進主執行緒,不經過這段。`72903` 的探針路徑現在 Ctrl-C 也會收掉程序群組。`guard kill` 原呼叫端的資源收尾沒有變壞,只多了收程序群組這一步。
- **殘骸清理的誤清風險**:`sweep_repo` 的門檻是一天,不會清到其他會談正在跑的隔離工作樹。

severity 最高:major,blocking 共 1 條。
