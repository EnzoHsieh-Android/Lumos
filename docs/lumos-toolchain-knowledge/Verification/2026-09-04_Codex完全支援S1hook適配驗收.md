---
type: verification
status: pass
date: 2026-09-04
valid_under: codex-cli 0.144.1、macOS、隔離 clone+HOME+CODEX_HOME,hook 以 --dangerously-bypass-hook-trust 跑(只限驗收環境);Codex 逐字稿 fixture 版本 0.144.1
revalidate_when: codex 改版(enforcement codex-cli 列≠0.144.1)或逐字稿型別變(check-graph-sync 會印「格式未知,略過」就是訊號);REVISIT:2026-09-25 互動模式一併驗 SubagentStart 領席
tags:
  - type/verification
  - status/pass
plan_refs:
  - "[[Projects/Codex完全支援_計劃]]"
decision_refs_ai:
  - "Projects/Codex完全支援_計劃.md#d5"
---
# 2026-09-04_Codex完全支援S1hook適配驗收

> 白話:第一階段要證明三件事在真的 Codex 底下成立——改檔前有人把合約推到眼前(apply_patch 也吃得到)、派子代理時它開場拿得到圖譜鏡頭(不靠改派工詞)、收工時 Codex 逐字稿讀得懂、改了碼沒寫筆記會被唸。全部在隔離的 clone、HOME、CODEX_HOME 裡做,沒碰真機設定。

## 環境

- 本機 codex-cli 0.144.1;clone 本 repo 到 scratchpad `s1accept/repo`(遠端名 Lumos,主線 Lumos/main),先 commit 一筆「碰帶合約的檔」讓 `Lumos/main..HEAD` 有固定席(8 篇);工作樹換成本機未 commit 的 S1 碼。
- `HOME=s1accept/home lumos install --force` 後把隔離 hooks.json 的五條命令包一層落 stdout/stderr 檔(驗收 wrapper,不改產品碼);`codex exec --sandbox workspace-write --dangerously-bypass-hook-trust`(只在此環境帶)。

## 三條驗收

1. **apply_patch → impact-hook 注入**:提示 Codex 用 apply_patch 在 `scripts/merge-claude-settings.py` 尾加一行 → PreToolUse fire 1 次,stdout 是 `hookSpecificOutput.additionalContext` 1030 字,開頭「必看——這 9 篇帶著不能破壞的合約或出過事故:」(含 lumos-cli-lifecycle ★INVARIANT★、hook卸載殘留註冊 事故);Codex 最終回覆自己也貼了那行,證明模型收到。
2. **arm → SubagentStart 領席**:`lumos dispatch-lens --arm Lumos/main..HEAD --seats 1 --repo <clone>` 後派 explorer 子代理 → SubagentStart fire 1 次,stdout additionalContext 首行 `LUMOS-LENS range=Lumos/main..HEAD 第 1/1 席(…)`,其後是固定席清單(bound-tests-gate ★INVARIANT★ 等);子代理原文回報了那一行。
3. **Stop → check-graph-sync 讀 Codex 逐字稿**:第一次真跑 Stop fire 但 stderr 空——查出兩件事:(a)那次 Codex 把 patch 先存 JS 變數再呼叫,原正規式只認直接傳字串;(b)隔離家目錄裡的 hook 副本是修正前的。修正(任何含 Begin Patch 的 JS 字串字面值都解;相對路徑接 session cwd)後,用 wrapper 當場抓下的★真 Stop payload 與那一刻的逐字稿(35 行,含 patch)★餵修正後的副本 → 印出「提醒:這一輪改了 1 個程式碼檔,但知識筆記沒有跟著動: • scripts/merge-claude-settings.py」。★這條是「真 payload+真逐字稿+修正後 hook」的機械重現,不是再跑一次 codex exec;而且只證明當時那一份逐字稿的形狀★——代碼審 r1 外家席用同日 61 份逐字稿對出兩個沒覆蓋的形狀(shell 呼叫一半寫 `{cmd:` 沒引號;輪次邊界另有 `response_item/message role=user` 型),已折入 reader 與 fixture,但 0.144.1 還有沒有第三種形狀沒人保證;守衛=版本不在 fixture 表就略過並印一行。
4. 五支 hook 帶 `--harness codex` 全程無 Traceback(stderr 檔逐一 grep)。

## 單元/整合測試

- `-k codex_s1` 26 條(patch 標頭四種、8 檔取前 5、main 多檔合併一個輸出、arm/claim/exhaust/expired/disarm/status、5 並發 3 席恰 3 ok、hook SubagentStart 分支、Codex 逐字稿 exec/apply_patch/版本未知略過、Claude 逐字稿照舊)全綠;既有 impact-hook 81 條、dispatch-lens 42 條全綠。

## 代碼審後補驗(同日)

- r1 三席 14 條折入後:`-k codex_s1` 31、`-k impact_hook` 81、`-k dispatch_lens` 42、`-k graph_sync` 5 全綠;無引號 `{cmd:` 形用真逐字稿重驗抽到;單檔 timeout 用 mock 量回 30。

## 沒驗的

- 互動模式(REVISIT 2026-09-25)。
- Codex 改版後逐字稿型別(守衛=版本不在 fixture 就略過並印一行,不猜);同版本內其他沒見過的 JS 寫法(目前 fixture 涵蓋:有/無引號 cmd、換行縮排、直接傳字串與變數型 patch、兩種輪次邊界)。
- 同 repo 同窗口無關子代理搶席的頻率(計劃承認的界線;REVISIT 2026-10-04 抽看)。

## 結論

S1 三條驗收全過(第三條為真 payload 機械重現);S1 進場問題「Edit/Write 是否獨立工具」答:別名。
