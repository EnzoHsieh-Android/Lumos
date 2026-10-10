---
type: project
status: done
created: 2026-10-10
updated: 2026-10-10
tags:
  - type/project
  - status/done
  - scope/guards-gates
lands_in:
  - Systems/arch-alignment-lens
related:
  - "[[Projects/架構對齊可宣告目標架構_計劃]]"
  - "[[Systems/arch-alignment-lens]]"
---
# DDD目標架構範本_計劃

> 白話:目標架構功能讓專案宣告「這些目錄照某篇目標架構筆記審」,但每個想照 DDD 寫的專案都得從零寫那篇筆記。這份計劃在 lumos 的使用說明裡放一份可以直接抄的 DDD 目標架構範本(九條規則,含深模組與測試邊界),附採用步驟,並用一支測試確保範本照抄後讀得出規則、格式合規。

## 問題與最小解

立案:Enzo 2026-10-10 提出——把對話中起草、驗過的 DDD 目標架構節點收進 lumos。

現況:[[Projects/架構對齊可宣告目標架構_計劃]] 上線後,目標架構節點要由各專案自己寫;使用說明只有四行規則片段的例子,沒有完整可用的節點,也沒講深模組與測試要從哪個邊界驗。lumos 的測試規範(〈實作測試品質〉)要求斷言實際行為、綁死內部結構就驗一次重構,但刻意不規定架構——所以「從聚合根與應用服務的公開方法測」這類規則只能放在專案自己選的目標架構裡。

最小解:只加一份範本說明檔與一支守它的測試,不加新指令、不改任何判定。範本的日期欄位用佔位字,照抄沒換時 lint 會逐條印出日期格式警告(筆記格子目前只提醒不擋),提醒採用的人想過一次採用日與回頭檢查日。

PRIOR-ART: DDD 聚合規則借 Vaughn Vernon《Implementing Domain-Driven Design》的聚合設計四條(守不變規則、小聚合、用 ID 參照其他聚合、一個交易改一個聚合);深模組借 John Ousterhout《A Philosophy of Software Design》;測試邊界借 Matt Pocock 的 TDD 測試指引(專案測試規範已引用)。ArchUnit、NetArchTest、Konsist 等工具已有分層與 DDD 預設規則,範本只寫審查席判得動的規則並指路「能寫成架構測試的就綁 [test:]」,不自建規則引擎。
RETIRE-IF: 2027-04-10 人裁時,若 Enzo 手上的專案沒有任何一個在 arch_targets 宣告引用照這份範本建的節點,就撤掉範本檔與它的測試,只留使用說明那一列 [retire:人裁] [until:2027-04-10]。

## 做法

1. 新增 `skills/lumos-project-notes/commands/target-arch-ddd-template.md`:採用步驟(開節點、貼規則、換日期、加宣告)與一個可以直接存成節點檔的範本區塊。範本九條 RULE 行:Domain 不碰框架與資料庫、不變規則只在聚合根、聚合之間用 ID 參照且一個交易改一個聚合、Repository 整包存取、應用服務只協調、範圍外舊碼只經應用服務進入、值物件不可變、深模組(邊界劃在聚合)、測試只經公開方法驗。每條附「違反長怎樣」,日期欄位用 `<採用日>`、`<回頭日>` 佔位。
2. `commands/06-代碼審與推送.md` 的 `arch_targets` 那一列加一句指到範本檔。
3. 新增測試:讀範本檔裡的範本區塊,佔位換成實際日期後存進臨時圖譜,lumos lint 0 問題、目標架構的規則讀法讀到九條有效規則;佔位沒換照抄時 lint 印出日期格式警告;06 那一列提到範本檔名。
4. `Systems/arch-alignment-lens` 寫一段指路,並把測試總檔列進它管的檔(目標架構的測試都在那支檔裡)。

## 驗收條款

- [S1] 當範本區塊的日期佔位換成實際日期後存成節點時,lumos lint 應回報 0 問題,目標架構規則讀法應讀到九條有效 RULE 行。 [test:t_arch_target_ddd_template_valid]
- [S2] 當範本區塊沒換日期佔位就存成節點時,lumos lint 應對佔位的日期欄位印出「日期要寫成 YYYY-MM-DD」警告。 [test:t_arch_target_ddd_template_placeholder_warns]
- [S3] 當使用說明 06 的 arch_targets 那一列被讀時,應提到範本檔名。 [test:t_arch_target_ddd_template_linked_from_usage]

## 回退

刪掉範本檔、06 那一列加的那句、測試與 arch-alignment-lens 的指路段;測試總檔從它的管轄移除。已照範本建節點的專案不受影響(節點是它們自己的圖譜內容)。不碰任何帳本。

## 實務隱患

- 效能:只多一支讀檔與跑一次 lint 的測試。
- 已排除:併發:只讀範本檔、寫臨時目錄,不碰共用狀態。
- 已排除:金流:不碰任何金流或支付資料。
- 已排除:對外送出:只是使用說明與測試,不對外寄送。
- 已排除:不可逆:只新增檔案,可直接刪除回退。
- 已排除:守衛面:不改任何判定與擋下條件,只新增一份說明文件與一支測試;範本只是起點,各專案照自己的情況刪改規則。

## 審計修正紀錄

- 規格閘(2026-10-10):判風險低;三條條款的測試在實作移開時全紅、放回後全綠。起草時寫「照抄沒換佔位會被 lint 擋」,實測筆記格子只提醒不擋(rc0),改寫成「會逐條警告」並讓 S2 驗警告文字。測試裡取今天用了 `date.today()`,被新增告警閘當成新告警而把分級拉到 high,改成專案慣用的帶時區取法後回到 light。
- 代碼審 light(2026-10-10,架構對齊 1 席):4 條 minor 全數照改——技能首頁加入口(比照測試品質規範)、測試改用共用的 mkvault 夾具與 _need_src 守門、取範本改照「## 範本」小節切而不另立 HTML 註解標記。席報告:`governance/review-reports/code-DDD目標架構範本/`。
