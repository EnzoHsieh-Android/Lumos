severity: blocker

## 逐節讀完的結論

### 為什麼／兩層要分開／二 句式／三 綁定規則
已讀,無 finding。守衛面掛 `risk/` 標籤篇數用 `lumos query --tag "risk/守衛面"` 核對得 29 篇,與 spec 第一節「守衛面 29」一致;句式與綁定規則兩節內部無矛盾,且 S1–S8/S12/S14/S15 尚未落地,無程式碼可供對照,只能查內部一致性——一致。

### 一、門怎麼判 —— PF-1(重驗:section 一/五訂正段)
引句:「那四行通常由 AI 自己寫=自我認證、無獨立性」
這段本身誠實(spec 也承認)。但 d6→d8 的訂正只改了門檻數字(34→40),沒有改變「靠標籤/機械訊號」這條路線本身的弱點:AI 自我認證這件事,連「訂正」這個動作本身也是同一輪對話裡的 AI 做的,無法自證訂正是否又漏算。
severity: minor
blocking: 否(spec 已明寫靠逃逸帳事後量,不是本輪要解決的洞;無具體失敗場景升級的理由)

### 五、逃逸自動記 —— PF-2(重驗:section 五訂正段)核心問題

**F1** 引句:「只認「受波及合約的測試沒過」那型」
file: `scripts/lumos:22041-22042` `_CI_RED = ("failure", "timed_out", "startup_failure")`;`scripts/lumos:22321` `_ci_red_escape` 對 `_CI_RED` 命中的任何 CI 結論(含 lint 失敗、build 失敗、timeout、startup_failure 等與「合約測試沒過」無關的失敗)一律呼叫 `_auto_escape`,沒有任何依失敗型態篩選的邏輯。這與 spec 自稱「已收窄」直接矛盾——實際只有 push-gate 那一路(`scripts/hooks/pre-push:239` `grep -q "受波及合約的測試沒過"`)做了篩選,CI 這一路完全沒做。
severity: blocker
blocking: 是(RETIRE-IF① 的唯一判準是逃逸率,CI 雜訊直接灌水到分子,可能讓一套沒問題的雙向門被誤判超標而整套退回,或反過來把真正的漏網淹沒在雜訊裡)

**F2** file: `scripts/lumos:6181` `if loop and str(loop).startswith("code-") and severity in ("major", "blocker")`——只判 severity,沒有依「finding 型態是不是受波及合約測試沒過」篩選;任何 major/blocker 級的代碼審發現(可能是命名、可讀性、資源用法)都會被記進逃逸帳。與 F1 同根同源、同一份「已收窄」訂正宣稱。
severity: blocker
blocking: 是(理由同 F1,且這是三個自動來源裡預期觸發頻率最高的一個)

**F3(併發/資源/回滾三鏡頭共同命中,核心是「資料救不救得回」)**
引句:「三個來源:代碼審 major 以上的發現、CI 紅、推送閘擋下」
`scripts/hooks/pre-push:239-241` 在 push 被 `exit 1` 擋下的**同一次 hook 執行裡**呼叫 `loop escape --auto`,直接 append 進 `docs/.escape-log.jsonl`(git 追蹤檔,見 `git ls-files` 確認),但整份 pre-push 沒有任何一行 `git add`/`git commit` 把這筆寫入釘進歷史;`cmd_ci_status`/`_ci_red_escape`(由人手動跑 `lumos ci-wait`)同樣只 append、不 commit。也就是說:每一筆自動逃逸記錄,寫下去的當下都是「未提交的本機檔案修改」,要靠人後續自己想到 `git add docs/.escape-log.jsonl` 才會進歷史;沒有任何機關檢查它有沒有被提交(對照 `pre-push:109` 只驗 `anchor-baseline.json` 的 dirty 狀態,沒有把 `.escape-log.jsonl` / `.canary-log.jsonl` 納入同類檢查)。
現場佐證(不是引句,是本次對話開頭 git status 的事實):`docs/.governance-log.jsonl`、`docs/.usage-log.jsonl` 這兩支同類治理留痕檔,此刻正是 `M`(已修改未提交)狀態——同一種「寫了但沒人記得 commit」的情形已經在這個 repo 裡實際發生,不是理論風險。
severity: blocker
blocking: 是(這正是我被派來追的問題:退場要看逃逸率,但逃逸記錄本身可能從沒進過 git 歷史就被 `git stash`/`git checkout --`/下一次 `git commit -a` 覆蓋前的手滑清掉;沒有任何機械手段能事後證明「這段期間到底漏記了幾筆」)

**F4 —— RETIRE-IF① 承重牆目前是空的**
引句:「跑滿 30 份雙向門計劃後,雙向門的逃逸率高於單向門 → 整套退回」
`lumos loop escape --list`(`scripts/lumos:7599-7614`)完全不印 `door`/`attribution`/`auto` 欄位,讀側唯一能看到門別的地方是原始 JSONL;而「按門分開印」的健檢(S13)明列在「進度」段的「還沒做」清單裡,目前程式碼裡沒有任何指令能回答「已經跑滿幾份雙向門」「這些門的逃逸率各是多少」。spec 自己在「誠實界線」寫「RETIRE-IF ① 因此是承重牆,不是裝飾」,但承重牆的量測工具此刻不存在。
severity: major
blocking: 是(不阻擋本輪已落地的 S9/S10/S11,但阻擋「規格閘本體 S1–S8 可以照這份 spec 上線」的宣稱——沒有計數機制的退場條件等於無法退場)

**F5 —— 回退步驟②沒有可定位的錨點**
引句:「處置閘第五步改回原本的條款綁定檢查(git 上那一版)」
`scripts/lumos:15672-15739` 的 `_disposal_clause_step` 就是「原本那一版」,但 spec 沒有指定 commit sha 或 tag。S8 落地後這支函式會被改寫(呼叫共用條款檢查器),如果之後又有其他 bugfix 疊在上面,「git 上那一版」會變成模糊指稱,回退執行者得自己去 `git log` 猜哪一個 commit 是「原本」。對照 `scripts/lumos:4599`/`15742` 的 `_CLAUSE_GATE_SINCE`/`_LANDING_GATE_SINCE` 這種寫死日期常數的既有慣例,本案回退卻沒有留一個等價的錨(例如「回退到 tag `pre-spec-gate`」)。
severity: major
blocking: 否(S8 本身還沒實作,現在补一句"打 tag" 的承诺就能解決,不阻擋當前已落地的三個逃逸來源)

**F6 —— 併發:兩個 hook 同時寫逃逸帳**
`_auto_escape`(`scripts/lumos:7495-7541`)整段邏輯是「讀全檔算 known/existing → 逐筆判斷 → append」,`_jsonl_append_verified`(`scripts/lumos:6193-6221`)只用 `open(path, "a")` 沒有檔案鎖。若同一個工作目錄裡,一支終端機在跑 `git push`(觸發 pre-push 的 push-gate 來源)同時另一支在跑 `lumos ci-wait`(觸發 CI 來源),兩個行程各自讀到「尚未包含對方那一筆」的 `existing` 集合,都判定沒重複,各自 append——會讓 S11「同一計劃、同階段、同 sha 已有紀錄不應重複寫入」在真併發下失效(TOCTOU)。這個 repo 過去已有同類「同工作區共用檔沒鎖」的事故先例(既有慣例是原子寫入:暫存檔→驗證→`os.replace`),但這裡沒有套用。
severity: major
blocking: 否(目前只有 push-gate 一個來源是實際自動觸發的高頻路徑,CI 來源要人手動跑,同工作區同時觸發的機率不高;先記錄,不因此擋下本輪)

**資源鏡頭**:無,理由——`.escape-log.jsonl`/`.canary-log.jsonl` 目前分別 6 筆/948 筆,append-only、每次全檔讀入記憶體的 O(n) 開銷在這個規模下可忽略;沒有具體會失敗的量體門檻可指。

**遷移順序鏡頭**:無,理由——`_CLAUSE_GATE_SINCE`/`_LANDING_GATE_SINCE` 這種「不回溯、寫死切點常數」的做法在本 repo 已有兩個先例且彼此獨立正確,S8 落地時比照同一種切法風險可控;S12(`_spec_gate_not_retroactive`)本身尚未實作,無法對照程式碼進一步驗證,但沒有具體矛盾可指。

### 四、新閘 / 六、退場條件 / 進度 / 要動什麼 / 回退 / 誠實界線
已讀,除上述 F1–F5 外無新增 finding。「進度」段坦承的坑(中文路徑 `core.quotePath=false`)在 `scripts/lumos:7444-7446` 確實已修;「推送前要做一件事」的 anchor approve 提醒與目前 git status 顯示 `governance/anchor-baseline.json` 已是 `M` 狀態相符,操作上是一致的。

### 驗收條款 [S1]–[S15]
已讀,句式格式合格,`[test:]` 名稱與各節描述對得上;因規格閘本體未落地,無法逐條跑測試驗證,只能核對句式與敘述一致性——一致。

## 固定席節點逐條判

- **Systems/design-loop ★INVARIANT★(處置閘第五步)**:不影響。S8(改呼叫共用條款檢查器)尚未落地,`_disposal_clause_step` 現況仍是原本判準;但一旦 S8 上線,這條 INVARIANT 的敘述文字必須同步改寫——spec 第四節已明講這是「不可變合約行」要改。
- **Issues/code-loop守衛main-direct盲區**:不影響。本次改動集中在逃逸自動記與 CI/push-gate 字串比對,未觸及 main-direct 分支判斷邏輯。
- **Systems/anchor-integrity ★RISK★**:不影響,前提是人確實執行 `lumos anchor approve`(進度段已寫明);錨點機制本身未被繞過。
- **Systems/每支檔有家**:不影響。`lands_in` 已規劃新開 `Systems/規格閘` 收留新程式檔,符合鐵則。
- **Systems/canary-audit ★INVARIANT★**(record/second readback、second 不影響 gate rc):不影響,且是正面案例——逃逸自動記直接重用 `_jsonl_append_verified`,沒有另開一條寫入路徑繞過落盤自驗;second 判定的 telemetry-only 特性未被觸碰。
- **Systems/guard-kill ★INVARIANT★**:不影響。本次改動未觸及 guard kill 的 rc 優先序或 `--json` 輸出邏輯。
- **Systems/lumos-cli-lifecycle ★INVARIANT★**(re-inject sentinel):不影響,本次改動未涉及 CLAUDE.md re-inject 路徑。
- **Systems/bound-tests-gate ★INVARIANT★**:不影響。push-gate 來源只對 code-loop check 既有輸出文字做 `grep` 字串比對(`"受波及合約的測試沒過"`),未改動 bound-tests 本身的判定邏輯或 rc。

## 對 panel 提問的直接回答

- **回退四步還原得掉嗎**:還原不到精確的「上線前」,因為②沒有 commit/tag 錨點(F5)。
- **kind: spec-gate 留痕退場後怎麼處理**:append-only 帳不會被清掉,`_door_for_loop` 會繼續讀到歷史紀錄;舊迴圈的 `door` 欄位是歷史事實不會被「判成另一種狀態」,但 spec 沒明講回退後(「只印不擋」模式)是否還繼續寫 `kind: spec-gate`,這點是敘述缺口,未達 finding 門檻(無具體失敗場景)。
- **讀側會不會被新欄位弄壞**:不會,`--list`/`gov --stats`/`_escape_rows_for` 全走 `.get()` 容錯,`door=unknown` 只是印出的字串,但反過來——`--list` 完全不印這些新欄位,是 F4 的一部分。
- **RETIRE-IF① 誰數、數哪本帳**:目前沒有任何指令會數(F4);等 S13。
- **三個自動來源 fail-open 的失敗看得到嗎**:看不到。全部只 `print(..., file=sys.stderr)`,沒有落盤記錄失敗次數;無人值守情境(例如自主迭代 loop)下失敗會完全消失,連事後回溯都做不到(F3 的延伸)。

---
最嚴重 severity: blocker;blocking 計 4 條(F1、F2、F3,以及 F4)。
