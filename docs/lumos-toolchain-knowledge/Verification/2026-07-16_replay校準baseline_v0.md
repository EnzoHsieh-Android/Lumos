---
type: verification
status: pass
created: 2026-07-16
updated: 2026-07-16
plan_refs:
  - "[[Projects/loop數據收集_計劃]]"
related:
  - "[[Systems/canary-audit]]"
  - "[[Systems/design-loop]]"
valid_under: "golden 語料=2026-07 世代;受試模型 haiku 4.5/sonnet;2 spec(fromscratch-m1/dloop-m2-cluster)×2 模型×釘住/未釘=8 席"
revalidate_when: "模型換代、golden 語料格式變更、replay 協議(釘定/prompt)修訂時重跑"
summary: |-
  TEST:8 席盲測完成;標籤=各 spec v1 文本中真實存在的 r1 級 major(fs 5/m2 7),嚴格逐標籤計分
  VERIFY:replay 校準 baseline v0——接住率:sonnet 釘住 3/5+3/7(另超前命中 r2/r3 級各 1+3 條),sonnet 未釘 4/5+4/7(+1 重建+3 超前);haiku 釘住 2/5+1/7,未釘 0/5+1/7。模型差距 >> 洩漏效應
  KEY:三結論——①haiku 剖面=grep 可得能抓(白名單/詞不存在),推理/交叉對照型全滅→pre-flight 的 haiku 只配機械清單,語意審最低配 sonnet ②單席 sonnet 一發命中 r1 標籤 6-8 成+數條當年 r2/r3 才浮出的洞→多輪的邊際價值主要在「折入後迴歸驗證」非「首輪廣度」,支持 delta-scoped 設計 ③sonnet 對洩漏免疫力強(先推導後驗算並自行揭露),haiku 直接抄答案
  KEY:★replay 方法論鐵則三條(v0 主產出)★——①golden 凍的是折入後 spec,replay 受試對象必須從 git 史撈前折 v1 ②repo 必須 worktree 釘在該 loop 開跑時的 commit(否則實作後 code=答案卡:haiku 抄答案/演化殘影被當缺陷) ③prompt 必須明示「spec 提案的新機制 code 尚未實作=正常」(否則弱模型刷範疇錯誤:把提案未實作當 blocker)
  KEY:誠實邊界——n=2 spec×2 模型,方向性結論非統計結論;標籤集由編排者事後建構(排除 v1 文本中不存在者),有裁判自由度;「超前命中」計分寬鬆面靠人判
---
# 2026-07-16 replay 校準 baseline v0

[[Projects/loop數據收集_計劃]] 的獨立實驗首跑。受試:fromscratch-m1 與 dloop-m2-cluster 兩份 spec 的前折 v1(git 史 5db767b/36540f5)+ 對應釘住 worktree;golden findings 當標籤。

## 接住率表(嚴格逐標籤)

| 席 | fs(5 major 標籤) | m2(7 major 標籤) | 超前命中(r2/r3 級) |
|---|---|---|---|
| haiku 未釘 | 0 | 1 | 0(洩漏污染:抄實作答案/演化殘影當缺陷) |
| haiku 釘住 | 2 | 1 | 0(範疇錯誤:提案未實作當 blocker) |
| sonnet 未釘 | 4(+1 矛盾重建) | 4 | +3(note 歸屬/混用時機/summary 互斥) |
| sonnet 釘住 | 3 | 3 | +1(lint 不掃 repo 契約)/+3(summary 互斥/混用粒度/升級撞守衛——含預言 M2 自審場景) |

## 三結論(進 loop 路由決策的第一批實證)

1. **haiku=機械清單專用**:grep 可得(白名單缺欄/函式名不存在)能抓;需推理或交叉對照(正則隱形/靜默放行/字母撞名)全滅。pre-flight cascade 的分工有據:haiku 掃清單、sonnet 起跳做語意。
2. **單席 sonnet 首輪廣度驚人**:一發命中 r1 標籤 6-8 成,並各自挖到數條當年 panel 跑到 r2/r3 才浮出的洞——多輪的邊際價值主要在「折入後的迴歸驗證」(canary+fold 核對護的那段),非首輪廣度。與 M1 delta-scoped 設計互證。
3. **洩漏效應分層**:sonnet 先獨立推導、拿 code 演化當驗算並主動揭露;haiku 直接抄。釘住對 haiku 反而提升(答案卡拿走後 grep 到的就是真缺陷態)。

## 方法論鐵則(v0 最大產出,折回 loop數據收集_計劃)

① 受試=前折 v1(git 史撈),golden 凍的折後版只能當標籤源;② repo 釘 worktree 於同期 commit;③ prompt 明示提案語意。三條缺一,分數即污染。
