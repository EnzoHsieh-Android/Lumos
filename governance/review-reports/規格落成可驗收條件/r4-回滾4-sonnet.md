severity: major

## 逐節閱讀記錄

- 標頭 / decisions / lands_in:已讀,無 finding。d1–d12 的疊代脈絡與 r1–r3 卷證吻合(逐份讀過 governance/review-reports/規格落成可驗收條件/r{1,2,3}-intake.md 存在且份數與正文引用一致)。
- 「為什麼」數字表格:已讀,無 finding(本輪未重新徒手驗算逃逸帳分母,因表格數字屬 r1–r3 已訂正過的既有帳,非本輪新主張)。
- 「兩層要分開」:已讀,無 finding。
- 一、門怎麼判 / 二、條款句式 / 三、綁定規則:已讀,除 F5 外無新 finding;`_TRIGGER_STOPWORDS`、`INV_TAG_RE` keeps 分支等尚未落地,屬設計不是現況,本輪不重複 r3 已折的洞。
- 四、新閘 spec-gate:F1、F5 見下。
- 五、逃逸自動記:F2 見下。
- 六、退場條件:F2 見下。
- 進度:F4 見下。
- 要動什麼 / 實務隱患 / 驗收條款 33 條(抽查 S6、S25 文法皆合一條文法) / 誠實界線 / 審計修正紀錄:已讀,無新 finding。
- 回退:F3 見下。

## Findings

### F1
severity: major
spec 第五節「CI」來源表格宣稱 `_ci_step_is_test` 用 `;` 切段、只看「/」後步驟名來判斷是不是測試步;但 `docs/.ci-log.jsonl` 裡真實存在的 `failed_step` 值本身就含有一個內嵌的 `;`(不是多步分隔用途),會被同一支函式誤切成兩段,而該值並非由多個失敗步驟組成。
引句:「多步用 `;` 串,只看每段「/」後面的步驟名」
file: `docs/.ci-log.jsonl:64`(`"failed_step": "test/code-loop gate (push 後盾;體檢"`,run_id 33307254740,同值另兩筆在 118、131 行)
file: `scripts/lumos:22168`(`_ci_failed_step` 用 `";".join(hits)` 組字串,假設步驟名本身不含 `;`)
file: `scripts/lumos:22360`(`_ci_step_is_test` 對輸入直接 `str(name or "").split(";")`)
用該值實測(`test/code-loop gate (push 後盾` → 段 1、`體檢` → 段 2)兩段目前都判不到測試詞,巧合沒有誤判成逃逸,但這證明「`;` 只在多步之間出現」這個前提在本 repo 真實資料上已經不成立——GH Actions 步驟名可以自帶 `;`。之後只要某個真正的失敗步驟名裡剛好在 `;` 前後恰好切出一段含 test/測試字樣,就會把單一非測試步驟誤判成命中,汙染逃逸帳與第六節門檻分子。
blocking: 是(判準第三次訂正時聲稱「已修」,但實際資料已證明切分假設有漏洞,應在落地前補上「先看整段有沒有測試詞,`;` 只在解析不出單一步驟時才切」或改用結構化分隔而非借用可能衝突的字元)

### F2
severity: major
第六節門檻分子規則「只數 `precision: finding` 與手動記的列」,但 `precision` 欄位目前只有 code-loop 來源的自動記錄會寫(`cmd_canary` 傳 `extra={"precision": _precision}`);CI 來源(`_ci_red_escape`)與推送閘兩路(`push-gate`、`push-gate-unreviewed`)呼叫 `_auto_escape` 時都沒有傳 `extra`,寫出的紀錄完全沒有 `precision` 欄。而既有 6 筆手動列(`docs/.escape-log.jsonl`)也沒有 `door`/`precision` 欄,只能靠沒有 `auto` 欄位這件事間接認出是「手動記」。
引句:「分子只數 `precision: finding` 與手動記的列」
file: `scripts/lumos:6211`-`6216`(code-loop 來源帶 `extra={"precision": _precision}`)
file: `scripts/lumos:22399`(CI 來源 `_auto_escape(env, "CI", ..., source="CI")`,未帶 `extra`)
file: `scripts/hooks/pre-push:240`、`scripts/hooks/pre-push:246`(push-gate / push-gate-unreviewed 兩路呼叫 `loop escape --auto`,severity 固定寫死 `major`,程式沒有逐條精度概念)
file: `docs/.escape-log.jsonl`(現存 6 筆手動列,`sorted(keys)` 均無 `precision`/`door`,只有 `token/loop/stage/severity/desc/ts` 加選填 `defect_ref`/`rule`)
第六節文字沒定義「沒有 `precision` 欄且有 `auto: True`」這第三類該不該計入分子——照字面讀,CI 與推送閘兩個來源的自動記錄會被永久排除在門檻分子之外,等於「雙向門計劃逃逸率」這個主要指標實質上只看得到代碼審一路,兩個來源(CI 紅、push-gate 擋下)量到的逃逸永遠不會觸發 RETIRE-IF ①②。這正是第六節自稱要防的「靠標籤/口徑漏記多數該審的東西」同一種洞。
blocking: 是(門檻計算的正確性是本案自稱的核心糾錯機制,分子定義有歧義且現況程式會漏記兩個來源,S34 落地前必須先把這條路徑寫清楚並補測試)

### F3
severity: minor
回退節「回退基準 sha:(待填)」綁 REVISIT 2026-10-17,要求「S8 若已落地,回退基準 sha 必須已填」;但 S8(處置閘第五步改呼叫同一支條款檢查器)如果分兩次提交落地(先寫檢查器、後接線;或先接線、後補測試),spec 沒說要填「哪一次」的 sha——是最先讓行為改變的那次,還是最後補齊測試的那次。
引句:「落地那次提交的 sha 落地時填進這裡」
本 repo 現行提交紀律(CLAUDE.md「提交與推送」節)要求「做到一半的本機提交,推之前壓成一個」,理論上落地應該只有一次可回退的提交,因此實務風險不大;但這條約定沒有在本篇明文覆述,若實作者為了過代碼審而分批推送(如 260f64b1/bf301098 這類「fix: 代碼審抓到的幾條全部折入」後續修正提交,參見 `git log --oneline` 近期紀錄),回退基準就可能指向錯的中間態。
blocking: 否(有既有提交紀律間接兜底,不影響本輪能不能放行,但建議正文補一句「取最後一次讓 S8 行為改變的提交」消歧)

### F4
severity: major
本篇「lands_in: Systems/design-loop、Systems/規格閘」,但 `Systems/規格閘` 尚不存在;已在工作樹落地(雖未提交)的三處程式改動——CI 判準三版(`_ci_step_is_test`)、逐條精度(`--finding-severity`/`precision`)、推送閘 `push-gate-unreviewed` 一路——在既有的 `Systems/design-loop.md` 裡完全查不到任何一筆 KEY 提及(grep `逃逸自動記`/`_auto_escape`/`_ci_step_is_test`/`finding_severities`/`push-gate-unreviewed` 全部零命中)。
引句:「`Systems/規格閘` 管 `cmd_spec_gate`、`_clause_check`、`_excluded_line`」
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md`(grep 上述五個關鍵詞皆 0 命中)
file: `scripts/lumos`(git status 顯示為 `M`,即這些改動已在工作樹但尚未提交)
CLAUDE.md 鐵則一要求「改了會影響行為/決策/驗證的 code,當次就把脈絡寫回圖譜」,pre-commit hook 也會擋「改 code 沒動圖譜」;本篇把落點釘死在一個還不存在的節點上,卻沒交代「規格閘節點開張之前,這些已落地但未提交的改動說明暫時寫進哪一篇」。真的要提交時,實作者要嘛臨時把 KEY 塞進 `design-loop.md`(之後 `Systems/規格閘` 開張時要記得搬,搬不搬沒人守),要嘛被 hook 卡住現場即興開一篇範圍不明的節點(正是「節點範圍列最優先」那條記憶點名的破口)。
blocking: 是(這是提交前一定會撞到的機械閘,現在不寫清楚,落地那一刻就是臨場即興)

### F5
severity: major
留痕的「條款區塊指紋」定義成只對 `[S]` 定義行正規化後取雜湊,刻意不含整檔(理由是避免 `updated:` 這類維護性欄位變動造成假過期)。但門的判定除了條款文字本身,還依賴「計劃連到的節點是否帶 ★IRREVERSIBLE★/★CHECKPOINT★ 合約行或 `risk/` 標籤」(第一節硬單向門訊號 2);這個訊號來自 `related`/`lands_in`/正文連結指向的**外部節點**,不在條款區塊指紋的雜湊範圍內。
引句:「條款區塊的指紋(全部 `[S]` 定義行正規化後串起來的 sha256,不是整檔」
若某計劃當初留痕時門判定為雙向門(通過放行),之後它所連結的某個節點被別的工作補上了 ★IRREVERSIBLE★ 合約行或 `risk/` 標籤,而本計劃的 `[S]` 條款文字完全沒改——指紋不變,推送閘仍讀到舊留痕視為有效(S31「若計劃只改了條款以外的內容,則推送閘應仍視留痕有效」明確保護了這種情況),門也不會被重新判定成單向門。S21 雖然會把留痕測試清單重新跑一次,但那是重驗行為結果、不是重驗門類別——一份實質上已升級成該派人審的計劃,可以在不改一個字條款的情況下持續用舊的雙向門待遇通過推送閘。
blocking: 否(窗口需要「外部節點合約在留痕之後才被追加」這個不算罕見但也非高頻的時序,且 doctor 對 30 天無新留痕會軟提醒;不足以擋這一輪,但第六節門檻計算或 S24 應把「門判定所依賴的外部節點合約行版本」一併納入 staleness 判準,否則逃逸帳量到的也只是「條款文字沒改」而非「門判定仍然正確」)

## 固定席節點影響判斷

- `Systems/design-loop`(★INVARIANT★ 處置閘第五步):本案明確要改寫這條 INVARIANT 的合約文字(第四節給出新草稿並綁 `t_disposal_clause_gate`+`t_disposal_step5_shares_checker`),屬於正常的「改合約要綁測試+審計」流程,不是破壞;但如 F4 所述,現況缺一個過渡期落點,建議先在此節點掛一筆暫時 KEY。
- `Systems/bound-tests-gate`(★INVARIANT★):spec 第四節已自行訂正「借 `bound-tests-gate` 是錯的,那支不數支數」,確認新的支數解析是獨立新寫的判準,不耦合、不改動該節點合約,不影響。
- `Issues/code-loop守衛main-direct盲區`:spec 第四節明文「range 沿用 pre-push 現有的 push-range 計算、不得自算 merge-base」,已主動避免重開此事故,不影響。
- `Systems/anchor-integrity`(★RISK★):`pre-push` 是錨點檔,本案「進度」段已記錄「這次改了要先 `lumos anchor approve`」,走既有核可路徑,不影響機制本身。
- `Systems/每支檔有家`:`scripts/lumos`/`scripts/hooks/pre-push` 已各自有既存的家(如 `design-loop.md` 對 `scripts/lumos`),本案沒有新增沒有家的檔案,結構上不影響;內容是否即時寫回是 F4 的問題,不是「有沒有家」的問題。
- `Systems/lumos-cli-lifecycle`(★INVARIANT★ re-inject 保留 sentinel 外內容):本案改 `CLAUDE.md` 的方式是「改模板第 60 行、本 repo 跑 `lumos update` 重新注入」,走 sentinel 內覆寫的既有機制,不手動改 sentinel 外文字,不影響。
- `Systems/canary-audit`(★INVARIANT★ record/second 落盤可讀回、second 純 telemetry):本案的 `spec-gate` 留痕走既有 `cmd_canary` 寫入口(而非另開寫路徑),沿用同一支落盤自驗;不涉及 `cmd_canary_second`,不影響兩條 INVARIANT。
- `Systems/guard-kill`(★INVARIANT★ rc 優先序、`--json` 純淨):本案只在文字上類比「規格閘不收弱證據」跟 guard-kill 的 `killed_unattributed` 同一類判斷,沒有呼叫或重用 guard-kill 的程式碼路徑,不影響。

## 統計

最嚴重 severity:major(F1、F2、F4、F5 皆 major)
blocking 計數:3 條(F1、F2、F4;F3、F5 為 blocking: 否)
