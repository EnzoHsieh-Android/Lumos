severity: major

**固定席逐條判**

- **Systems/pitfalls-code-loop**:會影響。範圍 3 說的「分支、版本、合併提交那一側照 `_disp_bj_source` 讀」在沒有表態紀錄時接不起來,見 F1。範圍 3 說「`_lint_new_verdict` 與 `_lint_new_classify` 完全不動」,但放寬延後與關閘的判定就住在 `_lint_new_verdict` 裡,見 F5。
- **Systems/lint-declaration-health**:會影響。該節點管「宣告驗證要擋掉壞命令」。範圍 1 另寫一份驗證,漏了 `{LINT_SARIF_OUT}` 這道,見 F6。
- **Systems/kotlin規則包**:不影響。已查證 12+50=62 條規則的訊息開頭都有型錄編號,提示級 7 條出處不全、覆核級 0 條,跟計劃宣稱一致(`check.py` 的 `main_rows` 對得上)。
- **Systems/棧別提問表態閘**、**Systems/linter精選目錄**:不影響。前者的情境題流程只被旁路;後者只是改範本那一句。唯一的連動是 F4(情境型錄壞掉會卡住規則命中記帳)。

**F1 範圍 3 與 5、S12:覆核判定的讀取與人複查事件沒接上現有的合併側查找**

severity: major
blocking: 是(合併推送會誤擋、人複查對合併推送無效,屬判錯擋停)

引句:「分支、版本、合併提交那一側照表態那一道 `_disp_bj_source` 的讀法」

- `_disp_bj_source(rec, …)` 要靠表態紀錄 `rec["_merge_side"]`。這個值只由 `_disp_record_for` 產生,而它只在 `_dispositions_verdict` 有適用情境題時才呼叫。
  - 沒有表態紀錄時,`if not app: … return out` 會先返回。
  - 合併側查找用 `_codeloop_merge_side_lookup(..., ("dispositions",), ...)`。它只認 `dispositions` 事件,不認 `blind-judge` 事件。
- 失敗輸入:feat 分支只動了覆核規則會碰的碼(沒有情境觸發字),判定記在 feat。推 main 的合併提交時沒有表態紀錄,讀 main 自己的帳,結果每一筆都是「還沒判」被擋。S12 的測試只有在同時有表態紀錄時才會綠。
- `_codeloop_lint_new_step(repo_root, diff_range, tier)` 沒有 `marker_branch`、`marker_sha`、`merge_side`、`merge_ledger` 這些參數。呼叫點在 `_codeloop_guard_verdict` 的 3.6 一處,和 `lint_on_pf_fail` 那處,需要改簽名,計劃沒寫。
- 範圍 6 的 `rule-review overturn` 寫「一筆治理帳事件」,但事件的 kind、分支欄與必要的 `head_sha` 都沒定義。
  - `_codeloop_ledger_events` 只產出 gate 為 `code-loop`、kind 在指定集合內、且有非空 `head_sha` 的事件。
  - 合併側讀的是被合進來那一側的帳(`raw` 是那一側的),人在目標分支上寫的 overturn 讀不到,推翻無效。
- `token` 欄也有問題。`_gov_row` 對 `blind-judge` 的 token 取 `written_at`,不取事件自帶的 `token`,所以「另帶 token」跟現有語意衝突。人要用的 `--batch <token>` 從哪裡拿到,計劃沒說。

佐證:file: `scripts/lumos:73640-73655`、`scripts/lumos:74237-74244`、`scripts/lumos:74850`、`scripts/lumos:73370-73385`、`scripts/lumos:71517-71537`、`scripts/lumos:17575-17590`

**F2 範圍 6、d4:人推翻後可以重派盲判,等於人的意見會被 AI 蓋掉**

severity: major
blocking: 是(d4 的「人推翻就恢復成要擋」只在重判之前成立)

引句:「`overturn` 之後那幾筆的判定作廢、恢復成要擋,可以重派盲判」

- 失敗輸入:人覺得某筆 `false` 是真問題,執行 `overturn`。推送被擋,擋下訊息印出的指令就是跑盲判。AI 重派一個代理再判 `false`,又放行。
- 這個循環沒有「人釘死 real」的狀態。S4 只測了推翻當下,沒測重判後。
- 同一個機制還有 `unsure` 的出口(見 F3)。這跟計劃引用的 Semgrep 做法(人不同意就重新打開、不由模型再關)不一樣。

佐證:file: `scripts/lumos:74191-74210`(同一格只認第一筆、重判只能靠材料變)。計劃要放寬這條,但沒有人的最終判定欄。

**F3 範圍 6:`unsure` 判兩次後悄悄放行,而且不在任何清單**

severity: major
blocking: 是(該擋的命中變成沒人看、沒人數)

引句:「仲裁判 `real` 擋、`false` 照上一條、仍 `unsure` 只提醒並記帳」

- 「待人看清單」的定義只收 `false`。`unsure` 兩次終局不擋,卻不進清單,`gov --stats` 的複查統計也數不到。
- 這是模型自己說「判不準」的最不確定的一類,被看見的程度反而比 `false` 還低。
- 失敗輸入:代理對難判的命中先後兩次都答 `unsure`,推送放行,doctor 不唸,RETIRE-IF 也不計入。

佐證:計劃〈用詞〉待人看清單、範圍 6 與 S5。程式端沒有對應機制,`_kt_bj_check` 的 `majority` 提醒也不會替它代勞。

**F4 範圍 4 最後一點與範圍 5:記帳路徑仍卡在情境題機制上**

severity: major
blocking: 是(型錄或情境段一壞,規則命中就沒法記判定,又因 d2 而被擋)

引句:「`blind-judge --rule-hits` 這條路不需要情境型錄與情境段算得出來」

- 這句只講 `--template --rule-hits`。記帳走的是結果檔頂層 `rule_hits`,沒有 `--rule-hits` 旗標可以識別。
- `_cmd_codeloop_blind_judge` 在讀結果檔之前,先 `if _KT_DT_ERR: … return 2`,接著 `segs = _kt_bj_segments(...)`,為 `None` 就 `return 2`。`_kt_bj_validate` 也要靠 `segs` 才能驗。
- 失敗輸入:型錄情境表壞掉,或情境段算不出來(`_KtSitUnverifiable`),只有 `rule_hits` 的結果檔記不進帳。推送一直被「還沒判」擋住,唯一的出口是 `lint-waive`。
- 另外 `_kt_bj_event_ok` 要求 `blind_judge` 是非空 dict。只含 `rule_hits` 的事件過不了這支,要新寫一條讀取路徑,計劃沒寫這個折疊函式。

佐證:file: `scripts/lumos:74188-74199`、`scripts/lumos:74064-74080`、`scripts/lumos:73831-73841`

**F5 範圍 3:模式與跳過規則只說「一體適用」,但放寬延後在 `_lint_new_verdict` 裡面**

severity: major
blocking: 是(守衛面,可繞過)

引句:「新增告警閘的 `mode`(`warn` 降成提醒、`off` 整道不跑)與 `LUMOS_SKIP_LINT_NEW` 一體適用於覆核」

- 一般段有 `_lint_new_relax`:這次推送把 `lint_new.gate` 從 block 放寬成 warn 或 off 時,照放寬前的設定判。它改的是 `cfg` 和 `out["mode"]`,在 `_lint_new_verdict` 內部。
- 覆核段若自己重讀 `_lint_new_config`,看到的是放寬後的值。失敗輸入:同一次推送改 `.lumos/config.json` 把 gate 設成 warn,同時帶進一筆判 `real` 的覆核命中。一般段仍擋,覆核段只提醒。
- 要共用 `lv["mode"]`,但 `lv` 在一般段出例外時是 `None`,計劃沒說這時覆核段怎麼取模式。
- `LUMOS_SKIP_LINT_NEW` 一般段會寫 `skipped-env` 事件,覆核段有沒有留帳,計劃也沒寫。

佐證:file: `scripts/lumos:42448-42500`、`scripts/lumos:42540-42566`、`scripts/lumos:74556-74575`

**F6 範圍 1 與 7:「沒跑原因四種」不完整,另有兩處不對稱**

severity: major
blocking: 是(計劃宣稱「沒跑要講出來」,實際有靜默路徑)

引句:「範圍 2 那支回的沒跑原因分四種:工具不可用、時間預算用完、參數太長、例外」

- 一般段還有三類:`oversize`(檔太大,會擋)、`sep_emptied`、逗號與分號路徑的檔(從 csv 命令拿掉,會擋)。覆核段只說「照新增告警閘的做法」,沒說這三類怎麼處理。照字面做會變成靜默沒掃。
- 「時間預算用完」在覆核段是 fail-open,一般段同一情形是 `undone kind=budget` 並擋。覆核吃剩餘預算,一般段慢就能讓覆核不跑。
- 範圍 1 的驗證只要求檔案佔位符,漏了 `{LINT_SARIF_OUT}`。沒有它時 `_lint_run_and_parse` 讀到空暫存檔,回 `([], False)`,被歸成 `env`。結果是每次都印「工具不可用」並 fail-open,整條覆核形同關掉。
  - 對照 `_lintcheck_validate` 是要求這個佔位符的。
- 宣告檔 JSON 壞掉或格式錯:`_lint_deps_load` 風格會回錯誤。覆核段若比照 `_lint_load_config` 回 `None`,就當成「沒有宣告」,連那行「覆核沒跑」都不印。
- 範圍 1 寫「讀法照 `_lint_deps_load`」,那支讀的是 `{"cmds":[…]}`;〈用詞〉與 S1 預期值卻是 `{"kt":[…]}`(副檔名到命令)。兩者形狀不同,實作時會撞上。

佐證:file: `scripts/lumos:42610-42640`、`scripts/lumos:42664-42690`、`scripts/lumos:41702-41703`、`scripts/lumos:39607-39625`、`scripts/lumos:41928-41945`

**F7 範圍 8:統計要的「被放行」資料,治理帳沒有**

severity: major
blocking: 是(升擋建議會算錯方向)

引句:「`real` 判定後被放行幾筆(人放、AI 放分開數)」

- `cmd_lint_waive` 寫的 `waived` 事件只帶 `origin`,以及情境段才有的 `scope`,加上被截短的 note。沒有指紋也沒有規則。
- 規則欄 `--rule` 是選填,只存在 `.lumos/lint-waivers.json`。計劃說「全部從治理帳算」,但治理帳裡無法把放行對回某筆判定。
- 失敗輸入:某規則判 `real` 20 筆、實際被放行 15 筆。統計數到 0 筆放行(低於一成),建議把它移到 `rules/` 升成擋。
- 要補的是 `waived` 事件加指紋與規則,以及 `_gov_row` 帶出。計劃只寫了 `rule_hits` 登記。

佐證:file: `scripts/lumos:41262-41266`、`scripts/lumos:42297-42310`、`scripts/lumos:17575-17640`

**資料狀態五問**

- 新舊版互讀:舊版讀新帳時 `rule_hits` 被忽略,沒問題。新版讀舊帳全部「還沒判」,會誤擋,這是預期。唯一疑點是 F4 的 `blind_judge` 空值被舊版拒收,只丟掉該筆,沒有其他影響。
- 寫一半:判定只寫治理帳一處,無此問題。
- 衍生對源頭不一致:指紋與處數是衍生的,「同片段處數」只會變多才重判。處數先減後增(同片段換位置)沿用舊判定,已寫進〈天花板〉,不另標。
- 時間:判定綁分支名加指紋,不綁版本;其中合併側的缺口是 F1。
- 不可逆:放行檔不被本案寫,退提交即回原狀,已讀,無 finding。

**各節狀態**

- 〈實務隱患〉、〈回退〉、〈依據來源〉:已讀,無 finding。
- 〈驗收條款〉、〈預期值表〉:S4、S5、S7、S8、S12 需配合上述 finding 補案例,見 F1、F2、F3、F6、F7。

總結:最高 major,共 7 條,全部 blocking;主要風險是合併側讀帳與人複查沒接上(F1)、AI 重判可蓋掉人的推翻(F2)、記帳卡在情境機制(F4),以及不一致的沒跑與放寬處理(F5、F6)。
