---
type: project
status: doing
created: 2026-08-24
updated: 2026-08-24
summary: |-
  FLAG:DECISION
  KEY:立案(2026-08-24 Enzo「好」)——Check S 是「喊了等人看」:兩篇樞紐筆記被喊 44/40 天(546/499 次)沒人理,終於派乾淨 agent 審=2/2 全站不住、11 處真漂移(兩處「照做出錯」級)。抽檢命中率 100%,問題不在閘在「沒人看」;backlog 裡自主 loop 兩次啃不動的「腐化偵測延遲」正是這題
  KEY:方案=每週自動迴圈尾端派乾淨 agent 審「從未確認+過期」功能筆記(上限 N=2/週,PR 高者先)——站得住→自動戳 self_audit(model 名寫 auto 供追溯);站不住→報告+修正建議進 pending 等人放行,★不自動修筆記★(寫入紀律不破)
  KEY:成本錨——乾淨 agent 一篇 ~10 分鐘/1-2 美金(今天實測),對照 orchestrator 一輪 34-68 美金;零新演算法,全現成零件(gov --nags 資料同源、claude -p 派工、self-audit 戳)
  DEP:[[Systems/autonomous-iteration-loop]]｜governance/autonomous-loop.sh
plan_refs: []
related:
  - "[[Systems/autonomous-iteration-loop]]"
tags:
  - type/project
  - status/doing
---
# 自足性審計閉環_計劃

> 白話:體檢每天喊「這篇筆記該找沒背景的人重新確認」,喊了一個半月沒人動——今天真的派人去看,
> 兩篇全是爛的。所以把「派沒背景的 agent 去看」變成每週自動的事:站得住自動蓋章,站不住把
> 修正建議放進待放行匣等人。機器不改筆記,只蓋「我看過還行」的章。

## 症狀(會翻紅的指令)

```
python3 scripts/lumos gov --nags 14 --since 120
```
2026-08-24 前:兩組 44/40 天空轉(546/499 次)。本案成功=同款空轉結構性不再累積(≥14 天即有審計紀錄)。
佐證:2026-08-24 手動派審 2/2 站不住(governance/review-reports/self-audit/ 兩份報告,11 處漂移)。

## 設計

1. **選目標**:`governance/autonomous_loop/selfaudit_pick.py`——讀 doctor 的 Check S 同源判定
   (sa_missing ∪ sa_stale;★不 shell 出去 grep doctor 輸出,直接 import lumos 模組呼叫同一套判定,單一實作★),
   按 PageRank 降冪取前 `N=2`(週配額;knob `SELFAUDIT_WEEKLY_N`,0=關)。
2. **派工**:autonomous-loop.sh 加 `run_selfaudit`(週戳記防重跑,同 run_nags 慣例):
   對每篇 `claude -p` 派乾淨 agent(sonnet;prompt=今天手動版的同款:只讀該篇+對照 code 抽驗,寫報告到
   `governance/review-reports/self-audit/<日期>-<篇>.md`,結尾一行機械可讀判定 `VERDICT: PASS|FAIL`)。
3. **處置**:
   - `VERDICT: PASS` → `lumos self-audit <篇> --model <agent-model>-auto`(自動蓋章;model 名帶 -auto 供追溯,
     誠實邊界:這是「agent 看過」不是「人看過」,Check S 的天花板本來就是這層)。
   - `VERDICT: FAIL` → 報告+修正建議寫 `governance/pending/<日期>-selfaudit-<篇>.md`,★不動筆記★;
     pending >3 天既有喊人機制自然接手。
   - 抽不到 VERDICT 行 → 當 FAIL 處理(fail-closed)+ log 死因尾段(NO_JSON 教訓同款)。
4. **成本護欄**:單篇 timeout 15 分鐘;週配額 N=2;LINE 通知沿 run_nags 慣例(有 FAIL 才通知)。

## 不做什麼(邊界)

- 不自動修筆記(寫入紀律);不動 Check S 本身;不碰 design/code-loop;不審 Systems 以外 type(Check S 口徑)。
- 不新增評測尺——成功看 nags 清單與 pending 產出,兩者都既有。

## PRIOR-ART

`PRIOR-ART: borrow-design`——派工/週戳/LINE 全抄 run_nags/run_probe 既有慣例;判定同源 Check S(不另立);
「agent 審+人放行修正」= design-loop 收貨模式的單席簡化。零新依賴。

## 測試(草)

①selfaudit_pick:missing/stale 各造一篇→選中、PR 排序、配額截斷、knob=0 空 ②VERDICT 抽取:PASS/FAIL/缺行(fail-closed)
③PASS→self_audit 戳記寫入(model 帶 -auto)④FAIL→pending 檔產出、筆記未動 ⑤週戳防重跑 ⑥翻紅釘:把 fail-closed 改 fail-open→②翻紅。
shell 段落照 t_install_global_hook_sync 模式(bash -n+函式抽測)。

## 實務隱患

- **守衛面**:自動蓋章會不會洗掉真問題?→ 蓋章只在 VERDICT: PASS,而 agent prompt 是「找站不住」框架(今天 2/2 抓到證明有牙);
  model 名 -auto 留追溯;Check S 天花板本來就是「agent 誠實性」,本案沒把它變差,只把「沒人看」變「有人看」。
- **成本**:N=2/週×~2 美金,月 ~16 美金,可忽略;timeout 護欄。
- **回滾**:knob=0 整段關;pending 檔可直接刪。
- **併發**:週戳+循序派工,無共享寫。

## 下一步

design-loop standard(3 席+arch+Codex)→ 過了實作。
