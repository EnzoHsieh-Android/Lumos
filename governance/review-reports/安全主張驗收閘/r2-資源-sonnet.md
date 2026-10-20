severity: major

審查席:資源-sonnet(第 2 輪)。白話:這套判定把「每個檔多大」管住了,但沒管「讀進來之後在記憶體裡多大」「同一個檔被很多條護欄引用時算幾次額度」「判定要跑多久」。三個缺口都落在大輸入下會出事的地方。

## Findings

### F1 XML 深度上限沒有落點,JSON 的「深度上限」只是 Python 遞迴例外

spec 段落:〈二〉〈讀不可信資料的上限與失敗處理〉。

引句:「JUnit XML 在解析時數元素深度,超過 64 層判 invalid。」

引句:「JSON 巢狀沿用 `_secinv_json_loads` 的深度上限;」

問題:
- 〈二〉JUnit 那列說「沿用 junit()」。`junit()` 用 `ET.fromstring(raw, parser=ET.XMLParser(target=NoDtdTreeBuilder()))` 把整棵樹建完,沒有任何深度計數。
- 〈四〉列的 `scripts/test_quality.py` 改動只寫「抽出核對本體的純函式」,沒有一項是在解析時計深度。所以「解析時數深度」沒有人負責。
- 我實跑:6.7 MiB 的 `<a>` 深巢狀,`junit()` 照吃,最後才報 zero testcases,常駐記憶體 387 MiB。外推 16 MiB 約 0.9 GB。
- `_secinv_json_loads` 本身沒有深度檢查,只擋重複鍵和 NaN。現有呼叫端靠捕捉 Python 的 `RecursionError` 當深度上限。我實測 10 萬層可以解析成功,100 萬層才拋 `RecursionError`。
- spec 新增的呼叫端(證據圍欄、SARIF 嚴格解析、k6、工具清單)沒寫要不要捕捉它。S42 的預期寫成「evaluation_error 或 invalid」,沒定下是哪一個。

具體例:一份 16 MiB 的深巢狀 JUnit(上限內)送進閘門。
- 預期:只讓引用它的護欄判 invalid。
- 照 spec:沒有深度檢查,整棵樹先建好,約 1 GB。
- JSON 同理:若新呼叫端漏接 `RecursionError`,落到「任何例外一律整道 evaluation_error」,所有護欄一起被擋。這跟同節「只擋引用它的那幾條護欄」矛盾。

佐證:
- file: `scripts/test_quality.py:151` 的 `junit()`
- file: `scripts/lumos:6688` 的 `_secinv_json_loads`
- file: `scripts/lumos:6975` 的 `_secinv_parse_block` 才有 `except RecursionError`

severity: major
blocking: 是
判準:照字面實作,XML 深度防護根本沒人寫,深層輸入會吃光記憶體或把整道閘打成 evaluation_error,實作者會做出壞系統。

### F2 位元組上限管不到解析後的記憶體,「快取解析結果」沒說存什麼

spec 段落:〈二〉〈讀不可信資料的上限與失敗處理〉。

引句:「同一次判定內,以(路徑、blob)當鍵快取解析結果:一份專案級 JUnit 被一千條護欄引用,只解析一次。」

問題:
- 上限(16 MiB 單檔、256 MiB 總量)全是原始位元組。解析成 Python 物件會放大很多倍。
  - XML 實測約 58 倍(6.7 MiB 吃 387 MiB)。
  - 我造的 11.6 MiB SARIF(6 萬筆 result,走 `_secinv_json_loads` 的 `object_pairs_hook`)實測常駐約 219 MiB,連同原始字串。
- spec 沒說快取放的是整棵解析樹,還是濃縮後的判定事實(案例表、命中清單)。
- 若照字面存整棵樹,整次判定結束前一份都不放。256 MiB 位元組上限允許約 16 份 16 MiB 的檔,解析後留存約 3 至 15 GB。
- 〈四〉另寫「git cat-file --batch 取全部需要的 blob」,要推的版加 merge-base 版的快照與證據位元組也全部同時在記憶體裡。

具體例:order-demo 之外的專案有 16 份各 15 MiB 的 SARIF,都在上限內。
- 預期:判完擋或放行。
- 照 spec:全部樹留在快取,GitHub runner(約 7 GB)與本機都可能被 OOM 殺掉。
- hook 把 rc≥128 當中斷、整個推送停下(file: `scripts/hooks/pre-push:90` 的 `pp_stop_if_signaled`),使用者只看到「被中斷」,看不到原因代碼。

建議的落點:快取只存濃縮事實,並寫一個解析後記憶體預算。這句是修法建議,不是這條 finding 本身。

severity: major
blocking: 是
判準:快取內容未定,字面實作最自然的做法(存解析結果)在 spec 自己允許的輸入量下會壞掉。

### F3 256 MiB 總量額度的記帳方式沒定,跟 S43 互相打架

spec 段落:〈二〉讀不可信資料的上限;S41、S43;〈二〉REVISIT 的量測目標。

引句:「超過任一上限,只把超限的那一項(或總量超過之後的每一項)判 `invalid:evidence_too_large` 並指出是哪個檔,」

問題:
1. **同檔重複計費。** 「一次判定讀的證據總量」若按引用次數累加,一份 16 MiB 專案級 JUnit 被 17 條護欄引用就爆 256 MiB。S43 要的正是「一千條護欄引用同一檔只解析一次」。若按不同 blob 計一次,spec 沒寫。
2. **順序未定。** 「總量超過之後的每一項」由誰先誰後沒規定。新增一條排序較前的護欄,會把別條原本合格的護欄推過額度線,變成 `evidence_too_large`。這違反「同一提交永遠同一個答案」,也讓作者修不了自己的證據。
3. **目標跟上限貼死。** REVISIT 量測目標是「一千條護欄、每條十份證據」,剛好等於項數上限 10000。再多一條就超限。而 256 MiB 除以一萬項,平均每份只有約 26 KiB,跟「單檔 16 MiB、夠裝中型 repo 的 Semgrep SARIF」的設計理由對不上。

具體例:1000 條護欄共用 3 份專案級 SARIF(各 10 MiB)。
- 預期:3 份各讀一次,共 30 MiB。
- 照 spec 若按引用累加:第 26 條護欄之後全判 `evidence_too_large`。

severity: major
blocking: 是
判準:實作者必須在「按引用計」和「按 blob 計」之間自己選,選錯就是整批護欄誤擋。

### F4 整道判定沒有時間預算與逾時,hook 現有慣例是每道閘都寫預算

spec 段落:〈四〉閘門、〈二〉REVISIT(實作後才量)。

問題:
- 現有 pre-push 對每道閘寫了最壞時間預算:`scripts/hooks/pre-push` 約 400 至 403 行寫「最壞每個 ref 判定本體 60 秒的預算」「每次最多 20 秒逾時」。
- 新閘排在所有早退之前,每個 ref 都跑:一次推分支加數個 tag 就重複算同一個 sha。判定函式沒有時間預算,也沒有「超時算什麼」的判定。
- 唯一與時間有關的是 REVISIT「實作完成後量一次」,而它的目標值「pre-push 可接受的時間」沒定義。
- 這一輪核對時 hook 的行為(`scripts/hooks/pre-push` 約 616 行):`code-loop check` 回傳碼不是 0 或 1、也不是 128 以上時是 fail-open 放行。spec 只保證判定本體的例外會變 rc=1,沒保證逾時、被殺、argparse 之類路徑回傳 1。

具體例:大庫判一次要 90 秒,沒有逾時規則。使用者在 hook 卡住時只能 `--no-verify`,而 d9 已承認這擋不住進主線。

severity: major
blocking: 是
判準:沒有預算與逾時規則,實作者只能自己決定,而「超時放行」與「超時擋下」是相反的守衛面決定。

### F5 `approved_on` 晚於今天(UTC)沒有原因代碼,台灣清晨簽的例外會被鎖約 8 小時

spec 段落:〈四〉〈核可物件〉的 30 天怎麼算;〈原因代碼〉例外無效列。

引句:「`approved_on` 晚於今天(UTC)無效;」

問題:
- 〈原因代碼〉例外無效只有 `exception_expired`、`exception_too_long`、`exception_fields_missing`、`exception_unsigned`、`exception_content_changed` 五個,沒有一個對應「核可日在未來」。
- `lumos security payload` 沒說 `approved_on` 怎麼填(UTC 今天,還是使用者輸入)。
- 簽章內容含 `approved_on`,錯了只能重簽。

具體例:使用者在台灣時間 10-20 01:00(UTC 10-19 17:00)簽,`approved_on` 填本地日期 10-20。
- 預期:例外生效。
- 照 spec:判無效,沒有對應代碼。使用者再簽一次還是同一天,要等到 UTC 進入 10-20,約 7 小時後。
- S25 測了到期日的台灣清晨,沒測 `approved_on` 的台灣清晨。

severity: minor
blocking: 否
判準:先補代碼與 payload 的填值規則即可,不會做出壞系統。

### F6 時間過期的事件沒有預警,無關改動也被擋

spec 段落:〈二〉依賴掃描跟著漏洞庫變、審查 90 天;〈四〉例外 30 天。

問題:
- `vulndb_stale`(建議 14 天,Q5 未決)、`review_expired`、例外到期,都在沒有任何程式改動的情況下讓整道推送變紅。
- 閘不看 diff,所以文件小修或緊急修也被擋。
- 輸出表只列「例外到期日」。`security evidence` 與放行時的小結沒有「N 天內將過期」的提醒欄。
- tag 推送也判,替老版本補打 tag 時,舊證據的時間欄位照樣算。

具體例:兩週沒推送的專案,第 15 天要推一個與依賴無關的修正。
- 預期:先前有警告可準備。
- 照 spec:當場擋下,補救路徑是重掃(需使用者核可工具)或簽例外。

severity: minor
blocking: 否
判準:這是使用者在 d9 與 Q5 要的行為,缺的是預警提示,不會做出壞系統。

### F7 證據圍欄所在的 Verification 節點受單檔 2 MiB 限制,超過是整道讀取不完整

spec 段落:〈二〉證據從哪來、讀不可信資料的上限。

問題:
- 證據圍欄在 vault 的 Verification 節點裡,走盤點快照。快照單檔上限是 `_SECINV_FILE_MAX` 2 MiB,超過是 `file_too_large`,屬於 `_SECINV_READ_KINDS`,等於讀取不完整。
- 〈四〉「盤點讀取不完整」就整道擋,不是只擋引用它的護欄。
- 這跟「超限只判該項 invalid」的隔離說法不一致。
- 每個證據項要列完整 `bindings`(全部 about_code 檔加測試、環境、夾具,見〈二〉綁版本)。一個家有 100 支檔,每項就有 100 組路徑加 blob,圍欄很快脹到 2 MiB。

具體例:一個 Verification 節點收 15 項證據,每項 100 組綁定,約 165 KB。13 條護欄共用同一節點就超限,整個專案被擋。

severity: minor
blocking: 否
判準:判不清就擋是已決的方向,只缺「圍欄大小」的預算說明與拆節點指引。

### F8 `observed_in_future` 沒說比哪個提交時間,amend 或 rebase 可能誤判

spec 段落:〈二〉鍵名表 `observed_at`。

引句:「晚於要推的提交的提交時間判 `invalid:observed_in_future`」

問題:沒寫是 author date 還是 committer date。
- 先跑測試(observed_at 14:00),再 `git commit --amend` 補進舊提交(author date 13:00、committer date 14:01)。
- 取 author date:誤判。
- 取 committer date:正常。

severity: minor
blocking: 否
判準:選 committer date 即可。

## 已讀,無 finding 的項目
- **ssh-keygen 逐物件驗章的成本。** 我實測 50 次 `ssh-keygen -Y verify` 約 0.46 秒(每次約 9 毫秒),spec 沒寫快取不構成問題。
- **治理帳重試。** 冪等鍵(護欄、種類、head_sha)讓同一提交重推不重記。amend 後 sha 變會多記一筆,屬正常增長。
- **沒登記的專案。** `git grep` 預檢路徑夠便宜,資源沒有疑慮。
- **批次讀取。** `ls-tree` 加 `cat-file --batch` 的批次設計本身是對的,問題只在 F2 的「全部同時在記憶體」。

最嚴重 severity:major,blocking 共 4 條(F1、F2、F3、F4)。
