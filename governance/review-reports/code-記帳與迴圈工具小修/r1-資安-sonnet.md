severity: clean

我看了 `scripts/lumos` 的所有新增程式,以及 `scripts/test_lumos.py` 裡與這些改動相關的部分。文件與 skill 的改動沒有程式路徑,我只掃過,沒有逐行審。三類都沒找到能用的洞。

**① 提示注入:已看,無。**
- `loop next` 新印的範本和提示(`_loop_next_hints`、`_SNAP_PLACEHOLDER`、`_SCOPE_PLACEHOLDER`)都是固定字串。
- 迴圈編號進指令示意時,一律先過 `shlex.quote`(`_round_format_write_block` 的 `q`,`loop next` 既有的 `_qid`)。印在說明文字裡的編號先過 `_esc_clean`。
- 「提醒:…指紋已經寫進帳」那行印檔名,也先過 `_esc_clean(n, 80)`。
- `pitfalls` 新印的「這級仍要代碼審」席位清單,資料來自程式內的名冊 `_TIER_ROSTER` 和 `_REQUIREMENT_LABEL`,不含帳本欄位或使用者輸入。
- 擋下訊息裡帳讀不懂的原因是 `_loop_records_checked` 產的固定字串,例如「不是 UTF-8(第 N 個位元組)」,不帶帳本內容。

**② 讀寫與執行越界:已看,無。**
- 這份 diff 沒有新增 subprocess、`os.system`、環境變數讀取、下載來源、密鑰或信箱。
- 寫帳只走既有的 `_jsonl_append_verified`。`_ledger_rel_path` 沒有被改動。
- 新增的擋下事件字串 `round-format:{tag} loop={loop}` 把原始編號寫進治理帳。這是治理帳的寫入,不會進給 AI 的指令,而且寫進去之前沒有路徑操作。
- 沒有對外來路徑寫檔,也沒有執行不可信位置的檔。

**③ 非刻意一步繞過守衛:已看,無。**
- `none` 當空集合:`_set_or_none` 只在單一項目、不分大小寫是 `none`、且不是發現清單裡的 id 時才轉成空集合。`none` 跟其他 id 並列會直接擋下(rc2)。轉成空集合後,是否判為已處置仍由原本的集合核對決定,不會因此把全部發現靜默判成已處置。
- `--regression-set` 限 `code-`:設計審不使用這欄,讀它的只有代碼審修正關卡,所以不會丟掉設計審該記的回歸。
- 輪次規則新增的 `_round_format_write_block` 寫在 `outcome is None` 的路徑上,結局帳(`--outcome`)被整段跳過,這是設計意圖。舊的循序代碼審(帳上全無輪次、standard、`code-`)照舊放行,沒有拿這個豁免繞進新迴圈的路徑:新編號零筆時 `seq` 已改成 `bool(rounds)`,不再走循序。
- 帳讀不懂時 `lerr` 會擋下,不會照零筆放行。
- 這個擋下是 `hard=True` 加 rc2,按一次 Ctrl-C 或檔名帶空白/中文都走不過去。

pitfalls manifest 附的併發類檢核題在這個 repo 判範圍外,不審。

最嚴重 severity:clean,blocking 共 0 條。
