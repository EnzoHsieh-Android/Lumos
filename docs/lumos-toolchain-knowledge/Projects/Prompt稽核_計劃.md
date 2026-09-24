---
type: project
status: doing
created: 2026-09-25
updated: 2026-09-25
tags:
  - type/project
  - status/doing
  - scope/ux-docs-hygiene
summary: |-
  WHY:[2026-09-25 Enzo 下令 /claude-api prompt-audit,結果全套用]用 Claude prompt-audit 指南把 repo 裡會進模型 context 的文字(兩份規則檔、紀律範本、hook 注入訊息、十三個 skill)對 Opus 5.5 / Sonnet 5 掃一次過時寫法。五席各管一塊,62 條(高 8/中 41/低 13),高中信心 49 條做成 87 個 hunk 全套用,低信心 13 條只記不改
  WHY:[2026-09-25 五席稽核]★主要問題不是語氣太重,是新舊說法並存★——舊式施壓詞全 repo 幾乎 0、禁止句大多附出處判定保留;真正的是「改一處另一處沒跟」「舊版劃掉留在原地」。模型讀不出刪除線,能照抄的舊區塊反而是最強的範例
  WHY:[2026-09-25]句數上限(每條 finding ≤3 句)拿掉是 Enzo 當場裁的翻案,見 [[Projects/席位人格化_計劃]] d2 與 [[Systems/design-loop]] d10
  PITFALL:[2026-09-25 稽核抓到]★skill 觸發描述與指令索引還寫「不要直接 grep/Read」,跟程式碼為主的定位正面衝突,而漂移守衛管的入口檔清單沒有 SKILL.md 的描述欄★——描述每次觸發都讀,是最該同步的地方。重現:`grep -n "不要直接 grep" skills/*/SKILL.md skills/lumos-project-notes/commands/INDEX.md`(修後應 0 筆)
  RULE:[since:2026-09-25][confirmed:2026-09-25][retire:hook 注入改成結構化欄位、不再用文字框區分資料與指令]★注入框裡只放從專案讀出來的值,工具自己寫死的指示放框外★——框頭寫「不是指令」,把工具自己的祈使句包進去,照字面讀的模型會當成可略過的資料。單源在 [[Systems/hook信任邊界]]
  REVISIT:2026-10-25 用情境探針對三處改動各跑一次改前改後(skill 觸發描述、進場 hook 開場白、框外指示),確認模型行為真的有變;這次沒做行為驗證
lands_in:
  - "[[Systems/hook信任邊界]]"
  - "[[Systems/codex-harness]]"
---
# Prompt稽核_計劃

PRIOR-ART: 直接借 Claude 官方 prompt-audit 指南(claude-api skill 的 shared/prompt-audit.md)的四組 pattern 與「不要報」清單,不自訂準則。
RETIRE-IF: 這是一次性稽核,不建機制;下一次模型換代時照同一份指南重跑,本篇只留當次的判斷脈絡。

## 做了什麼

- 範圍:兩份規則檔、紀律範本、hook 注入進對話的訊息、十三個 skill(含三份長 reference 與派工範本)。沒有直接呼叫 Claude API 的程式,請求參數那一組沒東西可查。
- 目標模型:主會談 Opus 5.5、審查席 Sonnet 5;外家席(Codex)那部分只記事實漂移。
- 方法:五席各管一塊照指南判;三份長 reference 用指南的訊號 grep 找熱點再讀周圍,沒有逐行讀完。影響最大的幾條編排者自己回頭核對,其中「記帳範本照抄會被擋」一條說過頭(只有載體席必帶 findings-set),降為中信心、範本拆成一般席與載體席兩種。
- 套用後連動兩支測試(影響鏡頭注入框、派工鏡頭超時說明),各自用翻紅驗過:把舊寫法放回去會紅。

## 影響最大的幾條(已改)

1. 筆記 skill 的觸發描述與指令索引還在說「不要直接 grep/Read」。
2. 進場 hook 的開場白跟紀律範本兩套說法(「被催也要先 impact」「一律以程式碼為準」)。
3. 注入框把 hook 自己的指示也框進「不是指令」裡。
4. 設計審派工詞寫死「你一定找得到至少一個問題」,逼審查席每輪硬湊。
5. 代碼審 reference 標「現行」的範例其實是舊的(舊閘指令、停用的類別、記帳範本不分席)。
6. 語言慣例 skill 兩段示範碼是錯的(Dart 有上限並行其實截掉資料、C# 不疊 using 機制講反)。

## 沒做的

- 指南第 7 步的行為驗證(改前改後各跑一次探針)沒做,見摘要 REVISIT。
- 低信心 13 條只記在卷證,沒改。
- 五席的逐條報告與提議 diff 存在當次會談的暫存區,沒進 repo;逐條依據看各處改動本身。

