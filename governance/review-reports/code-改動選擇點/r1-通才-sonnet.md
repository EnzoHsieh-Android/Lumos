severity: major

## g1 重跑判斷只看測試名集合:補強既有測試、修好環境後 choice-kill 不重跑,推送閘卻叫人重跑
severity: major
blocking: 是(處置指示照做不會動作,存活行與跑不出結果的行會一直擋推送;能指出具體失敗輸入且測試沒抓)

- **輸入**:某行上次記 `survived`(或 `no_result`),使用者把綁定的既有測試補強(測試名不變),或把壞掉的基準修好後再跑 `lumos choice-kill`。
- **壞在哪**:`_choice_kill_pick` 用 `evs[-1].get("tests_sha") == tests_sha` 判斷。`_choice_tests_sha` 只雜湊「平台:測試名」,測試本體改了不會變。`no_result` 的原因是基準不綠、逾時、編譯環境,這些也跟測試名集合無關。
- **預期 vs 實際**:推送閘的處置文字寫「測試太弱 → 補測試後重跑 lumos choice-kill」、「跑不出結果 → 修好後重跑 lumos choice-kill」。實際重跑只印「上次存活、守的測試沒變,這次不重跑」。帳上那筆不會更新,推送閘照擋。這段提示也沒提 `--only` 才能強制重跑。
- **重現(未跑完整 choice-kill,直接呼叫挑行函式)**:

  ```
  m._choice_kill_pick({"lines":[x]}, idx(no_result,tests_sha=S1), set(), set(), "S1", None)
  → todo [] carried {('a.kt','ffff…'): 'no_result'}
  m._CHOICE_PUSH_FIX["跑不出結果"] → 看 lumos choice-points 印的原因修好後重跑 lumos choice-kill;…
  ```
- **為何測試抓不住**:`t_choice_kill_incremental` 只測「新增一支綁條款的測試」會重跑。補強既有測試這條最自然的修法沒測。
- **規格**:S11 只寫「已 survived 而守的測試沒變」不重跑,沒寫 `no_result`。〈範圍〉2 第 108 行把 `no_result` 也併進去,理由「測試沒變,重跑結果一樣」對環境類原因不成立。

引句:「if disp in ("survived", "no_result") and only is None and evs[-1].get("tests_sha") == tests_sha:」
file: `scripts/lumos:77680`(`_choice_kill_pick`,patch 內 3473 行起);`_CHOICE_PUSH_FIX` 見 patch 3801–3808 行

## g2 回報上限的抽樣種子把「已放行的行」剔除,放行抽中的行會讓抽樣重洗、擋的行變多
severity: major
blocking: 是(違反 S16「只擋抽中的」與「已處置的仍算處置」;放行是等價壞法的主要處置路徑,測試只涵蓋 killed 路徑)

- **輸入**:20 行曾存活、上限 14,人把閘要求的那 14 行全部 `lint-waive choice:`。
- **壞在哪**:`_choice_push_judge` 裡 `if key in waived: continue` 在 `ever.add(key)` 之前。放行一行就讓 `ever` 縮小,`_choice_cap_pick` 的種子改變,抽中的批次重洗。規格第 98 行寫「帳上同鍵有任一筆 survived」,沒有排除放行。
- **重現**:

  ```
  before waive: blocked 14 unpicked 6
  after waiving the 14 demanded lines: blocked 6 unpicked 0
  after killing the 14 demanded lines: blocked 0 unpicked 6
  ```

  同樣是處置 14 行,殺掉是 0 行擋,放行反而又擋 6 行。放行一路放下去,上限形同取消。
- **為何測試抓不住**:`t_spec_gate_push_choice_cap` 處置抽中行只用 `killed` 事件,沒放行。
- **修法**:把 `ever.add` 移到 waived 判斷之前。

引句:「if key in waived:」
file: `scripts/lumos:77760` 附近(`_choice_push_judge`,patch 3901–3929 行)

## g3 字串串接的 `+` 只在「直接運算元」以引號開頭才排除,巢狀串接產出編不過的壞法
severity: major
blocking: 是(違反 S2「字串串接的 + 應不產生」,常見寫法會產出編不過的壞法,記 no_result 後擋推送,得逐行放行)

- **輸入**:`val s = name + ": " + id`。
- **壞在哪**:`_choice_excluded` 只看直接運算元 `A`、`B`。外層節點 `A = name + ": "` 不以引號開頭,`B = id` 也不是,不被排除。
- **重現(真 ast-grep 0.51.2,`choice-points`)**:

  ```
  src/main/kotlin/A.kt:4  C-11 AOR  val s = name + ": " + id → val s = (name + ": ") * id
  ```

  候選 `- * / %` 對字串全部編不過,6 個候選裡佔 4 個,由行指紋洗牌決定。抽中就是編不過,choice-kill 判 `no_result「壞法編不過」`,推送閘擋「跑不出結果」。
- **為何測試抓不住**:S2 的測試只測 `"id=" + n` 這種左邊直接是字面值的。
- **修法**:改成檢查整條 `+` 鏈的頂層運算元有沒有字串字面值或字串樣板。
- **註**:`s + t` 兩個變數都是字串屬於純型別問題,語法樹判不出,規格已承認。這條只針對「鏈裡明明有字面值卻沒排除」。

引句:「return any(x.startswith('"') for x in ops)   # 字串字面值、字串樣板,或左邊開頭就是字串的串接」
file: `scripts/lumos:76965` 附近(`_choice_excluded`,patch 2886–2894 行)

## g4 `gov --stats` 的「第一次跑殺掉率」把人裁寫回(via situation-rule)的第一筆也算進去
severity: minor
blocking: 否(只扭曲 RETIRE-IF 用的統計,不影響擋或不擋)

- **輸入**:對從沒跑過 choice-kill 的行直接 `situation-rule --point`。`_situation_rule_point_target` 只要求 `status == "mutant"`,事件 `attempt = len(ck)+1 = 1`、`via = situation-rule`、`verdict = killed`。
- **壞在哪**:`_gov_choice_count_verdict` 的 `if r["attempt"] == 1: c["first"][v] += 1` 沒看 `via`。
- **重現**:

  ```
  rows = [killed attempt1 via situation-rule, survived attempt1 via run]
  → c["first"] = {'killed': 1, 'survived': 1};印出「第一次跑殺掉率 1/2(0.50)」
  ```

  實際自動跑只殺掉 0/1。
- **修法**:`first` 只算 `via == "run"`。

引句:「if type(r.get("attempt")) is int and r["attempt"] == 1:」
file: `scripts/lumos:77912` 附近(`_gov_choice_count_verdict`,patch 1620–1633 行)

## g5 每個壞法的 choice-kill 事件帶 `aborted` 清單,沒過 `_gate_event_fit`,100 支守的測試時超過 4096 位元組
severity: minor
blocking: 否(S20 寫了位元組上限,但帳寫入端沒有硬上限,後果只是帳長得快;rubric 上算「測試沒涵蓋的條款」,但無錯行為)

- **輸入**:100 支守的測試基準全紅(Gradle 編譯壞時就是如此),`aborted` 列 100 個測試名。
- **重現**:同欄位組成下 `aborted` 帶 30 支 → 2963 位元組,帶 100 支 → 8073 位元組。
- **為何測試抓不住**:`t_spec_gate_push_choice_unverifiable` 量 choice-kill 事件時沒帶 `aborted`。
- **範圍**:`run` 事件有 `_gate_event_fit`,per-mutant 事件沒有。每次最多 30 個壞法 × 8KB。

引句:「if aborted:」(`_choice_event_extra` 內 `ex["aborted"] = list(aborted)`)
file: `scripts/lumos:77622` 附近(`_choice_event_extra`,patch 3438–3447 行)

## g6 `choice:` 放行與一般「新增告警放行」同池計數,doctor 的放行清單數與 AI 未看過數混在一起
severity: minor
blocking: 否(只影響 doctor 提示的口徑,不影響擋或放行)

- **背景**:情境段放行(`kt-situation:`)在代碼審 r2 通才 F3 之後被分開數。
- **壞在哪**:新加的 `choice:` 放行同檔,但 doctor 區段(`scripts/lumos:4217`)的 `_wl`(排除 `kt-situation:` 剩下的)和 `_lint_waivers_ai_pending(..., situation=False)` 都沒排除 `_CHOICE_WAIVE_PREFIX`。
- **後果**:「新增告警閘的放行狀況」的條數與「AI 放的還沒人看過」把選擇點放行算成新增告警。人讀數字會誤以為是 lint 規則跟專案不合。

引句:「_wl = {_k: _it for _k, _it in _wv.items() if not _k.startswith(_KT_SIT_WAIVE_PREFIX)}」
file: `scripts/lumos:4217`

## 圖譜鏡頭(固定席)
- 這次訊息明寫「鏡頭計算超時,沒附固定席節點」,沒有可逐條判的固定席,不另判。
- patch 內只有 `skills/kotlin-idioms/checks-catalog.md` 的選擇點表與乾節點規則:我用 `check.py --catalog-only` 實跑,「型錄問題 0 個」,統計行(31 列、14 列)對得上。
- 我沒看到圖譜筆記本身的 patch,所以「程式與筆記同提交」那條沒法判。

## 抽查過、判為沒問題
- 治理帳新欄位型別:拿既有 125,642 行治理帳(排除 choice-kill)逐行比對新登記的鍵,無任何型別衝突,舊事件不會被 `_gov_event_types_ok` 丟掉。
- `_gate_event` 的 `head_sha` 有存,`_choice_push_event` 的去重有效。
- `_lint_wt_cfg_inside`、`_lint_waivers_parse`、`_kill_log_rows`、`_isolated_worktree` 的抽出,語意沒變。
- 巨大 `+` 鏈(1500 項約 7.8 秒、690MB;3000 項時 ast-grep 被 SIGXFSZ 殺掉)走「沒檢查到」,推送時是只提醒不擋,可接受。
- pre-push 的 bash 空陣列慣用法正確。
- 引用的符號(`_real_chars`、`_DAY_RE`、`_kt_sit_*` 等 44 個)全部有定義。

最嚴重:major;blocking 共 3 條
