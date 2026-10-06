severity: minor

席名:合約圖譜-r4-sonnet(第 4 輪,鏡頭:合約與圖譜一致、手冊說法、★INVARIANT★)

查證範圍與沒問題的部分(不是 finding):
- 計劃〈條款〉S1–S19、`Systems/loop-retro.md`、`Systems/loop-convergence-recording.md`、`Systems/reversibility-governance-ledger.md` 裡全部 `[test:]` 名稱在 `scripts/test_lumos.py` 都有對應函式;S17、S18、S19 新增的測試名都存在。
- 六處手冊到頂句、指令速查、`templates.md` §9 都接到 `cap-decision` 與回顧指令(`skills/` 底下逐處 grep 過),沒有殘留的 `--template >` 重導向寫法。
- 這三篇筆記沒有 ★INVARIANT★、★CHECKPOINT★、★IRREVERSIBLE★ 行被本次改動違反(grep 為零或不涉及)。
- 20 處讀者改走 `_ledger_lines`:逐處看過空字串尾段的處理(都有 `strip` 跳過或 `ValueError` 接住),對 text 讀法行為不變(`read_text` 本來就把 `\r` 轉成 `\n`,只有 U+2028/U+2029/U+0085 的切法不同,這正是修正目標);計數對得上計劃寫的 20。
- `_json_text_escaped` 實測:孤立代理、C1、U+2028、DEL、超出 BMP 的 Cf 字元都跳脫成合法 JSON、讀回值不變。
- `_drift_ledger_path_err` 新增 `is_file` 子句:既有的漂移帳測試(`t_note_audit_drift_share_repo_path_guard`、`t_drift_fix_dry_run_lock_and_ledger`、`t_drift_m1_review_r1_ledger_kinds_and_umask`、`t_drift_m1_review_r3_ledger_miss_short_write`)全綠;本機 harness 底下十個 repo 的治理帳與審查帳都不是捷徑、硬連結數都是 1,新規則不會誤擋現有佈局。
- 單測實跑全綠:`t_cap_retro_bad_ledger_fail_closed`、`t_cap_retro_accept_risk_ledger_bad_exit`、`t_cap_retro_r3_gov_ledger_rule`、`t_cap_retro_gov_tail_newline`、`t_cap_hint_at_cap_shows_cap_decision`、`t_cap_retro_loop_next_hint`、`t_cap_retro_r3_ledger_lines_everywhere`、`t_cap_retro_r3_prompt_table`。

### F1 治理帳還有四個讀者只在換行字元切行,跟「一律走 _ledger_lines」的說法與計劃〈切行〉不一致(修補引起)
severity: minor
blocking: 否 — 只在帳檔用單獨 `\r` 當行尾時才分歧;寫入端永遠寫 `\n`,現實觸發面窄,但守衛與文件都宣稱已統一
- 輸入:治理帳 `docs/.governance-log.jsonl` 的行尾是單獨的 `\r`(例如被某些編輯器或工具轉換過)。
- 走到哪:跑滿回顧一族用 `_retro_gov_events`(經 `_ledger_lines`,認 `\r`)讀到兩筆事件;同一個檔,`_fix_check_events`(`scripts/lumos:12688`,`raw.split(b"\n")` 再交給 `_drift_jsonl_parse`)讀到零筆。另外三個走 `_drift_jsonl_iter`(只在 `\n` 切)的治理帳讀者:`_gov_ledger_rows_by_time`(`scripts/lumos:1408`)、doctor 帳增速段(`scripts/lumos:2454`)、`gov` 載入器(`scripts/lumos:8372`),同樣把整檔當一行。
- 壞在哪:r3 把 `_ledger_lines` 的說明寫成治理帳讀者「一律走這一支」、計劃〈誠實界線〉寫「審查帳與治理帳的所有讀者(20 處…)」,但治理帳另有這四個讀者仍是另一套切行規則;`_drift_jsonl_parse` 的說明還白紙黑字寫「只在 \n 切行」,跟 `_ledger_lines` 說明裡「也不只認 \n(整本 \r 行尾會被當成一行丟掉)」互相矛盾。`t_cap_retro_r3_ledger_lines_everywhere` 的掃描只認 `.splitlines()` 與具名變數,看不到這種寫法,所以不會紅。
引句:「審查帳(.canary-log.jsonl)與治理帳(.governance-log.jsonl)的讀者一律走這一支」
- file: `scripts/lumos:35182`(`_drift_jsonl_iter` 的 `split("\n")` 在 35186)、`scripts/lumos:12688`、`scripts/lumos:1408`、`scripts/lumos:2454`、`scripts/lumos:8372`
- 重現(實跑輸出:`fix_check_events: []` 與 `retro_gov_events: 1 None`):
  ```
  c=t._cr_repo()
  ev=[{"gate":"fix-check","kind":"passed","loop":"L","round":"r1","record_sha256":"a"},
      {"gate":"loop-retro","kind":"cap-decision","loop":"L","decision":"extra-round","rounds":["r1"]}]
  (c["docs"]/".governance-log.jsonl").write_bytes(("\r".join(json.dumps(e) for e in ev)+"\r").encode())
  m._fix_check_events(c["root"],"L","r1")      # -> []
  m._retro_gov_events(c["root"],"L")           # -> ([一筆人裁紀錄], None)
  ```

### F2 治理帳壞時 retro-stats 把假迴圈「(治理帳)」算成一個有人裁紀錄的迴圈(修補引起)
severity: minor
blocking: 否 — 只影響統計輸出與 `--json` 計數,不影響任何閘的判定
- 輸入:治理帳是符號連結(或管線、有別的硬連結),跑 `lumos loop retro-stats`(或 `--json`)。
- 走到哪:`_cap_retro_scan` 的帳壞分支回一筆編號為 `(治理帳)` 的假項目,`cmd_loop_retro_stats` 把它當成真迴圈累計。
- 壞在哪:輸出第一行是「有人裁紀錄的迴圈 1 個(人裁:? 1;分級:? 1)」,`--json` 的 `totals.loops` 是 1、`by_decision` 是 `{"?":1}`、`loops` 陣列有一個叫 `(治理帳)` 的項目;實際上一個人裁紀錄都讀不到。計劃 S12 與〈二〉寫的是「以迴圈為單位印有人裁紀錄的迴圈數」「壞檔只標那一個」,這裡把「讀不到」計成「有一個」,吃 `--json` 的下游會多算一個不存在的迴圈。doctor I2 段同一筆被列在「N 個迴圈記了人裁,但跑滿回顧沒有或過期」的標題底下,措辭也不符。
引句:「return [("(治理帳)", {"error": gerr, "decision": {}, "applies": True, "state": None, "problems": []})]」
- file: `scripts/lumos:13490`、`scripts/lumos:13845`(`cmd_loop_retro_stats` 逐項累計)
- 重現(實跑輸出第一行):
  ```
  c=t._cr_repo(); t._cr_loop(c)
  gl=c["docs"]/".governance-log.jsonl"; tgt=c["root"]/"shared.jsonl"; tgt.write_bytes(b""); gl.unlink(); os.symlink(tgt,gl)
  lumos --vault <c.vault> loop retro-stats --repo <c.root>
  # [retro-stats] 有人裁紀錄的迴圈 1 個(人裁:? 1;分級:? 1)
  ```

### F3 計劃〈名詞〉「狀態四選一」與〈合約候選〉「完全相同」沒跟上 gov-bad 這第五種狀態與 S17 的例外(修補引起)
severity: minor
blocking: 否 — 只是文件內部不一致,程式行為符合 S17
- 輸入:讀計劃〈名詞〉合格回顧與〈合約候選〉第五條,對照 r3 之後的程式。
- 走到哪:程式的 `_RETRO_STATE_LABEL` 現在有五個鍵(新增 `gov-bad`,「判不了(治理帳壞)」);`canary record` 在治理帳壞、帳上已到上限、有卷證時,即使這個迴圈從沒有人裁紀錄也回 2(實跑:3 輪、無人裁、治理帳是捷徑,記 r4 → rc 2、`cap-gov-bad`;帳正常時同樣的記帳 rc 0)。
- 壞在哪:計劃第 73 行仍寫「狀態四選一:已記回顧、已跳過…、過期、沒有」;計劃第 206 行〈合約候選〉寫「沒有人裁紀錄的迴圈,`canary record` 與處置閘的行為跟現狀完全相同(S1、S15)」,與 S17 新增的 `cap-gov-bad` 例外直接衝突(S17 自己是對的,候選行沒更新);`Systems/loop-convergence-recording.md` 第 34 行那條 WHY 也還寫「同一輪後續席與沒有人裁紀錄的迴圈行為不變」且只列 `cap-ledger-bad`,沒提 `cap-gov-bad`。之後有人照〈合約候選〉蓋章、綁測試,會綁出一條跟 S17 打架的合約。
引句:「沒有人裁紀錄的迴圈,`canary record` 與處置閘的行為跟現狀完全相同(S1、S15)」
- file: `docs/lumos-toolchain-knowledge/Projects/審查跑滿回顧_計劃.md:73`、`docs/lumos-toolchain-knowledge/Projects/審查跑滿回顧_計劃.md:206`、`docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:34`、`scripts/lumos:13018`(`_RETRO_STATE_LABEL`)
- 重現:`_cr_loop(c)`(3 輪、不記人裁)→ 把治理帳換成符號連結 → `canary record none --loop crx --round r4 …` → rc 2、stderr 開頭「擋下:crx 帳上已到上限、有卷證,但治理帳 …」。

### F4 loop next 判到 cap-reached 時,記人裁指令印兩次,而且第二次在人裁已記之後仍叫人先記
severity: minor
blocking: 否 — 只是輸出重複與措辭互相打架,指令本身正確
- 輸入:標準分級迴圈 3 輪、處置閘沒過(G3 不過)→ `loop next --spec …`;之後先 `cap-decision` 再問一次。
- 走到哪:cap-reached 那段(`_cap_retro_next_lines`)先印一行「人裁要破例再開一輪或接受剩下的風險,先記人裁:lumos loop cap-decision …」,緊接著 S19 新增的 `[cap-hint]` 段又印一行同樣意思的「人裁:要破例再開一輪或接受剩下的風險,先記人裁(已記過就不用再記):lumos loop cap-decision …」。人裁記完之後,前一段改印「已有人裁紀錄(extra-round),回顧沒有——繼續之前先寫跑滿回顧:…」,後一段照舊叫人先記人裁。
- 壞在哪:同一份輸出同時說「已有人裁紀錄」與「先記人裁」;計劃〈三〉3 把 S6(cap-reached 段)與 S19(cap-hint 段)各自規定了這行,沒有講兩者同時出現時誰讓位。實際走一遍的輸出(實跑)末尾兩段就是上述兩行,中間隔著五行 [cap-hint] 明細。
引句:「lines.append(_esc_clean(P + "人裁:要破例再開一輪或接受剩下的風險,先記人裁(已記過就不用再記):"」
- file: `scripts/lumos:13631`(`_cap_retro_next_lines` 的第一行記人裁指令)、`scripts/lumos:8988`(`_cap_hint_lines` 新增的行)
- 重現:`_cr_loop(c)`、`c["spec"].write_text(_CR_SPEC_TEXT + "審後又改了一行。\n")`、`loop next crx --spec … --repo …` → 輸出含兩行 `lumos loop cap-decision crx --decision extra-round|accept-risk`;`cap-decision` 記完再跑一次 → 「已有人裁紀錄(extra-round)」與「先記人裁」同時出現。

總結:最嚴重 minor,blocking 0 條
