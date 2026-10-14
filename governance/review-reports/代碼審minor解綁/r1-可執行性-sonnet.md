severity: major

我照字面把計劃〈做法〉實作了一遍。處置閘那段(`scripts/lumos` 約 27150 行)接得上。取 `latest`、`carrier["finding_severities"]`、`_report_severities` 都是現成的。`finding_severities` 又要求鍵等於 findings_set 全集,逐 id 查表可行。難處在三個地方:防放水檢查本身擋不住它宣稱要擋的事、降級清單可以把分母灌大、「各席最新一筆」認不出來。

我做了這些驗證:
- 現行程式、現有測試和帳本都對照過,沒有實際動手寫實作。
- 對帳本跑過統計,結果在 F3 和 F6。

**F1 防放水檢查擋不住把 major 標成 minor**

引句:「分子:accepted 裡逐條嚴重度標成 minor 或 clean 的 id 數。」

severity: major
blocking: 是

- **字面會怎樣**:分子只算 accepted 裡的 minor,分母卻是全輪所有 minor 宣告。
  - 帳上 77 個有 major 的輪次平均每輪 2 條以上 minor(176 條 minor 除以 77 輪)。
  - 編排者只要把一條真 major 標成 minor 再放行,分子是 1,分母只要有一條 minor 就過。
  - 其他 minor 全折入也一樣,它們一樣佔著分母。
  - 計劃〈實務隱患〉寫「記帳時數量檢查擋住把 major 標成 minor」,字面做出來的不是這個效果。
- **應該是**:算 findings_set 全集(折入加放行)裡標成 minor 或 clean 的總數。這個數不得大於報告 minor 宣告數加(經核實的)降級數。
  - 再加一條下限:輪內既然有 major 席,findings_set 至少要有一條標 major 或 blocker,或有降級紀錄。
  - 否則只改一條標籤就不會被數量差抓到。

**F2 降級清單沒有上限,可以任意灌大分母**

引句:「再加上載體降級清單的條數。」

severity: major
blocking: 是

- **字面會怎樣**:降級項的驗證條件只有五項:id 在 findings_set、標 minor 或 clean、理由至少 4 字、有 `--intake`、intake 同一列出現該 id。
  - 沒有任何一項證明「這條原本被某份報告宣告為 major」。
  - 每多列一個降級 id,分母就加 1。
  - 編排者把原本就是 minor 的 id 也列成降級,就能把分母撐大,F1 那道檢查形同虛設。
  - 降級 id 若只被折入、沒被放行,分母也照樣加,分子卻不動。
- **應該是**:
  - 降級條數不得多於報告裡 major 與 blocker 的宣告數。
  - 只有 accepted 內的降級 id 才算進分母。
  - 或者改成直接從 major 宣告數扣掉再比。

**F3 「各席最新一筆」在現行帳上定義不出來**

引句:「分母:同輪各席最新一筆帳」

severity: major
⚠
blocking: 是

- **現況**:處置閘的 `latest` 是該輪所有帳列。
  - 其中沒有「各席最新」這個概念。
  - `auditor` 欄放的是模型名,不是席名。
  - 我查帳本,`code-delguard` r1 有三列 `sonnet` 的 sha 都不同(是同一席重記還是三個不同席,帳上看不出來)。
  - 帳上有 18 組(迴圈、輪、auditor)帶不同 report_sha256,其中 5 個是 code 迴圈。
- **兩個人會寫出不同結果**:
  - 甲照標題取「每個 auditor 的最後一列」:同名的不同席被併成一席,分母偏小,合法放行被誤擋。
  - 乙照括號取「(auditor, report_sha256) 全部去重」:同一席被取代的舊報告也進分母,分母偏大,放行被放寬。
- **應該是**:二選一寫死。
  - 若採 (auditor, sha) 去重,就承認舊報告也計入,刪掉「最新」二字。
  - 並說明這樣會偏寬(跟 `_review_yield_round` 現行做法同款)。

**F4 降級清單照字面無法「比照 `--refuted-set`」共用程式**

引句:「id 在收貨紀錄的重現表同一列出現(整字比對)」

severity: minor
blocking: 否

- **現行 intake 驗證不能直接共用**:它是內嵌在 `cmd_canary` 裡的 inline 程式(約 10786–10818 行),不是函式。
  - 它要求 id 不在 F,降級要求 id 在 F,兩者相反。
  - 同一列還要含 HIT/MISS/重現/採信 其中一個字。降級項的 intake 列不一定有這些字,計劃沒說沿用還是換關鍵字。
- **旗標格式沒定**:`--refuted-set` 是一個逗號分隔字串,`--finding-severity` 是 `action=append` 可重複。計劃寫「可重複」,但沒說用哪種。
- **缺的規格**:
  - 帳上欄位名與型態沒定,同 id 重複給了算不算兩條也沒定。
  - `_GOV_FIELD_TYPES` 型別白名單沒提到新欄位。
- 這些要先抽共用 helper,實作者才寫得一致。

**F5 報告讀取失敗時的 fail-closed 語意有歧義**

引句:「報告讀不到時照處置閘既有的留痕重驗判不過(fail-closed)。」

severity: minor
blocking: 否

- 數量檢查在 ② 步,留痕重驗在 ③ 步,而且 ② 先讀檔、③ 才驗 sha。
- 讀不到時,② 自己判不過,還是放過、交給 ③?兩種寫法最終都是整體不過,但 ② 的訊息和 `fails` 標籤不同。
- 讀檔要像 `_severity_check_row` 一樣用 `errors="replace"`。否則非 UTF-8 報告會在 ② 直接 traceback,而現有 ③ 對這種檔有自己的處理。
- `root=None` 時 `_prov_path` 會回相對路徑,也要想一下。

**F6 計劃對舊帳的事實陳述不精確,S6 結論仍成立**

引句:「舊帳的載體都沒在 major 輪帶」

severity: minor
blocking: 否

- **帳本實況**:`code-規格閘半套` r1 的載體在 major 輪帶了 `finding_severities`,並放行 X4 和 X7,兩條都標 minor。r1 的 major 席和這條放行都在同一輪。
- **為什麼 S6 仍成立**:`loop replay` 判的是 `groups` 最後一輪(r3),r3 的 accepted 是空的,所以回放判定不變。
- **該改的**:把那句話改成「判定輪(最後一輪)沒有這種載體」,別寫成全帳都沒有。
- **另一個保護點**:現有測試 `t_panel_probe_retired`(`scripts/test_lumos.py` 約 9049 行)斷言舊分支訊息含「major 一律折」。沒帶逐條嚴重度的舊分支要保留這串字。

**F7 分母把 clean 也算進去**

引句:「數 minor 與 clean 的宣告行」

severity: minor
blocking: 否

- 現行 `_report_reported_count` 刻意排除 clean(clean 不是發現)。
- 分母把 clean 算進來會灌大分母,使檢查更鬆。
- 「去掉檔級那行」是 `decl[1:]` 的做法,只在報告已正規化、第一行確實是檔級宣告時才對。2026-09-09 前的舊報告不保證。
- 數量檢查只該對新迴圈生效,或者先確認檔首是檔級行。

**F8 測試造帳可行,有兩點要先補進計劃**

引句:「當代碼審某輪有 major 席、載體沒帶逐條嚴重度、accepted 非空時」

severity: minor
blocking: 否

- **造帳可行**:`t_panel_probe_retired` 的做法可以直接沿用。迴圈名要 `code-` 開頭,報告第一行是檔級 `severity:`,另附一行一條宣告,再加 `--snapshot`、`--spec`、`--reviewed`。
- **S5 和 S8 要補的東西**:
  - 同一輪至少要有兩列帳:一列 major 席,一列載體。兩份報告內容不同。
  - 需要手寫 intake 檔,含 HIT 字樣的列。
  - 計劃沒提這些,測試作者得自己摸索。
  - S5 還應該加一個「分子剛好等於分母」的邊界案,以及 F1、F2 對應的案例。
- **S1 到 S4 與 S6**:只需要在上面那套造帳上改嚴重度和 accepted,可行。

**固定席節點**:派工詞尾端沒有附任何固定席節點,所以沒有可逐條判的項目。

總結:最嚴重等級 major,blocking 共 3 條(F1、F2、F3),minor 共 5 條(F4 到 F8)。

相關檔案:
- /tmp/代碼審minor解綁-r1.md
- /Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-rst/scripts/lumos
- /Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-rst/scripts/test_lumos.py
- /Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-rst/docs/.canary-log.jsonl
