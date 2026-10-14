severity: major

這次修補讓門掃描少抓到一種以前抓得到的危險詞(`send`、`mail`、`prod` 這類要比單字邊界的英文詞),這條是 major。其餘項目已讀,沒有發現問題。

先說我跑了什麼。我把修補前(用 `git apply -R` 還原 `scripts/lumos`)和修補後的 `scripts/lumos` 都載入,放在實驗目錄 `/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-Backend-improve/fe5c4f58-e7fb-477f-be55-0823b5438608/scratchpad/cr-sgn11-通才/`。我在這個目錄的 clone 裡跑了測試子集 `-k note_lines`、`-k door`、`-k nogo`、`-k zero_width`、`-k pq_blank`、`-k shard`、`-k durations`,全綠。

## finding 1

severity: major
blocking: 是 — 風險低的門多放行了一種以前會被判成風險高的寫法,是修補自己引進的回歸
引句:「isspace 為真卻看不見的控制字元與行段分隔也拿掉」
問題:`_door_scan_text` 的 `_is_invisible` 現在會把 `\x0b`、`\x0c`、`\x1c`–`\x1e`、`\x85`、U+2028、U+2029 直接刪除,不是換成空格。這幾個字在修補前是 `splitlines` 的切行點,詞會被切到不同行,所以 `\bsend\b`、`\bmail\b`、`\bprod\b` 比得到。現在它們被刪掉,前後兩個字黏在一起,單字邊界消失,比不到。
具體失敗情境:這幾個字是 Word 貼上(`\x0b` 是 Word 的手動換行)、網頁或 Notion 貼上(U+2028)很常帶進來的。我拿 `_door_keyword_hits` 在修補前後各跑同一段文字,結果是:
- `"we deploy to\x0bprod now"`:舊版命中「不可逆/prod」,新版沒命中。
- `"deploy to\u2028prod"`:舊版命中,新版沒命中。
- `"will send\x85mail"`:舊版命中 `send` 和 `mail`,新版沒命中。
- `"push to\x0cprod"` 和 `"upload to\x1cprod"`:舊版命中,新版沒命中。
一份計劃把這類句子放進正文,再把四類「已排除」寫齊,門就判風險低、不派審。修補前它會被判高。
修法建議:這幾個字在比對前換成一個空格,不要刪。換成空格後,後面的壓空白步驟會把連續空白併掉。它們做詞中夾字時,黏起來的效果要靠「漢字間空白拿掉」那一步,不必靠刪除。再補一支測試,讓 `"deploy to\x0bprod"` 和 `"send\u2028mail"` 這種句子要命中。現有的窮舉測試只驗「看不見的字被拿掉」,沒驗拿掉會不會讓字黏起來。
佐證:``file: `scripts/lumos:5042` ``(`_is_invisible`)、``file: `scripts/lumos:8189` ``(`_door_scan_text`)

## finding 2

severity: minor
blocking: 否 — 只是筆記裡的量測宣稱已經不準,不影響行為
引句:「門掃命中與不做清單略過的詞跟修補前逐篇相同(0 篇不同)」
問題:我把 944 篇 `docs/**/*.md` 的 `_door_keyword_hits`、`_nogo_skip_lines`、`_door_exclusions`、`_nogo_skipped_rows` 在新舊版各跑一次,有 2 篇不同。這兩篇是 `Projects/規格閘不把不做節的詞算進風險_計劃.md` 和 `Systems/規格閘.md`,它們這次新寫的範例字(「退 款」「收斂　判準」)現在會命中「金流」和「守衛面」。`規格閘.md` 原本命中的 `pre-push hook` 也換成了較前面類別的命中。計劃本身在 `.canary-log.jsonl` 裡已是 `plan_risk` 高,所以沒有誠實計劃從低變高。
具體失敗情境:這只是把「0 篇不同」寫成了永遠成立。另外在 `docs/.canary-log.jsonl` 裡,現有的 61 筆風險低留痕全部是 `door_rule: 1`,升到版本 9 後它們不再算進雙向門的前 30 份計數,是整批重數,不是逐篇變化。這是合併回主線的一次性效果,先前幾輪已經知道。
佐證:``file: `docs/.canary-log.jsonl` ``(61 筆 low、320 筆 `door_rule: 1`)

## 已讀,無 finding

- **`_note_lines` 取代 `splitlines`**(對應 `scripts/lumos:4929`):
  - 本 repo 6489 個 md 檔裡,含 `\r` 或那幾個行段字元的只有 24 個,全部是 `governance/review-reports` 的席報告,不是計劃。
  - `docs/` 底下的計劃和筆記都沒有這些字,條款定義、條款指紋、`[keeps]`、條款檢查、條目、計劃連結的行號和指紋不會變。
  - 結尾換行、空字串、`None` 的行為我也比對過,和 `splitlines` 一致。
- **壓空白和漢字間空白**:
  - 四類關鍵字正則裡沒有漢字間空格,也沒有 `\s`,所以拿掉漢字間空白只會增加命中,不會讓原本的命中消失。
  - 對 944 篇筆記的實測只有上面那 2 篇自帶範例字的差異。
  - 效能:200 萬空白、30 萬個「測 試」、20 萬行、`\t` 重複 100 萬次,新版耗時 0.02 到 1.3 秒,不是新瓶頸。
- **分支接上主線 5c1e8794 之後**:
  - 目前分支就是主線上多一個功能提交,沒有衝突。
  - 耗時分片的測試(`-k shard`、`-k durations`)全綠,分片計算不受影響。
  - `governance/test-durations.json` 這次沒動,新測試走預設權重。
  - `_nogo_ctx` 現在每次推送都多讀一次治理帳(`docs/.governance-log.jsonl`,約 20MB),實測 0.15 秒,而且只在有風險低計劃要查時才發生。
  - `_nogo_ctx` 讀帳失敗時 `gov_events` 是 `None`,`_cap_retro_status` 會自己重讀,語意沒變。
- **其他修補段落**:`_nogo_full_review_shape` 改用 `_loop_anchor_tier`(`scripts/lumos:27339`),函式存在、行為合理;`_spec_gate_print_door` 加 `_esc_clean` 沒問題;`events` / `gov_err` 參數的改名在各呼叫端一致。

最高等級 major,blocking 1 條。
