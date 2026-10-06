severity: major

席:併發資源-sonnet(最壞時序鏡頭)。重現全在臨時目錄造帳,沒碰真帳、沒改 repo。重現腳本在 /private/tmp/claude-501/scratch/(exp.py 造 repo,e1.py、e2.py、e4.py、e3.py 各一條)。

### F1 治理帳檔尾缺換行(上一次寫一半)時,cap-decision 回報 ✓ 實際讀不到,且 canary record 新一輪照放
severity: major
blocking: 是 — 人裁紀錄是整個回顧機制的觸發源,記丟了而且回 0,擋點整個失效且使用者照訊息救不回來
- 輸入:docs/.governance-log.jsonl 最後一行沒有結尾換行(磁碟滿時 _gate_event 的 `open(path,"a")` 寫到一半、flush 丟 OSError 留下半行;或編輯器存檔去掉末尾換行)。
- 時序:第一次寫失敗,指令照訊息回 1 說「修好再記一次」;使用者修好空間後重記 → `_gate_event` 把整行接在半行後面,回 True,指令印「✓ 已記人裁」回 0。讀側 `_retro_gov_events` 用 `raw.split(b"\n")` 切行,半行加新事件黏成一行 JSON 壞掉,整行被「壞行跳過」吞掉。
- 壞在哪:`cmd_loop_cap_decision` 回 0 但帳上沒有可讀的人裁紀錄。後果鏈:`loop retro crx --template` 回 2「沒有人裁紀錄」(使用者剛記完);`canary record --round r4` 回 0,第一席新一輪直接寫進帳(擋點 `_cap_retro_record_block` 判 applies=False 放行);處置閘第八步印「沒有人裁紀錄,不需要回顧」。也就是計劃的核心擋點在這條路徑 fail-open,而且是「回報成功但實際沒落盤」,同型於 Issues/canary-record未落盤事件 與 canary-audit 的 ★INVARIANT★「回報成功 ⟺ 該行已落盤且可讀回」。--record 與 --skip 走同一支寫入器,同樣會黏。
- 對照:同檔 `_local_ledger_append` 用 `_regular_own_fd` 開檔、單次 os.write 核對長度(「短寫不算寫成」),新指令走的版控帳分支沒有這層;也沒有寫後讀回。
引句:「ok = _gate_event(root, "loop-retro", "cap-decision", note.strip(), hard=False,」
- file: `scripts/lumos:1445-1503`(_gate_event 版控帳分支 `with open(path, "a", encoding="utf-8") as f: f.write(line)`)
- file: `scripts/lumos:347-367`(_retro_gov_events,新增讀側;落點在 diff 的 _retro_gov_events)
- 重現(實跑輸出):
  `python3 /private/tmp/claude-501/scratch/e1.py` — 先把治理帳寫成 `{"ts":...,"gate":"x","kind":"half`(無換行),再 cap-decision:
  輸出 `decide rc 0 ✓ 已記人裁:crx extra-round`;接著 `template rc 2 擋下:crx 沒有人裁紀錄`;帳檔尾端是半行與新事件黏成一行;`record r4 rc 0`(新一輪放行)。
- 建議方向(給修的人):寫入前補 `\n`(或整行單次 os.write 並核對長度),新增事件寫完讀回驗;讀側不要靠「壞行跳過」吞掉整個事件。

### F2 回顧檔被換成管線/無窮裝置的符號連結時,處置閘與 canary record 永久卡住
severity: minor
blocking: 否 — 要有人把 cap-retro.json 換成特殊檔,不是例行時序;但卡住的是擋點本身且無逾時
- 輸入:--record 成功之後,governance/review-reports/<編號>/cap-retro.json 被換成 FIFO(符號連結到 /dev/stdin 之類也同型;git 能提交符號連結)。
- 走到:`_cap_retro_status` 只用 `p.stat().st_size > _RETRO_MAX_BYTES` 擋大檔(FIFO 與 /dev/zero 的 st_size 是 0),隨後 `_sha256_file(p)` 是 `Path.read_bytes()`,對 FIFO 無寫端會永遠阻塞。`_cap_retro_check` 有 `is_file()` 檢查,這一支沒有;此外 `_retro_gov_events` 對治理帳也是直接 `read_bytes()`,既有讀者(_gov_ledger_rows_by_time)只讀「最終指向一般檔案」的帳。
- 重現:`python3 /private/tmp/claude-501/scratch/e4.py`(--record 後 unlink 回顧檔、mkfifo 同名):輸出 `HANG: loop status --disposal 卡住(FIFO)`、`HANG: canary record 卡住(FIFO)`(8 秒逾時才被外層殺掉)。/dev/zero 符號連結的無界讀入記憶體:未測。
引句:「        cur = _sha256_file(p)」
- file: `scripts/lumos:9125-9128`(_sha256_file 直接 read_bytes)
- file: `scripts/lumos:1397-1405`(既有讀者的一般檔案前提,對照)

### F3 --record 驗完與算指紋是兩次獨立讀檔,記下的指紋可能屬於沒驗過的內容,卻印 ✓
severity: minor
blocking: 否 — 閘端每次重驗,最壞是使用者被誤導一次;不會放行不合格回顧
- 輸入:`loop retro --record` 執行期間回顧檔被另一個編排者或編輯器改寫(check 讀的是 `p.read_bytes()` 的那份 raw,指紋另外 `_sha256_file(p)` 再讀一次)。
- 走到:`_cap_retro_check` 回無問題 → 檔被改 → `sha = _sha256_file(p)` 算到新內容 → `_gate_event(... "recorded" ...)` 寫帳 → 印「✓ 已記回顧」回 0。
- 壞在哪:帳上記的是沒被驗過的位元組。處置閘讀側 `_cap_retro_status` 會再跑一次 `_cap_retro_check`,所以判成「指紋相符但不再通過檢查」,fail-closed,不會放行;但使用者剛看到 ✓ 與回 0,要等到 canary record 被擋才知道。實測(e2.py 在 check 與 sha 之間換檔):`✓ 已記回顧:crx(指紋 5aa5ba061db0…)` rc 0,`status after: stale ['回顧檔指紋相符但不再通過檢查:…']`。
引句:「        sha = _sha256_file(p)」
- file: `scripts/lumos:9125-9128`
- 重現:`python3 /private/tmp/claude-501/scratch/e2.py`

## 固定席(圖譜鏡頭)必答
實跑 `lumos impact --diff ce2a961..HEAD` 取固定席(派工尾端沒有附筆記,我自己取的)。逐條判:
- Issues/canary-record未落盤事件 + Systems/canary-audit ★INVARIANT★「canary record/second 回報成功 ⟺ 該行已落盤且可讀回」:canary record 自己的審查帳寫入路徑這份 diff 沒動(擋點在 `rec["round"]` 之後、寫入之前,擋下時回 2 不寫帳),此合約對 canary 列不破。但新指令(cap-decision/retro --record/--skip)寫治理帳沒有寫後讀回,F1 就是同型的「回報成功、實未落盤」,精神上違反同一條家規,只是不在該節點宣稱的範圍。
- Systems/design-loop(處置閘 ★INVARIANT★):第八步在前七步之後、橫幅只列跑過且過的步驟;凍結/回放全程 retro_skip/spec_sha_override 印 —,不改前七步判定。判不影響。
- Systems/loop-convergence-recording ★RISK·守衛面★:canary record 新擋點 fail-closed 的方向正確,但 F1 的黏行讓擋點在帳壞時 fail-open;此節點宣稱「帳壞不放行」只在審查帳(S17)成立,治理帳壞行未覆蓋。
- Systems/reversibility-governance-ledger、cochange-guard、check-r-guard 等 ★RISK·守衛面★:diff 不碰它們的判定函式;loop-retro 閘名加進 `_KNOWN_GATES` 不屬 `_GOV_LOCAL_PAIRS`,走版控帳,不影響 loop list 關門判定。判不影響。
- 其餘 ★INVARIANT★(lumos-cli-lifecycle、lumos-cli-read、bound-tests-gate、guard-kill、授權與歸屬、測試假綠形態、節點範圍與索引守衛、slim 三節點、Systems/lumos-deinit):這份 diff 只動 loop 家族指令與 canary record 擋點;未碰 re-inject sentinel、search 濾網、guard 綁定、deinit、slim 安裝路徑。判不影響。
- Systems/loop-retro(新節點)的 WHY「寫帳用有回傳值的通用寫入器,寫不進去一律回 1、不印成功」:對「寫入器回 False」成立,對「寫入器回 True 但黏行讀不到」不成立(F1)。

## 查過、判無問題(不計為 finding)
- 兩支 --record/cap-decision 同時寫:各自單行 append(行 <8KB),不交錯;兩筆 recorded 並存無害(取最新)。cap-decision 與 --record 交錯:recorded 事件落在新 D 之後但 rounds 對舊 D,`_cap_retro_check` 的 rounds 比對會判 stale,fail-closed。
- 大檔:`_cap_retro_check` 先 stat 再讀,256KB 上限擋在記憶體前(僅 stat 與 read 之間檔變大才越界)。
- 12 萬行成本(各 37MB 的兩本帳實測):`canary record --round` 每次多約 0.8 秒(`_retro_canary_load` 解析整本審查帳 0.54 秒;`_retro_gov_events` 只做位元組預濾 0.07 秒),沒有人裁紀錄的迴圈也付這筆,但未造成失敗,不標。
- 寫不進去的回傳值:cap-decision/retro --record/--skip 在 `_gate_event` 回 None 或 False 時都回 1 且訊息明講沒留痕;canary 擋下事件寫不進去只印警告仍回 2(判定不被觀測故障改變)。
- 擋點救法:accept-risk → 改記 extra-round;cap-ledger-bad → --skip;經 e1 以外的路徑(寫入成功)實測救得回,見 F1 為唯一例外。

總結:最嚴重 major,blocking 1 條
