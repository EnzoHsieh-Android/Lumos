## Findings

1. severity: blocker｜blocking: 是｜判準：留下命令與輸出不等於定義了可接受的機械重現；本稿仍未規定何種命令足以證明佐證真偽、重現失敗如何處置，編排者可用只證存在的查詢自行宣告屬實，核心證據洞尚未封死。

引句:「真偽=編排者機械重現,且必留痕」

file: `skills/lumos-design-loop/SKILL.md:21` 至 `:24` 現行三道收貨只機械驗引句錨定、file:line 存在及材料觸及，沒有佐證內容真偽的判定或失敗閘。

2. severity: major｜blocking: 是｜判準：語意類雖新增留痕，但除核心裁定外仍由單一前掃 agent 直接改真檔且不列 finding；正式審查只看到修改後快照，無法判斷原宣稱是否被誤改，原本的繞審計問題只縮小、未消失。

引句:「語意類命中=修真檔+逐條(證據命令+結論)寫進 rN-intake.md 留痕」

file: `skills/lumos-design-loop/SKILL.md:18` 至 `:20` 顯示正式審查快照是在前掃修真檔之後才凍結，後續席位看不到被前掃覆寫的原文。  
file: `skills/lumos-design-loop/SKILL.md:25` 至 `:26` 的正式 finding 判讀、辯方及折入流程因此不會涵蓋這些未升級的語意修改。

3. severity: major｜blocking: 是｜判準：d1 把反引號格式稱為存在性守衛，實際卻承認漏格式會靜默失守且只靠人看；核心卷證通道仍是 fail-open，也沒有符合家規的具體升級回頭條件。

引句:「席位漏反引號=該條佐證靜默失守」

file: `scripts/lumos:68` 的抽取器只辨識反引號 inline code；格式漏寫時不會產生待驗 claim。  
file: `CLAUDE.md:38` 規定承認無機械守衛時必須附何時重驗的回頭條件；本項只寫收貨時人工過目，沒有連續失守後的升級條件。

4. severity: major｜blocking: 是｜判準：d2 的落地斷言只驗關鍵字存在，掛鉤又以自然發生且可缺席的命中作成功證據，沒有植入已知語意錯宣稱去驗證分流、留痕及核心升級，故實作者只補文字也能宣稱落地。

引句:「前掃語意類抓漏 ≥1(若 spec 有)→d2 生效」

file: `/tmp/loop-friction-v2-r1.md:43` 只要求 grep 兩個詞。  
file: `/tmp/loop-friction-v2-r1.md:46` 只驗 intake 存在及任一組命令輸出，未驗語意類逐條留痕、核心裁定升級或非核心分流。

## 七條舊 finding 核銷

已折乾淨：

- carrier 已明定為記帳載體而非證據總集，並保留全席報告及 intake。
- r2 歸因誇大已拆成審材外引用與巢狀截斷兩根因，不再把正常 delta 輪歸功於 d1。
- 波及比例分母問題隨 d3 整條撤回，未來案先立 schema。
- 雙訊號合取漏結構性重寫隨 d3 整條撤回。
- 30% 無校準 schema 已撤回，改為至少五案後另案設計。

未折乾淨：

- 機械重現已有留痕位置，但 oracle 與失敗處置仍未定義。
- 前掃直接修已有留痕及核心裁定升級，但非核心語意修正仍繞過正式 finding。

總結：最嚴重 severity = blocker；blocking 共 4 條。