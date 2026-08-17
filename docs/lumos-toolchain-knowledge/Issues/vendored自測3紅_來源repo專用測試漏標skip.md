---
type: issue
status: open
created: 2026-08-17
updated: 2026-08-17
aliases: []
tags:
  - type/issue
  - status/open
summary: |-
  FLAG:TECHNICAL
  KEY:2026-08-17 Landmark 跑 lumos update 後自測 2139綠/76skip/★3紅★,三紅全是引用來源 repo 資產的測試漏掛「來源 repo 專用」skip 守衛
  KEY:①t_precommit_whitelist_drift_guard 讀 docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md ②「snr 腳本 rc0」③t_s2_snr_synthetic 跑 governance/eval/canary_snr.py——兩檔皆僅存在 toolchain 本體,vendored 專案必炸 Errno 2
  KEY:修法=比照既有 76 支的 skip 判準(偵測 vendored 環境)把這 3 支納入;工具本身無回歸(doctor/query 冒煙皆過)
---
# vendored自測3紅_來源repo專用測試漏標skip

消費端現場:LandmarkMember@develop cec3645f(chore(lumos) commit message 引本案)。
三紅輸出原文:

```
✗ t_precommit_whitelist_drift_guard EXCEPTION: [Errno 2] No such file or directory: .../docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md
✗ snr 腳本 rc0  python3: can't open file '.../governance/eval/canary_snr.py': [Errno 2] No such file or directory
✗ t_s2_snr_synthetic EXCEPTION: Expecting value: line 1 column 1 (char 0)
```
