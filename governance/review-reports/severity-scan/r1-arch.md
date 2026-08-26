# 審查報告:嚴重度綁定機械掃 r1-snapshot(架構對齊席)

驗證:檔案 sha256 核對 `governance/review-reports/severity-scan/r1-snapshot.md` 與指定值 `6bc2b1be4...f82` 相符,逐行讀畢;並用 `scripts/lumos` 中 quote-check/refcheck/seat-check 三個子命令定義、roster 尾端留痕程式碼、既有 severity 值序三處重複定義逐一對照。

### arch-f1

severity: minor

引句:「lumos severity-check <帳列|loop+round+席>」

佐證:
file: `scripts/lumos:15849`(quote-check:正例位置參數 `qc_report` + `--spec` 皆為字面檔案路徑)
file: `scripts/lumos:15860-15863`(seat-check:`sc_report` + `--dispatch <rN-dispatch.json>` 同為字面路徑)
file: `scripts/lumos:15775-15778`(refcheck:`md` 亦為字面路徑)

說明:既有三道收貨(quote-check/refcheck/seat-check)的位置參數一律吃「呼叫端自己解出來的檔案路徑」,沒有一個吃「輪次代號」這種需要工具自己去查表解析的識別子;repo 內也搜不到任何「loop+round+seat → 帳列」的既有 resolver(`grep round_id`/`_resolve`/`_lookup` 均無對應命中,唯一 `_resolve` 是節點名稱解析,非帳列查找,scripts/lumos:10454)。S1 提出 `<帳列|loop+round+席>` 二選一形狀,是這四道裡第一個要工具自行做「代號→紀錄」查找的介面;spec 沒有交代為什麼要背離「呼叫端傳路徑」這個先例,也沒指出要複用或新寫哪個 resolver——這正是「有沒有第二種做法」該被點名但沒被討論的地方。

### arch-f2

severity: minor

引句:「值序 clean<minor<major<blocker。」

佐證:
file: `scripts/lumos:3911`(`_panel_round_conjuncts`:`order = {"clean": 0, "minor": 1, "major": 2, "blocker": 3}`)
file: `scripts/lumos:4100`(`_loop_status_panel_clusters`:同一 dict 逐字重複第二份)
file: `scripts/lumos:15463`(`canary record --severity` 的 `choices=("clean", "minor", "major", "blocker")`,同一值集合第三份)

說明:這串序列在程式碼裡已經是「複製貼上」狀態——兩個函式裡各自內嵌同一份 `order` dict,加上 CLI `choices` tuple 是第三份同義定義,沒有任何模組層級共用常數。PRIOR-ART 段只點名「quote-check/refcheck/seat-check 收貨三道」是可借的既有模式,完全沒提到這份已經重複兩次的值序——S1 打算怎麼落這行「值序 clean<minor<major<blocker」完全沒交代:是抽成共用常數三處回填,還是原地再開第四份字面值。鑑於這個 repo 對「同一比對邏輯禁止第二份實作」有明文紀律(見 arch-f4 佐證),這裡沒討論複用選項是缺口。

### arch-f3

severity: minor

引句:「本案先轉述+留痕 severity-alerts.log,比照 roster 尾端模式含 try/except 與 __seqN 跳過」

佐證:
file: `scripts/lumos:10301-10302`(`if roster or str(rid).startswith("__"): return` —— __seqN 跳過)
file: `scripts/lumos:10303-10316`(外層 try/except 降級 + 內層 try/except 包住檔案寫入,寫入失敗只損留痕不吞輸出)
file: `scripts/lumos:10311`(`with open(_ldir / "roster-alerts.log", "a", ...)` —— 現成檔案,`kinds` 欄本身就是逗號串接多種異常標籤的設計)

說明:S2 講的是「比照」roster 尾端模式(複製同一套控制流:異常才發聲、advisory 不動 rc、try/except 降級、__seqN 跳過),但落點是**另開一個檔案** `severity-alerts.log`,而不是在既有 `roster-alerts.log` 的同一寫入路徑上加一個種類欄。roster-alerts.log 現有格式(`日期 rid kinds`,kinds 為逗號串接的異常標籤清單,如 external_missing/seat_shortfall/單家族……)在結構上本來就能再塞一個新標籤(例如 severity_underreport)進同一個 kinds 清單,不必新檔案、新 try/except。spec 沒有評估這條複用路徑、也沒說明為何捨棄——不管最終該選哪一邊,這正是「有第二種做法但沒被交代」的落點。(若要主張新檔更好,理由該是「roster-alerts.log 的既有消費者——文中提到的『兩季覆核帳』——已經預期 kinds 是純 roster 域的標籤,混進 severity 域的標籤會破格式」,但 spec 同樣沒有講到這層取捨。)

### arch-f4

severity: minor

引句:「sha 不符→拒掃指路 quote-check」

佐證:
file: `scripts/lumos:10329-10361`(`cmd_quote_check` 全函式:直接讀 report/spec 文字,全程無 sha256 比對)
file: `scripts/lumos:10547-10611`(`cmd_seat_check` 全函式:直接讀 report/dispatch,全程無 sha256 比對)
file: `scripts/lumos:10226-10254`(disposal ③ 留痕重驗:對判定輪全席的 `report_path`/`report_sha256` 已經逐一重算 sha256 比對帳面,跑在 ④ quote-check 之前)

說明:「收貨三道」裡沒有一道自己做 sha256 對帳——quote-check、seat-check 都是拿到路徑就直接讀文字內容,sha256 一致性是另一個獨立關切點,已經在 disposal 的 ③ 留痕重驗這一步做過一次(對判定輪全席的 report/snapshot 逐一重算雜湊比對帳面,sha 不符當場 FAIL)。S1 把「sha 先驗與帳面一致」直接內建進 severity-check 本體,且 fixture 明講「sha 不符→拒掃」是這個新指令自己的行為,這跟既有三道「sha 驗證不歸這一層管」的分工方式不一樣。S2 又講「問閘收尾對判定輪逐席跑 [S1]」——也就是說當 severity-check 被埋進 disposal 尾端執行時,③ 已經對同一批 report_path 驗過一次 sha,S1 若照它自己的契約再驗一次,就是對同一個檔案重算同一個雜湊兩遍。這不是邏輯漂移風險(因為明講「跑 [S1]」是複用同一份判斷,沒有第二份平行實作),但 spec 完全沒討論「S2 情境下該不該讓 severity-check 信任 ③ 已驗過的結果、還是各驗各的」這個選項,也是一個沒被點名的第二種做法。

## 對齊良好的面

- PRIOR-ART 對三道收貨模式的定性是準的:quote-check/refcheck/seat-check 確實都是獨立頂層子命令,vault-free、rc0/1/2 語意一致(`scripts/lumos:15849`/`15860`/`15775`),本案「第四道」的框架定位本身沒有問題。
- 把 severity-check 立成獨立命令而不是塞進 seat-check 的擴充,是合理選擇:seat-check 比對的對象是派工單的 `materials` 清單(`disp.get("materials")`,`scripts/lumos:10561`),是派工當下寫的東西;severity-check 要比對的是 canary-log.jsonl 帳列裡事後記的 `severity`/`report_path`/`report_sha256`(`scripts/lumos:15493`)。這兩個是不同生命週期階段、不同資料源的紀錄,各自成獨立命令比硬塞進 seat-check 乾淨,spec 選第四道而不是擴第三道這一點站得住。
- 帳列欄位描述精準對得上既有寫側:「帳列有 severity(寫側白名單擋值域)、report{path,sha256}」跟 `canary record --report`/`--severity` 的既有實作(存 `report_path`/`report_sha256`、`--severity choices` 白名單,`scripts/lumos:15463`、`15493`、`3667-3674`)逐字對得上,沒有幻覺欄位。
- S2 明講「問閘收尾對判定輪逐席跑 [S1]」,代表要複用同一份判斷邏輯而不是另開一份實作,呼應 roster 尾端呼叫 `_roster_observe` 共用核心的作法(`scripts/lumos:10304`),也呼應這個 repo 對「同一比對邏輯禁止第二份實作」的明文紀律(`_quote_rows` docstring「★單一實作★」,`scripts/lumos:10069`,附帶 2026-08-02 兩份實作漂移的教訓)。
- S2「異常才發聲、advisory 恆不動 rc、try/except 降級不擋、__seqN 合成鍵跳過」四個特徵,逐項對得上 roster 尾端剛立的先例(`scripts/lumos:10298-10316`),控制流沒有走樣,只有落地檔案這一點(見 arch-f3)值得再想一下。
