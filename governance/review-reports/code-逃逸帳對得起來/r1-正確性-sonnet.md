severity: clean

已看,無:逐條核對設計條款 [S1]–[S21] 與 `scripts/lumos` 這次的改動(`_escape_loop_kind`、`_escape_reason_ok`、`_escape_log_guard`、`_escape_is_withdraw`、`_escape_withdrawn_targets`、`_escape_rows_for`、`_escape_withdraw`、`cmd_loop_escape` 的佐證/撤回/混用擋下段、`_escape_stats`/`_escape_row_bucket`/`_escape_released_loops`/`_escape_review_rows_by_loop`/`_escape_shared_evidence`/`_escape_cat_rows`/`_wilson_interval`/`_escape_stage_class`、`_plan_for_loop` 的 code- 前綴與 NFC、`cmd_rule_gap` 的撤回過濾),沒找到會讓它在某個輸入下算錯的洞:

- 手算驗證 Wilson 區間:拿真帳本 `design × standard × platform`(放行 2、漏網 1)手算 p=0.5、den=2.9208、mid=0.5、half=0.4056,得到 9%–91%,跟 `lumos loop escape-stats` 實際印出的區間逐位對上,公式(含 z²/(2n) 與 z²/(4n²) 兩處常見手誤點)沒寫錯。
- 分子/分母恆為迴圈集合(`cats[c]["leaked"]` 只在 `lid in released` 已確認之後才 `.add`,而 `released` 集合本身就是 `cats[c]["released"]` 的來源),結構上不可能率 > 1、放行 0 的格也走不到率的分支——實跑 `python3 scripts/lumos loop escape-stats`(真帳本,25 列有效、11 筆計劃、3 筆未放行迴圈、0 筆歸因不明)全部類別的率都落在 [0,1]。
- `_escape_shared_evidence` 用 `if key and lid in released` 先過濾到分母母體,`plan` 類的列（沒有審查帳的計劃)不會污染歸因不明判斷,對應 S20;無佐證列(sha、defect_ref 都空)彼此的空字串永遠 falsy,不會被誤判成「共用同一個佐證」。
- 撤回鏈路(`_escape_withdraw`)的「目標不存在/已撤過/本身是撤回紀錄/撤回者空白/理由不足」擋下與 `_escape_log_guard` 的符號連結擋下都在同一把 `_vault_write_lock` 裡,且 `_escape_raw_rows`(含撤回紀錄)只用於「確認撤回目標」這一件事,不會被拿去做統計(統計一律走過濾掉撤回的 `_escape_rows_for`)——這個切分是 r3 折入的重點,程式碼與帳上真實資料(27 列、0 筆撤回)行為一致。
- `_escape_row_bucket` 的判斷順序(plan → unreleased → no_evidence → unattributed → counted)跟第四節條款描述逐句對得上;`no_evidence` 的列仍計入「有效逃逸」(design 明講「至少一列有效逃逸(沒被撤回、不是下一站接住、不是歸因不明)」沒有排除無佐證),不是漏判。
- `_escape_stage_class` 對「消費專案真推送」這種沒收錄的站名會落到 `unknown`(仍算漏網、另計數),跟真帳本裡唯一一筆 `消費專案真推送(pos-ios)` 實測對上「站名不認得 1」。
- `python3 scripts/test_lumos.py -k escape`:111 passed, 0 failed(含這次新增的 S1–S21 全部條款測試與既有紅釘測試)。

唯一想過但沒有標記的一點(不夠格開 `## F`,因為找不到會真的觸發它的輸入):`_escape_released_loops` 判斷「放行」時只檢查 `d.get("kind") == "converged" and d.get("nodes")`,沒有額外檢查 `d.get("gate") == "design-loop"`。設計文件裡有提到要靠 gate 名字排除 `gate=code-loop, kind=passed`,但那筆本來就沒有 `nodes` 欄位,單靠 `kind` 這個檢查就已經排除它了。我查過全 repo 唯一會寫 `kind="converged"` 且帶 `nodes` 的地方是 `_loop_gov_mark`(固定 `gate="design-loop"`),所以現在這條路徑没有能讓它算錯的真實輸入——只是防禦性不夠嚴謹,不構成可證偽的缺陷,不標。

共 0 條。
