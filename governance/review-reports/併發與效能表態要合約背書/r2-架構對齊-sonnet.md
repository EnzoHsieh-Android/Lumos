severity: major

## 1. 分層與依賴方向:部分不對齊,⚠ 請編排者裁

對齊:推送前檢查只讀表態記錄,同 `_dispositions_verdict`(`scripts/lumos:37261`);寫表態時存衍生欄位有先例(candidates、written_at,`scripts/lumos:37055`;auto 欄 `scripts/lumos:37404`);硬編 docs 路徑讀帳同 `scripts/lumos:37111`、`scripts/lumos:7995`。

**AR1**
severity: minor
blocking: 否
引句:「讀本機 `docs/.kill-log.jsonl`(讀不到或沒有這個檔 → 背書=`none`,原因「本機沒有破壞測試紀錄」)。逐行 `json.loads`,壞行略過。」
file: `scripts/lumos:7291` kill-log 目前只有 gov 讀;guard kill 寫在 `scripts/lumos:13199`。code-loop 層直接讀 guard-kill 的帳沒有先例,等於第二個讀取者。建議抽共用讀取函式,或在 Systems/guard-kill 明寫有兩個讀者。⚠

## 2. 命名與錯誤處理

對齊:covers 與配方欄位同為小寫單詞(`scripts/lumos:12848`);method 同名區域變數(`scripts/lumos:13121`);contract_evidence 兩段式同 note_shape.negation(`scripts/lumos:25388`)與 `_stack_questions_config` warnings 慣例(`scripts/lumos:21417`);讀不到 kill-log 記 none 不擋,同 marker 寫失敗降級提醒的精神(`scripts/lumos:37693`)。

**AR2**
severity: minor
blocking: 否
引句:「在 `_STACK_QUESTION_SPECS` 的題目上加一個欄位 `evidence: "contract"`」
file: `scripts/lumos:37071` 表態記錄的 evidence 是實際證據;題目規格的 evidence 同名不同義,設定鍵又是第三種用法。建議改名如 needs_backing。

**AR3**
severity: minor
blocking: 否
引句:「配方=同一 node、同一 invariant、同一 file」
file: `scripts/lumos:12855` kill-add 判重複配方的鍵是 invariant、file、old;設計少了 old,同檔兩個不同 old 會併成一組。

**AR4**
severity: minor
blocking: 否
引句:「`contract_evidence` 為 `off` 或看不懂時」的對應處理設計未寫;r2 只寫了「附屬於整個表態閘」和回傳 dict 鍵。
file: `scripts/lumos:25433`、`scripts/lumos:29973` 兩個兩段式開關寫 off 或寫錯值時 doctor 都多唸一行,設計沒提。(席位自註:此引句不是 r2 原文)

## 3. 第二種做法

**AR5**
severity: major
blocking: 是
引句:「過期沿用表態既有的「改碼就要重表態」,不另寫一套過期判定」
引句:「對每一題「被標、而且 status=satisfied」的表態」
file: `scripts/lumos:37261` `_codeloop_record_valid` 綁提交;`scripts/lumos:13069` kill-log commit 整批只記最後一組。背書是寫表態那一刻對本機 kill-log 的取樣快照,卻存進被當成 CI 唯一真相的治理帳事件——「表態綁提交」之外引入第二種「值不綁提交、只綁本機當下狀態」的欄位,專案沒有先例。設計必須明說 backing 是本機快照、CI 不可重驗,提醒措辭跟著降級。嚴重度可由編排者降級。
派工鏡頭快取鍵本來就是整筆記錄 sha256(`scripts/lumos:35775`),設計這點說對了。

## 4. 落點

Systems/棧別提問表態閘 合理(DEP 已列相關函式,`docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:43`);Systems/guard-kill 合理。

**AR6**
severity: minor
blocking: 否
引句:「`lumos gov` 讀 kill-log 只取既有欄位,多出來的欄位不影響。」
file: `scripts/lumos:7291`;帳的形狀變動,lands_in 沒列 Systems/reversibility-governance-ledger,建議補列或在 Systems/guard-kill 明寫由它管。

不對齊共 5 條,其中 major 1 條(另有 1 條 minor 標 ⚠ 交編排者)
