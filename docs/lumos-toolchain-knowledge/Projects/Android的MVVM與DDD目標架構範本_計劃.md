---
type: project
status: doing
created: 2026-10-29
updated: 2026-10-29
tags:
  - type/project
  - status/doing
  - scope/guards-gates
lands_in:
  - Systems/arch-alignment-lens
related:
  - "[[Projects/DDD目標架構範本_計劃]]"
  - "[[Systems/arch-alignment-lens]]"
---
# Android的MVVM與DDD目標架構範本_計劃

> 白話:lumos 已有 DDD 與前端分層兩份目標架構範本,Android 專案要照「MVVM 加 DDD」寫時還得自己把兩套規則拼起來。這份計劃加第三份範本:十二條架構對齊席判得動的規則(六條 DDD 換成 Android 的寫法、四條 MVVM、深模組與測試邊界各一條),另附一份在消費專案實跑過的 Konsist 架構測試骨架,讓結構那一半交給機器守、語意那一半交給審查席。

## 問題與最小解

立案:Enzo 2026-10-29 提出——把 DDD 與 MVVM 結合成 Android 的固定範本。

現況:目標架構節點要由專案自己寫;DDD 範本是語言中立的寫法(ORM、HTTP client、Controller),沒講 ViewModel、畫面層與 Room 實體;前端範本是 Web 的分層。2026-10-29 在 macrobench-lab(Android 示範專案)的 arch-rules-draft 分支用 Konsist 寫了九條結構規則、16 種改壞各自只紅對應那條,同時確認兩件文件上看不到的事:Konsist 的 dependsOn 不禁止依賴其他層、Konsist 0.18 起綁 Kotlin 2.4 標準庫。

最小解:照 DDD 範本的形狀只加一份範本說明檔與守它的測試,不加新指令、不改任何判定。

PRIOR-ART:規則內容借 [[Projects/DDD目標架構範本_計劃]] 的九條(Vernon 聚合四條、Ousterhout 深模組、測試只經公開方法驗),MVVM 部分借 Android 官方架構指引(單向資料流、ViewModel 只公開唯讀的 UI 狀態、畫面只送事件)。機械那半借 Konsist(Kotlin 原生、讀原始碼);ArchUnit 加 jMolecules 規則最完整但屬 Java 生態,沒查到在 Kotlin 編譯出的類別上的實證,不選。
RETIRE-IF:2027-04-29 人裁時,若 Enzo 手上沒有任何 Android 專案在 arch_targets 宣告引用照這份範本建的節點,就撤掉範本檔與它的測試 [retire:人裁] [until:2027-04-29]。

## 做法

1. 新增 `skills/lumos-project-notes/commands/target-arch-android-template.md`:採用步驟、為什麼是這十二條、可直接存成節點的範本區塊(日期用 `<採用日>` `<回頭日>` 佔位)、Konsist 骨架(規則與測試名對照表加一個 Kotlin 圍欄)、調整與撤除。
2. `commands/06-代碼審與推送.md` 的 `arch_targets` 那一列與技能首頁各加一句指到新範本。
3. 測試照前端範本那兩支的形狀,另加一支核對 Konsist 骨架的對照表與程式碼一致。
4. `Systems/arch-alignment-lens` 加一句指路。

## 驗收條款

- [S1] 當產生器在 single、all、required、full、deep、any 這組產出節點時,lumos lint 應回報 0 問題,目標架構規則讀法應讀到十二條有效 RULE 行、沒有一條過期,也沒有留下日期佔位。 [test: t_arch_target_android_template_valid]
- [S2] 當使用說明 06 的 arch_targets 那一列被讀時,應同時提到 DDD、前端、Android 三份範本的檔名;技能首頁應指到 Android 範本。 [test: t_arch_target_android_template_linked_from_usage]
- [S3] 當產生器在同一組產出節點與 Konsist 架構測試時,RULE 行綁的每個測試名應在架構測試裡有同名測試函式,架構測試的每個測試函式也應被 RULE 行或命名慣例認領。 [test: t_arch_target_android_template_konsist_names_match]

2026-10-30 起範本內容改由產生器 `lumos arch-template android` 提供([[Projects/Android目標架構開關與舊檔畢業_計劃]]〈做法〉10):技能文件不再有照抄的範本區塊與 Konsist 骨架,S1、S3 綁的兩支測試名不變,條款句改成產生器在 single、all、required、full、deep、any 這一組的產出(跟原本的十二條同組;原本 S1 的「沒換佔位照抄」那半不再適用,產生器直接填日期)。

## 回退

刪掉範本檔、06 那一列與技能首頁加的那句、三支測試與 arch-alignment-lens 的指路句。已照範本建節點的專案不受影響。不碰任何帳本。

## 實務隱患

- 效能:只多三支讀檔與跑一次 lint 的測試。
- 併發:只讀範本檔、寫臨時目錄,不碰共用狀態。
- 已排除:金流:不碰任何金流或支付資料。
- 已排除:對外送出:只是使用說明與測試。
- 已排除:不可逆:只新增檔案,可直接刪除回退。
- 已排除:守衛面:不改任何判定與擋下條件。

REVISIT:2027-01-31 Konsist 骨架只在單一模組、類別依層分套件的示範專案跑過;拿一個依功能分套件或多模組的 Android 專案套一次,看 Layer 的套件寫法要不要改

## 審計修正紀錄

- 規格閘(2026-10-29):判風險低;三條條款的測試在實作換回實作前版本(範本換成空殼、使用說明與技能首頁還原)時全紅、換回後全綠。第一次被計劃裡講 ViewModel 公開狀態那句的一個詞誤判成會往外寄資料的那類風險,改寫用詞後回到低風險。
- 實地試用(2026-10-29,macrobench-lab 的 arch-rules-draft 分支):照範本建目標架構節點、宣告購物車目錄,埋 5 種 Konsist 骨架抓不到的違規(ViewModel 算免運、用例寫限購判斷、Repository 改單一明細、只有一個實作的用例另開介面、聚合用 internal var 讓用例直接改)加一個合規對照;派兩席架構對齊(Sonnet、同一份派工詞、不告知埋了什麼),兩席都抓到全部 5 種且判 major、對照組沒誤判,規則測試在同一份改動上全綠。範本規則文字沒因此改。結果與卷證在那個專案的 Verification/2026-10-29_架構對齊席抓語意違規。
- 代碼審 light(2026-10-29,架構對齊 1 席):2 條 minor 全數照改——測試讀範本的小工具改回跟 DDD、前端兩份同形(無參數、自帶前置檢查),範本教的測試綁定寫法改回跟兩份兄弟範本一致的 `[test:<測試名>]`,另註明測試不在預設平台目錄底下時才要先宣告平台再加前綴;Konsist 骨架是這份範本新增的內容類型,席位標判不準,編排者判為計劃要的新能力、不是第二種做法。席報告:`governance/review-reports/code-Android目標架構範本/`。
