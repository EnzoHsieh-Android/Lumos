severity: minor

**審查範圍**:整份 diff 讀完。我另外在 `rw`(已套用此 diff,HEAD 2f9cb94f)做了實量和重現,沒有改任何檔。派工尾端沒有附 LUMOS-IMPACT 固定席筆記,也沒有「圖譜沒有釘到節點」的備援段,所以圖譜鏡頭只能對照 diff 裡改動的筆記自述(見末段)。

**K1 推送時撤除條件那支:記帳和印出搬到 try 外面,記帳或兜底訊息出錯會讓整個推送檢查崩潰**
severity: minor
blocking: 否 — 要記帳寫入拋出 `OSError` 以外的例外才會觸發,實際上少見;但它是退步,原本有兜底
引句:「    return _drift_retire_report(root, mode, base, tip, must, unknown, acks)」
1. 舊版 `return _drift_retire_report(...)` 在 try 裡,任何例外都被兜底成「不擋、記一筆沒判」。新版把它搬到 try/except 外面。
2. 記帳那一步(`_gate_event`)只接 `OSError`。帳裡的 `nodes` 帶筆記路徑,路徑含 lone surrogate(`\udcff`,git 路徑解碼失敗時會出現)時,`json.dumps` 沒事,但 `f.write` 拋 `UnicodeEncodeError`,直接冒出 `_drift_retire_guarded`。
3. 重現:`python3.14 /tmp/t_r.py`。
   - 把 `_drift_retire_ledger` 換成拋 `UnicodeEncodeError` 呼叫 `_drift_retire_guarded`,結果是 `PROPAGATED UnicodeEncodeError`。
   - `_gate_event(d,"drift-check","warned","n",nodes=["Systems/\udcff"])` 本身就會 `raises UnicodeEncodeError`。
4. 這支檢查被呼叫的地方(`cmd_drift_check` 的 `max(rc_core, _drift_retire_guarded(...))`)沒有再包一層 try。鄰居 `_drift_m1_guarded` 的寫法是「記帳也包進兜底」。
5. 同一道漏洞還有印出那段:`_drift_retire_report` 的 except 裡又 `print(...)`,stderr 管線已關(`BrokenPipeError`)時,第二個 print 再拋一次,同樣冒出去,而且 rc 和記帳都丟了。
6. 建議:`return _drift_retire_report(...)` 外再包一層 try,失敗時只講一句、回 `rc`(判定已定),記帳錯誤只吞不改判定。
7. 另有一件小事:順序改成「印完才記」之後,印的途中如果被 `KeyboardInterrupt` 或 SIGTERM 打斷(`BaseException`),該擋的 hard 事件不會留帳;舊版是先記後印。這是這次修正本來接受的取捨,只是目前沒有任何測試覆蓋。
引句:「        print(f"存量漂移檢查:RULE 撤除條件的清單印到一半出錯({type(ex).__name__}),判定照舊", file=sys.stderr)」

**逐項檢查結果(都沒有具體失敗場景,不標 finding)**
- `_gov_tail_bytes` 的檔尾讀取:
  - stat 之後檔案變大,`read()` 會讀到 EOF,只是多讀,不會錯。
  - 讀到別的行程正在追加的半行時,`_drift_jsonl_parse` 會略過非 JSON 的行。
  - 檔案在 stat 和 read 之間被截短時,`seek` 超出檔尾回空,走 `b""` 分支沒事。
  - 這支函式不吃 FileNotFoundError。但呼叫前有 `is_file()`,視窗極小。
- 24MB 載入的記憶體尖峰:實量 repo 的 16MB 治理帳(10.3 萬筆),`_gov_metric_events` 前後最大常駐記憶體從 42MB 升到 209MB,耗時 0.37 秒。
  - 外推到 24MB 約 250MB,只在有度量式撤除條件的 RULE 存在時才讀。
  - 帳目前約 0.17MB/天,24MB 約涵蓋 137 天,「暖機」(帳最舊一筆不早於 N 週前就不判)這關不會誤吞度量。
  - 這是已知成本,不是失敗場景。
- doctor 三段各重讀全部筆記:實量 622 篇圖譜,`_slot_summary_entries` 單次約 0.09 到 0.21 秒,S17、S18、S19 各自實跑 0.08 到 0.14 秒,三段加起來不到 0.5 秒。
  - 隨篇數線性成長,幾千篇約幾秒,可接受。
  - S17 只在有 `[被取代:]` 值時才進 `_node_decisions`,沒有二次放大。
- `drift scan` 預算:
  - 回頭條件那半先跑,不受 retire 影響。
  - 反過來,回頭條件把預算吃完時,retire 每一列都標「判不了(超過預算)」,不會漏判成「沒事」,只是輸出會變長。
  - 第二次 `_drift_probe_prefetch` 有 `_over()` 把關,subprocess 逾時沿用既有 deadline,沒有新增無上限呼叫。
  - 共用同一棵 `ptree`,沒有重複建樹。
- 兩個推送同時跑:每次推送最多記一筆,以 append 模式寫入,帳面不會互相覆蓋;順序改成印完才記,沒有新增共享狀態。

**圖譜鏡頭**
- 這份 diff 改了 `存量漂移守衛`、`lumos-cli-read`、兩篇 Issue/計劃的筆記自述,和 `scripts/lumos` 一致:
  - `drift scan` 納入 `retire`,對應 `_DRIFT_SCAN_KINDS` 的改動。
  - S17、S18、S19 不計問題數、不寫帳,程式裡走的是 `warn_soft`。
  - 兜底帳條數記 null。
- 筆記說「S19 照跑、最多列 20 條」與程式的 `_FACT_RECHECK_SHOW` 相符。
- 沒有發現 diff 破壞既有節點宣稱的行為。
- 筆記說「判定出錯兜底」。K1 的記帳例外洞讓這句話對記帳那一步不成立,建議修程式,而不是改筆記。

最高嚴重度 minor,blocking 0 條
