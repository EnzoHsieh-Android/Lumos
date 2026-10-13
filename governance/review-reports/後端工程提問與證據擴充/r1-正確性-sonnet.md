severity: blocker

## 逐節結果

- 緣起與現況、PRIOR-ART、RETIRE-IF、REVISIT:已讀,無 finding。`_STATUS_ENUM`、`_BOOKKEEPING_*`、`toolExtra` 的現況描述都與程式一致。Q3「外掛不存回傳值」也屬實,file: `mods/claude/lumos-ledger/hooks/register.ts:67-83`。
- A 塊(待決問題):finding 1、2、3、4。
- B 塊(MCP 權限):finding 11。
- C 塊(證據):finding 5、6、7、8、9、12。
- E 塊(停止條件):finding 10。
- 驗收條款 S1–S13:finding 1、2、5、6、7、10 已涵蓋。

## Findings

### 1.
severity: major
blocking: 是
判準:S1 的閘門與 A 塊「依階段出題」互相衝突,照字面實作會卡死,屬流程走不通。
- 哪一段:S1 與 A「時機」。
- 問題:S1 對所有標阻塞且待查或待人的題目一律擋規格閘,沒有依階段過濾。標了 `[階段:效能]` 或 `[階段:驗證]` 的阻塞題,依設計要到實作後才能問、才能有證據,規格閘卻要它先已決才放行實作。
- 查證:file: `scripts/lumos:7800`。`cmd_spec_gate` 目前沒有任何階段概念。spec 只說規格閘「帶需求與架構」去呼叫 pitfalls,沒說 S1 的擋法也只看這兩階段。

### 2.
severity: major
blocking: 是
判準:一個字就能繞過 spec-gate 的阻塞檢查,而且 lint 抓不到。
- 哪一段:A「機械把關」、S1、S2。
- 問題:閘只擋「狀態是待查或待人」。把阻塞題改成 `[狀態:自答]` 或 `[狀態:延後]`(附任意理由)就放行。S2 只檢查「已決無連結」和「延後無理由」,不檢查「自答」是否附出處,也不檢查「`答:人` 卻標自答」。
- 查證:spec 在 A 要求自答「附出處」,但 S1、S2 都沒有對應條款。RETIRE-IF ① 只是事後量測,不是閘。

### 3.
severity: major
blocking: 是
判準:S3 排序和交付檢查依賴的欄位在行格式裡不存在,條款照字面無法實作。
- 哪一段:A「題目住哪」的行格式、S3、A「機械把關」。
- 問題:行格式只有 `類/階段/答/阻塞/狀態` 五種標記。S3 要排「不可逆」「跨多個模組」,沒有對應標記可讀。A 還說「標了要驗的已決題沒有證據列,不放行」,但沒有「要驗」標記。
- 查證:行格式見 spec 第 97 行。`_PITFALL_QUESTIONS` 只回題目字串,見 file: `scripts/lumos:26474`。

### 4.
severity: major
blocking: 是
判準:「已決」只驗連結存在,與題目沒有綁定,連到任何一條決策都算數,等於可捏造答案。
- 哪一段:S2、A 的決策擴三欄。
- 問題:
  - 已決只要求連到「存在的決策」,不要求該決策 `valid: true`,也不要求決策的 `--answers` 指回這題。連到已作廢或無關的 d1 照樣過。
  - `--answers` 是選填,所以題目和決策之間沒有雙向約束。
  - 連結寫法有 `#dN`(本節點)和 `<rel>#dN`(全域)兩種,spec 沒說兩種是否都認。
- 查證:file: `scripts/lumos:20434`。`cmd_decision_add` 現行簽名沒有 answers。`parse_decisions` 有 `valid` 欄,見 `:18101`。

### 5.
severity: blocker
blocking: 是
判準:有效性判法與「提交驗證筆記」的正常流程自相矛盾,照字面實作會讓每一篇新 pass 筆記一提交就變 lint 錯誤。
- 哪一段:C「pass 要有證據」、「繞過 lumos set」、S8、S10。
- 問題:
  1. 證據列的版本是跑指令當下的 HEAD(X)。之後提交驗證筆記和計劃筆記得到 Y,X 到 Y 之間改的是 `docs/.../Verification/*.md`,不在 `_BOOKKEEPING_FILES` 或 `_BOOKKEEPING_DIRS`。spec 只打算加進證據帳和原始檔目錄,所以 X 變成「非簿記的祖先」,證據判無效。
  2. lint 是持續性檢查。任何後續的程式提交都讓 HEAD 往前,使所有 2026-10-19 之後的 pass 筆記全部變成 lint 錯誤。spec 沒區分「轉態當下檢查」和「事後持續檢查」。
- 查證:file: `scripts/lumos:48870-48930`。`_codeloop_record_valid_ex` 只在 `files` 全是簿記時才豁免。名單見 file: `scripts/lumos:27097-27123`,沒有 Verification 或 Projects 筆記路徑。代碼審的帳本提交只動簿記檔,驗證筆記不是。

### 6.
severity: major
blocking: 是
判準:「AI 不能編造證據」的承諾不成立,指令內容和判準都由 AI 自己決定。
- 哪一段:C「證據結果只由退出碼與 --expect 決定」、S5、S10。
- 問題:
  - `lumos evidence run --verify V --criterion P#S3 -- true` 退出碼為 0,就留下 PASS。指令和 `--expect` 都是 AI 自填,spec 沒有「指令必須與條款相關」的約束。
  - S10 只用驗證節點 V 比對,不比對 `--criterion`。任何一列指向 V 的 PASS 就滿足所有綁 `[evidence:V]` 的條款。
  - 證據帳是版控內的純文字檔,可以手動追加列,spec 沒有簽章或雜湊鏈。
  - 沒帶 `--expect` 且退出碼為 0 的結果,S5 沒定義。
- 查證:spec 第 119 行與 164 行。`cmd_spec_trace` 的判定只看條款綁定狀態,見 file: `scripts/lumos:8168`。

### 7.
severity: major
blocking: 是
判準:`[evidence:]` 條款在現行 spec-gate 和 spec-trace 會先被判成「未標」,spec 沒定義新增的狀態。
- 哪一段:D 表第 7 關、S10、實務隱患「守衛面」。
- 問題:
  - `clause_bindings` 只認 `[test:]` 和 `[manual:]`,只有 `[evidence:]` 的條款落入 `untagged`。spec-gate 設計期會擋它,spec-trace 也回非零。
  - 設計期證據還不存在,`[evidence:]` 條款應該算已綁定;交付期才要求有效 PASS。同一個標記有兩套判定,spec 沒寫清楚。
  - spec 只提到要同步 `INV_TAG_RE` 和條款文法,沒提 `clause_bindings` 的狀態表 `_CLAUSE_STATE_ZH` 與 `_clause_check`。
  - 本篇 S12 和 S13 用的是 `[manual:]`,spec-trace 對它回 0,所以交付檢查不會要求這兩條有證據列。
- 查證:file: `scripts/lumos:7370-7462`、`:6900-6910`、`:8168`。

### 8.
severity: major
blocking: 是
判準:「2026-10-19 之後新建」的判定欄位不存在或可被偽造,舊筆記豁免機制失效。
- 哪一段:C「pass 要有證據」、S8。
- 問題:驗證筆記範本只有 `date:`,沒有 `created:`。手改欄位就能把日期寫成 10-19 之前來繞過限制。spec 沒指定用哪個欄位,也沒說該欄位要用 git 首次提交日期交叉驗證。
- 查證:file: `scripts/lumos:21293`,範本是 `type: verification\nstatus: pass\ndate: {today}`。

### 9.
severity: major
blocking: 是
判準:S7、E 的「BLOCKED 不得 pass」與 S8 的「至少一列 PASS」互相矛盾。
- 哪一段:S7、S8、E。
- 問題:同一節點同一版本先有 PASS、再重跑得 BLOCKED 或 FAIL 時,S8 看「至少一列 PASS」會放行,S7 卻要求拒絕。spec 沒有「以最新一列為準」的語意。
- 補充:spec 說「指令跑不起來」判 BLOCKED,但經 shell 執行時找不到指令的退出碼是 127,會被判 FAIL 並計入 E 的 FAIL 累計。逾時秒數也沒有旗標或預設值。

### 10.
severity: major
blocking: 是
判準:停止條件的累計不重置、判定函式沒定義且沒有接線,實際上要嘛永遠不觸發、要嘛永遠鎖死。
- 哪一段:E、S9。
- 問題:
  - 「累計三列 FAIL」沒說遇到 PASS 是否清零。S13 本身(拿掉保護得 FAIL、還原得 PASS)和長期迭代都會累積,最終 `evidence check` 永遠非零。
  - 「失敗原文摘要(去掉時間與路徑後的雜湊)」沒有正規化規則。行號、port、隨機 id 會讓同一個錯誤雜湊不同,相同雜湊也可能是截斷造成的假重複。
  - `evidence check` 是獨立指令,spec 沒說它被規格閘、推送前或 lint 呼叫。「停」沒有後果。
  - E 說 BLOCKED 時「不准把計劃設成 done」,但 S1–S13 沒有對應條款,`lumos set <計劃> status done` 也沒有被列為要改的命令。
- 查證:`_drift_c3_hit` 只處理 `pending`,見 file: `scripts/lumos:35788`。

### 11.
severity: major
blocking: 是
判準:MCP 與真實系統寫入的防線只是「建議」加自報分類,對 `evidence run` 完全沒有約束。
- 哪一段:B「權限邊界」、實務隱患「不可逆」、S11。
- 問題:
  - `permissions.ask` 只是印出建議讓人貼(Q1 還在待人),不是強制。
  - S11 只檢查設定檔裡宣告的能力。沒登錄的 MCP 寫入工具和環境標成「staging」的正式連線都不會報錯。
  - `evidence run -- <任意指令>` 本身就是任意 shell。若使用者為了跑壓測允許 `Bash(lumos evidence run:*)`,`psql $PROD -c "DROP TABLE x"` 會以通過的 lumos 前綴被放行。spec 說「破壞性指令照 Claude Code 既有權限確認」,但前綴規則會直接放行包在裡面的指令。
  - 指令欄原文寫進版控的帳,沒有遮蔽。`curl -H 'Authorization: Bearer xxx'` 這類寫在命令列的秘密,S6 只處理環境變數值和輸出,漏掉。
- 風險類回答:
  - payment、external-send:spec 已排除,理由成立,k6 目標限定 localhost。
  - prod-irreversible:如上,防線不足。
  - 併發:證據帳追加寫有提到,沒有另外發現。
  - 資源:大小上限有提到。

### 12.
severity: minor
blocking: 否
判準:證據列只記 HEAD,沒記工作樹是否乾淨,PASS 可能對應未提交的程式。
- 哪一段:C「`lumos evidence run`」、S5。
- 問題:在髒工作樹跑測試得 PASS,列裡的版本是尚未包含這些修改的 HEAD。之後若只提交筆記與帳,證據判有效,但測的是未提交的程式。S5 的欄位清單沒有 dirty 標記。
- 查證:`_codeloop_record_valid_ex` 只比對提交,不看工作樹,見 file: `scripts/lumos:48887`。

### 13.
severity: minor
blocking: 否
判準:新決策欄位名可能撞到既有保護鍵,spec 沒指定寫入的欄位名。
- 哪一段:A「決策紀錄擴三欄」、S4。
- 問題:`decided_by` 已存在,在 `decision-amend` 被視為結構鍵,也在筆記形狀擋的結構鍵正規式裡。`--by` 沒說寫成哪個鍵;若另取名字,`decision-amend` 可改寫 `answers`、`by`、`rejected`。`--rejected` 要寫成多行清單,也要確認 `parse_decisions` 與 surgical 寫入(`decisions_items`)支援。
- 查證:file: `scripts/lumos:40949`、`:30513`、`:18101`。

### 14.
severity: minor
blocking: 否
判準:`fail` 與 `blocked` 加進狀態值會擴大 drift c3 的可選值,spec 沒處理。
- 哪一段:C「驗證筆記狀態」。
- 問題:`_DRIFT_C3_STATUSES = verification 狀態 − {pending}`,新增的值會自動變成 `lumos drift fix --kind c3 --status` 的合法選項。人可以把待定筆記標成 `blocked` 來消掉漂移警告。範本預設改 `pending` 也會讓每篇新驗證筆記在計劃收尾後多出 c3 警告。
- 查證:file: `scripts/lumos:38475`、`:35788`。

## 總結
最嚴重 severity:blocker;blocking 共 10 條(findings 1、2、3、4、5、6、7、8、9、10、11 中 blocking 為是者,計 11 條,其中 blocker 1 條、major 10 條)。

更正計數:blocking 為「是」的共 11 條(1–11),blocking 為「否」的 3 條(12、13、14)。

## 補引句(編排者續談請同席補,只補不改判)

- F1 引句:「當計劃筆記的〈待決問題〉有一題標了阻塞、狀態是待查或待人時」
- F2 引句:「還有標阻塞、狀態是待查或待人的題目,規格閘不放行」
- F3 引句:「待人的題目依序:①標了阻塞的 ②不可逆的 ③影響跨多個模組的 ④其餘」
- F4 引句:「當〈待決問題〉一行的狀態是已決卻沒連到存在的決策、或是延後卻沒附理由時」
- F5 引句:「證據帳與原始檔目錄要加進這兩份名單,不然每提交一次帳檔,帳上的證據就全部過期」
- F6 引句:「結果只由退出碼與 `--expect` 判準機械決定(PASS/FAIL)」
- F7 引句:「新寫:擴 `spec-trace` 認 `[evidence:]` 綁定」
- F8 引句:「2026-10-19 之後新建的驗證筆記,狀態要設成 pass,證據帳裡至少要有一列指向它」
- F9 引句:「拿不到證據(BLOCKED)不准把驗證筆記設成 pass,也不准把計劃設成 done。」
- F10 引句:「同一條款累計三列 FAIL,不論原因都停。」
- F11 引句:「由 Lumos 產出建議的 Claude Code 原生 `permissions.ask` 條目讓人貼進設定」
- F12 引句:「寫一列進證據帳:證據編號、需求(計劃條款)、驗證節點、執行工具、環境、時間、程式版本(HEAD)、指令、退出碼」
- F13 引句:「加選填的 `--answers Q3`、`--by <誰>`」
- F14 引句:「`_STATUS_ENUM` 的 verification 加 `fail` 與 `blocked`」
