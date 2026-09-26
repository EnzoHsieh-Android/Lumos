severity: major

## F1 逃逸帳有近三成的列沒有可拿來去重的提交或 CI 編號
severity: major
blocking: 是——照 S1 字面「同一個缺陷佐證(提交編號、CI 執行編號)只算一次」去重,實作者遇到沒有這兩個欄位的列時無所適從:要嘛每列都當獨一無二(算重複,逃逸率被灌水),要嘛整段丟到「歸因不明」(母體又少算),兩種都不是 spec 交代的行為,會做出錯的統計。
引句:「先去重:同一個缺陷佐證(提交編號、CI 執行編號)只算一次」
file: `docs/.escape-log.jsonl:3`——`{"loop": "code-推播漏網量測", "stage": "prod", ...}` 整列沒有 `sha` 也沒有 `defect_ref`,無任何可當「提交編號、CI 執行編號」的欄位。
file: `docs/.escape-log.jsonl:19`、`docs/.escape-log.jsonl:20`——loop=「收工點名問版本控制」、stage=「實作」的兩列同樣沒有 `sha`/`defect_ref`。
file: `docs/.escape-log.jsonl:1`——有 `defect_ref: "code-gov-stats-root-b"`,但那是個修復用的分支/迴圈代號,不是提交或 CI 編號,S1 講的「佐證」欄位格式不只一種、spec 沒交代怎麼統一解析。
機械數:對 25 筆逃逸帳實跑,8 筆(32%)同時缺 `sha` 與可辨識成提交/CI 編號的 `defect_ref`。

## F2 計劃可以掛兩個 scope 標籤,範圍類演算法只講單數
severity: major
blocking: 是——`scope/<類>` 標籤實際上可以有 2 個,S4 只處理「零個標籤→未分類」,沒有「兩個標籤→算進哪一類/算不算兩類各一次」的規則;實作者照字面只會取到其中一個(例如 fm 讀出的第一個),另一類的放行數/逃逸數永遠少算,而且哪個被丟掉不可預期(讀檔順序決定)。
引句:「取計劃的 `scope/<類>` 標籤(九類之一);對不回的標」
file: `docs/lumos-toolchain-knowledge/Projects/新增告警閘_計劃.md:9`、`:10`——同時有 `scope/guards-gates` 與 `scope/stack-knowledge` 兩行。
file: `docs/lumos-toolchain-knowledge/Projects/OpenSpec_調研.md:25`、`:26`——同時有 `scope/node-content` 與 `scope/guards-gates` 兩行。
這不是理論案例,是真實存在的計劃筆記。

## F3 治理帳裡同一提交出現重複/測試性質的 code-loop 通過紀錄,母體定義沒排除
severity: major
blocking: 是——第二件的母體是「已推上遠端、有代碼審通過留痕的提交」,直接讀 `gate=code-loop, kind=passed`;但帳上同一個 `commit` 可以有多筆通過紀錄,其中內容明顯是驗證指令輸出而非真實審查收斂,spec 沒交代抽樣母體要不要先按 commit 去重、也沒交代怎麼分辨「這筆通過紀錄是不是真的迴圈收斂」——實作者照字面把每一筆 `passed` 都當一個母體成員,會讓同一個提交在雜湊抽樣的分母裡被算兩次以上,S5「抽中比例在大量提交上接近設定值」的驗證會被這種重複污染。
引句:「母體:已推上遠端、有代碼審通過留痕的提交」
file: `docs/.governance-log.jsonl:68705`——`{"commit": "c150c74", "gate": "code-loop", "kind": "passed", ..., "detail": "驗證留痕會不會列出該提交的簿記檔"}`
file: `docs/.governance-log.jsonl:68706`——同一提交 `c150c74` 同一秒又一筆 `passed`,`detail`「驗證縮範圍後的輸出」——兩筆的 detail 讀起來像是在測試 `lumos gov` 本身的輸出,不是「這次改動的代碼審收斂」,但欄位形狀跟真的通過紀錄完全一樣,程式無法區分。

## F4 逃逸帳記的迴圈名跟審查帳存分級的迴圈名不同,分級 join 不上
severity: major
blocking: 是——代碼審通過後自動記逃逸帳(`--auto`)寫入的 `loop` 欄位是不帶 `code-` 前綴的計劃名,但同一次代碼審在審查帳(`.canary-log.jsonl`)裡存 `tier` 的紀錄用的是 `code-<計劃名>` 前綴;S1 的「分級」演算法说「取審查帳裡那個迴圈記到的分級」,若直接用逃逸帳的 `loop` 字串去比對審查帳的 `loop` 字串,比對到的是同名的設計審迴圈(沒有 `tier` 欄位),而不是真的存了 `tier=high/standard/light` 的代碼審迴圈——每一筆 stage=code-loop 的逃逸列都會被誤判成「未定錨」,不是邊緣案例而是代碼審逃逸列的常態情形。
引句:「取審查帳(`docs/.canary-log.jsonl`)裡那個迴圈記到的分級」
file: `docs/.escape-log.jsonl:21`——`{"loop": "收工點名問版本控制", "stage": "code-loop", "auto": true, "source": "code-loop", ...}`(無前綴)
file: `docs/.canary-log.jsonl:1676`——`{"loop": "code-收工點名問版本控制", "tier": "high", ...}`(有 `code-` 前綴,真正存 tier 的那筆)
file: `scripts/lumos:9885`——`_roster_kind` 靠 `loop_id.startswith("code-")` 分辨代碼審/設計審,印證這兩種迴圈識別字串在既有程式裡本來就分屬不同命名空間,spec 沒有交代逃逸帳分級 join 要怎麼跨過這道前綴差。

## F5 每週抽查上限 3 個,按目前推送量 10% 雜湊抽樣常態性超過上限,延後佇列沒有排空機制
severity: major
blocking: 是——按 S9,超過上限的延到下週;但用近 20 天實測的 `code-loop passed` 量(日均約 7 筆,週約 50 筆),10% 雜湊抽樣期望值約每週 5 個,已經高於週上限 3 個,代表幾乎每週都會觸發延後;spec 沒有交代佇列上限、優先序、或「多久沒排到就放棄/過期」,照字面實作會讓待抽佇列單調成長、離放行時間越來越遠,而「抽查已放行的改動」原意是量最近的漏網,佇列一直積壓會讓抽到的提交系統性偏舊,量出來的漏網率跟不上實際的放行品質。
引句:「每週最多 3 個(外家審查席有額度限制;也讓成本有上限)」
機械數:`grep -c '"gate": "code-loop", "kind": "passed"' docs/.governance-log.jsonl` 近 20 天分佈(`docs/.governance-log.jsonl`,依 ts 前 10 碼分組)單日高至 17 筆、多數工作日介於 6–13 筆之間,週總量遠高於「10% 抽樣後仍落在 3 個以內」所需的週量(≤30)。

已看,無:一句話段落與「為什麼先做這兩件」是背景敘述,不含可執行斷言,略過。第二件「誰來查、怎麼查」裡「不給原本的審查報告與結論」「外家席不通時退用同家族模型,但帳上標『同家族,獨立性弱』」與 S6/S8 一致,`lumos loop next --orchestrator` 已有「外家=不是編排者那一家」的既有語意(`scripts/lumos:30807` 一帶),沒有衝突。S5「抽不抽由提交編號雜湊決定、可重算」的形狀跟既有 `_TIER_ROSTER`/`loop next` 一類「帳面定錨、不可事後回改」的既有規矩一致,沒看到會破壞既有合約的地方。第三件「盲審對照實驗」的配對邏輯(鏡頭與家族跟同輪某一席相同)在單席 light/standard 編制與多鏡頭 high 編制下都能找到至少一席可配對(`_TIER_ROSTER` 逐輪內鏡頭名互不重複,配對=複製既有一席的鏡頭名開一席新的,不是「同輪內找重複鏡頭」),依既有代碼審的量(近 20 天多輪、每輪多席),12 對的量在數週內可以湊齊,不是瓶頸。回退段與誠實界線段已經誠實列出「量很小」「啟發式會歸錯」等限制,跟本輪抓到的 F1–F5 屬於同一類問題但這幾條是可以先在 spec 裡把演算法寫清楚就避免的,不算已經誠實承認過的範圍,所以仍然單獨列出。條款 S2/S3/S7/S9/S10/S11/S12 本身的敘述内部自洽,測試名可對應,沒發現矛盾或壞引用。

最嚴重 severity: major;blocking 共 5 條(F1–F5)。
