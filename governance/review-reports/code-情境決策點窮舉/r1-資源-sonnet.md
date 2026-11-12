severity: minor

整份 diff 我讀完了,沒找到會把正常操作擋下或放行的資源問題。三問(孤兒子程序、時間預算、記憶體)都過關,只有一條效能熱點屬 minor。

## 三問逐項結論

**① 子程序與執行緒收尾**
- `scan_ranges` 沿用 `subprocess.run(..., timeout=SCAN_TIMEOUT)`。逾時時 `run()` 會自己殺掉 ast-grep 子程序並等它結束,沒有新增殘留。
- 兩道新檢查本身不開子程序或執行緒。
- 逾時後 `_TIMED_OUT` 為真,`scan_ranges` 回 None,`check()` 把 `scan_index` 設成 `SCAN_FAILED`。反查的「規則」改由全判問題,不會偷放行,行為合理。
- 逾時若發生在 `loaded_count` 或 SARIF 探針,後面的壞例掃描也會回 None,同樣走 `SCAN_FAILED`。路徑一致。
- 測試端 `tempfile.mkdtemp` 都有 `finally` 的 `rmtree`。
- `_sit_repo` 在 TMPDIR 底下開的 `gctl-sit-*` 沿用既有慣例,由測試執行器的 `gctl-run-*` 根目錄回收。我跑完三支新測試後,`/private/tmp` 裡沒有殘留的 `gctl-*`。

**② 時間預算**
- 兩道靜態檢查都沒有逾時機制,但單次只要 0.26 秒和 0.18 秒,不會卡住推送。
- 我的複本沒有 `.pyc`,`--catalog-only` 全程 4.7 秒。慢在每次要解析約 7 萬行的 `scripts/lumos`,這是改動前就有的成本。作者量到 0.9 秒應該是有快取的情況。
- 同一支進程的常駐記憶體約 400MB,幾乎全來自載入 `scripts/lumos`,改動前就有。作者自量的 60MB 跟我量到的差很多(我量到 `--catalog-only` 的 maximum resident set 約 408MB),不影響判定。

**③ 記憶體與二次方工作**
- 母體檔只有 110KB 和 187KB,`n not in jtext` 的子字串搜尋沒有實際成本。
- `scan_index` 只存壞例掃描的命中,大小跟命中數成正比。
- `_bad_lines` 每個「規則」單位重讀一次該規則的壞例目錄。目前 5 個單位,成本可忽略。

## 本案鏡頭:型錄變大時的成長

用同一份型錄複製決策表與名稱來放大,實測如下:

| 倍數 | 決策表 | 反查(`_reachable`) | 反向同步(`_api_sync_problems`) |
|---|---|---|---|
| 1 倍 | 60 列 | 0.09 秒 | 0.08 秒(426 名) |
| 2 倍 | 120 列 | 0.33 秒 | 0.32 秒(851 名) |
| 4 倍 | 240 列 | 1.29 秒 | 1.27 秒(1702 名) |

兩者都是二次方,約 3.5 到 4 倍速成長,但絕對值很小。

**其他熱點(同量級)**
- `mentioned_by` 內的 `_word_in` 每次重新呼叫 `_kt_trigger_re`。profile 顯示呼叫 92,486 次,約 0.26 秒。
- 測試在同一個進程裡反覆呼叫這兩道檢查:`api_decision_points` 約 8 秒,`bad_snippets_reach_rows` 約 4.7 秒。表放大兩倍時,這兩支測試各會再慢幾秒,仍在可接受範圍。

severity: minor
blocking: 否
引句:「return any(rid in sg["rows"] for sg in lumos._kt_sit_text_segments(path, code, dt_rows))」
file: `configs/ast-grep/kotlin-android/check.py:1067`(`_reachable`)。每個反查單位都呼叫 `_kt_sit_text_segments`,它每次重編 `_kt_sit_rows_rx(rows)`(對全部決策表列重編觸發字正規式,`scripts/lumos:39903`)。profile 顯示 172 次呼叫佔反查 0.31 秒中的 0.29 秒。單位數與列數會一起長,所以是二次方。決策表加到 120 列時,這段約 0.33 秒;240 列約 1.3 秒。不影響判定,只是變慢。修法是在 `bad_snippet_reach_problems` 外層預編一次 `rows_rx`,或讓 `_reachable` 重用。

最高嚴重度 minor,blocking 0 條。

## 圖譜鏡頭
- 機器附的固定席節點因鏡頭計算超時沒給,我無法逐條判。
- 就我讀到的範圍,對 `scripts/lumos` 的改動只是把「不是測試檔且過 `_stack_changed_ok`」這個條件抽成 `_kt_sit_path_ok`,推送端兩處改呼叫它。輸入輸出條件與原內聯式相同,不影響既有節點行為。
- 我沒有另外驗證 `_lens_changed_lines` 那一處的行為。
