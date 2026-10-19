---
type: verification
status: pass
date: 2026-10-15
valid_under: order-web 用 vitest 5.0.4、設定 profile 寫 node-jest、run_cmd 是 npx vitest run -t {method}
revalidate_when: vitest 升主版號、或跑過證據的比對樣式改動時
tags:
  - type/verification
  - status/pass
  - scope/stack-knowledge
plan_refs:
  - "[[Projects/前端框架從vue分出_計劃]]"
---
# 2026-10-15_order-web實地跑vitest合約測試

> 白話:在 order-web 的一份複本上綁一條合約、跑合約測試閘,舊版工具把 vitest 真跑過的那次擋下(證不出跑過),新版放行;把那支測試改成 skip,新版照樣擋。**這不是 S30 本身**——S30 要 order-web 用它自己的中文測試名綁合約推送一次,那要等測試名能收中文句子。

## 怎麼做的

- `git clone` order-web 到暫存目錄,`node_modules` 用連結指回原專案(只讀),原專案沒動。設定照 order-web 現況:`node` 平台 profile 寫 `node-jest`、`run_cmd` 是 `npx vitest run -t {method}`。
- 在 `src/domain/clock.test.ts` 加一支英文名的探針測試 `it('ran_evidence_probe', …)`(中文名現在綁不上),在 `Systems/下單畫面` 摘要加一條 `KEY:★INVARIANT★ … [test:ran_evidence_probe]`、正文用反引號提到 `src/domain/clock.ts`;再改一行 clock.ts 提交,跑 `lumos bound-tests --diff HEAD~1..HEAD`。

## 結果

| 工具版本 | 探針測試 | 結果 |
|---|---|---|
| 改動前(提交 43924dea) | 正常 | **擋下**:「證不出它真的跑過任何一支測試」——vitest 摘要沒有冒號,舊樣式對不上(逾期清單第 10 節說的誤擋,實地重現) |
| 改動後 | 正常 | 放行:`{"status": "green", "ran": 1}` |
| 改動後 | 改成 `it.skip` | 擋下:同一句「證不出跑過」,修法提示多了 vitest reporter 那句 |

## 這篇不能證明什麼

- order-web 真的推送時拿到綠燈:它現在沒有任何合約行,`[test:]` 都是中文句子,綁不上。
REVISIT:2027-01-15 測試名能收中文句子之後,在 order-web 用它自己的測試名綁一條合約推送一次,過了才算計劃 S30 與逾期清單第 10 節做完
