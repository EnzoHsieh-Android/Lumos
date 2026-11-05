severity: major

我讀了 r2 稿的做法與條款,對照 `scripts/lumos` 的鄰居碼逐問比對。沿用既有機制這件事,大方向對齊:先紅模式走 `_spec_gate_twoway_static`、`_spec_gate_twoway_run_verdict`、`_spec_gate_low_not_red`;簽核走既有 `signoff` 閘名與 `_waive_origin_tty`。不對齊的集中在三處:「設計審過了」怎麼判、沿用 `_spec_gate_push_one` 時沒列出鄰居裡寫死「風險低」的地方,以及新寫的表格拆格與帳欄細節。

## 1. 分層與依賴方向:不對齊(1 條 major,3 條 minor)

先紅模式的開關、預期值表檢查放在 `_spec_gate_front` 之後,推送前讀簽核放在 `_spec_gate_push_scan` 一帶,這些位置都跟鄰居一致。問題在開關的第一項:怎麼判「設計審過了」。

- **規格閘一帶沒有任何人讀判定檔。** 第 13700 到 16530 行沒有 `_codeloop_*`,也沒有讀 `governance/replay`。唯一的讀者 `_codeloop_pass_read_verdict` 在第 68468 行,屬於代碼審層,而且它的入口 `_codeloop_pass_precheck`(約第 68425 行)明文拒收非 `code-` 編號:「設計審的判定不能代替」。
- **規格閘一帶已經有自己的「設計審過了」判法。** `_nogo_full_review_gate`(第 15995 行)先確認每筆紀錄審的是這份計劃(`_same_file_path`),再用即時的處置閘 `_disposal_judge` 判。稿裡改成讀凍結的 `verdict.rc == 0`,是第三套定義。
- **稿的讀法比代碼審的弱。** 代碼審的 `_codeloop_pass_check_verdict`(約第 68510 行)還會比 `all_row_shas` 是否過期,並接受人裁的 accept-risk。稿只看 `rc == 0`,也沒有綁到這份計劃。
- **稿寫的是「照形狀檢查」,等於複製一份。** 要直接呼叫,又得帶代碼審的 `_codeloop_refusal` 與 `_CODELOOP_SKIP_CMD` 措辭。

severity: major
blocking: 是
引句:「讀法照 `_codeloop_pass_read_verdict` 的形狀檢查」
file: `scripts/lumos:68468`、`scripts/lumos:68425`、`scripts/lumos:15995`

另有三條分層面的 minor:

- **先紅模式沒有單一判斷函式。** 稿在規格閘、`high-red-missing`、預期值表推送前檢查三處各列一次「門高、判定檔 rc 0、首筆帳不早於生效時間」。鄰居的做法是 `_door_judge` 一處判、各處拿結果。
severity: minor
  blocking: 否
  引句:「預期值表解析、表指紋與它的推送前檢查」
  file: `scripts/lumos:15258`、`scripts/lumos:16248`

- **推送前檢查讀 `_loop_first_ts_key` 會重複整本讀帳。** 該函式每呼叫一次就讀一次 `.canary-log.jsonl`(第 14975 行)。推送前檢查的慣例是帳讀一次、存進 `_nogo_ctx["by_loop"]`(第 15787 行起、第 16248 行註解),`ts` 欄也已在 `_SPEC_GATE_PUSH_FIELDS` 裡。稿把它用在每份被碰到的高風險計劃上。
severity: minor
  blocking: 否
  引句:「審查帳裡這份計劃的迴圈編號最早一筆非結局帳的時間」
  file: `scripts/lumos:14975`、`scripts/lumos:15787`

- **治理帳讀取不是「同一趟」。** 稿說簽核事件跟留痕索引同一趟讀(`_spec_gate_gov_index`)。實際上那支只讀 gate `spec-gate`、kind `spec-gate-record`(第 15492 行),而 `expected-signed` 掛在 gate `signoff` 下,不會被撈到。`_gov_vc_gate_events` 雖然收 tuple 閘名(第 22229 行),稿沒指名要這樣接。稿的「某一筆符合就算」也跟鄰居 `_spec_gate_pick` 的「取最晚一筆」不同:簽完、改表、改回去,舊簽又生效。
severity: minor
  blocking: 否
  引句:「跟現有的留痕索引同一趟讀」
  file: `scripts/lumos:15492`、`scripts/lumos:15519`

## 2. 命名與錯誤處理:大致對齊(minor 為主)

命名本身對得上:

- `_HIGH_RED_SINCE` 對 `_SPEC_GATE_SINCE`(第 13714 行)。
- `red_first` 對 `manual_only`、`needs_light_review`(第 14275 行起)。
- 事件 kind 命名對 `nogo-light-review-missing`。
- 簽核 rc2、規格閘 rc1,都跟鄰居一致。

不對齊有四條:

- **`red_first` 沒進推送前讀帳的欄位白名單。** `_SPEC_GATE_PUSH_FIELDS`(第 15792 行)的註解明寫「要讀新欄位就加進來,不然讀到的永遠是 None」。稿的新帳欄只有 `red_first`,沒提這份名單。審查帳那筆勝出時(同一秒本機優先),`red_first` 會讀成 None,誤判成沒有先紅。
severity: minor
  blocking: 否
  引句:「新帳欄只有留痕的 `red_first` 一個」
  file: `scripts/lumos:15792`、`scripts/lumos:15519`

- **生效常數的取值慣例不同。** 鄰居的 `*_SINCE` 都是當日零點的固定時間戳(第 13713、13714、14809、35295 行)。稿寫「合併上主線那一刻」,寫程式時還不知道值,得合併後再補一個提交。
severity: minor
  blocking: 否
  引句:「值取本計劃合併上主線那一刻」
  file: `scripts/lumos:13714`

- **簽核的「誰簽的」寫法與鄰居不同。** 稿說簽的人取環境變數 USER,「同端到端驗收放行」。但端到端驗收用的是 `_e2e_who`(先 git `user.name`、再 `getpass`,第 43283 行),AI 放行時 `who` 寫死 `"ai"`(第 43520 行);取環境變數 USER 的是 lint-waive。另有兩處稿沒講:
  - 答 n 時的回傳碼。鄰居都回 1(第 38517、43518 行),稿只講「不寫」。
  - `_waive_origin_tty` 寫死印「沒放行」(第 38429 行起),稿要印「沒簽」,得加參數或改共用函式。
severity: minor
  blocking: 否
  引句:「簽的人(環境變數 USER,同端到端驗收放行)」
  file: `scripts/lumos:43283`、`scripts/lumos:38429`、`scripts/lumos:38517`

- **`_gov_row` 要帶的不只 `by`,還有 token。** `_gov_row` 的 token 欄是依閘名寫死的(第 16999 行,fix-check 先例)。去重鍵含 token,稿只提 `by`,沒說 token 也要帶出。另外稿沒講事件裡「表指紋」「簽的人」的欄位名;鄰居有 `clause_sha`、`fingerprint`、`who`。這些欄位在 `_gov_row` 之外讀不到。
severity: minor
  blocking: 否
  引句:「`_gov_row` 要把它帶出來」
  file: `scripts/lumos:16987`、`scripts/lumos:16999`

## 3. 第二種做法:大部分沒長出第二套,有兩處風險

**對齊的部分:**

- 表指紋用 `hashlib.sha256` 加 `join`,跟 `_clause_block_sha`(第 14144 行)同一個模式。
- 不壓縮格內空白是刻意跟 `_clause_block_sha` 的 `\s+` 全壓不同,稿有寫理由。
- 用 `nfc`(第 454 行)沒問題。
- 簽核不走 `_gate_event_fit`,跟 `_spec_gate_record` 的註解(第 14295 行)一致。
- `--expected` 旗標分支到另一條路,跟 lint-waive 的 `--ack` 做法一致(第 38517 行一帶)。
- AI 簽不一直列出來,是 d3 明文裁定的刻意分歧,不算第二套。

**不對齊兩處:**

- **表格拆格。** 專案現有兩處行內拆格:`scripts/lumos:27561`(`s.strip().strip("|").split("|")`)與 `scripts/lumos:51363`(`ln.strip().strip("|").split("|")`)。兩處都不認 `\|`,也都用會連剝多個管線的 `strip("|")`。稿自建 GFM 規則的拆格(`\|` 是字面、每列剛好四格),沒說它是不是可共用的函式,也沒交代跟這兩處的關係。結果會是同一行表格在不同地方拆出不同格。
severity: minor
  blocking: 否
  引句:「格與格之間用沒被反斜線跳脫的 `|` 分開」
  file: `scripts/lumos:27561`、`scripts/lumos:51363`

- **找節的重複與圍欄判斷。** `_h2_section_lines`(第 13774 行)遇到同名的兩節會悄悄合併,圍欄內的行會直接跳過,所以「同名的節出現兩次」與「表在程式碼圍欄裡」無法從它的回傳值分辨。函式 docstring 明寫「找節邏輯不准長出第三套」。稿沒說是擴充這支還是另寫一支標題掃描。
severity: minor
  blocking: 否
  引句:「找節用 `_h2_section_lines` 找 `## 預期值表`」
  file: `scripts/lumos:13774`、`scripts/lumos:13793`

## 4. 落點:合理,但漏一個

- **`Systems/規格閘`。** 現況 66 KB、20 行 KEY、責任範圍有寫,已含風險高半套與推送前讀留痕。先紅模式、預期值表檢查、推送前擋下都放這裡合理。
- **`Systems/reversibility-governance-ledger`。** 已有 signoff KEY(`[2026-07-10]signoff 簽核留痕…`)、gov 彙整說明,以及 fix-check 新閘名時順手補 `_gov_row` 欄位的 WHY 先例。簽核 `--expected` 與 gov 統計寫在這裡合理,稿也寫了順手補負責範圍。
- **不需要另開節點。** 預期值表解析只服務規格閘。
- **漏列 `Systems/bound-tests-gate`。** 稿第 5 點要改 pre-push 掛鉤那兩行(`scripts/hooks/pre-push:560` 與 `:581`)。規格閘節點自己寫明那段的家在 `Systems/bound-tests-gate`,依專案「改了程式要寫說明就寫進改到那支檔的家」的規則,它應列進 `lands_in`。
severity: minor
  blocking: 否
  引句:「pre-push 掛鉤那兩行」
  file: `scripts/hooks/pre-push:560`、`scripts/hooks/pre-push:581`

## 5. 稿宣稱「全部照舊」,但鄰居有三處寫死風險低 ⚠

這條放在最後,因為它更像正確性問題,可能被其他席升級成 major,請編排者裁。稿說「同一支 `_spec_gate_push_one`……起點已 done 的寬待……全部照舊」,但沿用時有三處會走偏,稿只列了 `_spec_gate_push_stale` 與 `_spec_gate_push_scan` 兩處要改:

- **done 寬待。** `_spec_gate_push_one` 的寬待條件寫死 `now.get("door") == "low"`(第 16138 行)。帶 `red_first` 的高風險計劃門重判是 high,寬待不會生效,照 doing 擋。
- **全靠人驗的計劃。** `if not tests` 會改跑小改動閘(第 16150 行),稿第 1 點卻說先紅模式不套這道。全部通過時,`_spec_gate_push_check` 會印「改動風險分級:light(計劃風險低且全靠人驗……)」與「代碼審只派架構對齊席」(第 16339 行)。這等於讓一份高風險計劃的代碼審降級。
- **輕量審。** `_spec_gate_push_light` 對 `nogo_skipped` 非空的計劃要求輕量審或 `-std` 完整審(第 16058 行)。稿沒說高風險計劃的 `nogo_skipped` 非空時怎麼處理。

severity: minor
blocking: 否
引句:「之後同一支 `_spec_gate_push_one`」
引句:「不套風險低的小改動閘」
file: `scripts/lumos:16138`、`scripts/lumos:16150`、`scripts/lumos:16339`、`scripts/lumos:16058`

不對齊共 11 條,其中 major 1 條。

相關檔案:
- 被審材料:`/Users/enzo/harness/lumos-highrisk-evidence/governance/review-reports/高風險測試證據加嚴/r2-snapshot.md`
- 程式:`/Users/enzo/harness/lumos-highrisk-evidence/scripts/lumos`、`/Users/enzo/harness/lumos-highrisk-evidence/scripts/hooks/pre-push`
