---
type: project
summary: |-
  FLAG:TECHNICAL
  KEY:第 2 批接活⑥——loop status --roster(席位編制對帳:dispatch 快照 vs 應派,含外家缺席轉述)測試齊全但治理帳 0 呼叫;併入 --disposal 輸出(問閘每輪必經,缺席轉述自動出現),--roster 獨立旗標退場指路
  KEY:tier=light 理由:只動轉述輸出不動判定布林,實作 ≲50 行孤立;light 輪冒 ≥major 即升級開 -std 編號
  DEP:[[Projects/建了沒人跑批次裁定_計劃]]
status: doing
created: 2026-08-26
updated: 2026-08-26
tags:
  - type/project
  - status/doing
---

# roster對帳併入問閘_計劃

> 白話:席位對帳(派工快照跟編制表對不對得上、外家缺席要不要降級措辭)功能是好的、測試 17 條斷言齊全,但獨立旗標沒人記得敲——治理帳掛零。搬到問閘輸出裡,每次問收斂自動轉述。

## 條款

- **[S1] 併入**:`loop status <id> --disposal` 的輸出尾端自動附 roster 對帳行(復用既有 `--roster` 的全部邏輯與措辭:席數/家族桶/外家缺席單家族措辭/兼任警示/vacuous),**不影響 PASS/FAIL 判定**(對帳恆 advisory,與現行 --roster 的「rc 與不帶完全一致」釘同語意)。
- **[S2] 旗標退場**:`--roster` 獨立旗標改為拒絕+指路(「對帳已併入 --disposal 自動輸出」),比照 panel 退場模式;既有 17 條 roster 測試改打 --disposal 路徑(斷言語意不變),skill 兩處提及同步。
- 邊界:編制表本身(_TIER_ROSTER/lens 值域)不動;--panel/--light/--settle 模式的觀測輸出不動。

## 行為斷言

--disposal 輸出含對帳行(外家在/缺兩態措辭);--disposal rc 與加對帳前完全一致(advisory 釘沿用);--roster → rc2+指路;skill grep 無殘留。

## 實務隱患

- 守衛面擦邊:動的是問閘的**輸出**不是判定;PASS/FAIL 布林路徑零改動由「rc 完全一致」釘鎖住。light 若冒 ≥major 立即升級完整迴圈(-std)。已排除:金流/對外/不可逆不涉。
