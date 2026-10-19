severity: major

邊界可執行鏡頭,第 1 輪。已讀完凍結審材 §1 到 §11、驗收條款 S1 到 S31、實務隱患、不做、回退。spec 引用的既有成員已逐一用 grep 核對,都在 `scripts/lumos`:`_summary_line_hits`、`_drift_fix_shape_err`、`_lands_in_bad`、`_excluded_line`、`_spec_gate_push_scan` 等。`_set_keys_text` 與 `cmd_summary_add` 是 spec 說要新增的,不算。

我也驗了「B1(b) 的 `git restore --source=<實作前提交>` 對新檔會不會報錯」。在臨時 repo 實跑,新檔在來源提交裡不存在時 rc=0,檔案被換回實作前狀態(等於移除),所以這條不報。

## 1. §9 W6:列檔指令沒帶 `-z`,中文節點名會被引號跳脫,新節點的家對不上
severity: major
blocking: 是(照字面實作,W6 對中文節點名整個失效,實作者會做出壞行為)
- spec 段落:〈做法〉9 的 W6。
- 問題:spec 指定 `git ls-files --others --exclude-standard` 與 `git diff --name-only`,沒寫 `-z`,也沒寫 `-c core.quotePath=false`。圖譜節點大量是中文名(`規格閘.md`、`筆記內容閘.md`)。git 預設把非 ASCII 路徑印成帶引號的八進位跳脫字串,不經還原就拿不到真路徑。
- 具體例:新開 `Systems/新節點中文名.md` 未追蹤並已把某支檔列進 about_code。實測 `git ls-files --others --exclude-standard` 輸出 `"\346\234\252\350\277\275\350\271\244\344\270\255\346\226\207.md"`。照 spec 字面讀不到這篇,S8 照舊把那支檔列成沒家,W6 修不到。
- 佐證:`_nodehome_list` 用 `ls-files -z` 與 `diff --name-only -z --no-renames`,即 file: `scripts/lumos:32777` 起那段;`_spec_gate_push_check` 也特地帶 `core.quotePath=false`。S23 若用 ASCII 節點名寫測試,抓不到這個缺陷。
引句:「另列圖譜 Systems 底下未追蹤(`git ls-files --others --exclude-standard`)與工作目錄有改(`git diff --name-only`)的 .md」

## 2. §4 規則 3:條件詞用子字串比對,「若干」「這時間」會誤吞現況句
severity: major
blocking: 是(新規則會把該提醒的現況句靜默收掉,守衛面放寬)
- spec 段落:〈做法〉4 規則 3。
- 問題:規則 3 說「否定字眼所在那一小段裡、在它前面出現」若、如果、要是、只要、這時、此時等開頭詞。沒有要求詞邊界或位置。單字「若」會命中「若干」,「這時」「此時」會命中「這時間」「此時間」,「要是」會命中「重要是否…」。
- 具體例:「若干頁面尚未實作」與「這時間點還沒有資料」是現況句,應該提醒。照字面,前者的「若」在段內且在「尚未」前面,後者的「這時」同理,兩句都被當條件子句收掉。
- 佐證:`_NS_NEG_SEG_CUT_RE` 只在逗號、頓號、括號等處切段,「若干」不會被切開。S11 只測「前端頁面還沒做」「匯出功能尚未實作」兩句,抓不到。S12 對 150 行的「真句一行不少」只保證抽樣內不退步,抽樣外的「若干」不保證。
引句:「在它前面出現條件或時序開頭詞「若、如果、假如、要是、一旦、等到、只要、這時、此時」。不收「當」(「當前還沒有測試」是現況句)。」

## 3. §1 第 6 點:summary-line 對舊行傳 `old=None`,會擋掉提交時放行的編輯
severity: minor
blocking: 否(summary-line 變得比提交檢查嚴,但手改是退路)
- spec 段落:〈做法〉1 第 4、6 點。
- 問題:第 4 點寫 `_ns_slot_line_problems(新行, None, 現在)`,`old` 固定給 None。第 6 點讓 summary-line 同一支共用,但 summary-line 編輯的是既有行。提交時 `_ns_is_old(_ns_slot_key(line), old)` 會把「文字鍵與連結都沒變」的行當舊行,免套必有鍵。
- 具體例:舊的 `FACT:xxx` 沒寫 `[confirmed:]`(歷史遺留)。用 summary-line 只在句尾補一個 `[[連結]]` 或改標點:提交檢查視為舊行放行,summary-line 在 block 模式傳 None 視為新行,rc2 擋下。
- 佐證:`_ns_slot_line_problems(line, old, commit_time, head=None)` 的 `old` 參數就是為此設計的(file: `scripts/lumos:35749`)。S7 沒有「改舊行」的案例,看不到這個差。
引句:「這是 summary-line 行為的收緊:以前寫得進去、提交才擋的,現在寫入時就擋。」

## 4. §6 F6:lint 對已排除行的判法沒跳過引用塊,散文句也會被唸格式錯
severity: minor
blocking: 否(只提醒、不影響 rc)
- spec 段落:〈做法〉6。
- 問題:規格閘的 `_door_exclusions` 先跳過 `>` 開頭的引用塊行才呼叫 `_excluded_line`。spec 的 lint 只寫「去掉列表記號後以『已排除』開頭的行」,沒寫跳過引用塊。`_EXCL_LEAD_RE` 的前綴集合含 `>`,會把引用塊行當已排除行判。
- 具體例:實務隱患節裡「> 已排除這個風險,因為…」(引來的話),或散文句「已排除 X 的可能性,見下」。`_excluded_line` 回 None,lint 唸「冒號沒寫對」,但規格閘根本不看這兩行。
- 佐證:file: `scripts/lumos:8110`(`_door_exclusions` 內的 `startswith(">")` 判斷)與 `scripts/lumos:8049`。S15 沒有引用塊或散文案例。
引句:「各唸一行並印正確格式 `已排除:<四類之一>:<理由≥4 字>`(四類名照 `_DOOR_CLASS_ZH`)。warn,不影響 rc。判法跟規格閘同一支,不另寫正則。」

## 5. §9 W6:工作目錄已刪除的節點沒有處理規則
severity: minor
blocking: 否(邊角、單人少見)
- spec 段落:〈做法〉9 的 W6。
- 問題:`git diff --name-only` 會列出「索引有、工作目錄已刪」的 .md。spec 說「用 `_nodehome_parse_note` 讀工作目錄版本」,沒說檔案不存在時怎麼辦。
- 具體例:`rm Systems/舊節點.md` 還沒 `git rm`,跑 `lumos doctor`。照字面讀檔會丟 `OSError`,健檢整段中斷。
- 佐證:`_nodehome_parse_note(raw)` 吃的是已讀好的位元組,讀檔與例外處理在呼叫端。spec 沒要求呼叫端 try/except。S23 只有「未追蹤新節點」一種情境。
引句:「用 `_nodehome_parse_note` 讀工作目錄版本;只靠這些節點才有家的檔,從 S8 的沒家清單拿掉」

## 6. 〈依據〉段與〈名詞〉的編號計數對不上
severity: minor
blocking: 否(文件精度)
- spec 段落:開頭白話。
- 問題:開頭寫「17 個編號收成 11 節」,但〈名詞〉列出的編號是 F8、B6、W8、B7、F14、F17、W9、F29、F6、F9、W5、B8、B9、W6、B1、B11、B2、B3、W10、F15,共 20 個。
- 具體例:接手者拿 17 去對比對表會對不上,找不到是哪三個多出來。
引句:「這份把 F、G、H 三組 17 個編號收成 11 節,能用一條規則收的就不逐點補,拆成 7 個小提交。」

## 7. §10 B3 讀端:去重規則在「只有帳缺才讀」的條件下沒有作用,「取最後一筆」也沒有排序鍵
severity: minor
blocking: 否(目前條件下不會取錯)
- spec 段落:〈做法〉10 B3 讀端。
- 問題:spec 說推送閘「在審查帳找不到留痕時,才讀一次治理帳」,又說「兩邊以 token 去重、取最後一筆」。審查帳沒有該計劃的留痕時,只有治理帳一邊有資料,去重沒有對象。若實作者照字面把兩邊合併再取最後一筆,兩本帳沒有共同排序鍵,只靠各自 append 序,合併後哪筆是「最後」沒有定義。
- 具體例:消費專案的舊本機帳有上線前的 rec1,治理帳有上線後的 rec2;「找不到才讀」的條件判成「rec1 存在,不讀治理帳」,新留痕被忽略。
- 佐證:`_spec_gate_latest_records` 只取單本帳每個 loop 的 `gates[-1]`;留痕有 `ts` 與 `token`(file: `scripts/lumos:8444` 起)。S28 沒有「兩邊都有」的案例。
引句:「推送閘有候選計劃在審查帳找不到留痕時,才讀一次治理帳,讀之前先用字串 `"spec-gate-record"` 篩行再解 JSON」

## 風險類
- 守衛面:有 finding 2(放寬否定現況提醒)。F29、F6 只是 lint 提醒,不改擋下判定。B1(a) 的放行條件綁指紋與規則版本,已讀,無 finding。
- 舊資料與舊帳相容:finding 3 是舊行編輯。B3 舊留痕不補寫,spec 已明講。
- 已在途分支:B2 讓改到 done 計劃的推送重跑測試,spec 已自述範圍,已讀,無 finding。
- 跟其他會談或計劃的交界:無。各提交互不依賴,引用的其他計劃在 `related` 列出。

最嚴重 severity: major,blocking 共 2 條(finding 1、2)。
