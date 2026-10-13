severity: minor

我跑了 full-span-v1 的各種形狀和規模、擋下事件的各種輸入、處置閘診斷行的 30 多種路徑形狀,也跑了 `quote-check` 的各種參數組合。沒有找到 blocking 級問題。

**已驗過、沒問題的部分**
- **整段引句形狀**:巢狀 `『』`、跨行、CRLF 和單獨的 CR、標籤落在引句內部、未閉合後又接合法引句、`「…』` 混型、落單的 `」` 和 `』`、空引句、NUL、孤立代理字元、零寬字元。判定都合理,CRLF 與換行統一後的結果一致。
- **規模**:20 萬條未閉合標籤、100 萬個 `「`、30 萬層 `『`、100 萬個落單 `」`、500 萬字元的單一未閉合引句,每種都在約 1 秒內跑完。舊判準在 2 萬條未閉合標籤要 6.7 秒(二次方),新判準 0.02 秒。舊判準的二次方成本是已知的 Issue,不算這次的新問題。
- **舊判準函式本體**:與 cb832b56 版逐字相同,`-k quote` 的 173 個測試全過。
- **拿掉比較模式**:`compare-rules`、`qc_compare`、`qc_repo` 和兩個大小上限常數在 scripts 與 docs 都沒有殘留。`--repo` 已移除,沒有文件還在引用。`--compare-rules` 現在被 argparse 擋成 rc2。
- **`quote-check` 參數組合**:缺報告或缺 `--spec` 回 rc2。`--rule bogus` 回 rc2 並列出可選值。`--rule` 沒給值回 rc2。重複 `--rule` 以最後一個為準。
- **診斷行路徑**:空白、單引號、雙引號、中文、`-` 開頭(補成 `./-x.md`)、`$()`、反引號、分號、`*`、`~`、`\` 全部用 `shlex.split` 還原後與原路徑相同。換行、tab、U+0085、U+2060、U+202E、孤立代理字元、超過 1000 字的路徑,都改印「不印可照貼的指令」的說明。
- **擋下事件的片段**:ESC、雙向覆寫、零寬、U+2028、tab、孤立代理字元都被 `_kill_esc` 轉成 `\uXXXX`;全空白的片段記成 `-`;長度被截到 60 字。

**1. 擋下事件的 note 裡,`report=` `loop=` `auditor=` 還是原樣寫進去**
severity: minor
blocking: 否
引句:「    return (f"quote-rule:{write_rule} kind={kind} cats={','.join(cats)} report={report} report_sha={sha12} "
file: `scripts/lumos:25885`(約在 `_quote_block_note` 的 return 處)
- 片段已改走 `_kill_esc`,但 `report` 路徑、`loop`、`auditor` 沒有經過同一道處理。
- 報告路徑如果寫成 `/tmp/a report=evil id=1234 /x`,note 裡第一個 `id=` 就是偽造值,真的 `id=` 排在後面。程式註解自己說讀者照「第一個 report=/id=」取值。
- 報告檔名是非 UTF-8 時,note 帶孤立代理字元,`_gate_event` 的 `f.write` 丟 `UnicodeEncodeError`,被吞成 False,只印一句 telemetry-write-failed,這筆擋下事件就沒進帳。
- `report=` 沒有長度上限(5000 字的路徑原樣寫入)。
- 路徑是記帳的人自己給的,不是審查席能控制的內容,所以只算 minor。這和 `loop=` `auditor=` 在既有 note 裡本來就是原樣寫的做法一致。

**2. 手動 `quote-check` 文字模式把整段引句原樣印出**
severity: minor
blocking: 否
引句:「        rows.append(_quote_anchor_row(q, hay, hay_ns))」
- 在 `scripts/lumos` 的 `cmd_quote_check` 文字輸出那行,引句只截 `[:60]` 就印出,沒有跳脫。
- full-span-v1 的引句可以跨行,印出來會把一條結果拆成多行,編號對不上。
- 引句裡的 ESC 也直接進終端,實測 `\x1b[31m` 原樣印出。
- 這行印法是改動前就有的,不是這次新增;但整段引句讓換行變成可達,第一階段未啟用 full-span-v1 時影響不大。

**3. 診斷行遇到 `=` 開頭的相對路徑,在 zsh 下可能被展開**
severity: minor
blocking: 否
引句:「        rows.append(_quote_anchor_row(q, hay, hay_ns))」
- ⚠ 這條沒有對應的 patch 行可引,借用上面那行當錨,內容與它無關。
- `_drift_sh` 的白名單包含 `=`,所以路徑 `=ls` 不加引號,照貼到 zsh 會被展開成 `/bin/ls`。
- 處置閘只有在找不到 repo 根(`root` 為 None)時才會印相對路徑,實際上很少遇到。這個白名單是共用函式的既有行為,不是這次改動造成的。

總結:最高等級 minor,blocking 共 0 條

我建的實驗目錄已刪除。
