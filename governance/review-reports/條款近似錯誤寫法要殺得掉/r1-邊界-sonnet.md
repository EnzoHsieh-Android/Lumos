severity: major

審稿範圍:逐節讀完 r1-snapshot.md,並對照 `/Users/enzo/harness/lumos-near-miss/scripts/lumos` 與前置分支 `/Users/enzo/harness/lumos-srl-android/scripts/lumos`。交叉引用(範圍 1–4、S1–S10 對預期值表各列、天花板 2、〈用詞〉各項)目標都存在、說法一致,已讀,無 finding。

## b1 `[near:]` 含 `]` 的形狀檢查,用 INV_TAG_RE 實作根本偵測不到
severity: major
blocking: 是,照字面把 `near` 加進 INV_TAG_RE,「含 `]` 要擋」會被靜默放行,並在條款正文留下殘渣,弄壞雜湊與文法判定。
- 位置:〈用詞〉近似錯誤寫法「不得含 `]`(含了會讓標記截斷)」,以及範圍 1「INV_TAG_RE 的名單加 `near`……含 `]` 也擋」。
- 問題:INV_TAG_RE 是 `\[(?:…):\s*[^\]]+…\]`,遇到第一個 `]` 就收尾。含 `]` 的 near 只會被截成一個「看起來合法的短標記」,規格閘無從得知後面還有字。
- 實測(把 `near` 加進 INV_TAG_RE 後):
  - 輸入 `[near:用 a[0] 代替 b[1] 的寫法]`,剝完剩 ` 代替 b[1] 的寫法]`。比對到的內容是 `用 a[0`,形狀「合格」,殘渣留在 `_clause_body_of`,改變 `_clause_sha` 與文法輸入。
  - 輸入 ``[near:用 `a]` 代替 b]``,剝完剩 `` ` 代替 b]``。
- 應該怎樣:實作要在標記後多檢查殘留的 `]` 或 `[`(或直接放行成對括號),而且要有專屬測試。現有的 `_slot_scan` 能處理成對括號,見 b2。

## b2 `[near:]` 的掃描器沒選定,反引號、全形、大小寫三種寫法的結果互相矛盾
severity: major
blocking: 是,「第幾個」、`near_text`、雜湊會因掃描器不同而算出不同的值,有效紀錄跟著對不上;而且這份計劃自己的條款行就會踩到。
- 位置:〈用詞〉第幾個、有效紀錄,範圍 1。
- 問題:
  - `clause_bindings` 看的是 `_clause_visible` 的可見行,反引號 span 已被剝掉,`_strip_inline_markup` 在 `scripts/lumos:375`。
  - `_clause_sha` 與 `_clause_body_of` 吃的是原始行(`scripts/lumos:13913`),INV_TAG_RE 不管反引號。
  - spec 沒說 `[near:]` 的偵測、計數、實字數、`near_text` 用哪一邊。
- 具體例,三種寫法兩種掃描器的結果相反:
  - 反引號包住的範例:條款行含 `` `[near:用 a 代替 b]` `` 當說明文字。可見行不算宣告;原始行會算,雜湊也會剝掉它。
  - 反引號在 near 內:`[near:改用 `flatMapConcat`]` 這種中文作者常見的寫法。可見行剩 `[near:改用 ]`,只有 2 個實字,被判太短;原始行是合法的。
  - 全形冒號與大小寫:`[near:用 …]` 寫成 `[near：…]` 或 `[NEAR:…]` 時,INV_TAG_RE 不認,偵測不到,規格閘回報「沒有 near」。作者明明寫了,訊息卻無從解釋。`_clause_body_of` 對 manual 另外處理了 `[:：]`,有先例。
  - 空標記:`[near:]` 不被 INV_TAG_RE 剝掉(要至少一個字),也不被計入,殘渣留在條款正文。
- 這份計劃自己會踩到:`[S2]` 那行含反引號範例 `` `[near:無 …]` ``。用原始行掃會把它當成理由只有 1 字的壞標記,擋住這份計劃;用可見行掃則是「沒有 near」,一樣擋。S1、S3 的行也各含 `` `[near:]` `` 這種文字。
- 另外:repo 有「全檔唯一」的欄位掃描器 `_slot_scan`(`scripts/lumos:4912`,認全形冒號、不分大小寫、成對括號、略過反引號,見 `_SLOT_KEY_RE` 在 4905)。spec 沒講為何不用它。專案記憶「防護工具先找既有」要求自寫前先搜。
- 應該怎樣:spec 要寫死一種掃描器與一份「實字」定義,並加上「條款行含反引號範例」的測試。

## b3 有效紀錄沒比對「條款現在綁的測試」,換成較弱的測試後舊紀錄仍有效
severity: major
blocking: 是,照字面實作可以不重跑殺傷力就換掉被證明過的測試。
- 位置:〈用詞〉有效紀錄,以及範圍 3 的比對項。
- 問題:紀錄有 `test_name`,但有效性列了「計劃、條款編號、條款雜湊、第幾個、那句原文」,沒要求「現在條款綁的測試」等於紀錄的 `test_name`。`_clause_sha` 不含 `[test:]`(`scripts/lumos:13913` 註解自己說「不含綁的測試」)。
- 佐證:人裁那條路明確補了這一步,`_spec_gate_ruled_events` 比 `got[1] == {e["test_name"]}`(`scripts/lumos:14571` 附近),且寫明原因「多綁、換綁都不算」。
- 具體例:S1 原綁 `t_strong`,clause-kill 殺掉並記帳。作者把 `[test:t_strong]` 改成 `[test:t_weak]`(只送一次值的版本),雜湊不變、`old` 仍在,推送前那一道放行。這正是這份計劃要防的洞。
- 另外,測試本體被改弱也不會失效,這屬於天花板 2 的「周邊」範圍。但「換綁」可以機械比對,不該歸進天花板。

## b4 `--file`、`--old`、`--new` 沒有任何約束,壞法可以打在測試檔,與近似錯誤寫法也無關
severity: major
blocking: 是,可以用打壞測試檔的方式得到「殺得掉」紀錄,機制整個空轉。
- 位置:範圍 2「驗」那一串,以及〈用詞〉殺得掉。
- 問題:
  - 驗證清單裡沒有「`--file` 必須是正式程式、不是測試檔」。
  - 沒有「`--old` 要落在 `[near:]` 描述的位置」。人裁路徑有:`--old` 要「落在這一段裡、含那一列的觸發字」(前置分支 `scripts/lumos:76063` 附近的 argparse 說明)。
  - `--new` 與 `near_text` 之間沒有任何關聯,`near_text` 只出現在 `note`。
  - 具體例:`--file src/test/.../XTest.kt --old "assertEquals(1" --new "assertEquals(2"` 必紅,判 killed;或 `--new "throw RuntimeException()"` 也必紅,都拿到有效紀錄。
- 路徑形式:人裁路徑把 `kfile` 換算成「平台根所在 repo 最上層」的相對路徑(前置分支 `scripts/lumos:75898` 起,註解說子目錄平台會指錯)。spec 沒說 `--file` 用哪個基準,但推送前要用 `git show <提交>:<file>` 對回去。monorepo 平台根在子目錄時,紀錄的 `file` 與 git 路徑可能不一致,結果誤擋或誤放。`./a/../a`、大小寫、反斜線也沒有正規化。
- 應該怎樣:spec 要寫明基準與正規化,並禁止測試檔當目標(可用 `_nodehome_is_test`)。要不要把 `--old` 與 near 掛勾,至少要挑一個明確選項,不能留白。

## b5 推送前那一道套用到哪些狀態、哪些條款沒定義,設計階段或部分實作就被擋
severity: major
blocking: 是,兩種合理實作會給出相反的行為,其中一種會把設計審的推送整個卡死。
- 位置:範圍 3「接在 `_spec_gate_push_check` 現有的計劃清單上」。
- 佐證:`_spec_gate_push_scan` 的 `cands` 含「範圍改到的任何狀態計劃」(`scripts/lumos:17243`);預期值表那圈明確限定在 `_live`(doing,或這次碰到的 done)。
- 具體例:
  - 一份 high-risk、status: todo 的計劃,只是進設計審、推送計劃檔本身,清單內有它。如果近似錯誤那一道沒套 `_live`,每個 `[near:]` 都沒有紀錄,整份計劃被擋。這時還沒有實作,根本無從跑 clause-kill。
  - doing 計劃分多次推送實作:第一次只推 S1 的實作,卻因連到被碰到的 Systems 節點而被要求 S2–S5 全部有紀錄。
- 免除集合沒定義:
  - `[keeps]` 條款綁的是既有測試,近似錯誤寫法沒意義。範圍 1 只免 `[manual:]`。
  - 人裁寫回的條款(`_spec_gate_ruled_ids`)已經過殺傷力,`_expected_requirement` 把它們從 `new` 扣掉,近似錯誤這邊沒說。
- 應該怎樣:寫明「只在 `_live` 的計劃」「只對 `new - ruled` 的條款」,以及部分實作的處理(例如只對 `old` 還在的條款要求)。

## b6 新閘名與生效日要登記的清單、測試總開關沒提
severity: minor
blocking: 否,S4 與既有的漂移守衛測試會立刻翻紅,但照字面實作會先寫不進帳。
- `_gate_event` 對不在 `_KNOWN_GATES` 的閘名直接拒寫,回 False(`scripts/lumos:1840`)。`clause-kill` 要加進 `_KNOWN_GATES`(17706 起)。
- 人裁那組另外登在兩處,忘了會被守衛測試翻紅:17760 的注釋清單、20659 的「非關門」`(gate, kind)` 集合。
- 測試總開關:`scripts/test_lumos.py:159` 對 `LUMOS_HIGH_RISK_EVIDENCE_SINCE` 預設 9999-12-31,讓既有規格閘測試停在生效前。`LUMOS_NEAR_SINCE` 若不同樣預設,3700+ 案例裡凡是 high-risk 又綁測試的計劃都會突然要求 `[near:]`。
- CLI 說明目錄(78119 那組)也會有同名描述守衛。spec 只提「同 `_expected_since` 的寫法」。

## b7 生效日當天要求、與 repo「設隔日不設當日」慣例衝突,這份計劃自己也會被擋
severity: minor
blocking: 否,日期常數在上線時可調整,但 spec 的文字會讓上線當天出事。
- 位置:〈用詞〉生效日(`_NEAR_SINCE` 為「上線當天」、「不早於」要求),範圍 1。
- 佐證:`scripts/lumos:15775` 註解寫明慣例「設隔日不設當日(合入當天白天用舊碼寫的帳,日粒度切不開先後)」。`day < since` 是比較式,所以 `day == _NEAR_SINCE` 當天要求;這份計劃 created 與首次進 git 都是 2026-11-13,若同日上線自己先被擋。
- `scope` 參數沒指定:預期值表那圈傳 `scope="note"`(`scripts/lumos:14595` 附近,註解說不限 `_計劃.md`,否則其他命名的節點會被當成新計劃)。spec 的 `_plan_effective_day` 預設 `scope="plan"`,用到非 `_計劃.md` 的節點日期會讀不到。
- created 缺、格式錯:`_plan_effective_day` 取 `str(created)[:10]` 並以 `_DAY_RE.fullmatch`,不合就被忽略,兩邊都讀不到回 None,呼叫端當生效日之後(要求)。這是對的,但 spec 沒有一句講。
- 淺複製只看 created,所以 CI 淺複製下可以把 created 倒填成更早日期來免除。本機推送閘有完整歷史,所以只是 CI 這一側的天花板,可在天花板補一句。

## b8 `[near:無 …]` 的邊界與「實字」的定義缺漏
severity: minor
blocking: 否,不同實作會做出不同行為,但每種都是保守方向。
- 位置:〈用詞〉免宣告與近似錯誤寫法、預期值表 S2 兩列。
- 「無」後面沒空白:`[near:無法保證順序的寫法會讓舊結果顯示]` 是合法的 near,不是免宣告。反過來 `[near:無,純格式輸出沒有錯寫法]`(全形逗號)會被當成 near,逼作者去跑 clause-kill。
- `[near:無]` 沒理由:會被當成只有 1 字的普通 near,訊息說「太短」而不是「免宣告缺理由」。
- 空白種類:全形空白 U+3000 是否算分隔沒講(Python 的 `\s` 會算)。
- 「實字」:`_real_chars` 與 `[^\W_]` 兩種既有判法不一樣(預期值表用前者)。`>=` 這類符號、重複字(例如 `aaaaaa`)是否算,spec 都沒寫。S1 預期值表的 `[near:用 >= 代替 >,…]` 靠的是中文字數,不是符號。
- `[near:無 …]` 的理由只要 10 個字就能繞過整個機制,沒有任何占比的度量。RETIRE-IF 只量「第一次就殺掉的比例」,沒量「無」的比例。

## b9 clause-kill 對 drifted、abort、error 的 rc 與記帳沒定義,和 guard kill 的 rc 約定不一致
severity: minor
blocking: 否,不會造成錯誤放行,但訊息誤導且會讓好紀錄被蓋掉。
- 位置:範圍 2「記」那一條、S5。
- `cmd_guard_kill` 的 rc 約定是 survived→1、drifted/abort/error→2(`scripts/lumos:27769` 說明,也是固定席 INVARIANT)。spec 寫「判定不是殺得掉時 rc 1,印『補測試讓它紅』」,把 baseline 非綠、`old` 命中 0 或多次、`file` 開不了都歸到 rc 1,訊息會叫作者去補測試,實際原因是環境或壞法本身。
- 「不論判定都記一筆」加「同一條款同一個第幾個取最新一筆」,一次 Gradle 失敗的 abort 會蓋掉先前有效的 killed 紀錄。
- 另外紀錄沒存 `new`(欄位清單只有 `old`),事後看不出當初套的壞法是什麼,推送前也驗不了;kill-log 也沒存。建議把 `new` 與 imports 一起記。
- 推送前讀的是工作目錄的治理帳(`_gov_vc_gate_events` 讀 `root/docs/.governance-log.jsonl`),`old` 卻讀推送提交;紀錄沒提交時本機會過、CI 才發現。可在天花板 3 補一句。

## 固定席節點逐條判:Systems/guard-kill
- ★INVARIANT★ rc 優先序(survived→1、drifted/abort/error→2):不影響。新增的 `source` 只改寫入殺傷力帳本的欄位,不碰 rc 判斷,但見 b9,clause-kill 自己把非 survived 的結果全部映成 1 是呼叫端的選擇,不是改了這條合約。
- ★INVARIANT★ `--json` 成功跑完時 stdout 恰一行 JSON:不影響。clause-kill 以 `as_json=False` 呼叫,`source` 不增加任何 stdout。
- 否決「另抽共用殺傷力函式」:spec 沿用 `recipes_override`,與該決定一致。

## 實務隱患鏡頭
- 輸入形狀(空、空白、全形、反引號、`]`、換行、超長):見 b1、b2、b8。超長的 `near_text` 與 `old` 進治理帳會超過 4096 位元組,但 `_gate_event_fit` 註明超過照寫,所以不會丟事件。這點沒問題。
- 路徑與基準:見 b4。
- 日期與淺複製:見 b7。
- 計劃在消費專案的路徑:紀錄的 `plan` 欄應與 `situation-rule` 一致用圖譜內路徑(`Projects/…`),spec 沒說。一個 repo 裡兩個圖譜有同名計劃時會撞,屬於罕見情境。
- 併發與交易:已排除,單人依序操作,spec 的說明成立。
- 回顯安全:blocking 訊息若印 `near_text` 或計劃名,現有程式習慣走 `_kill_esc`,spec 沒提醒;依專案威脅模型(單人自用)可放行。

最嚴重:major;blocking 共 5 條
