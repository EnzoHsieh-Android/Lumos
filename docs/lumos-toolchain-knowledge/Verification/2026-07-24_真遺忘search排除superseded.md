---
type: verification
status: pass
date: 2026-07-24
valid_under:
  - "cmd_search 濾網插「命中確認後、三路分岔前」;_is_forgotten 只認 superseded 不認 stale"
  - "--include-superseded 逃生;隱藏數走 stderr、--json 加 hidden_superseded 欄位"
revalidate_when:
  - "動 cmd_search 候選迴圈/三路輸出/_is_forgotten,或改 status 語意(superseded/stale)"
plan_refs:
  - "[[Projects/真遺忘召回過濾_計劃]]"
tags:
  - type/verification
  - status/pass
summary: |-
  TEST:t_search_forget_superseded 19 checks(預設排除 superseded/stale 不被藏守門/活節點保留/valid:false 不誤傷/隱藏數走 stderr 精確=命中被藏筆數/--include-superseded 逃生/三路 ranked+legacy+regex 一致/--json hidden_superseded 欄位+合法 JSON/--files-only stdout 檔名+stderr 提示)+全套 1355 綠零迴歸
  KEY:真遺忘第一刀落地——search 預設藏 status=superseded(agent 進場翻筆記不再把已殺合約當活的讀),**不藏 stale**(重驗警訊);緣起 GateMem(arXiv 2606.18829)照出「標記≠遺忘」
  KEY:實作=_is_forgotten(env,rel) 判 status==superseded;濾網插 cmd_search「if not hits:continue 之後、if ranked 分岔之前」→ranked/legacy/regex 三路一致、hidden 數=命中被藏筆數非全庫;提示走 stderr(全模式)、--json 加 hidden_superseded
  KEY:行為合約——回歸守衛 t_search_forget_superseded+獨立審計 sonnet/2026-07-24(含 mutation 實測:把 stale 也濾/濾網插錯位置→測試翻紅);因 doctor Check T 無 Python profile 未標形式硬合約標記(invariant)(dirs 錯配,csharp 找 Tests/ 而 Python 在 scripts/),當一般回歸守——Check T Python 化另立
  VERIFY:design-loop 3 審收斂(2 Sonnet light+1 跨家族 Codex std,跨家族接住兩輪 Sonnet 漏的 hidden 數插點 F6+goldset 安全網破洞 F7);使用者裁定進 TDD;TDD 紅→綠
  KEY:已知殘留(本刀不做)——context 基本鄰居/推薦、impact(永不做預設藏,事故記憶)、doctor 對作廢驗證不一致;餵未來「全系統真遺忘」決定
---
# 2026-07-24_真遺忘search排除superseded

真遺忘第一刀落地。spec：[[Projects/真遺忘召回過濾_計劃]]。緣起：GateMem（arXiv 2606.18829）2026-07-24 治理調研照出 lumos「supersede 只蓋章、召回照樣遞給 agent」——標記 ≠ 遺忘，agent 進場 `lumos search` 可能把已殺合約當活的讀。

## 做了什麼
`cmd_search` 候選集在**命中確認後、三路（ranked/legacy/regex）分岔前**濾掉 `status=superseded` 節點（`_is_forgotten` 判定，**只認 superseded、不認 stale**）；`--include-superseded` 逃生；隱藏數走 **stderr**（全模式含 `--files-only`，不污染 stdout）、`--json` 加 `hidden_superseded` 欄位。

## 為什麼這樣
- **stale 不被藏**是樞紐：stale＝待重驗警訊，藏了＝把該看見的提醒也遺忘、製造新盲區（Check S 把 stale+superseded 綁一起 skip 正是反例）。立為核心行為合約（因 doctor Check T 無 Python profile，未走形式硬合約標記，見下）。
- **濾網插點**在命中確認後：否則 hidden 數變成「全庫 superseded 總數」而非「本次命中被藏筆數」（Codex std F6 接住，兩輪 Sonnet 漏）。
- **召回不退**：goldset §6 gate 只比相對 lift、擋不住「兩邊一起藏掉好答案」（Codex std F7）——測試改用改動前後對照式 fixture（活節點保留、只 superseded 被藏）。

## 審計軌
- design-loop：r1 light（canary missed，但 orchestrator 查碼證實 4 major，縮範圍 search-only）→ r2 light（canary caught，2 major 折入，ratchet 升 standard）→ std 單席 Codex 跨家族（7 major，接住 Sonnet 漏的 F6/F7）→ 使用者裁定進 TDD。
- 行為合約：回歸守衛 `t_search_forget_superseded` ＋ 獨立審計 `sonnet/2026-07-24`（mutation 實測守得住）；因 doctor Check T 無 Python profile（dirs 錯配），未走形式硬合約標記，當一般回歸守——Check T Python 化另立。
- 測試：`t_search_forget_superseded` 19 checks + 全套 1355 綠。
