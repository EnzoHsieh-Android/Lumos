---
type: project
status: doing
created: 2026-10-30
updated: 2026-10-30
tags:
  - type/project
  - status/doing
  - scope/guards-gates
lands_in:
  - Systems/arch-alignment-lens
related:
  - "[[Projects/Android的MVVM與DDD目標架構範本_計劃]]"
  - "[[Systems/arch-alignment-lens]]"
---
# Android目標架構開關與舊檔畢業_計劃

> 白話:上一份範本是固定的十二條,專案只能整份照抄再自己刪。這份計劃把它改成「開關」:採用時由 AI 逐題問人六個架構選擇,再用一支產生器照答案組出規則節點、宣告與 Konsist 架構測試;另外讓舊檔可以照舊鄰居審、新檔才套目標規則,舊檔重構時刪掉它那一行宣告就在同一個分支當場改照目標規則審。

## 用語

- **宣告**:`.lumos/config.json` 的 `arch_targets` 清單,每條 `{"path": 樣式, "node": 節點或 none}`,一支檔由上往下第一條命中的算數。
- **none**:命中這條的檔不套目標規則,照「鄰居」審——架構對齊審查席拿同資料夾、同副檔名、檔名最像的既有檔當對照,問新寫法跟它們一不一樣。
- **目標節點**:一篇 Systems 筆記,摘要裡的 `RULE:` 行就是這個範圍該照的規則;派工鏡頭(派審查席那一刻自動附在派工詞尾端的材料)會把規則原文附給架構對齊席。
- **Konsist**:讀 Kotlin 原始碼的架構測試庫,跑在一般 JVM 單元測試裡。
- **畢業**:舊檔重構成新架構後,刪掉它的 none 宣告,改照目標規則審。

## 問題與最小解

立案:Enzo 2026-10-30 在 Android 範本合併後提出三件事——多模組要寫進範本、檢查要有開關(不只多模組,還有其他架構選擇)、舊 class 維護照既有架構而新 class 才套用;並補充「一開始配置時詢問我再決定」與「舊檔重構」。開關清單由 Enzo 同日從建議裡全選:模組切法、舊程式處理、用例層可省略、DDD 深度、介面策略、畫面狀態形式。畢業生效時機 Enzo 選「同分支就生效」(不選「先合一個只刪宣告的小合併請求」)。

現況:
- 範本的十二條與 Konsist 骨架寫死在技能文件 `skills/lumos-project-notes/commands/target-arch-android-template.md` 裡,不適用的規則要人自己刪,刪了規則卻忘了刪對應測試、或反過來,沒有東西會抓。
- arch_targets 只認 `path` 與 `node` 兩欄,第一條命中算數;可以寫到單一檔,所以「舊檔逐一列成 none」現在就做得到,不用加欄位。
- 代碼審的宣告只讀「改動起點跟主線的分岔點」那一版(防被審分支自己放寬怎麼被審;下文的「起點版」都指這一版),所以舊檔重構時在同一分支刪掉 none 那行,這次重構照樣比鄰居——最需要照目標審的那次反而沒審到。

最小解:
1. 規則與 Konsist 測試的唯一來源搬到開關資料檔 `scripts/templates/android-arch-target.md`(新增)(範本目錄會跟著安裝進消費專案;同時登記進工具自帶檔清單 `_VENDORED_TREE_FILES`,不然推送時會被當成專案自己的檔、風險分級被降),每條規則與每支測試標「哪些開關值才收」。
2. 加 `lumos arch-template android` 產生器:吃六個開關與根套件、範圍目錄,預設只印預覽,`--write` 才寫節點、宣告、架構測試三樣:節點檔或架構測試檔已存在、或 `.lumos/config.json` 已有 `arch_targets` 這一鍵,就整批拒寫;設定檔存在但沒有這一鍵時,只加這一鍵、其他鍵原樣保留。
3. 舊程式處理選「舊檔照舊」時,產生器用 git 列出範圍內現有的程式檔,逐一寫成 none 宣告,最後一條才是目標節點;Konsist 測試讀同一份 `.lumos/config.json` 的 none 宣告跳過舊檔,不另存清單。
4. 畢業:起點版宣告判這支檔是 none、分支頂端的宣告改判成某個目標節點、而且那個節點在起點版本就是目標節點時,這支檔當場照那個節點審;規則原文照樣從起點版讀。其他任何宣告改動照舊下次推送才生效。
5. 技能文件改成講開關與訪談題目,指向產生器;不再內嵌規則與測試全文。

舊否決對照:[[Projects/架構對齊可宣告目標架構_計劃]] 定了「代碼審只讀起點版宣告,分支改的宣告下一次推送才生效」,理由是被審分支不能自己改宣告決定自己怎麼被審。畢業部分推翻這條;Enzo 2026-10-30 在聽完這道保護與「另開一個只刪宣告的小合併請求」替代做法之後,仍選同分支生效。範圍因此只開一個口:起點判 none、頂端改判成起點版本就有的目標節點;規則原文照讀起點版,新增宣告、改節點、刪目標宣告都照舊。

PRIOR-ART:開關借 Android 官方架構指南本身的分歧點——領域層(用例)在指南裡標為可選、UI 狀態指南建議單一狀態物件但不強制;DDD 輕量版借「只取分層與 Repository、不取戰術模式」的常見做法;多模組借 Now in Android 的 core/feature 拆法。產生器借 lumos 既有 `lumos new` 寫節點的慣例與 `scripts/templates/` 的安裝路徑,不加依賴。舊檔照舊借靜態分析工具常見的 baseline(採用當下的違規清單凍結、新碼才擋,例:detekt baseline、Android Lint baseline)。畢業只放寬「起點已是目標節點、只是被 none 切開」這一種改動,其他宣告改動維持只讀起點版,沿用既有的可信版本讀法。
RETIRE-IF:2027-04-30 人裁時,若沒有任何 Android 專案用產生器建過目標架構節點,撤掉產生器與開關資料檔,範本退回固定版 [retire:人裁] [until:2027-04-30]。
RETIRE-IF:畢業判定若出現一次「分支靠刪 none 行讓本該比鄰居的檔逃過審查」的實例,撤掉同分支生效、改回下次推送才生效 [retire:人裁] [until:2027-04-30]。

## 開關

| 開關 | 選項 | 影響 |
|---|---|---|
| 模組切法 `modules` | `single` 單模組 / `multi` 多模組 | multi 加一條模組依賴規則(交給編譯器擋),拿掉兩支分層 Konsist 測試 |
| 舊程式處理 `legacy` | `all` 全部套用 / `new-only` 舊檔照舊 / `dirs` 指定目錄 | 只影響 arch_targets 宣告怎麼產 |
| 用例層 `usecase` | `required` 一定要有 / `optional` 可省略 | optional 時 ViewModel 可收 domain 的 Repository 介面,只禁 data 層實作與資料來源 |
| DDD 深度 `ddd` | `full` 完整 / `lite` 輕量 | lite 拿掉聚合根、識別碼參照、值物件三條規則與對應測試,其餘規則的「搬進聚合根」改成「搬進領域層」 |
| 介面策略 `interfaces` | `deep` 深模組 / `always` 一律開介面 | always 換成「用例與 Repository 一律介面加 Impl」規則與測試 |
| 畫面狀態 `ui_state` | `single` 單一 UiState / `any` 不限 | single 換成「每個 ViewModel 只公開一個 uiState」規則與測試 |

## 驗收條款

- [S1] 當產生器跑遍六個開關的全部組合時,每一份產出的節點經 lumos lint 應回報 0 問題,目標架構規則讀法讀到的有效 RULE 行數應等於那個組合該收的規則數;每一條帶測試綁定的 RULE 行指到的測試名都應在同一份產出的 Konsist 檔裡有同名測試函式,Konsist 檔裡的每個測試函式也都應被某條 RULE 行或命名慣例清單認領。 [test: t_arch_template_android_all_combos]
- [S2] 當只切換一個開關時,產出的規則與測試應只在那個開關負責的地方不同:usecase=optional 時 ViewModel 規則不再禁 Repository 介面;ddd=lite 時沒有聚合根、識別碼參照、值物件三條;interfaces=always 時沒有深模組那條而有一律介面那條;ui_state=single 時有單一 uiState 那條;modules=multi 時有模組依賴那條、沒有兩支分層測試。 [test: t_arch_template_android_switch_effects]
- [S3] 當 legacy=new-only 時,產出的宣告應把範圍內 git 已追蹤的每支程式檔各寫成一條 none、最後一條才是目標節點;legacy=all 時只有一條目標宣告;legacy=dirs 時每個指定目錄一條目標宣告;舊檔數加一超過派工鏡頭讀得到的宣告上限時應拒絕並提示改用 dirs。 [test: t_arch_template_android_legacy_modes]
- [S4] 當產生器帶 --write 而節點檔或架構測試檔已存在、或 .lumos/config.json 已有 arch_targets 鍵時,應整批拒寫並說明是哪一個;都沒有時應三樣都寫出,設定檔原有的其他鍵原樣保留,寫出的節點經 lumos lint 0 問題。 [test: t_arch_template_android_write_refuses_existing]
- [S5] 當起點版宣告把某支改動檔判成 none、分支頂端版刪掉那一行後改判成起點版本就有的目標節點時,推送前風險分級與派工鏡頭都應把那支檔放進那個目標節點;頂端改判成起點版沒有的節點、頂端新增 none 或刪掉目標宣告、頂端宣告讀不懂時,都應照起點版判。 [test: t_arch_target_graduate_same_branch]
- [S6] 當這段範圍的宣告改動只有畢業(刪掉 none 行)時,代碼審判定印的說明應寫這幾支檔本次已照目標審,不應印「下次推送才生效」;同時有其他宣告改動時兩句都印。 [test: t_arch_target_graduate_check_note]
- [S7] 當讀技能文件的 Android 範本時,文件列出的開關名與選項應跟產生器實際收的開關名與選項完全一致。 [test: t_arch_template_android_doc_matches_switches]

## 回退

刪掉產生器子命令、開關資料檔 `scripts/templates/android-arch-target.md` 與它在工具自帶檔清單的那一行、畢業判定函式及兩處呼叫、七支測試,技能文件改回上一版。已用產生器建好的節點與宣告是普通的節點與宣告,不受影響;畢業回退後,那些已刪掉 none 行的檔改成下次推送才照目標審。不碰任何帳本。

## 實務隱患

- 效能:舊檔照舊會產生跟舊檔數一樣多的宣告;每支改動檔比對宣告是線性掃描,派工鏡頭已有 500 條與 5 秒的上限(推送前風險分級那條路沒有上限,兩條路對超過 500 條的宣告會判得不同),產生器在超過上限前就拒絕,所以產生器產出的宣告兩條路判得一樣。畢業判定多讀一次頂端版宣告,只在起點版判成 none 的檔才比對。
- 併發:產生器寫節點、架構測試兩個新檔,另在 `.lumos/config.json` 加一鍵(先寫暫存再整檔替換);任一已存在就整批不寫;不跟其他指令共用狀態。
- 守衛面:畢業放寬了「只讀起點版宣告」的保護,範圍限定成只能把 none 改成起點版本就有的目標節點(審得更多,不是更少),規則原文仍讀起點版。
- 已排除:金流:不碰任何金流或支付資料。
- 已排除:對外送出:產生器只寫本機專案檔。
- 已排除:不可逆:產生器拒寫已存在的檔,寫出的檔可直接刪除。

REVISIT:2027-01-31 Konsist 讀 .lumos/config.json 跳過舊檔的寫法只在 macrobench-lab 一個專案驗過;拿一個多模組的 Android 專案套一次,確認路徑比對在子模組也對
