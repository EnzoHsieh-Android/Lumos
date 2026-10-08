結論：`resources-F1`、`resources-F2` 均未被反駁；編排者補充的 `groups=None` 問題也成立。三項皆存活，維持 `major`。

1. `resources-F1` — `agree / major`

- 靜態證據：`_nodehome_list` 建立完整樹的 `files` 與 `all_paths`（[scripts/lumos:26881](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:26881)）；函式層 `route_cache`（[scripts/lumos:27456](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:27456)）按 SHA 保存整份結果且直到函式返回前沒有淘汰（[scripts/lumos:27484](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:27484)）。提交列舉也沒有 K 上限。
- 實跑：12 個 mixed 提交重跑仍是 `peak_full_tree_pairs=13`、`list_calls=15`、結束後 `remaining_pairs=0`。
- 界線：3000 paths 是合成擴充，量到的是物件生命週期，不是 RSS，也沒有直接證明某個規模必然 OOM；但它已證明候選遍及 K 個提交時，完整樹常駐量可成長為 O(K×P)。這不是跨呼叫洩漏，而是單次檢查的尖峰保留風險。
- 最小修法：將完整樹快取改成逐 group 釋放或小型 LRU；若要保留零重讀，可先計算 SHA 剩餘使用次數，最後一次使用後立即淘汰。回歸測試應守「常駐版本數有界」，另以 RSS 測試確認實際天花板。

2. `resources-F2` — `agree / major`

- 舊機制確實已有 reader 快取競態：建立 reader 時只算一次差異清單（[scripts/lumos:26933](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:26933)），稍後對當時未列入差異的路徑直接讀工作樹（[scripts/lumos:26942](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:26942)）。
- 但本 finding 不需要把所有舊 reader 議題算進來：本批新增了明確的新消費路徑——把該 reader 放入路由快取（[scripts/lumos:27483](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:27483)），借給 route side（[scripts/lumos:27497](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:27497)），再用它判斷無副檔名測試的 shebang（[scripts/lumos:27129](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:27129)）。
- 實跑：兩方向仍分別得到「提交無 shebang，expected 1／actual 0」及「提交有 shebang，expected 0／actual 1」。現有 `shebang-index-*` 控制固定走 `--staged`（[scripts/test_lumos.py:48042](/tmp/lumos-review-snapshot-encoding-preflight/scripts/test_lumos.py:48042)），沒有覆蓋 push/HEAD 的兩步競態。
- 實跑界線：父席 counter 是實際改 temp 工作樹；我核對 wrapper 與目前 CLI SHA，並用不落盤的 `Path.read_bytes` 等價注入重跑，得到相同 `0/1` 翻轉。
- 最小修法：只讓新增的 route evidence 使用 object-only reader，例如為 `_nodehome_reader` 增加預設關閉磁碟捷徑的選項；舊呼叫端不動。路由的內容必須由 `git show <sha>:<path>` 或同一 tree 的 blob OID 取得。

3. `groups=None` 補充項 — `agree / major`

- `_nodehome_commit_groups` 在 `rev-list`／`diff-tree` 失敗時會回 `None`（[scripts/lumos:27414](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:27414)）。`cmd_home_check` 未區分「真正 staged」與「diff 分組讀取失敗」，都把 `None` 傳進 evaluator（[scripts/lumos:28005](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:28005)）。
- 新碼看到 `groups is None` 就從整段端點建立含測試的 `routeN/routeB`（[scripts/lumos:27635](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:27635)），再合成 `sha=None` 的單一 group（[scripts/lumos:27639](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:27639)）。因此第一個提交的測試變更可以被第二個提交的程式／錯家筆記借用，違反逐提交路由判準。
- 實跑：同一兩提交 fixture 正常分組 `rc1`；注入分組失敗後目前版本 `rc0`；凍結 patch 基線仍為 `rc1`。基線檔 SHA 也已確認等於 `53d1c458:scripts/lumos`，不是拿錯版本比較。
- 即使接受既有「Git 故障偏 fail-open」政策，這裡也不是單純跳過：它把未知分組誤當 staged 證據模型，主動生成正向測試路由；本 finding 只涵蓋這個新增放行面，不擴張成所有舊 fallback 問題。
- 最小修法：將 staged sentinel 與 commit-group failure 分開。只有真正 `--staged` 才能使用端點 `routeN/routeB`；diff 分組失敗時保留舊整批 fallback，但 `route_tests` 必須為空，不能跨提交借測試證據。

依辯方三態，三項都是 `agree`；沒有取得可作 `evidence` 降級的反證。全程未改根目錄，也未追 Windows 或全圖健檢。