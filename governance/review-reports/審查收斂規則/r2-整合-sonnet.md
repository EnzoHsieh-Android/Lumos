severity: major

**一、碰到帶殘留合約就升 high(做法 5)**

severity: major
blocking: 是 — 這條要求的做法和既有的「分級不讀圖譜」決策正面衝突,計劃沒有承認,也沒說怎麼解。
引句:「`pitfalls --diff` 算風險分級時,改動碰到的檔若在某篇帶 `[residual:]` 合約的節點 about_code 裡,分級升為 high」
問題:`_pitfall_tier` 的設計是「★vault-free★,pitfalls 在 pre-push 熱路徑上不載圖譜」。這是代碼審 r1 架構席的決定,[[Systems/pitfalls-code-loop]] 的 2026-09-18 KEY 行也這樣寫。要判斷「檔在不在某節點的 about_code 裡」,必須載入並解析圖譜,等於推翻這條決策。計劃沒有 `decision-add` 翻案,沒寫 `lands_in` 到 [[Systems/pitfalls-code-loop]],驗收條款也沒有「pre-push 熱路徑耗時」或「找不到 vault 時的行為」。
具體失敗情境:
- 圖譜載入失敗時,是 fail-open 變回 standard,還是 fail-closed 升 high,計劃沒定。fail-open 會讓殘留合約悄悄失去守護。fail-closed 則所有沒有圖譜的消費專案都被升 high。
- 規格閘的 `spec-gate --push-check` 在全靠人驗且小改動閘過時,會印 light 並派 `loop next --tier light`。它和 high 的優先順序沒定義。一個改到帶殘留合約守的程式的小改動,可能先被 push-check 判成 light,於是不派代碼審。這正是做法 5 想堵的洞。
- 分級說明目前只有「命中風險型樣/新告警」「沒有程式檔」「有程式檔」三種,JSON 的 `tier_reason` 也要同步。
- 另一個既有衝突:`_pitfall_tier` 的 `claims` 判斷在前,殘留升級必須排在 `light` 判斷之前。計劃沒寫順序。
- `lands_in` 缺少 [[Systems/pitfalls-code-loop]] 與 [[Systems/規格閘]]。
佐證:file: `scripts/lumos:43677`(`_pitfall_tier` 的 docstring);file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:58`;file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:36`

**二、`[residual:]` 新標記的登記範圍(做法 3、做法 7)**

severity: major
blocking: 是 — 只列了手冊與測試,漏了解析層。不登記到合約行剝標記的正規式,殘留標記會污染乾淨宣稱文字和合約定位。
引句:「合約行加 `[residual:<節點>#<決策 id>]`(可以多個,一個殘留決策一個標記」
問題:做法 7 只列出要改的文件。程式裡至少有這幾處沒提:
- `INV_TAG_RE`(`scripts/lumos:5495`)目前只剝 `test|audit|kill|src|git|manual|keeps`。不加 `residual`,`strip_test_refs`、`guard` 定位、`kill-add` 和 `audit` 共用的子字串比對、`contracts` 與 lint 訊息都會把 `[residual:節點#d12]` 當成宣稱正文的一部分。
- 同一個 `INV_TAG_RE` 上方的註解已經記載過:加標記會連帶改變 11 處行號和 8 類呼叫點的行為。計劃沒做這個影響面盤點。
- 計劃要新增 `RESIDUAL_REF_RE`,doctor 在做法 3 提到「跟 `[audit:]` 同一段檢查」,但 `guard list` 的輸出(`scripts/lumos:15828`)、`contracts` 指令和 lint 的已知標記也沒登記。
- `guard residual` 要寫入並自驗。它得走 `atomic_write_verify` 並和 `kill-add` 共用定位函式,計劃沒寫。
- 手冊方面,漏了 `skills/lumos-project-notes/SKILL.md:61` 的合約行範本、`reference.md:672` 的標記清單、`docs/methodology/圖譜即合約.md` 的 Check T 描述(142、322–323 行)。
具體失敗情境:一條合約行是「KEY:★INVARIANT★ 文字 [test:x] [audit:m/d] [residual:A#d1]」,`guard audit` 或 `kill-add` 用「去標記後含子字串」定位。不剝 `[residual:]` 時,使用者貼乾淨文字能命中,貼 `guard list` 印出的文字卻不一定命中,定位行為不一致。
佐證:file: `scripts/lumos:5495`;file: `scripts/lumos:5485`;file: `skills/lumos-project-notes/SKILL.md:61`;file: `skills/lumos-project-notes/reference.md:672`;file: `docs/methodology/圖譜即合約.md:142`

**三、「第二個獨立代理同意」與穩定性探針、防應試化抽考並存(做法 2、做法 7)**

severity: minor
blocking: 否 — 計劃處理了抽考的比較口徑,只剩穩定性探針和不一致時的處理沒寫清楚。
引句:「兩邊都說測不到,才准記殘留。這一步寫進審計派工流程(`lumos-project-notes` 審計段)」
問題:
- 落點對了,就是 `reference.md` 五問段(約 552–553 行)。但第二代理「只給那條反例與合約」,這和審計員有五問 rubric 不同,是第二套判斷流程。穩定性探針的規則是「兩問判決不一致=unstable,不蓋章、交人裁」。計劃沒說第二代理和審計員意見不一致時,是照探針規則交人裁,還是照做法 2 的更嚴方向直接當局部退化。兩條規則並列時,「交人裁」和「當局部退化要補測試」會衝突。
- 計劃只處理了抽考,沒提穩定性探針。「約每 5 次 audit 抽 1 次」的計數,第二代理那一次算不算一次 audit,也沒定。
- 「maker≠checker」是對的引用,這一點不用改。
具體失敗情境:審計員說「繞過設計」,第二代理說「測得到」。編排者一看是要往嚴的方向,就當局部退化。但探針規定要記 note 交人裁,兩份文件的處置不一致。
佐證:file: `skills/lumos-project-notes/reference.md:552-553`;file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:69-70`

**四、doctor 與既有檢查的並存(做法 3)**

severity: minor
blocking: 否 — 是描述不夠具體,不是設計錯誤。
引句:「跟 `[audit:]` 同一段檢查(既有的未審合約檢查),多驗 `[residual:]` 指到的決策仍然存在、沒被標無效」
問題:既有 Check T 是「綁測試後必須有 `[audit:]`」,檢查的是合約行本身。`[residual:]` 指到的是別的節點的決策(計劃說可以記在計劃節點)。這是第一次出現跨節點引用。doctor 要載入別節點的 `decisions`,這個依賴要說明。節點被改名或刪除時,是 doctor 報錯,還是 rename/delete 守衛先擋,也沒寫。
具體失敗情境:計劃節點歸檔或被改名後,殘留決策消失,doctor 才報錯。推送前被擋住的人不知道該去哪裡補。
佐證:file: `scripts/lumos:6723`

**五、「不做」節引用 [[Projects/代碼審資安席_計劃]](不做節)**

severity: minor
blocking: 否 — 引用的實質內容正確,只是說法有一處含糊。
引句:「這正是 [[Projects/代碼審資安席_計劃]] 第一輪用「同檔名內容改掉」實測出來、改成比內容才堵上的洞(r1 整合席)」
問題:資安席計劃第 59 行寫的是「代碼審 r1 通才 A1/資安 C1 改成比內容」,情節是「同一支檔換成含後門的內容照樣 PASS」,所以計劃的引用方向是對的。含糊之處:
- 「第一輪」是代碼審 r1,不是設計審 r1。本計劃自己也有 r1,容易混。
- 「帳上看過≠真的讀過」是計劃的推論。資安席計劃堵的是「看過後內容又改了」,並不是「席位實際讀了哪幾支」。建議改寫成「資安席計劃只保證帳上的凍結 patch 涵蓋,沒有保證席位真的讀完,是這個推論的前提,本計劃在此基礎上不放寬」。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/代碼審資安席_計劃.md:59`

**六、落點(lands_in)**

severity: minor
blocking: 否 — 現在列兩篇,實際會動到更多家。
引句:「lands_in:」(frontmatter,列 `Systems/guard-kill` 與 `Systems/design-loop`)
問題:做法 3 到 6 動了這幾處程式:`pitfalls --diff` 分級、派工鏡頭徽章、`loop escape` 與 `escape-stats`、doctor。每支程式檔要有一篇 Systems 家,所以應該補列 [[Systems/pitfalls-code-loop]]、[[Systems/loop-convergence-recording]](逃逸帳)、[[Systems/規格閘]]。原版有 `loop-convergence-recording`,這一輪被拿掉了,但做法 6 又回頭寫進逃逸帳。
佐證:file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md`

**已讀,無 finding 的節:** 緣起、PRIOR-ART/RETIRE-IF/REVISIT、回退、實務隱患、審計修正紀錄。派工鏡頭 200 字截斷與徽章的設計(做法 4)是合理的。

最高等級 major,blocking 共 2 條(第一、二條)。
