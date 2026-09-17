severity: blocker

**逐節審查結果**

---

一、frontmatter/summary/decisions(d1–d10)— 已讀,無 finding。d9 的 34/29/5/0/0 數字經我自己重新掃描 `docs/lumos-toolchain-knowledge/**/*.md` 開頭欄位驗證,與 spec 完全一致(538 篇總數、34 篇掛標、守衛面 29/不可逆 5/金流 0/對外送出 0),量法陳述可重現。

---

**finding 1**
severity: blocker
spec 第 80–90 節「為什麼」表格第 4 列:「分級用量 | standard 629 / high 83 / light 3」,同一數字重複於 summary KEY 行(「輕量檔 715 筆只用 3 次」)。這是 r1 A18(「沒回答 light 分級為什麼沒人走」)的正面回應,也是 panel 派工詞指名要查的優先項①。我用審查帳 `docs/.canary-log.jsonl` 以多種合理口徑重算(design-loop 記錄層級、去重迴圈層級、對齊 spec 聲稱的 2026-09-16 那個 commit),light 都落在 11–12,而不是 3;629/83/3(合計 715)這組數字在我試過的任何口徑下都無法重現。
引句:「分級用量 standard 629 / high 83 / light 3」
file: `docs/.canary-log.jsonl`(commit bf301098,對齊 spec 聲稱的 2026-09-16 資料日)— 篩「design-loop(`loop` 不以 `code` 開頭)」後,記錄層級 tier 計數 = standard 622 / high 90 / light 12;去重到迴圈層級 = standard 93 / high 9 / light 11。兩種口徑都與 3 差 4 倍以上,且都湊不出「715」這個分母。
blocking: 是——這個數字是 d3(「軟提醒已證明沒人照做,句式規則硬擋才有正當性」)的實證支柱,也是 panel 明確指名要重驗的一條;不同於 d9 那組數字有寫死的量法(只認開頭欄位 risk/ 標籤),這組數字沒有給出任何可重現的量法陳述,而且我重算出的結果與宣稱值不一致,屬於「重驗即翻案」的等級,不是措辭問題。

---

**finding 2**
severity: major
spec 第四節末段規劃「留痕走既有審查帳寫入口 `cmd_canary`,把 `kind` 的封閉列舉擴充一個 `spec-gate`」,並要求「讀側 `_round_valid_m2` 也要認得這個 kind」,但沒有說清楚 spec-gate 記錄在這個判準裡該怎麼算。
引句:「留痕走既有審查帳寫入口 `cmd_canary`,把 `kind` 的封閉列舉擴充一個 `spec-gate`」
file: `scripts/lumos:6337-6338` — `_round_valid_m2` 目前硬寫「kinds = [r.get("kind") for r in recs]; if any(k not in ("caught", "missed", "none") for k in kinds): return False; return (kinds.count("caught") + kinds.count("none")) >= 2 and kinds.count("missed") == 0」,這支函式是 fixed-seat 清單裡 `Systems/design-loop` ★INVARIANT★ 「處置閘第五步」判定用的同一顆謂詞(注解自己寫「gate/fold/定錨/ledger/W 歸屬五處共用」)。單純把 `spec-gate` 塞進白名單元組,若沒有額外規則排除它參與 `(caught+none)>=2` 的計數,會讓「兩份真的 canary 命中或 none 輪」這個安全語意被一份跟置入測試完全無關的 spec-gate 記錄稀釋掉。
blocking: 是——這條直接碰觸固定席 `Systems/design-loop` 的 ★INVARIANT★ 合約行(處置閘第五步),spec 只說「要認得」沒說「怎麼認」,implementer 依現有文字最自然的做法(直接加進白名單元組)就會在不知情下弱化這個安全謂詞;需要在動工前把「spec-gate 記錄是否計入 M2 分子、還是完全繞過這條判準走獨立分支」寫清楚。

---

**finding 3**
severity: major
第六節三條絕對門檻(blocker 逃逸一份即退、前 30 份 major≥3、push-gate:unreviewed ≥2)全篇找不到任何推導依據——不像 d9 的 34/29/5/0/0 有寫死的量法,這三個數字沒有統計基礎(此刻雙向門一份都還沒上線,不可能有經驗分布可比對)。
引句:「①任何一份雙向門計劃出現 blocker 級逃逸 → 立刻退回;②前 30 份雙向門計劃裡 major 以上逃逸 ≥ 3 份(10%)→ 退回」
blocking: 否——spec 自己在「誠實界線」與 RETIRE-IF 承認「在 30 份雙向門計劃跑完之前不得宣稱有效」,且 REVISIT:2026-10-17 有排回頭看,數字本質上是待驗證的假設而非既成事實,不必卡這輪放行,但寫作角度應該明講「這三個數字是拍的、靠 RETIRE-IF 自己收斂」,而不是用條列方式讓讀者誤以為有實證基礎。

---

**finding 4**
severity: major
「每條新行為各自紅」(第四節雙向門放行條件③)代表一份 8 條驗收條款的計劃,在規格閘放行前作者要先寫出 8 支各自會失敗的測試——這是把測試撰寫成本前移到設計審查之前(而不是像舊制那樣審完再實作再寫測試)。全篇(含「誠實界線」「進度」兩節)沒有任何地方估過這個前置成本,RETIRE-IF ②雖然預期「大家用不寫 [S] 繞過」,但沒說繞過的動機正是這個成本。
引句:「沒標 `[keeps]` 的每一條,其測試在規格閘時必須是紅的」
blocking: 否——這是流程可行性的隱患而非機制錯誤,本篇自己 20 條驗收條款也照這個規則寫,算是自我驗證了「寫得出來」,但沒有量出「多花多少工時」,建議 S13 健檢或 RETIRE-IF ②直接加一項「平均每份計劃補測試的工時」量測,否則「有條款的計劃比例下降」這個訊號出現時分不清是規則太嚴還是單純沒空。

---

**finding 5**
severity: major
第四節「推送前」段落:「改成讀審查帳裡所有 `kind: spec-gate` 且計劃仍 `doing` 的留痕,取它們的 `[test:]` 清單,這些測試全綠才准推」——S21 的條件是「對所有仍 doing 的雙向門留痕」,沒有按本次 push 的 diff 範圍篩選。這代表任何一次 push(哪怕只改一行跟任何 spec-gate 計劃無關的程式)都要等所有在途雙向門計劃的測試清單全綠,計劃越多、閘越慢,而且一份放置太久沒人管的 `doing` 計劃會變成擋住所有人推送的地雷。
引句:「這些測試全綠才准推」
blocking: 否——功能上不會做錯事(寧可多擋不會少擋),但沒有範圍限定或逾時/失效機制,是可預期會隨雙向門計劃數量增長而惡化的維運隱患,建議在第四節或第六節補一句「doing 超過 N 天或已無新進度的計劃排除在此清單外,另計逃逸」。

---

**finding 6**
severity: minor
第五節逃逸帳分母「逃逸帳 6 筆 / 127 條迴圈」——escape log 檔案行數(6)我核對相符,但 127 這個迴圈分母無法重現:我用「`loop` 欄不以 `code` 開頭」篩出的唯一設計迴圈數是 159,不是 127。
file: `docs/.escape-log.jsonl`(6 行,吻合)vs `docs/.canary-log.jsonl` 去重迴圈數 159。
blocking: 否——這個數字只是「從沒量過漏網率」這句話的背景陳述,不影響任何機制判定,且差距(127 對 159)遠小於 finding 1 的 4 倍落差,可能是篩選口徑不同(例如只算有 finding_kinds 標記或某個日期後的迴圈);標為低嚴重度純粹因為找不到明確失敗場景,但既然帳面數字已被 finding 1 證明有可重現性問題,建議一併重驗。

---

二、條款句式(一條文法)— 已讀,無 finding。r1 已裁定「五型只是名字,機械上一條文法」(A20),新文法禁止複合觸發、強制主體+「應」+回應的結構,相對舊的 [SN]+[test:] 慣例確實多換到「一條款一行為」的可驗性;既有 26 篇用 `[S1]` 格式的舊筆記靠 `_CLAUSE_GATE_SINCE`/`_SPEC_GATE_SINCE` 不回溯生效切開,不構成遷移成本。

三、綁定規則(keeps/manual/回退節)— 已讀,無 finding。「綁一支永遠失敗的樁測試」殘餘已誠實寫明留給代碼審/guard-kill 收尾,沒有假裝解掉。

五、逃逸自動記三來源篩法 — 除 finding 5 外,已讀,無 finding;`finding_kind`、`_CI_RED`、`_vault_write_lock`、NFC 正規化(`scripts/lumos:7557`)等機制在現有程式裡都查得到,S9(代碼審來源)在 `scripts/lumos:6178-6188` 已真的落地,與 spec 描述一致。

七、要動什麼/回退/誠實界線 — 已讀,無 finding。

固定席逐項判(是否破壞其宣稱的行為/合約):
- `Systems/design-loop`(★INVARIANT★ 處置閘第五步):**會影響** — 見 finding 2,`_round_valid_m2` 的 kind 白名單擴充語意未定死。
- `Systems/canary-audit`(record/second 落盤自驗、second 唯 telemetry):不影響——spec 沿用同一顆 `_jsonl_append_verified` 寫入函式,未改動 `cmd_canary_second` 的邏輯或呼叫路徑。
- `Systems/guard-kill`(rc 優先序、--json 純淨):不影響——規格閘不呼叫 guard kill,兩者是平行機制。
- `Systems/bound-tests-gate`(★INVARIANT★ code-loop 對合約行綁測試逐支真跑):不影響——spec-gate 存在性檢查沿用 `_clause_bindings_for`(處置閘第五步既有那支),跟 bound-tests-gate 驗證 ★INVARIANT★ 合約行是不同檢查路徑,兩者不互相覆寫。
- `Systems/anchor-integrity`(★RISK★):不影響設計本身——pre-push 改動已照既有錨點流程走 `anchor approve`(進度段已記錄),spec 未改動錨點判定邏輯。
- `Systems/每支檔有家`:已滿足——`lands_in` 列了 `Systems/design-loop` 與新開 `Systems/規格閘`,兩支要動的檔(`scripts/lumos`、`scripts/hooks/pre-push`)都有家可歸。
- `Issues/code-loop守衛main-direct盲區`(status: done):不直接相關——該盲區已用 push range 取代 merge-base 修掉,S21 的範圍問題(finding 5)是新的、不同的隱患,不是這個舊 Issue 的復發。

---

最嚴重 severity:blocker;blocking 計 2 條(finding 1、finding 2)。
