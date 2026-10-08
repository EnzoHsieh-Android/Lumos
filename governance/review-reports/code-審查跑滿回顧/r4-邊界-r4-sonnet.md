severity: minor

席:邊界-r4-sonnet(邊界與輸入:空值、無法編碼字元、各種行尾、超長輸入、特殊檔案類型)。
範圍:/tmp/code-capretro-r4.patch 的 scripts/lumos 全部 hunk 逐段讀完,並在臨時 repo(`_cr_repo`/`_cr_loop` 造帳,沒碰真帳)實跑。

實跑過、沒問題的邊界(不列為 finding):
- 治理帳是 FIFO、資料夾、帳內符號連結、帳外符號連結、懸空符號連結、`docs` 本身是符號連結、硬連結:cap-decision、--skip、處置閘、canary record、retro-stats、loop next 全都不卡住、回 2 或判 gov-bad,沒有往捷徑目標寫。
- 治理帳檔尾是半行、`\r`、`\r\n`、BOM、NUL 行、空檔、不存在:cap-decision、--skip、處置閘照常。人裁理由帶 U+2028、U+2029、U+0085、`\r\n` 照常。
- `_json_text_escaped`:全部 1114112 個碼位逐一往返(`json.loads(_json_text_escaped(obj)) == obj`),`_PATH_SPECIAL_CATS` 的字元(除結構換行)沒有任何一個原樣留在輸出裡。
- 回顧檔欄位塞 300 與 990 層巢狀陣列(version、loop、rounds、family、target):--check 正常列問題,不丟堆疊。審查帳某列 auditor 或 report_path 是 900 與 5000 層巢狀:--template 正常印出。
- 輪次 id 各 1500 字元:cap-decision 正常寫帳、不截斷。
- `_ledger_lines` 換掉的 20 處:逐處看了「尾端多一個空元素」的影響,凡是沒先 skip 空行的地方,json.loads 的 ValueError 都落在 continue,沒有新增壞行計數。

### F1 一個批次裡有一筆帶不能編碼字串,整批版控治理帳事件靜默全丟(修補引起)
severity: minor
blocking: 否 — 只在事件帶孤立代理字元時發生,影響是少記帳,不是閘判錯。
- 輸入:`_append_governance_log` 收到兩筆都會進版控帳的事件(例如 gate=check-s、hard=True),其中一筆的 nodes 帶 `"bad\udcffnode"`(Linux 上非 UTF-8 檔名經 surrogateescape 讀進來的形狀)。
- 走到哪:`text = "".join(json.dumps(...))` 整批組成一個字串,`f.write(text)` 在編碼那一步丟 UnicodeEncodeError;r3 把它跟 OSError 一起吞掉,一個位元組都沒寫。
- 壞在哪:另一筆沒問題的事件(`good-node`)跟著不見,而且沒有任何訊息。r3 以前是丟堆疊、使用者看得到;現在 doctor --ci 與 anchor approve 這類寫者會悄悄少記整批,14 天升級鏈要看的 hard 事件也在裡面。
引句:「帶不能編碼的字串也算寫不進去,不丟堆疊(代碼審 code-審查跑滿回顧 r3 正確性、邊界席)」
佐證行:file: `/Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos:1601-1620`(_append_governance_log)
重現(臨時 repo):
```
ev=[{"gate":"check-s","kind":"warned","hard":True,"nodes":["good-node"]},
    {"gate":"check-s","kind":"warned","hard":True,"nodes":["bad\udcffnode"]}]
m._append_governance_log(c['vault'], ev)
gov.read_bytes()   # → b'' (兩筆都沒寫、沒有輸出)
```
⚠ 判不準要不要升級:這條要不要逐筆寫、或把壞字串換掉再寫,是取捨,我只確定現況是整批靜默丟失。

### F2 治理帳讀者仍有一批只在 \n 切行,跟「全部換掉」的說法不符
severity: minor
blocking: 否 — 只在帳整本用 `\r` 行尾時兩邊讀到的列不同,不影響一般帳。
- 輸入:治理帳內容 `{"gate":"a","kind":"x"}\r{"gate":"loop-retro","kind":"cap-decision"}\r`(整本 `\r` 行尾,r2 就是為了這種帳才讓 `_ledger_lines` 認 `\r`)。
- 走到哪:跑滿回顧一族走 `_ledger_lines` 讀到兩筆(含 cap-decision);`lumos gov`、`_gov_ledger_rows_by_time`、doctor 增速與度量段、`_drift_jsonl_parse/_drift_jsonl_iter` 的讀者只在 `\n` 切行,整本當一行,json 解析失敗被跳過,一筆都讀不到。
- 壞在哪:同一本治理帳,閘看得到人裁紀錄、`lumos gov` 與 doctor 看不到;而 `_ledger_lines` 的說明寫「審查帳與治理帳的讀者一律走這一支……r3 全部換掉」,對 `_drift_jsonl_iter` 這一族不成立。守衛測試 t_cap_retro_r3_ledger_lines_everywhere 的正則只認 `.read_text(...).splitlines()`,抓不到這一族。
引句:「r3 架構對齊席指出其餘讀者還在 splitlines、同一列在不同讀者眼中行數不同,r3 全部換掉」
佐證行:file: `/Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos:35182-35194`(_drift_jsonl_iter)、file: `/Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos:1392-1408`(_gov_ledger_rows_by_time)
重現:
```
raw=b'{"gate":"a","kind":"x"}\r{"gate":"loop-retro","kind":"cap-decision"}\r'
[x for x in m._ledger_lines(raw) if x]  # → 2 列
list(m._drift_jsonl_iter(raw))           # → []
```

### F3 治理帳讀不動(權限不足)時,出口指令叫人去換成一般檔,對不上病因
severity: minor
blocking: 否 — 只是出口提示講錯,閘本身 fail-closed 判得對。
- 輸入:cap-decision 已記的迴圈,`docs/.governance-log.jsonl` 是一般檔但 chmod 000。
- 走到哪:`_retro_gov_path_err` 通過(是一般檔、一個硬連結),`_retro_read_bytes` 開檔失敗 → gov_err = 「讀不到(不存在、是資料夾、捷徑或管線,或打不開)」→ 處置閘第八步 ✗ → 印 `_cap_retro_fix_cmd(..., 'gov-bad')` 那句。
- 壞在哪:出口叫人「換回 repo 裡的一般檔(不是符號連結、管線、資料夾,也沒有別的硬連結)」,但檔本來就是一般檔,真正要做的是改權限;照做不會有任何變化,--skip 也被同一條擋掉,使用者沒有出口線索。
引句:「把治理帳 docs/{GOV_LOG_NAME} 換回 repo 裡的一般檔(不是符號連結、管線、資料夾,也沒有別的硬連結;」
佐證行:file: `/Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos:13171-13193`(_retro_read_bytes 的錯誤訊息)
重現(臨時 repo,`chmod 0` 治理帳後問處置閘):輸出 `判不了:治理帳 docs/.governance-log.jsonl 讀不到(不存在、是資料夾、捷徑或管線,或打不開)` 之後接 `把治理帳 … 換回 repo 裡的一般檔(…)再重跑`。

### F4 治理帳壞時 retro-stats 把假列算成一個「有人裁紀錄的迴圈」
severity: minor
blocking: 否 — 只影響統計數字與 JSON 欄位,閘不看它。
- 輸入:治理帳是符號連結、資料夾或 FIFO(任何 gov-bad),跑 `lumos loop retro-stats`。
- 走到哪:`_cap_retro_scan` 回一筆 `("(治理帳)", {"error":…,"decision":{}…})`;retro-stats 把它當一個迴圈累加。
- 壞在哪:實跑輸出 `有人裁紀錄的迴圈 1 個(人裁:? 1;分級:? 1)`,JSON 的 `totals.loops` 是 1、`by_decision` 是 `{"?":1}`。其實根本判不了有幾個迴圈記過人裁;「1 個」是工具自己造的假列。
引句:「return [("(治理帳)", {"error": gerr, "decision": {}, "applies": True, "state": None, "problems": []})]」
佐證行:file: `/Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos:13485-13490`(_cap_retro_scan)、file: `/Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos:13836-13870`(cmd_loop_retro_stats 累加)
重現(臨時 repo,`.governance-log.jsonl` 換成 FIFO):`lumos loop retro-stats --repo <root>` → `[retro-stats] 有人裁紀錄的迴圈 1 個(人裁:? 1;分級:? 1)`。

總結:最嚴重 minor,blocking 0 條
