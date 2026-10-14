severity: minor

我跑了實驗,留一條 minor finding。實驗目錄已刪。

**實測結果**
- 真實 20MB 帳(122107 列):`_residual_ask_rows_dropped` 約 0.09 秒,峰值約 112MB。
- 合成 100MB 帳(含 2000 筆 residual-ask):起點與頂端兩版比較約 0.7 秒,峰值約 450MB,約為帳大小的 4.4 倍。
- 同一份 100MB 帳走 `_gov_vc_gate_events(("residual-ask","guard-audit"))`,0.95 秒、峰值約 504MB。
- 兩版不是同時載入。起點的 raw 在函式返回後釋放,再讀頂端。所以峰值不是兩版相加。
- 把 `git cat-file blob` 換成拋 `TimeoutExpired` 後,`_residual_ask_rows_dropped` 回 None,`_residual_tier_hits` 回 `{'asks_dropped': -1}`。逾時的方向是升 high,沒問題。

severity: minor
blocking: 否 — 最壞結果是之後 `guard residual --add` 被擋,用戶得再審一次;沒有放行錯誤,也沒有資料遺失
引句:「這次審計沒記進治理帳(帳檔唯讀或是捷徑);這條合約之後要記殘留時 guard residual --add 會擋,修好帳再重審一次」
問題:這句警告只在 `_gate_event` 回 False 時才印。實際上寫入端跟隨捷徑和硬連結,捷徑帳會回 True。讀端 `_retro_gov_path_err` 卻拒收捷徑和 nlink>1 的帳。結果是警告承諾偵測「捷徑」,卻永遠不會為捷徑印出。
具體失敗情境:`docs/.governance-log.jsonl` 是指向別處的捷徑時,`guard audit` 把事件寫進捷徑目標(我實測寫進了 repo 外的檔),印出成功且沒有警告。之後 `guard residual --add` 讀帳時被拒,訊息是「治理帳 … 是符號連結 … 不往裡寫」。用戶只會看到「帳壞」,不會知道是這次審計沒被讀到。這是既有寫入器 `_gate_event` 的行為,這輪新增的呼叫端放大了它。
佐證:file: `scripts/lumos:1497`(`_gate_event` 以 `open(path,"a")` 追加)、file: `scripts/lumos:14557`(`_retro_gov_path_err`)、file: `scripts/lumos:18836`(新增的呼叫)

**已讀,無 finding**
- 記憶體峰值:100MB 約 450 到 500MB,單人使用可接受。反覆讀整本帳是既有模式,`_retro_read_bytes` 的 `chunks` 與 `join` 本來就雙份。
- 讀取逾時方向:base 或 head 逾時、物件遺失、淺層 clone 都走 "unreadable" 然後升 high。`ls-tree` 的 20 秒逾時同樣走 fail-closed。
- 列集合比對:含 residual-ask 字樣但讀不出的列,以原始位元組計入。`\r` 行尾或合併行只會多算刪除,不會漏算。
- 索引寫入:`_residual_index_write` 用 `_write_lf`,是唯一暫存名加 `os.replace`,具原子性。`WriteBlocked` 繼承 `ValueError` 和 `RuntimeError`,會被 `except` 接住。內容相同時不重寫檔。
- `guard audit` 的 `_body` 在作用域內。`ok is None`(沒有 docs 目錄)不誤報。審計與問答同一秒時,靠 `_seq` 排先後。

最高等級 minor,blocking 0 條。
