severity: major

## 逐條 finding

### F1. 回退與新舊並存:舊版 vendored CLI 讀到新狀態值 fail/blocked 會報 lint 錯誤
severity: major
blocking: 是(舊版 CLI 遇到新狀態值就擋,spec 沒有版本過渡期的出口)
- 段落:C「驗證筆記狀態」,以及「回退」第一條。
- 問題:新版 CLI 把驗證筆記寫成 `fail` 或 `blocked`。消費專案若有人還在用舊的 vendored CLI,lint 會判這篇狀態不合法。「回退」只處理 revert 之後的清理,沒處理新舊版本並存的這段時間。
- 佐證:file: `scripts/lumos:6619`,`_created_e >= _ENUM_CUTOFF` 時,`status` 不在 `_STATUS_ENUM[t]` 就進 `errs`。本 repo 的 `.lumos/config.json` 設 `note_lint.gate: on`,所以這是錯誤等級,會擋。file: `scripts/lumos:6567` 的註解說明工具對「未知欄位」前向相容,但對「未知狀態值」不容忍。因此同一份帳的 `decisions` 加三個新欄位沒事,狀態值加 fail/blocked 卻會擋舊版。
- 另一處同族:`.lumos/config.json` 的 `capabilities`、決策新欄位舊版都容忍,只有狀態值例外。spec 沒寫「狀態值要等所有消費專案更新後才開始寫」的順序,也沒寫舊版會怎樣。

### F2. 新增的 `[evidence:]` 條款標籤,舊版 spec-gate 與 spec-trace 一律判成「未標」
severity: major
blocking: 是(舊版 CLI 擋住含新標籤的計劃,沒有出口)
- 段落:D 第 7 關、S10、「守衛面」。
- 問題:計劃條款只寫 `[evidence:節點]`、沒有 `[test:]` 或 `[manual:]` 時,舊版 CLI 把它算成 `untagged`。spec-gate 與 spec-trace 對 `untagged` 都擋。spec 只要求新版三處同步(`INV_TAG_RE`、規格閘文法、`spec-trace`),沒處理舊版讀新標籤的行為。
- 佐證:file: `scripts/lumos:7434`,`refs` 與 `manual` 都空時 `row["state"]` 為 `untagged`。file: `scripts/lumos:8212`,spec-trace 把 `untagged` 列為未滿足。file: `scripts/lumos:7343`,`_clause_check` 收集 `untagged`。
- 回退面:計劃筆記已寫進 `[evidence:]` 之後,把 S10 的 commit 回退,所有這類條款變成「未標」。spec 沒說這些條款要怎麼改。

### F3. S8 的 lint 檢查,與存量程式已有的「直接改 status」寫入路徑衝突,擋了又沒出口
severity: major
blocking: 是(合法的 pass 轉正路徑被新規則擋住)
- 段落:C「pass 要有證據」「繞過 `lumos set` 的寫法」、S8。
- 問題:新規則擋「2026-10-19 之後新建、狀態 pass、帳上沒有效證據列」的驗證筆記。但守衛紀錄(`guards` 欄位的 verification)是新建的 pending,日後由 `lumos guard settle` 直接改成 pass。`lumos drift fix --kind c3 --status pass` 也直接改 pass。這兩條路都不經 `cmd_set`,也不會有證據列。
- 佐證:file: `scripts/lumos:15706`,`_guard_settle_record_lines` 用 `edit_fm_scalar(…"status","pass")`。file: `scripts/lumos:38813`,`_drift_fm_status` 寫 status。file: `scripts/lumos:15052`,守衛紀錄建立時就是 `status: pending`。這些筆記不會帶證據帳列,lint 新規則會誤判它們,而 spec 沒有豁免條款。
- 後果:S8 只改 `lumos set`,繞過它的兩條路等於讓 pass 無證據(drift fix 直接繞過),另一條(guard settle)被 lint 誤擋。spec 的「舊筆記不追溯」只靠日期切,守衛紀錄在 10-19 後新建就受影響。
- 同族:`_DRIFT_C3_STATUSES = _STATUS_ENUM["verification"] - {"pending"}`(`scripts/lumos:38475`)會自動吸收 `fail` 與 `blocked`,讓 drift fix 可以把待定驗證改成 blocked 當作「解決」。spec 沒檢查這個連鎖。

### F4. S8 的證據版本有效性與專案規定的「推送前壓成一個提交」直接衝突,沒有不重跑的出口
severity: major
blocking: 是(證據在壓提交後全部失效,出口只有重跑,含壓測)
- 段落:C「pass 要有證據」。
- 問題:有效性採 `_codeloop_record_valid` 的判法:證據列的 HEAD 必須等於當前 HEAD,或是祖先且之間只動簿記檔。專案規定本機提交推送前要壓成一個、也常 rebase。壓過之後,帳上記的 sha 不再是祖先,所有證據列失效。
- 佐證:file: `scripts/lumos:48870` 的 `_codeloop_record_valid` 與 file: `scripts/lumos:48899` 附近的 docstring/訊息,明寫「把本機提交壓成一個、或 rebase 之後,內容可以一模一樣,原本記的那個提交卻不再是祖先」。code-loop 用重跑指令補救,證據帳沒有等價物。
- 後果:squash 之後 pre-commit 的 lint 與 `lumos set` 都擋 pass 的驗證筆記,唯一出口是整批重跑 `evidence run`。S12 那種 1000 併發 Docker 測試與 k6 壓測重跑成本高。spec 沒有「重新綁定同內容證據」的出口,也沒說淺 clone 的 CI 怎麼處理(`_codeloop_missing_commit` 會回「判不了」)。

### F5. 本案撤除與回退沒列齊要拿掉的東西,舊否決「復活」的指令走不通
severity: major
blocking: 是(回退路徑存在斷點,撤除條件觸發時無法照 spec 做完)
- 段落:RETIRE-IF ①②③、「回退」第二條。
- 問題 a(復活指令):spec 說用 `lumos decision-supersede` 把本篇 d1 作廢、指回舊決策。但舊決策(開發工作流總覽 d1)已經是 `valid: false` 且有 `superseded_by`,指令遇到這種情況會拒絕重翻。就算本篇 d1 被標成被舊決策取代,舊決策仍是 `valid: false`,兩條互指、沒有任何一條有效。
  - 佐證:file: `scripts/lumos:20383`,有 `superseded_by` 就丟 `ValueError`「這條決策已經被翻案過了…要改成被誰取代請手動編輯」。file: `docs/lumos-toolchain-knowledge/Systems/開發工作流總覽.md:30-39`,舊決策 `valid: false`、`superseded_by: Projects/後端工程提問與證據擴充_計劃#d1`。
  - 全域規則要求開頭欄位用指令改、別手改,所以 spec 要的「復活」沒有指令能做。
- 問題 b(RETIRE-IF 沒列清單):①只寫「撤掉小節與規格閘對它的檢查」,漏了 S2 的 lint 規則、S3 的排序與只列三題、`--stage` 參數、「後端資料與交易」風險類與 `_PITFALL_QUESTIONS` 雙形狀讀取。②只寫「撤掉指令,驗證筆記退回散文」,漏了 S8 的 `lumos set` 限制、lint 規則、範本預設、fail/blocked 狀態值、簿記名單新增項、E 的停止條件。③「交付前證據檢查」沒有指令名、沒有 S 條款,和 `evidence check`(S9)、`spec-trace`(S10)的對應也沒寫。
- 問題 c(「回退」節範圍):只涵蓋待決問題檢查、證據擷取、狀態值、範本預設。B 能力清單、E、`[evidence:]` 綁定、`decision-add` 三欄、`--stage` 都沒寫回退做法。

### F6. 證據帳加進簿記名單,回退或新舊並存時,留下的帳檔會讓代碼審留痕失效
severity: major
blocking: 是(舊版 CLI 或回退後的 CLI 會把帳檔提交當程式改動,擋推送)
- 段落:C「pass 要有證據」,「回退」第一條「證據帳留檔不刪」。
- 問題:spec 要把證據帳與原始檔目錄加進 `_BOOKKEEPING_FILES` / `_BOOKKEEPING_DIRS`。回退只寫「帳留檔不刪」,回退同一個提交會一併拿掉名單項目,帳檔從此被當成程式改動。舊版 vendored CLI 本來就不認這些名單項。
- 佐證:file: `scripts/lumos:27097` 與 `scripts/lumos:27116` 兩份名單。file: `scripts/lumos:48899`,`_codeloop_record_valid_ex` 只在 `all(f in _BOOKKEEPING_FILES or f.startswith(_BOOKKEEPING_DIRS))` 時豁免,帳檔不在名單就回「之後動了代碼」。file: `scripts/lumos:22677`,來源髒檔合併也只認名單。
- 後果:同一個消費專案有人用新版 CLI 記證據、有人用舊版 CLI 推送時,每次證據帳提交都讓舊版端的 code-loop 留痕失效,逼出重審;回退之後同樣。spec 的 `_BOOKKEEPING_*` 三個使用者對照測試只管加名單的當下,沒管這個方向。
- 另一個缺口:spec 沒給證據帳檔名與原始檔目錄的路徑(S5 的測試無從指定),Q2(原始檔進不進版控)又是未決的阻塞題;`scaffold` 的 `docs/.gitignore` 對新帳不會自動補,spec 只寫「不能被忽略清單擋掉」,沒寫誰負責確認。

### F7. E 的累計 FAIL 停止條件永不歸零,修好之後仍然擋,且帳是追加式、沒有作廢列
severity: major
blocking: 是(已修好的條款被永久標停,沒有出口)
- 段落:E「同一條款累計三列 FAIL,不論原因都停」、S9、S7、C。
- 問題 a:條款累計三列 FAIL 就停,後來的 PASS 列不會歸零。S13 要求「FAIL 後修好留 PASS」,第三次 FAIL 之後再修好,`lumos evidence check` 仍回非零。
- 問題 b:證據帳追加式,沒有「作廢某列」機制。`--criterion` 打錯條款編號,FAIL 就記到別人的條款上,累計進別條的停止計數,無法更正。
- 問題 c:S7 寫「BLOCKED 之後把對應驗證筆記設成 pass 應被拒絕」,但 S8 的規則是「有一列 PASS 且版本有效就放行」。BLOCKED 之後重跑成功的 PASS 列到底放不放行,兩條矛盾;E 的「拿不到證據不准設 pass」也沒說拿到之後的解除路徑。
- 這個檢查若接進交付前證據檢查,就是無出口的誤擋(spec 自己在「守衛面」承認誤擋會訓練人繞過)。

### F8. 證據帳與原始檔要進版控並推上遠端,遮蔽只抓常見命名,秘密一旦推出無法回退
severity: major
blocking: 是(prod-irreversible,回退不了已推出的內容)
- 段落:C「存檔前遮蔽」「證據帳要被追蹤」、實務隱患「秘密」、S6。
- 問題:`evidence run` 把 stdout/stderr 原樣存檔,帳要進版控、CI 要讀。遮蔽只針對名字像 TOKEN/PASSWORD/SECRET/KEY 的環境變數與連線字串密碼。指令輸出裡的 JWT、API 回應、`psql` 印出的資料、自訂名稱的變數都不在範圍。spec 實務隱患自己承認「抓不到自訂名稱的秘密」,處理方式只是「示範 repo 走環境變數」,這只管示範 repo,不管其他消費專案。
- 佐證:file: `scripts/lumos:23079`-`23084` 可見帳檔進版控的設計(治理帳刻意不忽略);spec 沒有任何提交前掃描、推送前掃描,也沒有「已推出的證據檔怎麼清」的回退步驟。revert 提交不會把秘密從遠端歷史移除。
- 缺的出口:提交前的機器掃描(例如把已知環境變數值反查原始檔),以及洩漏後的處理流程。

## 逐節與固定席

- 緣起與現況:已讀,無 finding。
- 做法 A(情境出題):已讀。回退面的問題併入 F5,新舊並存方面 `decisions` 新欄位舊版容忍(`scripts/lumos:6567`),無 finding。
- 做法 B(能力清單):已讀。`.lumos/config.json` 的 `capabilities` 舊版容忍未知鍵,回退時沒寫怎麼處理已填的清單,併入 F5 問題 c。
- 做法 C:見 F1、F3、F4、F6、F7、F8。
- D、F、驗收條款、分階段、不做:已讀,除上列外無 finding。
- 固定席(此設計會不會破壞該節點宣稱的行為或合約):
  - 開發工作流總覽 d1:不影響。翻案本身合法,但復活路徑有斷點,見 F5。
  - 規格閘、spec-trace:會影響。`[evidence:]` 讓舊版判未標,見 F2。
  - lumos-cli-write 的 `lumos set`:會影響。S8 與寫 status 的存量旁路,見 F3。
  - bound-tests-gate 與簿記名單三個使用者:會影響。名單新增與回退,見 F6。
  - 棧別提問表態閘、guard-kill、lumos-guard:不影響。本案不改它們的判定。

## 實務隱患逐類
- payment:無。spec 明寫訂單只到建立與扣庫存,不含付款。
- external-send:無,但範圍窄。spec 只在示範 repo 設定 k6 目標限定 localhost。`evidence run` 本身是任意指令代跑,對其他消費專案沒有目標限制。
- prod-irreversible:有,見 F8。能力清單禁止正式環境 WRITE 這條有寫,但已推出遠端的證據檔沒有回頭路。

總結:最嚴重為 major;blocking 共 8 條(F1 到 F8)。

## 補引句(編排者續談請同席補,只補不改判)

- F1 引句:「`_STATUS_ENUM` 的 verification 加 `fail` 與 `blocked`」
- F2 引句:「當計劃條款綁了 `[evidence:<驗證節點>]` 而證據帳沒有對應的有效 PASS 列時」
- F3 引句:「lint 對 2026-10-19 之後新建、狀態 pass、證據帳沒有有效列的驗證筆記報錯」
- F4 引句:「或證據列的版本是 HEAD 的祖先且之間只動簿記檔」
- F5 引句:「用 `lumos decision-supersede` 把本篇的翻案決策作廢、指回舊決策」
- F6 引句:「證據帳與原始檔目錄要加進這兩份名單,不然每提交一次帳檔,帳上的證據就全部過期」
- F7 引句:「同一條款累計三列 FAIL,不論原因都停。」
- F8 引句:「遮蔽規則只抓常見命名,抓不到自訂名稱的秘密」
