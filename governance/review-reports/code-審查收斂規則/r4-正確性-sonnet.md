severity: minor

審查範圍:修補差異全部,加上 `_diff_range_ends`、`_gate_event`、`_cmd_guard_residual_locked`、`_residual_index_entries` 的現行原始碼。未跑實驗,只有 `datetime` 邊界做了一次一行驗證。

severity: minor
blocking: 否 — 只影響已有殘留標記的合約再擴張反例時的分級,不放行拿掉或縮小殘留,推送範圍裡其餘新增殘留與刪帳路徑都升 high
引句:「已經有了:{rel[:-3]} 這條合約行尾已經有 [residual:」
問題:外層看門的 `added` 只比索引裡的(節點、合約指紋、殘留指標)。同一筆決策下追加新反例時,`--add <同一個指標> --case c2` 會走「已經有了」那條路。這條路照樣用 `_residual_check` 驗 c2 的 untestable 問答、驗 `guard audit` 事件比問答晚,而且驗得過。決策內容只要求含 `checker:<模型>/<日期>` 字串,同一個第二代理同一天判 c1 與 c2 時,舊決策內容本來就含這個字串。這條路不寫合約行,索引的鍵不變,所以 `added` 是空的。
失敗情境:合約 X 已掛 `[residual:N#d3]`,決策 d3 內容含 `checker:sonnet/2026-10-14`。作者對新反例 c2 重問到 untestable,重跑 `guard audit`,再 `--add N#d3 --case c2`。推送內容是帳新增幾列 residual-ask 與 guard-audit,可能還有索引不變。結果 `res` 是空的,tier 不升 high,「挑到想要的答案」這個動作沒進代碼審。要補的話,`added` 得涵蓋反例層級,或把「已經有了」這條路也視為新增。
佐證:``file: `scripts/lumos:19263-19285` ``(`_cmd_guard_residual_locked` 的 `if same:` 提早回 0)、``file: `scripts/lumos:44596-44651` ``(`_residual_tier_hits` 只比索引三元組)

severity: minor
blocking: 否 — 只有手改治理帳寫出極端的沒帶時區 ts 才觸發,後果是 `--add` 丟例外而不是放行
引句:「return (t if t.tzinfo else t.astimezone()), d.get("_seq", -1)」
問題:`try` 只包 `fromisoformat`,`t.astimezone()` 在 try 外面。沒帶時區的 `0001-01-01T00:00:00` 或 `9999-12-31T23:59:59`,我用 python3.14 實測會丟 `ValueError: year must be in 1..9999`(工具自己寫的 ts 都帶時區,所以只有手改才碰得到)。
失敗情境:帳裡有一筆這種 ts 的 residual-ask 或 guard-audit,`guard residual --add --case …` 在 `_residual_check` 裡直接崩出堆疊,不是回「ts 讀不出」的擋下訊息。呼叫端是 fail-closed 的,所以不會放行。
佐證:``file: `scripts/lumos:19060-19070` ``(`_residual_ev_order`,依 patch 行 251-258)

已讀,無 finding:
- `added` 的範圍寫法:`A..B`、`A..`、`..B`、`A...B`(起點取 merge-base)、單一版本(終點為工作目錄)都由 `_diff_range_ends` 拆對。無法解析的起點(例如 `x^!`)會讓索引與帳都讀成 unreadable,結果是 base_bad,偏向升 high。起點索引 missing 或 bad 時,頂端所有殘留都算 added,偏向升 high。
- 合約改字:改字後指紋變,索引出現 removed 加 added,雙雙升 high。舊索引缺 fp 欄時鍵為 "None",同樣偏向升高。
- 兩版帳比對讀不出:任一版 unreadable 回 None,再變成 -1,升 high。起點 missing 回 0。頂端 missing 而起點有列,全部算刪除。工作目錄那份是捷徑或非一般檔也算 unreadable。
- 帳的比對方式:改成比 `git cat-file blob` 取出的位元組集合,`.gitattributes` 的 -diff 與 NUL 影響不到。CRLF 與頭尾空白已被 strip。只有「刪掉兩列逐位元組相同的重複列」不會被數到,實務上發生不了(同秒同內容)。
- 審計與問答先後:`guard-audit` 事件是 `_gate_event` 寫的,ts 為帶時區、秒精度的 ISO。同一秒靠 `_seq`(帳內檔序)分先後,兩個 gate 混讀同一個序列,正確。沒帶時區的 ts 當本機時間。舊審計沒有事件時回「找不到紀錄」並擋下,偏向 fail-closed,不是漏放。審計事件的 fp 用審計當下的內文算,不含標記,與 `_residual_check` 的 ckey 一致。
- 同秒雙事件、`--date` 任填:事件用寫入當下的時間,不受 `--date` 影響。
- `touched()` 在檔名清單失敗時回 True,所以帳與索引的比對不會因 diff 失敗被跳過。
- `head_bad` 新增「索引被這次推送動過」條件,方向是多升不少升。
- `_RESIDUAL_GOV_REL` 已全數換成 `GOV_LOG_REL`,殘留的 `.testable` 與 `_residual_testable_cases` 沒有其他呼叫者。
- `_residual_case_key` 新規則:`c-1` 與 `c1` 同一個,`c1.1` 與 `c11` 不同,`-` 位置不會越界(頭尾已 strip、連續 `-` 已合併)。
- 指紋剝 Cf 與 Cc:已存在的合約若含這類字元,指紋會變。結果是一次性的 removed 加 added 升高,不是漏升。

資料狀態五問摘要:帳不存在、索引缺欄、時間戳記無時區、舊審計無事件、兩版任一讀不出,在已讀的路徑上都是偏向升 high 或擋下。唯一偏向不升的是第一條 finding 的同決策追加反例。

最高等級 minor,blocking 0 條。
