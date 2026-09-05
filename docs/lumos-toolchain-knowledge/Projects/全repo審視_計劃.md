---
type: project
status: doing
created: 2026-09-05
updated: 2026-09-05
tags:
  - type/project
  - status/doing
---
# 全repo審視_計劃

> 白話:2026-09-05 夜到 09-06,派 16 個不同鏡頭的乾淨 agent 把整個 repo 掃一遍找可優化處,每條再派兩個反方(一個查事實、一個查圖譜先例與家規)去推翻,活下來的才算數。這篇記進度、活下來的清單、以及還沒做完的部分怎麼接。★這輪只到「找出來並核對過」為止,一件都還沒改★

## 怎麼跑的

- **16 個鏡頭**:CLI 結構、圖譜資料模型與檢索、git 端強制力、AI 助理的 hooks、審查迴圈操作成本、排程自動化可靠性、測試套件、安裝發佈、文件與上手、skills 檔、安全健壯、成本可觀測、對照世界解、新手第一次用、能不能少、操作體感。每席上限 10 條、必附 file:line 逐字引句、必寫「世界上同類問題怎麼解、在零依賴/別治理過頭/誠實天花板/maker≠checker 四條家規下能不能借」。
- **每條兩個反方**:A 打開引用的行核對事實、實跑宣稱的行為;B 去圖譜查這個提案是不是早就明文否決過、違不違反家規。任一方推翻就出局。
- **卷證**:`governance/review-reports/repo-audit-2026-09-06/findings.json`(全文)與 `findings.md`(人可讀,依活下來/被推翻/未核對分段)。工作流可續跑:runId `wf_6a5f3932-9e1`,腳本在 session 的 workflows/scripts/ 下。

## 結果(2026-09-06,核對全數完成)

| 項目 | 數 |
|---|---|
| 16 席找出的原始發現 | 130 |
| 兩位反方都核對完 | 130(全數) |
| 活下來 | 91 |
| 被反方推翻 | 39 |
| 合併成幾群(=幾件可獨立交付的事) | 50 |

活下來的價值分佈:high 31 / med 52 / low 8。
**中斷史**:第一次撞 session 上限、第二次撞 Fable 額度、第三次最後的合成席斷線;工作流可續跑(runId `wf_6a5f3932-9e1`),完成的吃快取。去重席也失敗過——130 條全文超過單次 64k 輸出上限,改成核對後只輸出分群 id。

## 分群清單(依 價值→工量→風險 排,還沒裁要不要做)

| # | 一件事 | 編號 | 價值 | 工/險 |
|---|---|---|---|---|
| 1 | doctor 收尾行「0 issues」蓋掉同畫面的軟提醒 | F06、F15、F45、F100、F127 | high | S/low |
| 2 | 公開 repo 沒有 LICENSE | F62、F66、F104 | high | S/low |
| 3 | 版本發布線(release 分支/tag/CHANGELOG)裁定後零落地 | F58、F72、F86、F99 | high | S/low |
| 4 | 頂層 --help 說明段是凍結的舊 docstring、只列 10 支 | F01、F108 | high | S/low |
| 5 | KEY 行沒有順序慣例而 context --brief 取前兩行 | F11 | high | S/low |
| 6 | pre-commit delguard 掃描 15 秒超時降級 | F18 | high | S/low |
| 7 | pre-push 閘序與逃生口(便宜閘排後面、只有 --no-verify) | F19、F25 | high | S/low |
| 8 | 派工鏡頭超時不留快取與 hook 內外層逾時無單一來源 | F27、F28 | high | S/low |
| 9 | 派工單無 schema 與處置閘留痕重複灌水 | F35、F37 | high | S/low |
| 10 | 席報告收貨正規化沒有指令、臨場腳本會誤填 clean | F38、F124 | high | S/low |
| 11 | 每日 wrapper 沒有死人開關也沒有整跑鎖 | F43、F46 | high | S/low |
| 12 | 暫停自主迴圈連帶把週期觀測任務全關掉 | F44、F91 | high | S/low |
| 13 | ONBOARDING 教的入口與旗標不是現況 | F64、F67、F107 | high | S/low |
| 14 | 全域 SessionStart hook 執行被打開 repo 自己的程式碼 | F85 | high | S/low |
| 15 | 成本帳:覆蓋率、單位不通、沒有一頁總帳 | F93、F94、F96 | high | S/low |
| 16 | 全套測試跑太久:沒有分片並行、fail-fast、順序探針 | F52、F53、F56 | high | S/med |
| 17 | 測試污染真機:暫存目錄殘骸與真 HOME 改寫 | F48、F49 | high | S/med |
| 18 | 假綠形態:偽裝成通過的 skip 與走不到的被測分支 | F50、F51 | high | S/med |
| 19 | lumos update / bootstrap 把全域 hook 倒退、帳檔擋更新 | F59、F61 | high | S/med |
| 20 | 五支 Claude hook 執行沒有落盤帳 | F30 | high | M/low |
| 21 | 一輪審查的收貨記帳沒有任何指令串起來 | F40、F125 | high | M/low |
| 22 | 快速上手沒有安裝驗收也沒有教學路徑 | F68 | high | M/low |
| 23 | Check E4 連鎖提醒 nodes=[] 進不了空轉偵測與升級鏈 | F118 | med | S/low |
| 24 | CLI 版本身分:沒有 --version、LUMOS_VERSION 從未 bump | F60、F109 | med | S/low |
| 25 | argparse help 字串仍帶內部代號 | F02、F71 | med | S/low |
| 26 | 節點找不到時印成「決策沒地方掛」 | F03、F111 | med | S/low |
| 27 | 找不到圖譜與 argparse 用法錯的進場訊息 | F04、F110 | med | S/low |
| 28 | 退出碼逐命令各自裁、沒有 CLI 級的表 | F05 | med | S/low |
| 29 | frontmatter 欄位 schema 沒有機械守衛(打錯鍵、必填空欄) | F13、F14 | med | S/low |
| 30 | 測試 runner 靜默吞未知旗標改跑全套 | F54、F128 | med | S/low |
| 31 | git hook 的硬擋與 fail-open 放行零留痕 | F21、F95 | med | S/low |
| 32 | hooksPath 指向樹內、錨點只錨清單內三支 | F24 | med | S/low |
| 33 | Stop hook 死分支與已撤 hook 的 423 行殘骸 | F29、F34 | med | S/low |
| 34 | bypass 模式下 Stop block 落地已有實證可收窄風險 | F33 | med | S/low |
| 35 | impact-hook 把圖譜自由文字逐字注入主 session | F31 | med | S/low |
| 36 | 治理資料體積無守衛:Codex stderr 卷證與 jsonl 帳本 | F39、F47 | med | S/low |
| 37 | Windows 入口 get.ps1 停在 06-26 兩步版 | F63 | med | S/low |
| 38 | 文件裡的指令與旗標沒有存在性守衛(只驗命令總數) | F84、F105 | med | S/low |
| 39 | README 邊界句與 repo 內三份技術棧 skill 打架 | F70、F79 | med | S/low |
| 40 | docs/methodology 三份文件沒有任何入口且自相矛盾 | F69 | med | S/low |
| 41 | skill 頭版偏 Claude 主語、Codex 對照號稱單源實為多份 | F78、F83 | med | S/low |
| 42 | skill 文件內容過期與速查表欄位錯位 | F80、F112 | med | S/low |
| 43 | 同型修法只修一處:symlink 信任檢查與固定 /tmp 路徑 | F87、F88 | med | S/low |
| 44 | 受波及合約測試閘:圖譜寫的與 hook 實作不符 | F22 | med | S/med |
| 45 | 12 個讀取類命令沒有 --json | F07 | med | M/low |
| 46 | 測試單檔的重複 helper 層推高編輯成本 | F55 | med | M/low |
| 47 | 無空白中文查詢 0 筆不自動退成 bigram | F16 | med | M/med |
| 48 | repo 根目錄的測試殘留雜檔 lumos-calls.jsonl | F09、F75 | low | S/low |
| 49 | 紀律範本注入每個消費端卻寫著客戶專案名 | F74 | low | S/low |
| 50 | usage-log 零程式讀者、退場條件掃不到 | F98 | low | S/low |

## (舊)中途進度快照

| 項目 | 數 |
|---|---|
| 16 席找出的原始發現 | 130 |
| 兩位反方都核對完 | 92 |
| 活下來 | 71 |
| 被反方推翻 | 21 |
| 還沒核對(額度中斷) | 38 |

- 活下來的價值分佈:high 26 / med 38 / low 7。
- **中斷原因**:第一次跑撞 session 上限,第二次撞 Fable 模型額度;已切 Opus 續跑。去重席也失敗過一次——130 條全文超過單次 64k 輸出上限,改成「核對後只輸出分群 id」。
- **還沒做**:剩下 38 條的核對、分群、合成(排優先序、寫 PRIOR-ART、找漏)。續跑用同一個 runId,已完成的會吃快取不重跑。

## 活下來且判定高價值的(26 條)

| 編號 | 鏡頭 | 一句話 | 工/險 |
|---|---|---|---|
| F51 | test-suite | 第④型「現場走不到被測分支」已撞 8 次(累計 17 次假綠),仍只有散文前置斷言、沒有機械的「到達」檢查 | L/med |
| F28 | ai-hooks | 五支 hook 的內層 subprocess 逾時對外層天花板的關係沒有單一來源、沒有測試,四支違反自家「外>內」規則 | M/low |
| F30 | ai-hooks | hook 執行沒有任何落盤帳:成功/超時/rc≠0 只有 LUMOS_HOOK_DEBUG 才看得到,量測靠 grep 逐字稿 | M/low |
| F68 | docs-onboarding | 快速上手在「重啟 session」就結束:沒有「怎麼確認裝好了」,也沒有一條 30 分鐘走完核心迴圈的教學 | M/low |
| F58 | install-distribution | 版本發布流程計劃審完 38 天零執行,也沒有回頭條件——對外通道仍是 main 開發線 | M/low |
| F38 | review-loops | 收貨正規化(quote:→引句:「」、file:→反引號、補 severity 行)仍是「每個迴圈臨場寫一支腳本」的 SOP,不是 lumos 指令;今天又 | M/low |
| F40 | review-loops | 一輪標準級代碼審要手敲約 25 條指令(3 席),凍結→收貨→記帳→問閘→凍結判定沒有任何一條 lumos 指令串起來;圖譜的界線只禁「lumos 自己派  | M/low |
| F49 | test-suite | 「假 HOME 是最低門檻」只寫在事故筆記,runner 沒守:兩支 install 測試每輪都改寫真機 ~/.claude 與 ~/.local/bin | M/med |
| F53 | test-suite | 全套 8 分鐘純串行:527 次 subprocess 大多在等 IO,卻沒有分片並行入口 | M/med |
| F27 | ai-hooks | 派工鏡頭超時後不留快取,同一範圍的下一席再燒 45 秒再放空 | S/low |
| F01 | cli-structure | 頂層 --help 的說明段是 2026-06 凍結的模組 docstring:只列 10/66 個子命令、寫「四檢查」(現 22 個 Check),所以命 | S/low |
| F91 | cost-observability | 暫停自主迴圈的同時,把週報、空轉提醒(nags)、REVISIT 14 天升級鏈、連敗 LINE 告警全部一起關掉了——監看跟被監看的東西同命 | S/low |
| F66 | docs-onboarding | 公開 repo 沒有 LICENSE:curl|bash 叫人裝,法律上卻沒授權任何人使用 | S/low |
| F67 | docs-onboarding | ONBOARDING 四處寫的不是現況(已撤層、死旗標、無 Codex),且沒任何測試守它;README §6 說七步列五條 | S/low |
| F18 | enforcement-git-hooks | pre-commit 的 delguard 掃描 15 秒超時是自己造成的:git grep -w 掃到多 MB 的治理 .err/.jsonl 檔 | S/low |
| F19 | enforcement-git-hooks | pre-push 把 8 分鐘全套測試排在最前面,便宜的閘(pitfalls/code-loop 幾秒、doctor 1.2 秒)排在後面——被擋時全套白跑 | S/low |
| F43 | governance-automation | 每日 wrapper 沒有死人開關:死了整天沒人知道,退出碼永遠 0 | S/low |
| F44 | governance-automation | 暫停自主迴圈的開關順手把五支週期任務全關了,圖譜卻寫「便宜段照跑」 | S/low |
| F11 | graph-model-retrieval | KEY 行沒有順序慣例,`context --brief` 卻取「首兩行」——design-loop 最新一條(08-30)埋在第 20 條 | S/low |
| F15 | graph-model-retrieval | doctor 尾行「✓ 圖譜健康 — 0 issues」與同一次輸出的 7 段 ⚠(含 5 件回訪逾期、5 份驗證引翻案決策)並存 | S/low |
| F59 | install-distribution | `lumos update` 把全域 ~/.claude/hooks 同步成「更新前」的 vendored 版;bootstrap 在舊專案裡會把剛裝好的全 | S/low |
| F62 | install-distribution | 公開 repo 沒有 LICENSE——法律預設是 all rights reserved,所有消費端(含公司專案)其實沒有使用授權 | S/low |
| F35 | review-loops | 派工單 rN-dispatch.json 沒有機械 schema,席位對帳只讀 auditor 鍵——09-03 起 8 個迴圈全席被判 unknown,喊 | S/low |
| F85 | security-robustness | 全域 SessionStart hook 直接執行「被打開那個 repo」自己的 scripts/lumos——clone 一個陌生 repo、開 Clau | S/low |
| F86 | security-robustness | curl|bash 安裝鏈釘在 main HEAD、無 release 線、無 tag:2026-07-30 已裁的「release 分支對外線」五週未落地 | S/low |
| F52 | test-suite | 沒有 fail-fast 與 failed-first:pre-push 就算第一支就紅也得等滿 8 分鐘,註解還寫「~32s」 | S/low |

## 我自己另外抽查確認的四條(不靠 agent)

- repo 根目錄有一支 5 位元組的測試殘骸(內容是字面空陣列),跟著一個自主迴圈的 commit 被順手提交。
- **沒有 LICENSE**,git 全歷史從沒有過。公開 repo 叫人 `curl | bash` 裝,法律預設是保留所有權利,消費端(含公司專案)其實沒有使用授權。
- 治理帳本 3.6MB、24262 行,每次讀整檔載入。
- 每日治理腳本永遠回傳 0,死了沒人知道(昨天實際發生過)。
- 反過來,「測試殘骸 33 萬個暫存目錄」那條當下數到 0 個,對不上;等反方核對。

## 界線

- 這輪是「找」與「核對」,**不是裁定要做什麼**。哪些真要做、順序、要不要走設計審,等合成席出來再裁。
- 130 條裡有相當比例是同一件事被不同鏡頭各講一次(例如沒有 LICENSE 被三個鏡頭各提一次),分群還沒做,所以「71 條」不等於「71 件工作」。
- 各席的「世界解」是它自己寫的,只有反方 B 抽查過對應得對不對,沒有逐條查證來源真實性。

