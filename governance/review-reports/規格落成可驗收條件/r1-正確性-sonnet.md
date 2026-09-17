severity: blocker
# 審查報告(外部投稿:規格落成可驗收條件_計劃 r1)

severity: blocker

## 逐節 finding

**[F1] 一、門怎麼判 — 雙向門的自證機制會把自己判成單向,自相矛盾**
severity: blocker
blocking: 是——判準:雙向門是本案整套設計的核心分流,這條走不通,實作者會做出一個「雙向門實質上永遠判不成」的系統,跟宣稱的效果完全相反。
硬單向門第 1 條規則說「討論這些詞也會命中」,而雙向門必須寫的四行 `已排除:<類>:<理由>` 恰恰**必須用類別名稱本身**來寫(例:「已排除:金流:…」)。我直接用 spec 附的 `PITFALL_CLASSES` 正則跑這四行範例,金流/對外送出/不可逆三類的「已排除」句子本身就會命中同名關鍵字類別,把文件打回單向門。
引句:「光是**討論**這些詞也會命中——誤判的代價只是多一次審查,落在安全那邊,接受。」
file: `/Users/enzo/harness/lumos-toolchain/scripts/lumos:16962-16966`(`PITFALL_CLASSES` 定義,`payment` 含 `金流`、`external-send` 含 `送出`、`prod-irreversible` 含 `不可逆`)
佐證:用該表正則實測「已排除:金流:本案不碰業務資料…」命中 `payment`、「已排除:對外送出:…」命中 `external-send`、「已排除:不可逆:…」命中 `prod-irreversible`,三/四類自我否決;只有「已排除:自我治理:…」不命中(因為 `self-governance` 關鍵字表不含「自我治理」字面)。這不是我編的極端案例,是 spec 自己在「## 實務隱患」節示範的寫法(同一份文件裡「金流/對外送出/不可逆」三行已排除句已經活生生示範了這個自我否決)。

**[F2] 一、門怎麼判 — 「自我治理」與「守衛面」是兩個不同標籤,evidence 對不上被它拿去證明的東西**
severity: major
blocking: 是——判準:實作者無從決定硬單向門第 1 類的關鍵字類要對齊 `risk/守衛面`(標籤枚舉)還是另立「自我治理」,兩邊字面不同、機制也不同(一個是全文關鍵字掃描、一個是 frontmatter 標籤),寫錯任一邊都是做出偏離設計意圖的系統。
引句:「金流/對外送出/不可逆/自我治理;表在 `PITFALL_CLASSES`,沿用不另建」
file: `/Users/enzo/harness/lumos-toolchain/scripts/lumos:4422`(`_RISK_ENUM = {"金流", "對外送出", "不可逆", "守衛面"}`,沒有「自我治理」這個值)
「為什麼」節拿來論證「標籤稀疏、該把預設翻向單向」的 40 篇統計,量的是 `risk/` **標籤**(含 `守衛面`),但硬單向門第 1 項是**關鍵字比對**(含 `自我治理`)——兩種完全不同的判定機制被同一段文字當成同一件事在論證,稀疏性證據並不涵蓋真正會頻繁誤觸發的關鍵字掃描路徑(見 F1)。

**[F3] 一、門怎麼判 — 「前掃訂正後」的數字本身仍然是錯的**
severity: major
blocking: 是——判準:d8 這個仍生效(valid: true)的決策拿它當論證依據,數字站不住就等於決策的理由是假的,實作者會照著錯的統計去校正閘的鬆緊。
引句:「風險標籤 538 篇裡只有 **40 篇**掛了——守衛面 29、不可逆 5、金流 2、對外送出 0」
佐證:我直接掃 `docs/lumos-toolchain-knowledge` 的 frontmatter(只認 `---` 區塊內 `- risk/<值>` 這一行,排除正文/範例提及),得到 34 篇(守衛面 29、不可逆 5、金流 0、對外送出 0),不是 40/29/5/2/0。「金流 2」那兩筆命中,查實是 `Projects/圖譜結構化查詢_計劃.md` 與 `Verification/2026-08-16_圖譜結構化查詢query落地.md` 兩篇文章裡在描述**另一個消費專案(Landmark)**的範例查詢結果(`risk/金流+INVARIANT`、`risk/金流 --active` 等指令示例),不是本 repo 真實掛在某篇 frontmatter 上的標籤。「前掃訂正」把舊數字(34/守衛面全占)改成新數字(40),結果新數字反而是錯的、舊數字的 34 這個總數才對(但舊數字說「三類零篇」也錯,真實不可逆是 5 篇)——換句話說兩版數字都沒對過,doctrine 要求的「肯定斷言要驗證」在這裡沒有真的做到。

**[F4] 三、綁定規則 — 「沿用 `_classify_one`」引用了錯的函式**
severity: major
blocking: 是——判準:實作者照這句話去接既有機制,會接到完全不對的地方(★INVARIANT★ 綁定判定),而不是真正負責 `[SN]` 條款綁定判定的那支函式,導致重工或行為不一致。
引句:「每條條款只准 `[test:<測試名>]`,測試要真的存在(沿用 `_classify_one`)」
file: `/Users/enzo/harness/lumos-toolchain/scripts/lumos:8861`(`_classify_one` docstring:「單條 ★INVARIANT★ 的綁定狀態」——判的是 `classify_invariants`/`guard-list` 用的 ★INVARIANT★ 合約行,跟 `[SN]` 條款完全無關)
真正負責 `[SN]` 條款存在性/紅綠判定、且被 `_disposal_clause_step` 實際呼叫的函式是 `_clause_bindings_for`/`_clause_summary`:file: `/Users/enzo/harness/lumos-toolchain/scripts/lumos:4698`(`_clause_bindings_for`)與 `/Users/enzo/harness/lumos-toolchain/scripts/lumos:15672`(`_disposal_clause_step` 呼叫它)。PRIOR-ART 一段「不自建、借用既有」的立場是對的,但點名的目標函式錯了。

**[F5] 四、新閘「至少一支紅」— 可以被無關的綠測試 + 一支樁測試騙過**
severity: major
blocking: 是——判準:這正是派工詞明確要追問的騙法(「至少一支紅被綠的既有測試冒充怎麼騙過」),放過會讓雙向門放行完全沒被真的驗過的計劃。
引句:「雙向門放行的條件:每支測試都存在,而且至少一支是紅的。」
佐證:`_clause_bindings_for`(見上,`scripts/lumos:4698`)只判「測試方法存在/紅/綠」,不比對條款文字與測試斷言內容是否語意相關。具體騙法:N 條條款各綁一支既有、跟這條款毫不相干但恰好是綠的舊測試(這是 S7 想擋的「全綠」但這裡不是全綠),另外新加一支跟哪條條款都不真的相關的樁測試(例如 `def test_stub(): assert False`)綁在某一條上。四步驗收:①每支測試都存在 ✓ ②至少一支紅(那支樁測試)✓ →PASS。S6/S7 的判準是「全部存在」+「OR 邏輯的至少一支紅」,沒有「每條條款各自要有自己的紅測試」這種逐條檢查,一支樁測試就能讓一整批毫不相干的條款集體通過。

**[F6] 五、逃逸自動記(PF-2)— 收窄成只認「受波及合約的測試沒過」,結構性漏記兩種本該記的逃逸**
severity: major
blocking: 是——判準:d5 說「沒有這個數字,退場就是盲飛」,而漏記的偏偏是「tier=high 缺審查留痕」這種最該被記錄成逃逸的情形,會讓 RETIRE-IF ① 賴以判斷退場的逃逸率被系統性低估。
引句:「三個來源……只認『受波及合約的測試沒過』那型;缺表態、高風險缺審查留痕這些是流程未完成,不是下游抓到缺陷」
佐證:`code-loop check` 目前有三種 BLOCKED 成因(`scripts/lumos:27643` 的說明行:「合約測試紅、觸發到的效能檢核題沒表態、tier=high 又沒有效留痕」);pre-push 只在 grep 到「受波及合約的測試沒過」這串字面時才呼叫 `loop escape --auto`(`scripts/hooks/pre-push:239`),其餘兩種擋下不記帳。但按本案自己的邏輯(d1:雙向門「品質靠實作時的測試與代碼審兜底」),當一個雙向門計劃真的因為缺代碼審留痕在推送前被擋下,那正是「兜底那一道最後被觸發了」——是不是「下游抓到缺陷」不是重點,重點是**這一份雙向門計劃當初沒有被任何人真的看過**,直到 push 才被攔下;不記這一類,恰好把最需要被逃逸率捕捉的樣本排除在統計外。

**[F7] 二、句式(EARS)節 — 已讀,無 finding。** 五型句式與範例(S1–S15)內部標點一致(全用半形逗號),定義行與範例對得上,無交叉引用問題。

**[F8] 六、退場條件節 — 已讀,無 finding。** 健檢按門分開印、RETIRE-IF① 一致,無新增衝突。

**[F9] 兩層要分開節 / 進度節 — 已讀,無 finding。** 「規格書格式不限」與「句式只約束 [SN]」邏輯自洽;進度節提到的 `-c core.quotePath=false` 修法已在 `scripts/lumos:7445`(`_plans_in_range`)實際落地,聲稱屬實。

**[F10] 要動什麼 / 回退 / 誠實界線節 — 已讀,無 finding。** 三節內部一致,`誠實界線`節其實已自承 F1/F5 這類洞的存在方向(「四層都有洞」),但沒有具體點出 F1 這種會讓機制完全失效的自我否決——不算獨立 finding,已併入 F1 的 severity 判斷。

## 固定席節點逐條判(這份設計會不會破壞它宣稱的行為/合約)

- `Systems/design-loop.md`(★INVARIANT★ 處置閘第五步):**會被本案直接改寫**(S8 明說要讓處置閘第五步呼叫「同一支條款檢查器」)。風險在於如果實作者依 F4 的錯誤引用把新檢查器接到 `_classify_one` 而非 `_clause_bindings_for`,會讓這條 INVARIANT 現有的判定行為(未標條款判 fail 等)悄悄變掉。本案自己也承認要改這條合約行、且是單向門——判斷方向正確,但落地路徑有 F4 這個坑要先堵。
- `Systems/canary-audit.md`(record/readback、second 不影響 gate rc):**不影響**。本案寫 `.escape-log.jsonl`(用既有 `_jsonl_append_verified`),讀 `.canary-log.jsonl` 只做唯讀查詢(`_door_for_loop`/`known` 去重),沒有新寫入路徑會干擾 record/second 的 readback 或 rc 語意。
- `Systems/guard-kill.md`(rc 優先序、`--json` 純度):**不影響**。本案不碰 guard kill 指令或其 rc 路徑。
- `Systems/lumos-cli-lifecycle.md`(re-inject sentinel 保留):**不影響**。本案沒有改到 CLAUDE.md 注入邏輯。
- `Systems/lumos-cli-read.md`(search 排除 superseded 不排除 stale):**不影響**。本案的查詢/掃描(關鍵字表、標籤枚舉)不經過這條 search 濾網。
- `Issues/code-loop守衛main-direct盲區.md`:**不影響方向未變**,但 F6 描述的「tier=high 缺留痕不記逃逸」若與這個既有盲區疊加(main-direct 本身審查覆蓋率較低),會讓這塊本來就弱的區域的逃逸統計更失真——已併入 F6,不獨立開新 finding。

## 抑噪聲明
其餘節(綁定規則的「單向門回退節」要求、逃逸帳去重鍵、健檢分門印)讀過沒有找到可具體指出 file:line 的失敗場景,依規則不標。

## 總結
最嚴重 severity 是 **blocker**(F1:雙向門判定路徑的核心自我否決,會讓宣稱的「機器可信任地把雙向門放行」整套失效)。blocking 共 6 條(F1–F6)。
