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

## 目前進度(2026-09-06)

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

