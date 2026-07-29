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
  KEY:待辦 backlog(依價值序)——①合約普查(星標 INVARIANT 密度慘案:172 篇僅 2 條掛最強鏈;嚴禁 code 反推,按業務語意逐一判)②cluster 帳設為 panel 預設(capture-recapture 降 advisory 已在 cluster 模式,預設化即回應「統計儀式」批評)③測試 hermetic 化(碰真 ~/.claude 的測試改 temp HOME;Windows 分支無條件 pass 清除)④同名節點 resolver 載重操作 fail-closed⑤supply-chain:get.sh pin+fetch-notesmd SHA 驗證⑥branch protection required checks+PR auto-merge(GitHub 設定面,人做;合體版=紅燈進不了 main 又免手動合併)⑦**guard kill 排程化**(2026-07-29 使用者採納:合約「牙齒檢查」目前是手動按需跑,前四道關卡[Check T 綁定/[audit:]/pre-push 全套/CI 複核]只驗形式與綠燈,唯有 kill 證明測試真咬得住 → 排進每日治理腳本定期自動跑,讓三層[有測試/測試會跑/測試有牙]全閉環;成本考量:kill 要真弄壞跑一輪,排程時段與範圍[全部合約 vs 抽樣]待設計)
  DECISION:[2026-07-29]緩辦不採清單——單檔拆模組(P1):方向對但大手術,anchor/測試/vendor 全連動,單人維護期回報<風險,等第二維護者;tier 三檔收斂兩檔:與 d4「前置加重一律拒」同源但需 replay 數據支撐再裁;autonomous loop 非 dry-run 停用:2026-07-29 使用者已裁**停用**(--pr 硬閘 exit 2+scratch 改 mktemp;解禁=隔離落地過 code-loop;決策記於 nested-agent-permission-scope)
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
| autonomous confused-deputy 未修仍可跑 | **採，已停用** | 使用者 2026-07-29 裁定；--pr 硬閘拒跑、dry-run 照常 |

## 驗證

- P0 全套：本機 1588 checks 全綠＋乾淨 HOME 預演全綠（CI 可行性驗證）＋doctor 0 issues。
- CI 首跑實錄：run#1 **紅**——當場抓到 `t_impact_incidents_smoke` 硬編 `/Users/enzo/...` 絕對路徑（外審 hermetic 批評第一天就兌現價值）；改 `__file__` 相對後 run#2 **綠**（3m15s 全套 1588＋doctor --ci＋anchor verify）。信任根已活。
- **對話輪收官（2026-07-29，三輪互審）**：總分 5.2→**6.4**（方法論 7.5/治理 7.5/架構 6.0/可用性 5.5/安全 5.5）。全程五份文件歸檔 `governance/external-reviews/`。對話戰果：①它改口四處（canary 鑑別力/負結果文化/可移植性基準/拆檔時點——皆因實證）②我方採納其「第一刀」三步與 guard-kill 升準殺全案③**它反查出真事故**：code-testmap r2 三筆 canary record 回報成功未落盤（[[Issues/canary-record未落盤事件]]），11 中 10 降級為 8 原生+3 補記④終稿仍明標分歧：「圖譜為準」正文未改不給預支分、dry-run 寫權未隔離、required check 未設。⑤路線圖重排：P1-0 部署最後一哩/P1-1 oracle 品質包（record 落盤自驗+canary 第二判者抽查+guard-kill 歸因）/P1-2 砍統計儀式/P1-3 合約普查——與我方 backlog 合流，oracle 品質升為最高投資序。終稿結語可當北極星：「讓每一盞綠燈都能回答：證據真的落盤了嗎？紅燈真的是那條規則咬住的嗎？」
