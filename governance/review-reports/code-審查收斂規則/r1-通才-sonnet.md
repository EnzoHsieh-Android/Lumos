severity: minor

我沒有找到會弄壞既有功能的 bug。三個相關子集全綠:`residual`(75 個)、`retro`(357 個)、`escape_stats` / `guard_list` / `gate_drift`(共 23 個)。在 `1bb556f8` 的 clone 上,`doctor` 和 `contracts` 照常執行,`guard list` 照常執行並輸出「真綁 35 / 懸空 0 / 偽證據 0 / 裸 0 / 未審 0」。另外有三個小問題。

已讀,無 finding:
- 抽出的 `_gov_vc_gate_events` 和原本的 `_retro_gov_events` 行為一致,篩選條件和 `loop_id` 比對順序都沒變。
- `_walk_test_files` 多的 `with_path` 參數,預設走原本的回傳,舊呼叫點不受影響。
- `INV_TAG_RE` 多剝 `residual`,`guard audit`、`kill-add` 的合約定位以及 `_classify_one` 都經過它,沒有誤判。
- `_KNOWN_GATES` 補了 `residual-ask`,`_gate_event` 的 `extra` 欄位名也沒有撞到保留欄位。
- `cmd_loop_escape` 的 `--list` 混用檢查、`--withdraw` 混用檢查和 `--auto` 檢查都有涵蓋 `residual_ref`。
- doctor 的殘留檢查放在函式層級(不在 `if inv_all` 的 else 裡),所以不影響其他段落;`guard residual --reindex` 遇到符號連結索引檔會乾淨擋下,不會出堆疊。
- `pitfalls` 的 `_residual_tier_hits` 在沒有索引、讀不出或 git 失敗時都回空清單,分級照舊。

severity: minor
blocking: 否 — 只影響可見度,不影響任何判定或寫入
引句:「clean, refs = strip_test_refs(x)」
問題:`INV_TAG_RE` 現在把 `[residual:…]` 剝掉,但 `cmd_contracts` 印的是剝完的 `clean`,沒有像 `guard list` 加上殘留提示。
失敗情境:使用者在動手前查「這段有什麼不能碰」,`lumos contracts <節點>` 看不到任何殘留標記。只有 `guard list` 和派工鏡頭看得到。
佐證:``file: `scripts/lumos:6222` ``(`cmd_contracts` 印 `clean`);計劃筆記〈做法〉第 49 行寫 contracts 會經過 `INV_TAG_RE`,但沒要求要顯示。

severity: minor
blocking: 否 — doctor 的索引對照會抓到,且重跑 `--reindex` 就能修
引句:「atomic_write_verify(path, new_lines, f"[residual:{ref}]", check)」
問題:`_cmd_guard_residual_locked` 先把標記寫進合約行,下一行才重寫殘留索引。索引寫入若丟 `WriteBlocked`(例如 `governance/` 底下的索引檔是符號連結或唯讀),`except` 印「擋下:…」並回 2,但筆記已經改了。
失敗情境:使用者看到「擋下」,以為什麼都沒寫。實際上合約行已有 `[residual:]`,索引卻缺這一筆,`pitfalls` 會漏升 high,直到 doctor 報「殘留索引對不上」。
佐證:``file: `scripts/lumos:18822-18830` ``(patch 的 `_cmd_guard_residual_locked`);`--add` 和 `--remove` 都有這個情況。

severity: minor
blocking: 否 — 計劃有明文要這樣做,只是副作用值得提醒
引句:「for k in ("about_code", "test_files"):」
問題:索引把「綁定測試所在的檔」也算進分級用的檔案集合。
失敗情境:本 repo 的測試全在 `scripts/test_lumos.py` 一支檔裡。只要有任何帶殘留的合約綁了其中一個測試,之後幾乎每次碰到該測試檔的推送都被升成 `high`,不管碰的是不是那條合約的測試。結果是 `high` 常態化,審查人力被稀釋。
佐證:``file: `scripts/lumos` ``(patch 的 `_residual_index_files_at` 與 `_residual_test_files`)。

最高等級 minor,blocking 0 條。
