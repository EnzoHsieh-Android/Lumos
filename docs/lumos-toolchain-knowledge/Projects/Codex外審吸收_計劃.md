---
type: project
status: done
created: 2026-07-29
updated: 2026-07-29
tags:
  - type/project
  - status/done
related:
  - "[[Projects/上下文瘦身_計劃]]"
  - "[[Projects/GPT外部評審吸收_計劃]]"
summary: |-
  FLAG:DECISION
  KEY:2026-07-29 Codex(gpt-5.6 high)全項目外審(總分 5.2/10;全文存 session scratchpad):三大風險=假確信(形式合規≠語意正確)/治理熵超過維護力/強制力只在本機——P0 已落地,P1/P2 列帳待辦
  KEY:★P0 已落地★——①GitHub Actions CI 信任根(.github/workflows/ci.yml:compileall+SyntaxWarning 閘+全套 1588+doctor --ci+anchor verify 缺 baseline 必紅)②pre-push「CI 仍會抓」假話改為指名 Actions 的真話③外審實錘壞節點修復(heterogeneous-finder-ensemble d1 id 吞進 content)+lint decisions 結構守衛(正牌 parse_decisions 驗:空 content/條數對不上)④文件漂移批次(ONBOARDING 一鍵化/ARCHITECTURE+README.en 44→49/Obsidian 誠實註記/anchor 定性=改動偵測非信任根/方法論上手時間分層)⑤SyntaxWarning 歸零(3 處 docstring 轉 raw)⑥命令數漂移守衛測試(t_docs_command_count,首跑即抓到 README.en 漏網)
  KEY:待辦 backlog(依價值序)——①合約普查(星標 INVARIANT 密度慘案:172 篇僅 2 條掛最強鏈;嚴禁 code 反推,按業務語意逐一判)②cluster 帳設為 panel 預設(capture-recapture 降 advisory 已在 cluster 模式,預設化即回應「統計儀式」批評)③測試 hermetic 化(碰真 ~/.claude 的測試改 temp HOME;Windows 分支無條件 pass 清除)④同名節點 resolver 載重操作 fail-closed⑤supply-chain:get.sh pin+fetch-notesmd SHA 驗證⑥branch protection required checks(GitHub 設定面,人做)
  DECISION:[2026-07-29]緩辦不採清單——單檔拆模組(P1):方向對但大手術,anchor/測試/vendor 全連動,單人維護期回報<風險,等第二維護者;tier 三檔收斂兩檔:與 d4「前置加重一律拒」同源但需 replay 數據支撐再裁;autonomous loop 非 dry-run 停用:涉使用者工作流,攤給人裁未決
---
# Codex 外審吸收（2026-07-29）

`PRIOR-ART:` 外審本身即先例掃描——評審對照 ADR/Spec Kit/OpenSpec/coverage gate 界定差異化：「整合與治理生命週期是真差異，基礎方法論非發明」（與我方對外論述一致）；其批評「衝突時圖譜為準」應限縮為**意圖權威**、行為事實衝突該進 incident——此認識論修正值得吸入方法論文（待辦⑦）。

## 外審要點與裁決

| 外審批評 | 裁決 | 依據 |
|---|---|---|
| 無 CI 信任根＋hook 謊稱「CI 仍會抓」 | **採，P0 已落地** | 實錘：repo 無 workflows；謊言句 3 處已改真話 |
| 壞 YAML 逃過 doctor（d1 吞進 content） | **採，已修＋守衛** | 實錘；lint 新守衛用正牌 parser 驗空 content/條數 |
| 文件漂移（44 指令/兩步安裝/Obsidian 宣稱） | **採，已修＋機械守衛** | t_docs_command_count 首跑抓到 README.en 漏網＝守衛有效性自證 |
| anchor 非信任根應稱改動偵測 | **採，定性已改** | 同 repo 自簽悖論圖譜本有記載 |
| 合約密度 2/172 | **採，列 backlog①** | 最強鏈幾乎空載屬實 |
| capture-recapture＝統計儀式 | **半採** | 批評與圖譜自記天花板一致；但漏看 cluster 帳已降 advisory——待辦＝預設化，非砍除 |
| canary 有自嗨成分 | **不另動** | d4 定位（抬質量非保正確）＋誠實天花板已同款；其建議與現行定位一致 |
| 單檔拆模組 | **緩** | 見 DECISION |
| 一小時上手不可信 | **採，已改分層敘述** | |
| autonomous confused-deputy 未修仍可跑 | **攤給人** | 使用者工作流，未決 |

## 驗證

- P0 全套：本機 1588 checks 全綠＋乾淨 HOME 預演全綠（CI 可行性驗證）＋doctor 0 issues。
- CI 首跑實錄：run#1 **紅**——當場抓到 `t_impact_incidents_smoke` 硬編 `/Users/enzo/...` 絕對路徑（外審 hermetic 批評第一天就兌現價值）；改 `__file__` 相對後 run#2 **綠**（3m15s 全套 1588＋doctor --ci＋anchor verify）。信任根已活。
