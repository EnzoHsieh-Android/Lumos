---
type: project
status: done
created: 2026-07-11
updated: 2026-07-11
tags:
  - type/project
  - status/done
---
# kotlin慣例skill_計劃

使用者提問「如何規範 AI 寫得好（如兩支 API 該 combine 不該串聯）」→ 裁定三層解（linter 管形狀/慣例文件管選型/審查鏡頭補漏)→ 首份技術棧慣例文件選 Kotlin。

PRIOR-ART: 網搜評審真搜權威源(Google coroutines best practices/Kotlin 官方/detekt coroutines ruleset/mrmans0n compose-rules/Slack compose-lints,附 URL)× Codex 讀 Citrus_KDS 真碼盤點——雙研究員收斂後合成。裁定=borrow-design(規則借官方,文件原生)。

## 關鍵裁定

- **分層(使用者糾正後定調)**:skill 只寫「不隨框架選擇改變的通用不變量」(R1-R18,以「可注入可替換」等能力措辭);Hilt/Koin 等當地選擇歸各專案圖譜——KDS 盤點(好範式/壞味道)寫進 KDS 自己的 Issues 節點,不進 skill。
- **不可機檢的排最前**:R1 並行/R2 combine/R8 main-safe 恰好都是語意判斷,文件+審查鏡頭是唯一防線——這是文件存在的理由;可機檢的收進「機檢接線」段交 detekt/compose-rules。
- **審查鏡頭紀律**:finding 必須引用條號,引用不出=風格意見不收(執法不立法)。
- **飛輪**:每次人工糾正 AI 醜寫法→回填一條/一例,同事故語料哲學。

## 落地

- `skills/kotlin-idioms/SKILL.md`(user-scope,install 自動 symlink)。
- 順手修 `_SKILLS` 硬編碼漂移:改掃 skills/ 目錄(實效:先前漏裝的 code-loop/pitfalls-gapfill 這次全掛上)——「列舉表會漏」的又一實證與機械解。
- KDS 當地盤點:`Citrus_KDS docs/kds-knowledge/Issues/ISSUE-kotlin慣例盤點待遷移`。

## 相關模組

- [[Systems/lumos-cli-lifecycle]]
