---
type: issue
status: done
created: 2026-08-30
updated: 2026-08-30
aliases: []
about_code: []
tags:
  - type/issue
  - status/done
summary: |-
  FLAG:
  DECISION:
  KEY:
---
# E4confirm餵翻案根造成E3

**★已結案(2026-08-30 當場換 ref 解掉;根因留待另案)★**

## 發生什麼
房務清帳時對兩張連鎖待辦單跑 `rel-cascade confirm`(判「引用篇仍成立」),confirm 的**養成順手邏輯**自動把 cascade 的根決策餵進該篇的 `decision_refs`——但 cascade 的根**天生就是已翻案的決策**(翻案才開單),於是 4 篇驗證當場冒出 4 條 E3(「引用已翻案決策」)。**E4 的判定動作自動製造 E3 的告警**,兩道檢查互相打架。

## 當場處置
4 篇全部 prune 舊 ref → add-ai → promote 換到替代決策(probe輪退場 d1→d3;標註刷新 d1→跨節點 評測尺翻案#d1)。E3 歸零。

## 根因與該修的(留待另案,不阻塞)
`rel-cascade confirm` 的 decision_refs 養成應餵 **superseded_by 指向的替代決策**(同節點型直接解析 dN;跨節點散文型解析不出就不餵並提示),而不是餵翻案根本身。改它要動 confirm 寫側+一條測試。

FLAG: TECHNICAL

