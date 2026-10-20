severity: major

## 範圍與已讀

整份凍結審材我都讀了(frontmatter、一到六、PRIOR-ART、實務隱患、回退)。前掃留痕 r1-intake 也讀過,下面不重報它已改的項目。

我查證的現況:
- CI 的 checkout 全是 `fetch-depth: 0`,所以 blame 取得到完整歷史,這一點沒問題。
- `_secinv_snapshot` 讀的是磁碟目錄,不是 git 提交,見 F6。
- `_SECINV_CTRL_KEYS` 沒有「威脅類別」欄位,見 F1。

## Findings

### F1 威脅類別欄位在 schema 裡不存在,`insufficient_required_evidence` 照字面算不出來
- 位置:〈一〉彙總規則第 1 點與〈二〉「每條資安護欄的 `required_evidence` 不能比它威脅類別的最低種類少」,另有 S14、〈綁版本〉的「威脅類別或必要種類改了,舊證據 stale」。
- 問題:規則要比較「這條護欄的威脅類別」對應的最低種類。但 v2 只新增了 `question_refs`、`revisions`、`exception` 的新欄位,沒有任何欄位寫明這條護欄屬於哪個威脅類別。
- 具體例:一條 OD-01 護欄 `required_evidence: ["review"]`,輸入沒有任何類別欄位。照 spec,閘門不知道要拿姊妹計劃表的哪一列來比,實作者只能自己發明欄位或猜,最壞情況是整條檢查不執行,只宣告 `review` 的護欄就被判 sound。
- 佐證:file: `scripts/lumos:6397`,`_SECINV_CTRL_KEYS` 只有 id、revision、concerns、source、lifecycle、assets、surfaces、nullable 組、required_evidence、evidence_refs、reported_status、exception。file: `scripts/lumos`,全檔 grep `authz-object` 與 `insufficient_required` 皆 0 筆。

severity: major
blocking: 是

判準:不補欄位定義,實作者會做出沒有「最低證據種類」守衛的閘,還是會自己發明欄位。

### F2 必驗集合只凍結「條目在不在」,判定輸入沒凍結,可以把護欄改弱再過閘
- 位置:〈四〉必驗集合以 merge-base 版為底。
- 問題:起點版比對只看條目被刪、降成 candidate 或 retired、`concerns` 拿掉 security 這幾種。同一條 active 護欄改了 `required_evidence`、威脅類別、`evidence_refs`、`assets` 或 `surfaces`,都不是凍結比對的項目,也不需要 `revisions` 核可。
- 具體例:起點版 OD-01 要求 `[behavior, fault_sensitivity, review]`。這次推送把它改成 `[review]`,revision 不動,同時附一份 review_record。規則 1 只比威脅類別最低種類,類別又是作者可改的(F1),所以 `insufficient_required_evidence` 不會觸發。這條護欄判 sound 放行,等於 G1「不能由 AI 任選子集」從條目層退到了種類層。
- 補充:被降級或刪除但「照樣當必驗、照樣判」時,spec 沒說用起點版還是推送版的欄位去判。用推送版的話,同一次推送裡就能順手把要求改弱,再用弱的要求判自己。
- 佐證:
引句:「必驗集合 = 要推的提交裡 active 且關注面含 security 的全部條目」

severity: major
blocking: 是

判準:照字面實作,AI 可以不經任何核可就降低一條既有護欄的要求並通過閘。

### F3 沒有「證據種類 × format × 工具類別」的允許表,弱證據可以冒充強種類
- 位置:〈二〉證據圍欄鍵名表(`kind`、`format`、`tool`)與「每種格式的合格判定」。
- 問題:`kind` 和 `format` 是兩個獨立必填欄位,qualified 條件是按 format 寫的。沒有任何一處規定哪個 kind 只准用哪些 format,也沒規定 `tool` 的登記類別必須能產生該 kind。`tool_unregistered` 只查工具有沒有列在清單。
- 具體例:作者為 `static_analysis` 護欄提交一項 `kind: static_analysis, format: junit`,內容是 2 個通過的測試。JUnit 的 qualified 條件只要求「宣告的非法案例與合法對照都在、都 passed」,所以判 qualified。`calibration_path` 要求「掃描類必填」,但缺的後果只在 SARIF 列寫成 `uncalibrated`,JUnit 列沒有這條路徑。結果 dependency_scan、secret_scan 這類種類都能用一份 JUnit 過關,完全沒有掃過東西。
- 佐證:
引句:「`format` | 必填 | `junit`、`tq_capture`、`guard_kill`、`sarif`、`k6_summary`、`review_record` 之一」
〈三〉的「工具類別→證據種類→標準輸出」表只是說明,不是閘門核對的規則。

severity: major
blocking: 是

判準:照字面實作,最好過的 format 可以套到任何 kind,「為了合格而合格」的第一道防線被繞開。

### F4 同一種類有多筆證據時怎麼彙總沒有定義,S17 與「作者不能挑」互相拉扯
- 位置:〈二〉guard kill、test-quality 兩條路,S17,〈一〉彙總規則第 2、3 點。
- 問題:規則只定義「每個必要種類是不是 qualified」,沒說同一護欄同一種類下有多筆 item(一壞一好)時,種類判定怎麼算。
  - 取「任一筆 qualified 即可」:作者把壞的證據留著、另補一份好過的,failed 或 invalid 的缺陷被蓋掉。
  - 取「全部都要」:S17 要求另收的真正目標翻紅證據「應能單獨判 qualified」,這句只能解釋成種類層也 qualified,兩者矛盾。
- 相關缺口:`targets.tests` 是作者自己宣告的,沒有任何機制要求某個入口或某條主張至少要有哪些測試被涵蓋。一個 qualified 的 behavior 只證明「作者挑的那幾個測試」綠。
- 具體例:OD-01 有 3 個入口,作者只宣告 1 個測試與它的合法對照,種類判 qualified。

severity: major
blocking: 是

判準:實作者必須自己決定彙總語意,選錯會讓 S17 與守衛強度兩邊其中一邊壞掉。

### F5 校準沒有跟宣告規則綁定,校準夾具也不在綁定集合內
- 位置:〈二〉「找到 0 個問題不等於證成」、鍵名表 `calibration_path`、綁定集合。
- 問題:prose 寫「同工具、同版本、同規則對已知陽性樣本找得到」。但 schema 只有一個 `calibration_path`,沒有欄位說明「校準檔裡必須命中的是 `targets.rules` 的哪些規則」。校準夾具(植入假秘密的檔、有漏洞的鎖檔)也不在「至少涵蓋」的綁定類別裡,改掉夾具讓它變成不會命中,再另存一份舊的校準輸出,不會讓任何東西 stale。
- 具體例:SARIF 校準檔命中的是規則 R9,宣告掃描的規則是 R1。照 spec 能判 qualified,實際上沒有證明 R1 掃得到。

severity: minor
blocking: 否

判準:不改,實作者仍會依 prose 的「同規則」寫出比對,只是缺欄位時要自行決定來源,屬可補強的精度問題。

### F6 盤點函式吃的是磁碟目錄,spec 的「用 git 讀那一版、跑同一支盤點函式」缺一步
- 位置:〈四〉起點;〈二〉「工作目錄與要推的提交不一致時,不讀工作目錄、照提交內容算」。
- 問題:`_secinv_snapshot(vault)` 用 `os.open(vault, O_DIRECTORY)` 加 `O_NOFOLLOW` 讀目錄,沒有「從 git tree 讀」的入口。要判起點版與推送版,就得先把兩個提交各自匯出到暫存目錄,或新增 git 讀取層。spec 沒寫用哪一種。匯出用的是 `git archive` 或 `checkout`,各有符號連結、權限、大小上限的邊界(盤點的 `symlink_rejected`、`file_too_large` 要怎麼對應)。
- 佐證:file: `scripts/lumos:6660-6685`。

severity: minor
blocking: 否

判準:不改,實作者會自己選匯出做法,結果仍是同一支函式,只是 S4「輸入等於 security list --json」要注意比的是哪個版本。

### F7 簽章載體在 rebase、squash、merge 後會失效,spec 沒說合法流程
- 位置:〈例外核准用簽章金鑰〉「找出要驗的提交」。
- 問題:blame 找到「最後改到那幾行的提交」,要求該提交有效簽章。專案慣例是推送前把本機多個提交壓成一個、並 rebase。壓縮或 rebase 會產生新提交,簽章不是丟掉就是由重做的那個身分重簽。使用者簽好的例外因此失效,每次都得重新觸碰金鑰。這個方向是擋下,不是放行,但會卡住合法流程。
- 另外,要驗的提交若是 merge 提交,spec 沒有指定母提交取哪一個去讀 `.lumos/security-approvers`。

severity: minor
blocking: 否

判準:不改,實作者會發現「簽了還是擋」才回頭補,但沒有造成放行錯誤。

### F8 `revisions` 核可紀錄的有效範圍太寬,且節點被刪時紀錄跟著消失
- 位置:〈四〉核可修訂紀錄。
- 問題:紀錄以 `control_id` 比對,`removed` 型紀錄不帶 revision。同一個 id 先被核可移除、之後重新登記、再被移除,第二次移除會被第一次的紀錄蓋住。反過來,若被刪條目所在的 Systems 節點整篇被刪或搬走,紀錄就在被刪的檔裡,spec 說「紀錄就留在原 Systems 節點」只在節點還在時成立。

severity: minor
blocking: 否

判準:不改,正常流程不受影響,是重複使用同一個 id 的邊界。

### F9 `review` 與 `deployment` 共用 `review_record` 格式,一筆紀錄能不能同時滿足兩個種類沒說
- 位置:證據種類表 deployment 列;`format` 值域只有一個 `review_record`;原因碼 `review_record_missing` 只屬於 review。
- 問題:一條護欄的必要種類同時含 `review` 與 `deployment` 時,一筆 review_record 是否各算一次,沒有定義。

severity: minor
blocking: 否

判準:不改,實作者會選一種語意,最壞是 deployment 被 review 代打,但 review 本身已是必要種類,風險小。

## 風險類逐類

- **守衛面**:會放行該擋的有 F1、F2、F3、F4。誤擋方向有 F7。
- **舊資料與舊帳相容**:無新增 finding。`exception` 在 v1 是 `decision_ref/reason/expires_on` 的單一物件(file: `scripts/lumos:6841`),v2 加欄位的做法相容,既有 v1 專案沒有資安登記時行為不變(S1)。
- **已在途分支**:未發現會誤改既有分支行為的路徑。
- **其他會談或計劃的交界**:已讀,無 finding。

## 各節結論

- 〈一〉輸出欄位與彙總順序:F1、F2、F4。
- 〈二〉證據種類與格式:F1、F3、F4、F5、F9。
- 〈二〉k6、SARIF 讀法:已讀,無 finding。
- 〈三〉工具接入:併入 F3。
- 〈四〉閘位置與早退:已讀,無 finding。CI 全歷史成立。
- 〈四〉必驗集合與核可紀錄:F2、F6、F8。
- 簽章金鑰一節:F7。
- 〈五〉條款:S14 受 F1 影響,S17 受 F4 影響。
- 〈六〉與回退:已讀,無 finding。

最嚴重 severity:major,blocking 共 4 條(F1、F2、F3、F4)。
