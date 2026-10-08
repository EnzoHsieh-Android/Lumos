severity: major

固定席筆記:本次 prompt 尾端沒有附。

已讀的節:格子規格、擋、lint 與擋同一張表、格子欄位的過期檢查、分期、天花板、不做、實務隱患、驗收條款、回退、合約候選。r2 補丁的核對結果:
- `--slots` 旗標與格子記號:每個提交的樹裡掛鉤是否含記號,`scripts/lumos:25601-25603` 用子字串比對,所以「新記號包含舊記號」成立。
- `[被取代:]` 作廢不吃舊行豁免:語意自洽。
- 撤除條件判不了另列:語意自洽,但落地細節有洞(見 R3R3、R3R4、R3R9)。
- 核心一句改成「去掉欄位剩下的」:沒有時序問題。

「實務隱患」我只答最壞時序相關的幾類:時區與時鐘、治理帳讀取量、doctor 與 pre-push 時間、rebase 與逃生口。

**R3R1**
severity: major
blocking: 是——照字面實作,台灣時區每天有 8 小時,本機合法的新行會在 CI 被擋成「寫錯」。
- 輸入:台灣時間 2026-10-02 03:00 提交一行 `[confirmed:2026-10-02]`,提交時本機「今天」是 10-02,通過。
- 走到的段:CI 的 `note-shape --diff` 對新寫行重判。GitHub runner 預設 UTC,「今天」還是 10-01。
- 壞在哪:該行被判「晚於今天」。spec 沒寫「今天」用哪個時區,也沒有容忍天數。
- 既有的 `rule_lifecycle_warnings` 只比較「過期」,不查未來日期,所以這是本篇新增的失敗路徑。
- 本機 `date` 是 CST,`scripts/lumos:3353-3395` 用 `date.today()`。
- 建議:未來日期只在提交時查;或統一用 UTC 並容忍 +1 天。

引句:「`[since:]` `[confirmed:]` 晚於今天算寫錯;`[until:]` 可以是未來。」

**R3R2**
severity: major
blocking: 是——spec 允許的 N(1 到 26 週)在「24MB 檔尾上限」下撐不住,度量不是亂報就是永遠不判。
- 輸入:`[retire:度量 note-shape.blocked < 3 近26週]`,doctor 只讀治理帳檔尾 24MB。
- 實測:`docs/.governance-log.jsonl` 現在 15.9MB、100302 行,每行約 156B。2026-09 一個月就 74762 行(約 11.7MB),24MB 大約只裝得下兩個月。
- 壞在哪:檔案一過 24MB,檔尾的最舊事件就晚於「N 週前」。
  - 若暖機判「歷史」用整檔第一行,檔尾事件不足,數出來偏少,`<` 與 `==` 比較會亂報提醒。
  - 若用檔尾最舊事件,N 超過約 9 週的度量永遠在「暖機」,永遠不判。
- 既有 doctor 的 A2 段(`scripts/lumos:2041-2084`)對同一個問題寫了「讀檔尾讀不到 15 天前就不比」。本篇沒有這條。
- 建議:把 N 的上限與讀取範圍綁在一起,或明寫「檔尾涵蓋不到 N 週視同暖機」。同時承認 24MB 裝不下 26 週。

引句:「doctor;一次 doctor 只讀一遍治理帳檔尾(上限照既有 24MB),所有度量共用」

**R3R3**
severity: major
blocking: 是——doctor 會開始評估條件並讀程式檔,spec 沒給預算,也沒說 `--ci` 跑不跑。
- 輸入:`doctor` 的撤除條件兜底,「沿用 `drift scan` 的工作目錄判定」。
- 既有契約相反:`scripts/lumos:2312-2314` 的 Z 段註解與存量漂移防線計劃 [S14] 寫明 doctor「不評估條件、不跑 git、只讀筆記」,評估只在 `drift scan`。
- `cmd_drift_scan`(`scripts/lumos:31387`)的評估要列檔案樹、批次讀每個條件指到的檔,有 60 秒預算。
- pre-push 在每次推送前同步跑 `doctor --ci`(`scripts/hooks/pre-push:290`,註解說 doctor 約 1.1 秒)。spec 只替 FACT 提醒寫了 `--ci` 也限 20 條,撤除條件、`[被取代:]`、度量都沒講跑不跑。
- 先例:`_note_shape_doctor_lines` 在 `ci=True` 時刻意提早 return,不做線性變慢的掃描(`scripts/lumos:26297-26301`)。
- 後果:字面實作可能讓每次推送多等到 60 秒,或讓 Z 段契約與 S14 測試翻紅。
- 建議:在 doctor 欄明寫「全量 doctor 才跑、`--ci` 不跑」,以及評估的預算與判不了時的輸出。

引句:「doctor(沿用 `drift scan` 的工作目錄判定)」

**R3R4**
severity: major
blocking: 是——兜底提醒沒寫略過已作廢的行,作廢之後 doctor 會永遠唸同一條。
- 輸入:一條 RULE 的 `[retire:when-file:sandbox/policy.yaml]` 成立,作者照 spec 標 `[status:superseded] [被取代:無 理由]` 處理完。
- 推送欄寫了「已標 `[status:superseded]` 的行不抽」。doctor 兜底欄沒寫。條件是「檔案存在」這種永久真值,所以標了作廢也永遠成立。
- 結果:該行每次 doctor 都被唸,除了刪掉整個 `[retire:]` 鍵之外沒有出口。
- 再加上 doctor 的 Z 段註解:每天唸同一批會被 nags 升級成噪音(`scripts/lumos:2312`)。
- `drift ack` 已表態的行在 doctor 怎麼處理,也沒寫。
- S13 沒涵蓋這個案例。
- 建議:兩欄共用「略過已作廢、已表態另計」的規則。

引句:「工作目錄裡條件現在已成立(兜底:轉變那次判不了或被跳過就再也不會被擋)」

**R3R5**
severity: major
blocking: 是——單次跳過是逃生口,spec 卻讓它先跑一遍可能正是壞掉的那套機制,沒說失敗時怎麼辦。
- 現況:`cmd_note_shape` 在 `scripts/lumos:26370` 的 `LUMOS_SKIP_NOTE_SHAPE` 判斷,先於 git 檢查、淺層判斷、設定讀取與範圍計算。
- 本篇要求跳過時「先算一次格子違規」。這要做的事:
  - 讀 staged diff、HEAD 版本比舊行。
  - 讀 `.lumos/config.json` 的 `note_shape.slots` 與總開關。
  - 推送時還要算整個範圍。
  - 這不只是「新增行的字串比對」。
- 風險:逃生口最常被用在 git 或抽取本身出錯、超時的時候,現在逃生口也會出錯或卡住。
- spec 沒寫三件事:這段是否 try/except 後 fail-open、`slots=off` 或掛鉤沒帶 `--slots` 時跳過事件要不要算、推送時的跳過算不算。
- 建議:寫明「算不出就只記 `skipped-env` 不帶格子欄位」,並且受開關與 `--slots` 約束。

引句:「單次跳過時先算一次格子違規(只是新增行的字串比對)」

**R3R6**
severity: major
blocking: 是——spec 宣稱的「天然不溯及既往」在 rebase 或 cherry-pick 下不成立,而 S7 的測試抓不到。
- 機制:每個提交是否「格子上線」,看的是該提交自己的樹裡 `scripts/hooks/pre-commit` 是否含記號(`scripts/lumos:25601-25603`,`f"{c[0]}:{hook}"`)。
- 輸入:開擋前一週從舊 main 切出的功能分支,本機掛鉤還沒帶 `--slots`,提交時不查格子。開擋後該分支 rebase 到新 main。
- 壞在哪:rebase 後每個提交的新樹都含記號,全被當成上線後新寫行。推送時整批照格子規則查,但提交時從沒擋過。
- 這個專案同一工作目錄有多個會談與長命分支,最容易遇到。
- 結果是大批「新違規」,要靠 `LUMOS_SKIP_NOTE_SHAPE=1` 才推得出去。
- S7 只驗「提交發生在記號出現之前」。
- 建議:把這個缺口寫進天花板並附緩解辦法,或把「不溯及既往」改成「只對記號之後新建的提交」。

引句:「各專案 `lumos update` 換到新掛鉤那一刻才開始擋,天然不溯及既往。」

**R3R7**
severity: minor
blocking: 否——不會做錯決定,但治理帳欄位的型別與長度沒定,讀帳的人與 RETIRE-IF 抽查會踩到。
- 先例:否定現況句的 `extra` 裡 `notes` 是整數(`scripts/lumos:26476`),本篇把同一個閘 `note-shape` 事件的 `notes` 定成路徑清單,同鍵兩種型別。
- 先例:`blocked` 事件的 `nodes` 截斷在 `[:50]`(`scripts/lumos:26338`),舊句檢查把整行壓在 4096 位元組內(`scripts/lumos:31258-31269`)。
- 本篇的 `notes:[筆記路徑]` 沒上限。一次 200 篇筆記的整理,中文路徑可到十幾 KB,而治理帳是會進版控的追加檔。
- 若截斷,30 分鐘「同一批筆記路徑」配對就不全。
- 建議:鍵名換掉(例如 `note_paths`),寫明截斷上限,配對改成比對前 N 個路徑或雜湊。

引句:「用結構欄位記(同否定現況句提醒的 `extra` 寫法),不塞說明字串」

**R3R8**
severity: minor
blocking: 否——只是成本宣稱沒有依據,推送與 doctor 多一次 diff 不會做錯行為。
- 「改到舊行不算新寫」的跨篇搬移要有「別篇被刪掉的行」,而 `_notelines_parse_added`(`scripts/lumos:25656` 附近那一趟)只解析新增行。刪除行與改名後的舊版本,要另外讀範圍淨差異(類似 `_NotelinesNet`,`scripts/lumos:25728-25741`)加批次讀起點版本。
- doctor 事後掃描最壞:`_NS_DOCTOR_SCAN_CAP=200`(`scripts/lumos:25445`)只取最新 200 個提交,但起點是上線點。淨差異是「上線點到頂端」的整個圖譜 diff,範圍可能遠大於那 200 個提交。
- 「約 500 個提交 9 秒」也是舊量測,現在的上限是 200。
- 建議:改寫成「多一次範圍淨差異與一批起點版本讀取」,並說明 doctor 怎麼處理上限之外的範圍。

引句:「不為格子多跑一趟 git(doctor 事後掃描既有成本約 500 個提交 9 秒,不因格子加倍)」

**R3R9**
severity: minor
blocking: 否——只是效能宣稱不精確,預算內會降級成「判不了」清單而不是做錯。
- 宣稱:只看這次推送改到的路徑,不掃全庫。
- 事實:`_drift_probe_check` 開頭有早退(`scripts/lumos:29092-29096`),沒有條件行就不載入起點。
- 一旦 RULE 普遍帶 `[retire:when-*]`,每次推送都會走 `_drift_probe_prepare` 的 `_drift_tree_env(root, base, …)`(`scripts/lumos:29206-29219`)。那是整個圖譜(上千篇)的批次讀取,加上對所有筆記的逐行解析。
- 「預算排在回頭條件之後」若實作成第二趟 `_drift_probe_check`,這個起點讀取會做兩次。
- 先例:舊句檢查 m1 有自己的 30 秒預算,不吃主預算。spec 的「用剩下的」在大 repo 下,回頭條件一吃光,撤除條件整批變「判不了」,每次推送都這樣。
- 建議:明寫兩種條件共用同一次起點與樹的載入,以及「用剩下的」在最壞時的行為。

引句:「撤除條件只看這次推送改到的路徑、符號與測試必帶路徑,不掃全庫,預算排在回頭條件之後」

**R3R10**
severity: minor
blocking: 否——只是上線點可能被一句註解提前觸發,先立警語即可。
- 上線點是 `git log -S<字串> -- scripts/hooks/pre-commit` 找「字串出現次數第一次變動」的提交(`scripts/lumos:24922-24930`),註解裡出現也算。
- 既有 `scripts/hooks/pre-commit:227` 與 `pre-push:496` 都有專門警語。
- 本篇沒有。第 1 步寫掛鉤範本時若有註解提到 `note-shape --staged --slots`,上線點就落在那個提交,早於開擋步。
- 建議:在第 1 步與開擋步各加一句「掛鉤範本裡除了呼叫那一行,註解與其他位置都不准出現這串」。

引句:「用 `note-shape --staged --slots` 這串當格子自己的上線點記號」

**R3R11**
severity: minor
blocking: 否——第 3 步的邊界沒寫清楚,不影響其他步驟。
- 表格把 RULE 的確認與到期提醒外包給分類計劃的 doctor 段(`t_doctor_lists_stale_rules`)。
- repo 裡這個測試還不存在,只在分類計劃 S6 有條款,`scripts/test_lumos.py` 查不到。
- 本篇把 `[retire:人裁]` 的 `[until:]` 改成必有,到期提醒就完全靠那一段。
- 〈分期〉沒有「分類計劃那段先上線」的順序,也沒有「沒上線時人裁到期靠誰」的說明。
- 建議:在第 3 步加依賴註記,或把這段列為前置條件。

引句:「不新做:lint 既有的 RULE 生命週期提醒,加上 [[Projects/筆記標籤_過時判定與按需載入_計劃]] 的 doctor 段(`t_doctor_lists_stale_rules`)」

最高嚴重度:major,blocking 6 條
