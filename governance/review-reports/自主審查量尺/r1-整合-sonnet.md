severity: major

## F1 盲審席「標記+配對」沒有可用的帳欄位,字面實作會違反既有記帳紀律
severity: major
blocking: 是(實作者要嘛在 --note 塞機讀資料違反既有紀律,要嘛得自己發明未言明的欄位,兩條路徑都會讓 S11 的測試 t_blind_seat_record_requires_pair 判準模糊、日後被拿掉或誤讀)
引句:「帳上標明它是盲審、配對的是哪一席」
file: `scripts/lumos:30743`——`canary record` 目前的可用欄位只有 `--auditor`(自由字串)、`--note`(備註)與一串結構化欄(`--findings-set`/`--clusters`/`--outcome`…),沒有任何「盲審旗標」或「配對席名字」欄位;`python3 scripts/lumos canary record --help` 全列印證同一件事。
file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md`(2026-08-26 決策段)——該節點明寫「機器要回讀的資料開結構化欄,不塞 note 散文」,是這本帳現行的寫入紀律,S11 若靠塞進 `--note` 的文字判定「有沒有標盲審」就是正面違反這條已定案的紀律;若不塞 note、就沒有任何欄位能讓 t_blind_seat_record_requires_pair 讀到「這筆是盲審」。
spec 的 PRIOR-ART 行自稱「機制層沿用既有的…代碼審通過留痕、外家審查席,不加依賴」,但 S10–S12 實際上需要 canary log 新增欄位(或至少新增一種讀法),這個落差 spec 全文沒有一處承認或指名要改 `scripts/lumos` 的 `canary record` schema。

## F2 「不給原本的審查報告與結論」沒有技術隔離,只是派工當下不附——現行外家席派工慣例讓審查帳/報告本身可被審查者自行讀到
severity: major
blocking: 是(照 spec 字面「派工材料只給凍結改動」去派工,若沿用現行外家席慣例給完整 repo 讀權,審查帳、治理帳、逃逸帳與歷史審查報告全是版控中的一般檔案,盲審/抽查者能自己 grep 到,整組對照實驗與漏網率估計會被污染而不自知)
引句:「只給凍結的改動與它宣稱要做的事,不給原本的審查報告與結論」
file: `docs/.canary-log.jsonl`(尾三行,含 `report_path`/`snapshot_path` 指到 `governance/review-reports/code-驗收前提欄位可改/r3-架構對齊-sonnet.md` 等)——這些審查報告與 `docs/.canary-log.jsonl`/`docs/.escape-log.jsonl`/`docs/.governance-log.jsonl` 全是一般受版控檔案,不在任何存取控制之後。
file: 本次派工詞(`/private/tmp/.../scratchpad/dl/base.txt` 第 14 行)——本次審查任務給我的限讀規則是「除了 governance/review-reports/{LOOP}/r1-intake.md,不要讀 governance/review-reports/ 底下任何東西」,這正是現行外家席派工唯一的「材料限制」手法:靠**派工詞裡明寫禁讀哪個目錄**,而不是技術隔離;repo 其餘部分(含三本帳本)完全開放讀取,我在核這份 spec 時就直接 `grep`/`tail` 讀了 `docs/.canary-log.jsonl`、`docs/.escape-log.jsonl`、`docs/.governance-log.jsonl` 沒有任何阻擋。spec 全文找不到「凍結快照要放在審查者讀不到帳本的隔離環境」這類機制,唯一既有的「凍結快照」(`--snapshot`/`snapshot_path`)用途是 quote-check 核對引句,不是存取限制。S6、S10 若照現行慣例派工,盲審/抽查前提在有 repo 讀權的審查者手上並不成立。

## F3 盲審席不在 _TIER_ROSTER,12 輪對照期間 `loop status --roster` 會持續回報「應派/實派」不符
severity: minor
blocking: 否(`--roster` 是 advisory,恆不影響 rc,不會擋任何閘;只是雜訊)
引句:「接下來的代碼審,每一輪多派一席「盲審席」」
file: `scripts/lumos:9839-9878`——`_TIER_ROSTER` 是 (kind, tier) 到固定席位清單的字典,沒有任何一格列了「盲審席」;`loop status --roster` 逐輪拿實派(`rN-dispatch*.json`)對這張表算落差並印出來。連續 12 輪多派一席會被這個觀測段持續標成「編制外」,spec 沒有交代要不要把盲審席登記進 `_TIER_ROSTER`(哪怕只是臨時登記)或在輸出旁註記「實驗期間,忽略」。

## F4 相關連結漏了「風險低計劃放行紀錄」的權威來源 [[Projects/雙向門放行_計劃]]
severity: minor
blocking: 否(不影響機械判定,但下一個接手者會重新摸索一次已經做完的事)
引句:「治理帳只有規格閘每次跑的紀錄(`spec-gate-run`,記的是跑的當下的提交編號,不是後來推上去的那個)」
file: `docs/lumos-toolchain-knowledge/Projects/雙向門放行_計劃.md:1-19`——這篇正是「風險低計劃直接放行(PASS 不派審)並留痕 `kind: spec-gate`」機制的單一來源(2026-09-17 已落地、22 條條款綁 fixture 測試全綠),`docs/.governance-log.jsonl` 尾行的 `"gate": "spec-gate", "kind": "spec-gate-run"` 就是它寫的。但 `自主審查量尺_計劃` 的 frontmatter `related:` 只列了 `[[Projects/逃逸自動記_計劃]]` 與 `[[Projects/代碼審跑滿上限的判斷依據_計劃]]`,沒有連到雙向門放行_計劃——它的問題描述("後者目前沒有「放行」紀錄")其實是在重新發現雙向門放行_計劃自己就記錄在案的既知缺口(該計劃的 RETIRE-IF③ 就是在等 `push-gate-unreviewed` 筆數),兩篇該互相連結但目前沒有。

## 實務隱患(五類逐答,依 LENS 焦點)

- **整合(核心)**:見 F1、F2——盲審/抽查的「不給什麼」目前只靠派工詞紀律,沒有技術或帳欄位配套;canary log 現行決策明文禁止把機讀資料塞進散文備註,S10–S12 卡在這個縫裡。
- **既有處置閘/席次編制**:盲審席若照常記帳(`--auditor` 帶名字、`--report`/`--snapshot`/`--findings-set` 齊全),`--disposal` 閘的六步合取不會因為多一席而壞掉(找不到任何一步是按 `_TIER_ROSTER` 席數做硬性比對——硬擋的是 `--min-seats`,那是下限不是上限,不會因為多派一席而 FAIL)。真正會被牽動的只有 F3 說的 `--roster` advisory 觀測,不擋。
- **與逃逸自動記_計劃的既有決定**:核對「站名『抽查』寫進逃逸帳」與現有三來源(代碼審/CI/推送閘)的 `_auto_escape` 機制——沒有衝突:`_auto_escape` 接受任意 `stage` 字串與任意歷史 `sha`(CI 來源本身就用歷史範圍),抽查另開一個 `stage="抽查"` 呼叫並不違反現有寫法;去重鍵(計劃/階段/sha)邏輯照樣適用。唯一沒講清楚的是抽查要用 `--auto --range` 還是手動 `loop escape <loop_id>`,但不到需要標記的程度(command-level 選擇,非行為缺口)。
- **與收斂閘殘餘估計降級_計劃的既有決定**:spec 的 WHY 行已正確引用 2026-08-14 capture-recapture 降級的結論(鑑別力近零)並解釋這次改走直接抽樣、不走回頭路——查證屬實(`docs/lumos-toolchain-knowledge/Projects/收斂閘殘餘估計降級_計劃.md` 的 summary 與此描述一致),無矛盾。
- **資安席規矩**:code/high tier 的資安席是 `required-gated`(唯一會擋處置閘的席);盲審席若配對到的剛好是資安席所在輪,盲審席本身仍是「編制外加派」,不會被誤判成頂替資安席(資安席的 required-gated 判定看的是有沒有「資安-<模型>」這席報到,不是看總席數),故無衝突,不再展開。

## 已看,無

- 逃逸帳去重機制(S1)的機械可行性:實測 `docs/.escape-log.jsonl` 裡 `696709b` 四筆記錄(Codex行為精修/規格落成可驗收條件/逃逸自動記/雙向門放行)`sha` 欄完全相同,`FACT:` 行講的「09-17 記了四次」屬實,dedupe-by-sha 的假設成立。
- 分級來源(第一件「分級怎麼分」段)寫「不是每個迴圈都有…歸『未定錨』」——這是 r1 前掃已修正並經編排者重現驗證過的版本(`governance/review-reports/自主審查量尺/r1-intake.md` 第 1 條),我沒有重覆核。
- `lumos gov --escape-rates` 尚不存在、S1–S12 的 test id 尚不存在:spec 本來就是要做的東西,不是錯誤宣稱,不列為問題(intake 已同結論)。
- `lumos canary record` 現有的 `--tier`/`--orchestrator`/`--findings-set`/`--accepted-set`/`--refuted-set` 等結構化欄的語意,與 spec 對「代碼審通過留痕」「外家審查席」的既有描述(第二件「誰來查、怎麼查」段)一致,沒有找到字面矛盾。
- `--auto` 的既有用法(CI/推送閘來源)證實可以帶任意歷史 `sha` 與 `--range`,抽查對「已推上遠端多週」的舊提交寫入逃逸帳在機制上可行,不是新問題。
- `_TIER_ROSTER` 的 `("code", tier)` 三格與資安席、外家席的既有規則,和 spec 第二/三件想加的角色不衝突(見上「資安席規矩」段)。

最後一行總結:最嚴重 severity 為 major,blocking 共 2 條(F1、F2)。
