---
type: verification
status: pass
date: 2026-10-05
valid_under: Claude Code 2.1.289、macOS、haiku 模型;mod 以 --plugin-dir、熱重載、本機市集安裝三種方式載入
revalidate_when: Claude Code 換大版本、mod 型別檔的事件名或欄位變動、或事件帳 mod 出現漏記;日期上的回頭看寫在正文 REVISIT 行
tags:
  - type/verification
  - status/pass
  - scope/platform
plan_refs:
  - "[[Projects/Lumos事件帳_計劃]]"
---
# 2026-10-05_Claude-mod能力實測

> 白話:要用 Claude Code 的 mod(外掛裡的函式 hook)做治理之前,先驗它在各種跑法下會不會載入、記得到什麼、能不能讓既有 hook 讓位。寫了一個只觀察的 mod,用 haiku 跑了六場 `claude -p` 加本互動會談,全部成立;也推翻了一個原本的推測(MEMORY.md 不在系統提示的 memory 那一節)。

## 怎麼驗

- 只觀察的 mod:掛 `session.start`、`turn.start`、`turn.complete`、`session.append`、`tool.call`、`agent.spawn`、`prompt.compose`、`prompt.section`、`prompt.context`、`classic.SessionStart`、`classic.Stop`,每個事件記一行 JSON 到會談暫存資料夾;`classic.SessionStart` 只在路徑含 `modtest-suppress` 的目錄不往下傳(讓位測試)。
- 兩個臨時 git repo(一般、讓位)各跑一場「Bash 執行 echo、派 haiku 子代理跑 ls」;本 repo 跑三場「回答 1+1」看系統提示與第一則訊息的脈絡區塊;本互動會談啟用熱重載後故意跑一個會失敗的 ls;隔離設定目錄(`CLAUDE_CONFIG_DIR`)從本機市集安裝後不帶參數跑一場。

## 結果

1. `claude -p` 用 `--plugin-dir` 會載入,兩場都完整記錄。
2. 結構化觀察成立:子代理的每一列與每次工具呼叫帶子代理編號;`agent.spawn` 看得到派工詞與解析後的實際模型(claude-haiku-4-5-20251001);回合有編號與結束原因(實測看到 `answer`、`error`);prompt 列的來源分得出 `unclassified`(-p 的人類提示)、`task-notification`、`coordinator`(派給子代理的指示)。兩場一般與讓位的事件帳裡,每個主會談回合的 prompt 列(`door: prompt`)都比該回合的 `turn.start` 先記到(兩場共 4 個回合,4 次都是;樣本小,只能說沒觀察到反例)。
3. 讓位成立:讓位那場 lumos 三支開場 hook 在 `governance/runtime/hook-events.jsonl` 沒有紀錄,對照組三支都有;另一個外掛的開場 hook 也一起被跳過——讓位會連別人的 hook 一起擋,要用時必須只針對 lumos 自己。
4. 記憶:系統提示裡名為 `memory` 的那節(12,835 字)只有自動記憶的使用說明,字串比對不到 MEMORY.md 的索引標題與最後一條;MEMORY.md 全文在 `prompt.context` 的 `claudeMd` 區塊(跟 CLAUDE.md 一起),比對得到最後一條。要改記憶內容應掛 `prompt.context`。
5. 互動會談:熱重載啟用後,記到 `isInteractive: true`、`surface: terminal` 與使用者回合。
6. 工具失敗:`ls` 不存在的路徑被記成 `isError: true`。
7. 長期安裝:本機市集 → 隔離設定目錄 `claude plugin marketplace add` + `claude plugin install` → 狀態 enabled;不帶 `--plugin-dir` 跑 `claude -p` 照樣載入(那場因隔離目錄沒登入,回合以 `error` 結束,但 mod 在那之前已載入並記錄)。使用者全域設定沒被改到(grep 確認)。
8. 順帶:-p 下模型派完背景子代理就結束回合,引擎之後把完成通知當新回合送回,整場正常收尾(只跑一場,不推翻自主迭代迴圈那篇系統筆記記的舊事件)。

## 起動成本(同日本機量)

- Python 空跑 0.02–0.03 秒;改檔前 hook 收到不相干的工具直接退出約 0.07 秒;叫一次 lumos 只印說明約 0.4–0.6 秒。各三次。

## 沒驗的

- mod 的穩定度承諾:型別檔與說明都沒找到。
- 長時間會談下的寫入量與效能;Windows、Linux。

REVISIT:2026-12-05 重跑最小實驗,確認 mod 事件名與欄位沒變
