severity: major

審查範圍:資源鏡頭,逐 hunk 讀完修補差異與 `r2-snapshot.patch` 的程式部分。pitfalls manifest 的 lint 類條目與併發類題目不判。

固定席節點:這次派工詞說鏡頭計算超時、沒附,照指示不自行補算。「這次新增的殘留」段沒有可答的內容。

實驗用的臨時目錄已用字面絕對路徑刪光,`lsof` 也確認過沒有程序開著。實驗中我自己起的一個卡在 `/dev/zero` 的測試程序已殺掉。

1. 開場掛鉤讀紀錄只限份數與單份大小,沒限總時間,500 份各 2MB 的紀錄會讓掛鉤超過外層 10 秒
severity: major
blocking: 是
file: `scripts/hooks/claude/lumos-entry-hook.py:288`(`_e2e_ai_line`;外層上限見 `scripts/merge-claude-settings.py:111`,`"lumos-entry-hook.py": 10`)
引句:「for _m, name, p in rows[:_E2E_RECORD_SCAN_MAX]:」
- 失敗場景:專案 `.lumos/e2e-records/` 裡有 500 份各約 2MB、檔名合格的紀錄(都沒超過 2MB 單份上限)。`_e2e_ai_line` 在 `_enforcement_line` 之後才跑,自己沒有截止時間。整支開場掛鉤超過外層 10 秒就被收掉,開場的圖譜指引整段送不出去。
- 量測(同一台機器、同一支掛鉤):
  - 沒有紀錄目錄:整支掛鉤 1.05 秒。
  - 500 份各 2MB 的合格紀錄:9.66 秒,離上限只差 0.3 秒,慢一點的機器就破。
  - 500 份各 2MB,`waivers` 是 100 萬個 `1` 的清單:`_e2e_ai_line` 單獨 36.7 秒,整支掛鉤 37.9 秒,是上限的近 4 倍。
  - 最後一種情況記憶體尖峰 576MB。
- 這個上限只約束份數與單份大小,沒約束時間,所以是殘留。修補沒有補截止時間(例如 `_inner_budget`)或總位元組上限。
- 歸因:有證據的原有漏查。把同樣的紀錄交給修前版(0aecbf90)的 `_e2e_ai_line`,耗時 36.3 秒、582MB,跟修後版同量級。修補只改了取檔順序與符號連結,沒碰時間。
- 重現:用 `proj/.lumos/e2e-records/` 放 500 份 `{"fingerprint":"<64 碼>","waivers":[1,1,…]}`(約 2MB),把 `{"cwd":…}` 餵給 `lumos-entry-hook.py`,計時。

2. doctor 的 AE 段和 `waive --ack` 吃同樣的 500×2MB,要幾十秒到三分鐘
severity: minor
blocking: 否
file: `scripts/lumos:41796`(`_e2e_ai_pending_all`,經 `_e2e_load_json`,`scripts/lumos:40777`)
引句:「rec, err = _e2e_load_json(path, scrub=False) if path is not None else (None, "太大")」
- 失敗場景:同一批 500 份 2MB 紀錄,doctor 的 AE 段沒有時間上限,也沒有輸出,使用者看起來像卡住。
- 量測:
  - 500 份各 2MB 的正常放行紀錄:68.1 秒、70MB。
  - 同樣份數但 `waivers` 是 100 萬個整數的紀錄:179.3 秒、678MB。
  - 比掛鉤那條寬鬆路徑慢約 9 倍。多出來的時間來自 `_events_depth_ok` 的堆疊展開和 `_e2e_fix_surrogates` 整份遞迴複製(掛鉤那條只做 `json.loads`)。
- 掛鉤文字說「跟開場掛鉤同一套寬鬆規則」,只對判斷規則成立,對成本不成立。
- 歸因:未判定。修前 `_e2e_records_all` 沒有份數上限,工作量只會更大;修補把它收斂成 500 份,但沒有補總時間或總位元組上限。我沒有在修前版實跑 doctor。
- 重現:同第 1 條的紀錄,跑 `_e2e_ai_pending_all(root)` 計時。

3. 功能歸屬判斷的工作量是「改到的檔數 × 全部功能路徑數」,大改動加大型對照表會讓判定用滿 60 秒
severity: minor
blocking: 否
file: `scripts/lumos:41669`(`_e2e_gate_owners`)與 `scripts/lumos:40635`(`_e2e_owners`)
引句:「return [fn for fn, paths, flows in (index or _e2e_owner_index(feats)) if any(_e2e_under(f, x) for x in paths) or nf in flows]」
- 失敗場景:一次推送改到十萬支檔,對照表有 300 個功能、約 9500 條路徑(300×30 加一個 500 條路徑的功能)。判定把整道 60 秒用光,擋下並說「判定超過 60 秒還沒算完」,出口是 `LUMOS_SKIP_ANDROID_E2E=1`。
- 量測:
  - 10 萬檔、對照表精簡:`android-e2e check` 2.17 秒、365MB。
  - 同樣 10 萬檔、9500 條路徑:61.36 秒、user 60.8 秒(擋下);`_e2e_gate_owners` 單測約 1377 檔/秒,外推 10 萬檔要 73 秒。
  - 2 萬檔、200 條路徑:0.45 秒,一般規模不受影響。
  - 修補加的「每 1000 支查截止時間」有效,超時只多出約 1.4 秒。
- 修補只把正規化挪到迴圈外,沒有消掉檔數乘路徑數的二次方,也沒有前綴索引。
- 歸因:有證據的原有漏查。修補只削掉常數項,結構沒變。

4. `LUMOS_TTY_TIMEOUT` 給很大的數字,`select` 會丟 `OverflowError`,沒人接
severity: minor
blocking: 否
file: `scripts/lumos:33616`(`_confirm_tty_timeout`,修補新加)
引句:「return t if 0 <= t < float("inf") else 30.0」
- 失敗場景:`LUMOS_TTY_TIMEOUT=1e10`(或 `1e300`)通過這道檢查,`select.select(…, timeout)` 丟 `OverflowError: timestamp out of range for platform time_t`。`_confirm_tty` 只接 `EOFError`,`waive` 與 `--ack` 在這條互動路徑上直接崩。
- 量測:`nan`、`-1`、`inf` 都回 30,`0` 回 0.0;`1e10` 與 `1e300` 在 `select` 丟 `OverflowError`。我是用 `select` 直接驗的,沒有用偽終端跑完整的 `waive`。
- 修補說自己涵蓋「負數、NaN、無限大」,上界少夾一道。只有使用者自己設環境變數才觸發,所以不升級。
- 歸因:有證據的修復回歸。我沒在修前版實跑:修前版只擋 `ValueError`,同樣不會處理過大的值,所以這個洞原本就在,修補宣稱封口但沒封全。

三問

① 原問題的修復效果有何行為證據?
- 符號連結:指到 `/dev/zero` 的 64 碼 `.json` 在掛鉤與 doctor 都被 `lstat` 擋下,0.0 秒回、沒卡。
- 時間上限:修補的取檔順序與份數上限在 500 份 2MB 時沒讓耗時變多、也沒變少,時間問題仍在(見第 1 條)。
- 讀提交樹的檔:先用 `cat-file --batch-check` 問大小再讀,深層巢狀的 JSON 以 `RecursionError` 在 0.01 秒內被攔下,走「判定內部出錯」的擋下路徑,不是崩。
- 大改動:10 萬檔、精簡對照表時 2.17 秒完成,證明 ls-tree 帶 pathspec 與歸屬索引有效。

② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?
- 成立:提交樹讀檔、指紋的 pathspec、每 1000 支查截止時間、`_vault_write_lock` 取代自寫鎖。
- 鎖:殘留鎖不自動接手,是文件明寫的取捨,`waive` 搶不到時等 60 秒再擋,推送不拿這把鎖、出口仍有效,我不記為缺陷。
- 相鄰路徑不成立:開場掛鉤與 doctor 的讀紀錄沒有總時間上限(第 1、2 條)。
- 邊界不完整:`_confirm_tty_timeout` 沒夾上界(第 4 條)。

③ 新發現在修前、修後各是什麼結果?
- 第 1 條:修前 36.3 秒/582MB,修後 37.9 秒/576MB,同樣越過外層 10 秒。
- 第 2 條:修前沒有份數上限,修後 68 到 179 秒;修前沒實跑,只靠讀碼判斷更慢。
- 第 3 條:修前每檔每次重做正規化,只會更慢;修後 61 秒擋下。
- 第 4 條:修前修後都會溢位,修補沒有改變結果。

總結:最高等級 major,擋實作的 1 條(第 1 條,開場掛鉤讀紀錄沒有總時間上限)。
