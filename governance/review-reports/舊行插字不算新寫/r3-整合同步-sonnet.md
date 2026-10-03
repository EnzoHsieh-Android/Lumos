severity: minor

# 外部審稿報告:舊行插字不算新寫(第 3 版)

鏡頭:整合與知識同步,加實務隱患。
Spec 與圖譜節點 `Projects/舊行插字不算新寫_計劃.md` 逐字相同(diff 無差異),所以固定席只能對 spec 本身判。

本輪沒有 blocking 級問題。前兩輪的修正大多成立,殘留的是同步清單不齊、兩處診斷語句講過頭,以及幾處接不上電。

## 前兩輪修正查證

- **喚醒那一路不動程式也能維持現況:成立,但有一個互動要補測試。**
  - 喚醒那一路用上線點版本加 `old_by`,是自己的整行集合,確實獨立於前半(`scripts/lumos:28440-28468`)。
  - 互動見 R3G4。
- **前綴提醒不套用:理由站得住。**
  - `_ns_rule_hints` 對新文法 RULE 回的是「筆記格子『RULE:』…」字樣的寫法警告,再加日期到期提醒(`scripts/lumos:27938-27944`)。
  - 與 spec 說的「格子開擋後會擋」一致。
  - 補更正的 RULE 行仍會被這個預告喊到,與 REVISIT 2026-10-15 的格子判定一致。
- **`relaxed` 與 `gov`、治理帳讀者:不會壞。**
  - `_gate_event` 對 kind 不做白名單,只驗閘名(`scripts/lumos:1220`,`note-shape` 已在 `_KNOWN_GATES`)。
  - `lumos gov` 的「閘的動作」只數 `blocked`、`skipped*`、`fail-open`(`scripts/lumos:7753-7755`),所以 `relaxed` 與 `hinted` 一樣不會顯示。
- **既有測試翻紅風險低。**
  - 配對要求「起點的行在終點消失」才有額度。
  - `t_note_shape_negation_*` 的舊行都沒消失,例如 `scripts/test_lumos.py:60685` 起的 `舊行功能還沒做`,而且 O 不到 8 字。
  - 推送前仍要跑 `-k note_shape`、`-k negation`、`-k slots`、`-k doctor_note_shape` 驗一次。
- **`_note_shape_eval` 其實有三個呼叫端,spec 只提兩個。**
  - 第三個是 `scripts/lumos:28105`,即 `_ns_skip_slot_extra`。
  - 容器參數有預設值,不傳就不收,所以無害。

## Findings

**R3G1**
severity: minor
blocking: 否 — 只是文字同步不齊,實作前補進〈做法〉7 即可
引句:「[[Systems/筆記內容閘]](三種舊行的關係、放寬帳、doctor 的訊息解讀)」
〈做法〉7 的要改字句清單漏了好幾處,我搜「沒違規的放行不寫」「放行不寫帳」「hinted」得到:
- `docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:46`:〈做法〉主敘述「★只有擋下(blocked)與…skipped-env寫事件,放行不寫★」。清單只列 [S7](第 70 行)與資源併發段(第 90 行)。
- `docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:121`:「沒違規的放行照舊不寫」。
- `docs/lumos-toolchain-knowledge/Issues/治理帳多個寫入者都沒上鎖.md:43`:該 Issue 逐一登記每個新寫入者,並約定 2026-10-11 回頭一起算。spec 只說「沿用既有 Issue」,沒要求把 `relaxed` 登記進去。
- `scripts/lumos:28555-28557`:`cmd_note_shape` docstring(清單有列)。另有 `scripts/lumos:28695` 附近 `_note_shape_report` 的註解「沒違規的放行才不寫」,以及 `_note_shape_eval` docstring 沒講新容器。
- `scripts/test_lumos.py:50367`:`t_note_shape_block_message_and_fail_open` 的 docstring「只有擋下寫事件、放行不寫」。
- `skills/lumos-project-notes/commands/03-寫回圖譜.md:8`:使用者端文字寫「舊行不管」,沒告訴人「補更正要在原行插字,不要另寫一行」。
  - 例:先新增一行 `DEP:… (更正:…)`,同時留著原行 → 整行照查會擋(S4)。
  - 這是消費專案唯一看得到的說明,spec 沒列。若動 skill,依鐵則要重跑注入。
- doctor 的字串與函式說明:見 R3G2。

**R3G2**
severity: minor
blocking: 否 — 只影響 doctor 一行訊息的診斷措辭
引句:「表示它**寫下的那一刻**就違規卻進了主線(warn 模式或繞過)」
這句診斷講過頭,而且〈做法〉7 沒列要改的 doctor 字串。
- 要改的字串在 `scripts/lumos:28517-28548`(兩處「多半是 --no-verify 繞過」)。`_note_shape_doctor_lines` 的 docstring「③…(抓 --no-verify 繞過)」也要一起改。
- 反例一,檔案後來才被建立:
  - 輸入:上線後某行寫了 `src/new.py:5`。寫入時該檔不存在,放行。
  - 之後 `src/new.py` 才被建立。
  - 預期:doctor 以終點的檔案清單重判,該行唸出來。但它寫下的那一刻並不違規。
- 反例二,多次補字累加:
  - 輸入:上線前就在的舊 DEP 行,在提交 1 插 300 字、提交 2 再插 300 字。
  - 預期:每次提交都以 HEAD 為起點、都放寬。
  - 但 doctor 起點是上線點,累計插 600 字,超過 500 字上限,改整行查。
  - 結果是正當放行的行被唸成「多半是 --no-verify 繞過」。
  - 推送也是同樣的跨推送累加。天花板 3 只講「提交時更嚴」,沒講這個「事後掃描更嚴」的方向。
- 建議:把診斷語氣改成「可能原因」並列出以上幾種。或者讓 doctor 的字數上限只算相鄰一步,或乾脆在天花板補一條。

**R3G3**
severity: minor
blocking: 否 — 屬於範圍說明,不影響第一層正確性
引句:「靠第二層判定者——送審的是整行,沒標哪一段是新插的」
第二層會抵銷 S1 的實際效果。
- 筆記內容審對新寫行也走 `_notelines_new`,推送時整行送審(`scripts/lumos:28947`,預設 `block`,見 `scripts/lumos:28742-28757`)。
- 補更正後的舊 DEP 行,在推送時仍是「新寫行」,需要判定檔。判定者看整行,仍可能判成 CODE 而擋推送。
- 例:S1 的行 `DEP:付款走舊閘道 scripts/pay.py 還沒換掉 (更正:…)`
  - 預期:提交通過。
  - 推送:第二層仍要求這行的判定,可能被判成程式碼推得出來。
  - 這正是「逼人改寫成歷史 WHY」的老問題。
- 天花板 1 只把第二層當作防夾帶的保險,沒承認它也會讓放寬在推送時失效。
- 建議:在〈做法〉1 或天花板明講「放寬只到第一層」,並說明補更正行在推送時由誰判、怎麼申訴。

**R3G4**
severity: minor
blocking: 否 — 行為仍是擋,只是標籤與路徑變了,要補一支測試釘住
引句:「照舊用自己的整行集合;筆記格子的舊行判定」
前半放寬後,喚醒那一路會接手重報,而這個互動沒有測試。
- 喚醒那一路用 `seen = {(v[0], v[1]) for v in viol}` 去重(`scripts/lumos:28443`)。被放寬的行不在 `viol` 裡,所以不在 `seen`。
- 例:
  - 輸入:上線前的舊行引用 `scripts/x.py:5`,補更正後提交,而 `scripts/x.py` 在這次才變成程式檔。
  - 前半:O 與 N 都犯同一條,被放寬。
  - 喚醒那一路:N 不在 `old`(上線點版本)裡,於是以「程式行號引用(新程式檔喚醒)」擋下。
- 結果:今天也是擋,只是標籤和路徑不同。「完全不動」在程式碼上為真,在行為上有邊角。
- S14 只守既有測試照綠。建議補一條驗收:此情形仍擋,且 `relaxed` 帳裡不把這行記為已放行。

**R3G5**
severity: minor
blocking: 否 — 影響第 8 週的粗判抽樣品質,不影響閘
引句:「重產被提醒的行時,跳過放寬帳記的路徑與行號」
否定現況句計劃的抽樣接得上去,但跳過清單不夠可靠。
- 否定現況句計劃第 7 節(`Projects/否定現況句配回頭條件_計劃.md:163-170`)用量測程式 `neg_revisit_measure.py` 重產被提醒的行,該程式判整行。改版後,配對行的正式判定改成只看插入字,與量測程式不再逐行一致。
- 跳過清單的缺陷:
  - 只存最多 50 條。
  - 路徑與行號在提交模式是暫存區的行號,提交若被 amend 或重排就對不上。
  - 抽樣窗口(約至 2026-11-25)橫跨改版日。
- 輸入:一次提交補更正 60 行 → 預期:第 51 行起不在跳過清單裡,量測程式會把這些行當「被提醒」放進抽樣母體,稀釋準度。
- 該計劃 S8 的「兩邊逐行相同」宣稱,spec 只說「補上這個例外」,沒說量測程式要不要同步改。
- 好處是:只取 `check` 是 `negation` 的 `hinted`,同時順手修掉了既有的汙染。前綴提醒的 `hinted`(`check: tag-hints`)現在就混在這份抽樣裡。
- 建議:量測程式也加同樣的「只多了字」濾法,或抽樣直接排除該窗口內有 `relaxed` 事件的提交。

**R3G6**
severity: minor
blocking: 否 — 超過既有寫帳慣例的大小上限,但寫入器本身不拒
引句:「每條配到的 `[路徑, 終點行號]`(最多 50 條,不帶原文)」
50 條路徑會超過 4 KB。
- 本 repo 的慣例是一行事件壓在 4 KB 內:
  - m1 的 `_ledger_append` 超過 4096 位元組就拒寫(`scripts/lumos:18277`)。
  - m1 事件從尾端丟 rows 直到 4096 以內(`scripts/lumos:33636-33647`)。
  - `Issues/治理帳多個寫入者都沒上鎖.md:43` 也記了這條。
- 實測:50 條 `["docs/lumos-toolchain-knowledge/Projects/否定現況句配回頭條件_計劃.md", N]` 以 `ensure_ascii=False` 序列化是 4550 位元組。這還沒算 `nodes`、`note`、`rules` 等欄位。
- `_gate_event` 本身不拒絕,所以不會報錯,只會破壞併發慣例。
- 建議:改成按位元組裁(同 m1 的作法),或把上限降到約 25 條。

**R3G7**
severity: minor
blocking: 否 — 屬於可觀測性缺口,不影響閘的判定
引句:「②治理帳八週內一次放寬事件都沒有(沒人補更正,機制是死的)」
`relaxed` 沒有機械讀者。
- 專案慣例是「每一種新事件都要指名一個讀它的地方」(`scripts/lumos:7749`)。
- `_SLOT_METRIC_KINDS`(`scripts/lumos:3759`)只收五種,`relaxed` 不在其中。所以 RETIRE-IF ② 與 ① 都只能人工翻帳,不能寫成 `[retire:度量 note-shape.relaxed …]` 讓 doctor 唸。
- `lumos gov` 也不顯示 `relaxed`。
- 建議二選一:
  - 在 `gov` 的「閘的動作」補一行 `relaxed` 計數。
  - 或明寫「第 8 週人工翻帳,到期的接電處是某條 REVISIT」。
- 另有一個連帶:放寬會讓 `note-shape.blocked` 的事件數下降,偏向觸發筆記形狀擋計劃 RETIRE-IF ③ 的「零觸發」。spec 已寫「寫明起算日」,但沒說抽樣怎麼補償。

**R3G8**
severity: minor
blocking: 否 — 實作時會自己卡出來,但規格應先寫死
引句:「起點版本用 `_nodehome_cat_blobs_capped` 批次讀、`utf-8-sig` 解碼」
`_nodehome_cat_blobs_capped(repo_root, specs, max_bytes)` 必須給 `max_bytes`,spec 沒指名用哪個上限常數(`scripts/lumos:26424`)。
- 超過上限時回 `None`,spec 把它歸入「這篇不配對」,這點行為沒問題。
- 現有呼叫端各用自己的常數,例如 `_ROLE_MAX_BYTES` 和 `_CODELOOP_BOOKKEEPING_HEAD_CAP`。借錯會讓大型筆記悄悄不配對。
- 另外,路徑含換行時整批回 `None`,這一批所有筆記都不配對(偏嚴,可接受,但值得在天花板列一行)。

## 實務隱患逐類

- **守衛面(繞過):** 抄一份旁邊加字、搬出圍欄、改前綴都被擋,與 S4、S6 一致。累加繞過沒有堵:每次推送各插 ≤500 字,各自放寬。天花板 1 已承認,補一個「相鄰兩次推送累計」的說明即可。
- **併發與寫帳:** 只讀 git 物件,新增一種寫入。見 R3G6(超過 4 KB 慣例)與 R3G1(Issue 未登記)。
- **效能與記憶體:** 子序列判定線性,每次呼叫 ≤5000 次,可信。起點版本批次讀有上限。上限常數未指定,見 R3G8。
- **相容與回滾:** 還原一個提交即回到整行查。已寫的 `relaxed` 帳不混進 `hinted`,成立。doctor 事後掃描的更嚴方向見 R3G2。
- **可觀測性:** 見 R3G7 與 R3G5。
- **金流、對外送出、不可逆:** 已排除的理由成立,本案只讀筆記與 git 物件。

## 圖譜鏡頭(固定席)

節點 `Projects/舊行插字不算新寫_計劃.md` 是本案自己,沒有宣稱既有行為或合約(沒有 ★INVARIANT★ 類行),所以這份設計不會破壞它。
- 不影響,理由:它的 `lands_in` 指向 `Systems/筆記內容閘`,該節點也沒有合約行。
- 該 Systems 節點的摘要有一行「判定跟量測程式逐行一致」與一行「沒違規的放行不寫治理帳」。這兩句在實作後都需要補例外,已併入 R3G1 與 R3G5。

總結:本案沒有擋住實作的問題,8 條 minor 在實作前後補齊即可。

最高嚴重度 minor,blocking 0 條
