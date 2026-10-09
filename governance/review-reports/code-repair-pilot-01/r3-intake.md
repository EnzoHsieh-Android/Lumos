# 第3輪修復與分類

沿原案，前兩輪不可重置。使用者22:12:21要求續辦，22:51後準備最後輪。總時間與新增步驟細分仍缺完整打點，不估填。

動手前根因/改變/保持寫在已過設計審的Projects/探針讀碼結果證據_計劃，這份intake於實作後、正式r3前彙入；未完全遵守「先填當輪intake」的試行位置要求，不冒稱早已填表。設計審為read-result-evidence r1，不是額外代碼審輪。

| finding/根因組 | 根因、改變/保持 | 前後 | 壞例 | 好例/失敗路徑 | 來源 |
|---|---|---|---|---|---|
| C1/R2C1/R2C2 | 命令摘要不能證明讀碼，改成功回傳片段；維持合法cd/grep/sed，答案判分獨立 | 1c91755a→4a60b231 | r3-paired-cases.json：3假綠紅→綠 | 4合法讀碼綠→綠；缺結果排除、零呼叫有效失敗、失敗清理停批 | C1原有漏看；R2C2先前引入已撤回，本次修復同根因 |
| 設計B1/Git隔離 | 建立副本清洗後runner重繼承定位環境，延用_git_env至全鏈 | 1c91755a→4a60b231 | t_probe_source_probe_git_env修前紅、修後綠，兩暫存repo實際git config | 外側設定/檔案byte-equal；既有probe sandbox相關回歸通過 | 新抓的原有漏看，非上輪修復引入；第4根因組 |
| C2/C3 | 非零退出排除、逐題分母一致，保留前兩輪已驗修補 | 2db51cc4→1c91755a→4a60b231 | r1/r2既有卷證不改 | probe_157綠含既有98項與59新項 | 沒再改既有語意 |

新API測試先紅0/5，4組是尚未實作API，不算4個舊bug；初版綠測試2紅因fixture參數錯誤，修fixture後通過，保留r3-green-first.txt。9/28歷史摘要無原始結果，改記unknown，不能灌入好例綠→綠數。

原先以為平台新thread上限代表舊席不能續談，實際 followup_task 成功恢復 pilot01_r2_correctness，故於入帳前更正本段。原席只驗 R2C1/R2C2，兩條均 clean，獨立跑 source_probe 59 passed/0 failed；原文 r3-original-acceptance.md。正式新席仍是另派的全新席，不把原席驗收當第4輪。

正式全分支patch8435行，其中歷史卷證/帳本佔多數。新程式與上下文共享，歷史差異依連續行分成5份分派，無刪去全分支材料；scope超大限制明記，不能把席位clean當成強證明。pitfalls升high，原定錨standard不洗號，補高風險三一般席、架構、資安共5席；全部同家族，無外家否決票。

## 第3輪收貨與去重

五席全收齊後才更新圖譜，沒有改被審程式（仍4a60b231）。正確性1 major、邊界1 major、量測clean、架構1 minor、資安1 blocker及1 major：報告合計5條，去重為3項blocking行為缺陷與1項minor品質建議。Git設定注入被兩席重複指出，只計一次，保留報告最高blocker；辯方認可major底線，沒有用未執行真push的限制抹掉已證繞過。

| id | 機械重現 | 修前→修後同例 | 來源分類與處置 |
|---|---|---|---|
| correctness F1 | HIT，缺id的started/updated接turn.completed得到absent，有id未完成為unknown | 1c91755a及4a60b231的Codex runner輸入同原始流，皆scored=1、inconclusive=false；r3-missing-id-before-after.json | 原有漏看／新S3修補不完整，沒有前好後壞；major存活未折入，仍屬C1證據根因組 |
| boundary R3-B1 / security Finding 1 | HIT，Git COUNT注入remote與hooksPath；r3-git-config-repro.json | 兩版控制dry-run rc1，注入與具名remote rc0，臨時bare仍空，無網路 | 原有漏看；同設計B1的Git隔離修復組，blocker存活未折入；不聲稱已發生外部push |
| security Finding 2 | HIT，來源內absolute separate-git-dir；r3-separate-gitdir-repro.json | 兩版副本gitdir均等於来源，來源remote被刪、hooksPath改寫、HEAD推進 | 原有漏看；major存活未折入，本輪未著手修，不增加「已做根因修復組」分母 |
| arch A1 | HIT，r3-pitfalls的C901為34>10；無錯誤判分重現 | 舊版無source_evidence，新版新增此告警 | adapter拆分屬新建議／品質告警，非已證行為回歸；minor未處置，新增告警閘未豁免 |

修前後指在記憶體載入各commit，或為各版建立獨立臨時repo，未切換共享工作樹。Codex事件、兩runner完整批次入口、Git實驗方法見r3-parent-reproduction.md。完整入口驗證Claude及Codex各2場成功、每場不同副本、乾淨開始、清理、来源不變、標記不落結果；外部模型被fixture取代，非真探針。

辯方r3_defender逐條檢查三項blocking，只反駁既有finding，均agree；原始回覆另存r3-defender.md與r3-defender-separate.md。全部仍同家族，沒有外家辯方。

程序限制：資安席揭露一次遞迴搜尋誤帶出邊界席數行，不能把這兩席算嚴格獨立共識。採信依父代理修前後實驗與辯方核對，不靠票數。原始資安報告保留，續談僅補file座標反引號，沒有改觀察與等級；正確性原稿及原席格式版也並存。measurement clean無引句，quote-check rc2為零引句，不偽填通過；其他finding引句均錨定。

## 收尾

三輪上限用滿，未處置blocking，不建立假的全處置集合，不寫pass、不推送。raw canary記unconverged:cap，最終處置閘應為FAIL。新增根因組整理/配對/分類未全程打點，完整耗時未知；不以席位分鐘相加冒充牆鐘時間。

案1累計：3輪、4個已做根因修復組（C1/C2/C3/Git環境定位）；已證修復引入行為缺陷1（r2 R2C2，已撤回），新輪原有漏看4（R2C1及本輪3項去重行為），待查0，另列A1品質告警1。設計審B1是額外前掃抓到的既有定位環境缺口，不混入「新代碼審輪發現」4項；同一Git配置雙報不重算。仍僅1/5案，剩4個新工作名額。無放行/部署，14天窗不適用、追蹤0天、放行後缺陷未知。單例不支持流程有效或多數問題來自修復的結論。
