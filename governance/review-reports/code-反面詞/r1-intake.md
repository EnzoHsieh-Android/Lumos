# r1 intake — code-反面詞-b(2026-09-09;原編號 code-反面詞 首記載體選錯席、帳不能撤換編號重記;tier standard;單席通才 sonnet + 架構對齊 sonnet;外家 Codex 席 standard 退同門留痕)

preflight-4: ran(代碼審首輪;材料 r1-snapshot.patch 225 行;refcheck/quote-check 見下)

## 收貨:編排者機械重現
- f1(major)raw 整題看字串 → HIT:`logger.LogError("SELECT query failed")` 修前亮 cs-data、`console.log("remember to call JSON.parse")` 亮 node-eventloop、`throw new Error("db.query failed, check createPool")` 亮 node-data。折:raw 布林改成逐 pattern 的 `when_raw`(只剝註解),同題其他 pattern 照剝字串;SQL 字串要長得像 SQL(`FROM|INTO|SET|WHERE`)才算。釘:t_stack_question_triggers「假命中不回來」六條。
- f2(minor)`\bstatic\b.*Context` 對只傳參數的靜態工具函式亮 → HIT;折:收窄成 `static\s+(final\s+)?(Context|Activity|View)\b`(靜態欄位型別)。註:該行仍亮 kt-leaks,是既有範式詞 `\bContext\b` 的行為,不是本 diff 引入。
- f3(minor)`\.Open\(\)` 任何物件都亮 → HIT(`response.Body.Open()`);折:`[Cc]onn\w*\.Open\(\)`。釘同上。
- f4(minor)`viewDidLoad` 每個 UIKit 畫面都亮、題目卻是 SwiftUI 措辭 → HIT;折:拔掉。釘同上。
- f5(minor)`[LR]TRIM\(` 沒 `\b` → HIT(`fn_TotalTrim(`);折:加 `\b`。釘同上。
- manifest 判定(原 f6,席位引句抄自 manifest 不在 diff、依規改成段落不列 finding):scripts/usage_scan.py:91 裸 open → HIT(別的 session 的量測腳本,已 commit);編排者順手折:改 `with open`。第 64 行判誤報同意(已在 with 裡)。
- 架構對齊席 clean(0 條):反面詞塞同一個 when 清單、raw/in_strings 語意對齊、表格產生方式同上次。

## 處置
- f1–f5 全折,accepted 空,refuted none;manifest 那條編排者自折。
