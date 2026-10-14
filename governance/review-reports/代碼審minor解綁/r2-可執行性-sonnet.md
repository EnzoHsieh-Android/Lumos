severity: major

派工詞尾端沒有附固定席節點,所以沒有逐條判的項目。

我對著 `scripts/lumos` 現行程式推演,並對帳本裡 2223 列代碼審帳的真報告用 `_report_severities` 與 `_report_normalize_issues` 實際數過(腳本放在 `/tmp/lumos-seat-work/代碼審minor解綁/可執行性-sonnet-r2/`)。

### 1. 只有檔級行、沒有逐條宣告的 major 報告,不會產生任何「要被指到」的義務

引句:「報告已正規化(記帳寫側本來就擋沒正規化的),所以檔首必是檔級行。」

severity: major
blocking: 是

- **字面會發生什麼**
  - 第 2 點只要求「檔級行之後」的 major 宣告都被指到。
  - 但 `_report_normalize_issues` 並不要求每條 finding 都有獨立的 severity 行。
  - 真帳裡有 5 列代碼審帳是這種形狀:`governance/review-reports/接手視圖/r1-外家codex.md` 到 `r4-外家codex.md`,以及 `governance/review-reports/code-batch19/r1-架構對齊.md`。這些報告用 `### 1 / major / 標題` 的標題寫法,通過正規化,但 `_report_severities` 只回 `['major']`。
  - 這幾份裡 `接手視圖` 的四份帳列都是載體。
  - 照字面,這類報告去掉檔級行後是空清單,第 2 點對它零義務。
  - 編排者讓另一份 minor 報告當 `finding_sources` 來源,就能把整輪 minor 放行。實際的 major 內容散在散文裡,閘看不到。
- **應該是什麼**:第 2 點要補一條:某份報告檔級是 major 或 blocker,但去掉檔級行後沒有任何宣告達到該等級,就判不過並點名這份報告。順手建議寫側也補擋,避免再產生這種報告。
- file: `scripts/lumos:10252`

### 2. 辯方降級要核對 file:line,但它對照的是會漂移的工作樹,而凍結閉包沒有收它

引句:「現有帳上沒有任何載體帶這個欄位,所以所有既有凍結判定的判定輪都走舊分支,判定不變」

severity: major
blocking: 是

- **字面會發生什麼**
  - 第 3 點與 [S7] 用 `_refcheck_scan` 與 `_validate_repo_ref` 去驗 repo 現況的 `路徑:行號`。
  - 凍結閉包只收判定輪各列帳的 report 與 snapshot 兩種檔。
  - 上線後有迴圈用 evidence 降級放行原報 major 並凍結。之後 `scripts/lumos` 或任何被引用的檔一改,行號位移或檔案刪除,回放重算就判不過。
  - 這會被報成「邏輯漂移」,週跑紅燈 rc1。
- **這是設計自己的缺口**:設計只論證了「上線前的帳不受影響」(S11),沒處理「上線後新凍結的帳」。
- **應該是什麼**:二選一。
  - 讓這個檢查在凍結時把驗過的 file:line 結果(或被引檔的 blob)寫進閉包,回放用閉包重算。
  - 或像 `_refcheck_scan` 支援的 `路徑@提交:行號` 那樣,要求理由用釘版本寫法,對固定提交驗。
- 另外要加一條「凍結後工作樹改動,回放不漂移」的條款與測試。
- file: `scripts/lumos:1060`

### 3. 寫側「檔名要是同輪某一列帳的 report_path」會讓大多數載體的來源指不到自己的報告

引句:「寫側只驗格式:id 要在 findings-set、檔名要是同輪某一列帳的」

severity: major
blocking: 是

- **字面會發生什麼**
  - 寫側檢查發生在載體這一列落帳之前,當下帳上只有「已記的列」。
  - 我統計了 563 個有載體的代碼審輪,其中載體席在同輪還有另一列帳的只有 41 輪(約 7%)。
  - 其餘約 93% 的載體,席報告只在載體這一列自己的 `--report` 裡。
  - 字面實作的人若只查帳上已有的列,`--finding-source id=自己那份報告#1` 會被 rc 2 擋下。
  - 另一個實作者若順手把 `--report` 本身納入,就會放行。兩人結果相反,S10 的測試也造不出同一種帳。
- **應該是什麼**:明寫「合法檔名集合=帳上同輪既有列的 report_path 加上本次記帳自己的 `--report` 的檔名」。
- **同一段還有兩處沒定**
  - 「檔名」是 basename 還是帳上存的相對路徑。帳上 3873 筆是相對路徑,只有 2 筆絕對。
  - 序號後綴要用 `rpartition('#')`,因為檔名可能含 `#`。
- file: `scripts/lumos:10708`

### 4. 「file:line 佐證」的判準沒定義,不同實作者結果不同

引句:「路徑在 repo 裡存在且行號不超出檔長(沿用 refcheck 的解析)。」

severity: major
blocking: 是

- **含糊處一:`_refcheck_scan` 不認 `file:` 前綴**
  - 它掃的是整段文字裡所有含 `/` 且頂層目錄存在的 inline code。沒有 `/` 的 `README.md:3` 根本不抽取。
  - 「至少一個 `file:` 佐證」與 [S7]「附的檔不存在、或行號超出檔長就判不過」互相矛盾。
  - 一段理由同時有一個好引用和一個壞引用(例如其中一個行號超出檔長),實作者可以選擇至少一個 ok 就過,也可以選擇有任何 missing 或 out_of_range 就擋。
- **含糊處二:沒寫行號的引用也算 ok**
  - `_validate_repo_ref` 在 `line==""` 時只驗檔案存在就回 ok。
  - 照字面,理由裡寫一句 `scripts/lumos` 就能把原報 major 降級放行。這個降級關卡實際上只驗「檔案存在」。
- **含糊處三:`root` 為 None 時怎麼辦**:處置閘的 `root` 可能是 None(`_prov_path` 有處理),設計沒說。
- **應該是什麼**:明訂「必須帶行號,且全部引用都要 ok」(或「至少一條帶行號 ok」),並加上沒帶行號與一好一壞兩個案例。
- file: `scripts/lumos:28548`

### 5. 序號沒有對應的工具可查,算法又和 `reported` 的口徑不同

引句:「去掉檔首那一行檔級宣告之後的第幾個(從 1 起)。」

severity: minor
blocking: 否

- 序號是機械確定的,對 1948 份正規化的真報告用 `_report_severities` 都能算。
- 但它會把 clean 行也算進序號,而現有的 `_report_reported_count` 是 `decl[1:]` 排除 clean 的口徑。實作者很可能直接重用它而算錯。
- 設計沒有提供「列出某份報告的編號、等級」的指令。編排者要用眼睛數,而圍欄內的示範行不算、clean 行要算,很容易數錯。
- 數錯的結果是 S3 或 S13 把該過的輪擋下,不是放水。
- 建議 `severity-check` 或一支新指令印出「序號、等級」,手冊也寫明 clean 要算。

### 6. `_gov_event_types_ok` 的值檢查放錯地方,也沒有條款能測到

引句:「讀不到或 sha 不符,這一步判不過。」

severity: minor
blocking: 否

- `_gov_event_types_ok` 只被 `cmd_gov`(`scripts/lumos:9774`)用,處置閘讀帳走 `_canary_ledger_scan`,沒有型別檢查。
- 手改帳讓 `finding_sources` 變成非 dict,新步驟會 traceback,不是 fail-closed。新步驟應自己防壞值。
- 現有檢查是 `for k in ("finding_kinds","refute_verdicts")` 逐值要求是字串。把 `finding_sources` 照抄加進這個 tuple,每個合法的 list 值都會被判錯,整列從 gov 消失。要另寫分支。
- S1–S16 沒有任何一條測 `_GOV_FIELD_TYPES` 或 `_gov_event_types_ok`,這件事造不出紅燈。
- file: `scripts/lumos:9732`

### 7. 接線細節沒定,實作者要自己猜

引句:「新步驟接在 `_loop_status_disposal` 的步驟序列裡」

severity: minor
blocking: 否

這句含反引號。以下是對照現行程式後找到的,設計都沒寫:
- 步驟簽名:`_disposal_security_step(rounds, rid, loop_id, prov_path)` 只收 `rounds`。新步驟還要 `latest`、`carrier`、F/FO/AC、`reasons` 與 `root`,要明寫。
- 要不要加進成功橫幅 `_extra` 的清單和 `fails` 名稱。回放的 golden 會比 `fails`。
- 帳上沒帶 report 的列(例如結局帳)要跳過還是判不過。留痕重驗已經擋,但新步驟要自己決定。
- 同一輪有 48 輪出現兩列帳指向同一個 report_path(席先留痕、再當載體)。要明寫「按檔去重」,否則同一份報告的 major 會被重複要求交代。
- 現行 `_prov_check` 只回狀態、不回內容。「讀檔走 `_prov_check` 驗過 sha 的路徑」會變成先驗 sha、再讀一次,中間有 TOCTOU。建議一次讀位元組、同時算 sha 與解碼。
- 寫側 `scripts/lumos:10708` 那行「要跟 --findings-set 一起給」的清單沒列 `--finding-source`。沒列的話,單獨給旗標會被悄悄忽略,因為驗證在 `if f_set is not None:` 區塊裡。
- 條款空缺,以下都沒有對應的測試條款:同一個 `id=檔名#序號` 去重、多個 id 指同一條、S15 的辯方降級例外、`finding_sources` 為空 dict 時算不算「沒帶」。

### 8. 兩條條款本身有小問題

引句:「當用現有帳本對既有已凍結的迴圈跑」

severity: minor
blocking: 否

- S11 把 `_REPLAY_ENGINE_REV` 釘成不變,但〈回退〉規定回退時要 bump。回退那天這條測試必須同步改。
- S11 依賴真實的 `docs/.canary-log.jsonl` 與 `governance/replay/`,測試會隨帳本長大而變。建議改成造一組假帳。
- S6 與重現不到清單:24 個含 major 的載體輪帶 refuted-set(393 輪中)。這些輪的 major 沒有 id,放行任何 minor 都會被第 2 點擋。
- 唯一的出路是把那條 major 假裝成發現、折入或用 evidence 放行。這是設計明講「不提供豁免」的選擇,但誤擋率不低,手冊要寫出路。

總結:最嚴重等級 major,blocking 4 條(第 1 到第 4 條)。
