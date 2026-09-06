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

## 合成結果:23 個主題(2026-09-06)

50 群再合成成 23 個「可獨立交付的改動批」,依 價值高→工量小→風險低 排序。標「★要」的是新增治理層/改判準/新指令語意,動手前要走設計審。

| # | 主題 | 編號 | 工量 | 設計審 |
|---|---|---|---|---|
| 1 | 公開 repo 沒有授權條款 | F62、F66、F104 | S | 否 |
| 2 | pre-commit 刪除守衛半盲跑:15 秒逾時是自己造成的 | F18 | S | 否 |
| 3 | doctor 收尾行說 0 issues,同一畫面上方有七段警告 | F06、F15、F45、F100、F127 | S | 否 |
| 4 | 暫停自主迴圈把五段週期觀測一起關掉了 | F44、F91 | S | 否 |
| 5 | 更新通道的兩個真 bug:全域 hook 被倒退、來源被自己弄髒 | F59、F61 | S | 否 |
| 6 | hook 面的信任邊界:執行誰的碼、寫哪個目錄、注入什麼字 | F85、F87、F88、F24、F31 | M | 否 |
| 7 | 對外發布線落地(release 分支、CHANGELOG、--version、Windows 入口) | F58、F72、F86、F99、F60、F109、F63 | M | 否 |
| 8 | 死碼與帳面房務批 | F09、F75、F29、F34、F39、F98、F33 | S | 否 |
| 9 | CLI 進場面:說明段、錯誤訊息、退出碼、brief 選行 | F01、F108、F02、F71、F03、F111、F04、F110、F05、F11、F07 | M | 否 |
| 10 | 活文件對齊現況,再補存在性守衛 | F64、F67、F107、F69、F70、F79、F74、F112、F80、F84、F105 | M | 否 |
| 11 | test_lumos.py 地基:真機隔離與重複收攏 | F48、F49、F55 | M | 否 |
| 12 | 推送閘序與測試 runner 的五個旗標 | F19、F52、F53、F54、F128、F56 | M | 否 |
| 13 | 假綠:把偽裝成通過的 skip 改走 SKIP 通道 | F50、F51 | S | 否 |
| 14 | hook 逾時:預算單一來源,超時不要白燒 | F27、F28 | M | 否 |
| 15 | skill 頭版單源化:兩家對照只留一份 | F78、F83 | S | 否 |
| 16 | frontmatter 欄位守衛:打錯的鍵與空的必填欄 | F13、F14 | S | 否 |
| 17 | 受波及合約測試閘到底什麼時候跑 | F22 | S | ★要 |
| 18 | 每日治理 wrapper:死了要有人知道、不要兩份同跑、帳本要有門檻 | F43、F46、F47 | M | ★要 |
| 19 | enforcement 可觀測性:擋了幾次、放行幾次、跳過幾次、hook 有沒有跑 | F21、F95、F25、F30 | M | ★要 |
| 20 | 審查收貨線變成指令(正規化、三道機械檢查、派工單 schema) | F38、F124、F40、F125、F35、F37 | M | ★要 |
| 21 | 成本帳:機器取值、一頁總帳、單位可比 | F93、F94、F96 | M | ★要 |
| 22 | 無空白中文查詢的字對回退 | F16 | M | ★要 |
| 23 | 連鎖提醒的升級鏈接電 | F118 | S | 否 |

## 一小時內可做、不需審的(12 件)

1. git rm 根目錄的 lumos-calls.jsonl(5 bytes、無人讀無人寫,開發期手滑被批次 git add 進去);不必加 .gitignore、不必加「repo 根無新檔」斷言——沙箱隔離已經成立,那是守一條不存在的路徑(F09/F75)
2. governance/review-reports/**/*.err 與 *-stderr.txt 加進 .gitignore 並 git rm --cached(20 份、13.5MB、佔追蹤卷證四成),歷史不 rewrite;之後收貨用 codex exec --output-last-message(0.153.2 已實測有此旗標)(F39)
3. 刪掉 ONBOARDING.md:54 的 ./install.sh --copy 那一行(旗標 2026-06-26 就拆了、現在被靜默吞掉),連同 skills/lumos-project-notes/reference.md:1228 與 slim 鏡像的 --copy 剪貼簿條一起刪(F64/F107/F112)
4. install.sh 的 exec 加 "$@"——未知旗標會直接撞上 lumos install 的 argparse 吐 rc2,不必另外印提醒(F107)
5. usage-log 的退場條件從 HTML 註解改成獨立一行 REVISIT:2026-11-19(doctor 的到期掃描只認獨立 REVISIT 行,寫在註解裡等於沒寫)(F98)
6. Projects/版本發布流程_計劃 加一行 REVISIT:2026-10-05;status 要動只能改 todo——project 型的合法值裡沒有 deferred,寫下去會靜默變成 lumos query 篩不到的狀態(F72/F99)
7. commands/02-動手前算波及.md、05-設計審查迴圈.md、06-代碼審與推送.md 九列表格格數補齊——02 那張已經真的錯位,第 10 列的內容掉到第 14 列去了(F80)
8. README.md / README.en.md:346 與 ONBOARDING.md:129 的邊界句加限定詞(專案自己的框架選型不進來;跨專案通用的 *-idioms 是工具鏈的一部分);只改中文版會留下同款漂移(F70/F79)
9. README §3a/§3b 與 ONBOARDING TL;DR 各補一行「裝好了嗎:lumos enforcement」——精簡版的必要內容規格早就要求「怎麼確認裝好」,主 README 連段落都沒有(F68 的 A 半)
10. scripts/hooks/pre-push:64 註解的「~32s」改成實測數字,開跑訊息順手印預估耗時(那個數字是 2026-07-07、183 支測試時代的)(F52)
11. docs/methodology 三份從 README 的〈邊界與延伸閱讀〉與 ARCHITECTURE 頭部各連一行——最白話、本週還在改的〈全景圖〉目前從任何入口都走不到(F69 的一半)
12. 把 Python 版本宣告從 ≥3.8 改成與現況一致的 ≥3.9(scripts/lumos 有四處 removeprefix/removesuffix,那是 3.9 才有的);純事實訂正不需審,要不要再往上調才需要人裁(F65 的提案被推翻,但這個事實成立)

## 可以拿掉或合併的(9 件)

- 刪 scripts/hooks/claude/verification-rot-check.py 全本(423 行),從 _RETIRED_STUB_CLAUDE_HOOKS 移到 _RETIRED_CLAUDE_HOOKS;同 commit 結案 Systems/verification-rot-eval(status: planned、從未實作,是這支檔唯一的真引用,不結案會留下懸空相依);test_lumos.py 第 5 段寫死該檔名的斷言要改成合成名字,不要用刪測試換綠(F34)
- 刪 check-graph-sync.py 的 _impact_missing 分支與 emit_queue_patrol——exit 0 的 stderr 模型看不到(官方文件與 09-05 決策一致),.rot-queue.jsonl 的唯一寫者已撤、本機根本沒有這個檔;掛回 Issues/只退場不痛的機制 d1(那次拆 L3 漏拆的殘跡),Systems/graph-sync-coverage 的「三個點名位置」改兩處(F29)
- 刪 lumos --help 開頭 docstring 那份重複的 10 支子命令清單——argparse 下面已經全列一次,而且那份較舊、還夾內部代號(F01/F108)
- 四處「決策沒地方掛」只留 decision-add/supersede/reindex 那一處;讀側(links/backlinks/context/map/show/decisions/contracts)與寫側(set/append/remove)各換成對得上的句子(F03/F111)
- 兩份 SKILL.md 頭版各抄的那段 Codex 版本事實刪掉、只留一句指標——現在號稱「單源=templates.md §3 ④」實際是三份(F78)
- skills/lumos-project-notes/reference.md 的〈注意事項〉把 obsidian CLI 時代的六條(1、2、3、11、12、13:name=/path=/file= 語法、property:set、obsidian vaults、--copy 剪貼簿、「Obsidian 必須執行中」)刪掉,或搬進上方 Obsidian 節並標「舊 CLI 專用,lumos 不適用」——第 13 條與 README「不需要裝 Obsidian」直接打架(F112)
- roster-alerts.log 的重複行只採「尾行相同就跳寫」,不要改寫成 xN 計數(牴觸該檔 valid_under 宣告的 append-only);而且不單獨開工,併 2026-11-26 覆核一起裁(F37)
- 合併重複稿:F62/F66/F104(LICENSE)、F06/F15/F45/F100/F127(doctor 收尾行)、F09/F75(根目錄雜檔)、F38/F124(收貨正規化)、F40/F125(收貨串接)、F44/F91(週期任務隨派工停擺)、F64/F107(ONBOARDING --copy)——這七組是同一批稿子在不同鏡頭各撞一次,合起來是 7 件工作不是 18 件
- F07 的 --json 覆蓋收成一行「已知缺口」寫進 Systems,不排實作:doctor 有 --ci 側通道、合約可經 impact --json 與 query --contract --json 機讀,show 已裁 YAGNI、gov 已裁 v1 不做,真正沒有任何機讀面的只剩 decisions,而且今天沒有任何機器消費端在解析它們

## ★被推翻、明文不做的(25 條)★

這一段跟上面一樣重要:每條都是「有人提過、查證後發現早就裁過或違反家規」。之後有人再提同樣的事,先讀這裡。

- 不要把「每支命令一筆」寫進 docs/.usage-log.jsonl(F08)——主 session 鏡頭利用率 r1 五席(62 條、11 blocker)否決過同一個機制:使用帳無 session、無時區,而且它被 git 追蹤、每回合都寫會讓合併衝突變常態,計劃正文明寫「★本案不動它★」;r2 架構席還補了一刀「那是另一本帳、另一種語意」
- 不要把 search 預設改成 top N 有聲截斷(F17)——07-11 就是這樣做的,同日被 code-loop panel 以 [major] 折回,d2 裁「預設輸出資訊零損失」;一句話層供糧計劃也明文把「search 輸出改版」列為已排除,動它要另案
- 不要把 testmap affected 接到 pre-push 去挑測試(F20)——testmap 自己的計劃〈範圍刀〉寫死「不掛 pre-push、不進 doctor」,08-22 實查結論更直接:粒度是檔案級,答案就是「跑 test_lumos.py」那個 10 分鐘的怪物,接上去等於沒接;要有價值得先做到函式級,那是新工作不是接線
- 不要把 --no-verify 繞過補記成治理帳事件(F23)——08-21 已經落地成另一種痕跡形態(CI 紅燈,ci-wait/.ci-log 收得到),當時的理由是「CI 無法回寫本機帳」;要重提得先推翻這句
- 不要用 gh api 去查 branch protection 補進 enforcement(F26)——計劃〈誠實界線〉明文「離線可跑優先,不接 gh API」,而 enforcement 現在已經掛進每個 SessionStart 入口 hook(3 秒預算,r1 才把 20 秒降下來),塞一個網路呼叫進入場路徑會拖慢也會在離線時變成假訊號
- 不要把設計審鏡頭改成從主線讀節點正文(F32)——design-loop 從第一天就明文「防誤不防惡」,設計審的處置結果沒有任何機械消費端(沒過不擋任何東西),在一個宣告不防惡的層疊防惡儀式,而且編排者=作者本來就能直接寫進派工詞
- 不要去改 t_ci_wait 那個 15 秒輪詢常數(F57)——實測 132 秒有 91% 是 --grace 預設 30 秒的睡眠,而 --grace 早就是 CLI 參數、同一支測試別的案例已經在用;改那行對耗時的貢獻不到 1%
- 不要為 Python ≥3.8 加 CI matrix 或啟動版本檢查(F65)——前提已死:HEAD 自己就用了 3.9 才有的 removeprefix/removesuffix,而且那兩處正是 CLAUDE.md 表格直接教的主線指令;要做的是先把宣告訂到與現況一致(見 quick win)
- 不要為 SKILL.md 頭版加 7k bytes 硬上限(F76),也不要把日期與實測故事整批從頭版清掉(F77)——7k 在裁定當天就有三份破了(裁定者是在那個狀態下驗收的),而剪枝鐵則是「只准壓縮措辭與搬家,不得遺失任何規則」,日期常常承載語意(「自某日起改成 X」)
- 不要為 LINE token 改走 stdin 或檔案(F89)——pitfalls-code-loop d5 明文排除安全缺陷型鏡頭的對抗威脅模型(單人私有機、非對抗),同機沒有第二個人可以 ps
- 不要給自主迴圈加單輪或每週成本上限(F92)——自主迴圈修理計劃〈不做(邊界)〉明寫「不給 orchestrator 加 turn/成本上限」,那輪 $78 是正常跑滿六輪(6/6 canary caught、49 條折入);而 09-05 暫停派工已經是更強的替代
- 不要為治理帳做分檔歸檔或催 git gc(F97)——把 650 個歷史版本單獨打包實測只有 245KB(git 的 delta 壓縮已經解掉這題),loose object 也還沒到 gc.auto 的門檻;要裝的只有門檻觸發器(已收進主題 18)
- 不要把 tier 的四類 regex 做成消費專案可宣告的設定(F101)——機制陳述本身是錯的:PITFALL_CLASSES 不產出 tier,tier 來自另一張 diff 形態表,改那張表不會改變任何專案的風險分級
- 不要把 guard kill 排進每日治理(F102)——全圖只有一條 kill_recipes,「抽樣輪替」在 N=1 時就是每天跑同一條,證明的是這支程式今天還跑得動(工具煙測),不是合約的測試有牙;而且它的協議 08-14 已停用
- 不要為 status: doing 加老化守衛(F106)——撞新機制準入三問與 08-21 裁定,而且它引為重啟條件的那句「反方向沒實例」講的是另一件事(狀態表說已完成但節點還在 doing),至今仍未觸發;要接電就寫 REVISIT 行,那是既有機制
- 不要刪 canary second 與 loop canary-stats(F116)——d5 同一句話同時裁了「停用」與「不拆」:抽樣分權停用、工具封存不拆、歷史 caught/missed 帳唯讀可回放;skill 標 ⛔ 封存正是忠實執行,不是不一致
- 不要把治理帳改成只寫狀態轉換、不重寫同一批 warned(F117)——那些重複行正是 gov --nags 判「還在喊」的燃料(它比對 last_warned_ts 與 last_doctor_run_ts),改了那張空轉清單會靜默歸零,而空轉偵測是 REVISIT 升級鏈唯一的偵測器
- 不要拿 slim 的 26 支當 lumos --help 的「日常核心」(F121)——那 26 支的分界原則是「只想讀的新人」,impact 是被查證屬於日常維護、卻因為那個一次性交接情境刻意砍掉的;拿它當日常核心是把裁定的理由倒過來用
- 不要為 loop next 印的舊 caught|missed 記帳範本開案(F123)——08-14 起 skill 三處與驗證筆記明文「照跳過,工具封存未拆」,已歸類為已知殘留摩擦、非缺陷
- 不要讓 anchor approve 的 note 自動機械數測試數(F130)——實測 44 筆只有 5 筆帶測試數宣稱(不是「每筆」),而且那 5 筆數的是函式內的案例與斷言,不是新增的 t_ 函式,機械數會數錯單位
- 不要重提「消費端要能 hook-local 覆寫某道閘」與 rebase 偵測(F103)——.lumos/config.json 的宣告式開關已經是使用者親裁的正規出口(沒宣告 ci 區塊就完全靜默),LUMOS_SKIP 只收窄在源 repo 的 pre-push 四道閘
- 不要重提 MOC 對帳(F10)——08-26 地基盤點已裁「列觀察,不立案」(策展屬人工);但同批裡「Systems/Issues 沒人連到也沒人提醒」那半仍是還沒動手的小案,別跟著一起放掉
- 不要為 KEY 行加長度或條數上限(F12)——閥只會打到維護最勤的六個 hub(design-loop 29 條、lumos-cli-lifecycle 19 條…),而帶日期的增量 KEY 是家規明文鼓勵、且是新舊打架時的裁決優先方;守衛叫在被鼓勵的行為上就從證據退化成儀式
- 不要用 dispatch.json 的 dispatched_at 或報告 mtime 自動算 wallclock(F41)——126 份派工單只有 1 份有那個鍵(還是今天某位編排者自己加的),而 mtime 會被收貨正規化重寫、被 git checkout 重設,量到的不是席位耗時
- 不要把 code-loop pass 留痕綁審查編號或 range(F42)——檢核收緊五件 S3 就是這件事,三輪 panel 未收斂,結構性 blocker 是「range 符號名與 sha 永不相等、amend 改 HEAD 即失效、首推/多 ref/rebase 各自不同源」,編排者當時的建議是重設計而不是重做一次

## 這 16 個鏡頭沒覆蓋到的(13 條,完整性批評席指出)

- 防竄改只罩六個檔,沒人問為什麼:governance/anchor-baseline.json 的 anchors 只有 test_lumos.py、test_autonomous_loop.py、三支 git hook、dispatch-lens-hook.py——19k 行的主程式 scripts/lumos 本體不在裡面,另外四支 Claude hook(check-graph-sync.py 這支會擋停的、impact-hook.py、ci-status-hook.py、lumos-entry-hook.py)也不在,merge-claude-settings.py、slim-gen.py、以及 launchd 每天執行的 governance/daily-governance.sh 全都不在。16 個鏡頭只問了「hook 目錄新增檔沒人看」(F24),沒有一個問「這條防線罩的範圍是怎麼決定的、為什麼主程式不在內」
- 圖譜內容本身會不會腐化,今天沒有任何機制也沒有任何鏡頭在問:doctor 驗的全是機械面(雙向連結、路徑存在、欄位列舉),verification-rot-check 08-21 撤除之後,它的取代品 docs/lumos-toolchain-knowledge/Systems/verification-rot-eval.md 至今是 status: planned 的 design-only 稿(自陳「scripts/rot-eval/ 與 lumos 子命令皆未落地」)。425 篇筆記「說的還是不是真的」沒有抽樣對帳,而整套方法論的前提就是圖譜可信——這是最大的那個洞,而它剛好沒被分配給任何鏡頭
- 檢索這把尺多久沒校過沒人問:governance/eval/retrieval_eval.py 的 goldset snapshot 停在 7fd214f、最後一次 eval 是 2026-08-31,而跑它的 run_exam 正好住在被暫停的 autonomous-loop.sh 裡(主題 4)。語料從那時到現在又長了,沒有鏡頭問「30 題還代表現況嗎、hook P@8 的綠是哪一天的綠」——檢索是整個「圖譜先行」的入口,尺失準比任何一條 CLI 訊息都貴
- lumos export 產出的 HTML 從 CDN 拉第三方 JS:scripts/lumos:8021 與 :8483 寫死 https://cdn.jsdelivr.net/npm/3d-force-graph,而 scripts/vendor/ 裡躺著本機副本(marked v12.0.2 MIT、3d-force-graph 1.80.0)。沒有鏡頭問這兩份 vendored 第三方碼的授權標示、版本更新路徑、離線可用性與 SRI——而「零依賴」是這個 repo 的招牌,export 又是消費端真的在用的功能(Landmark 的 CI build 會嵌 standalone 圖)
- 消費端的落差沒人審:本機 11 份 vendored scripts/lumos 從 3628 行到 16288 行,最舊兩份(Compass_Kiosk、FrasersKiosk)連 LUMOS_VERSION 這個常數都沒有、也沒有 CLAUDE.md。對「舊 vendored 副本 + 新全域 CLI」這個組合的相容性、升級路徑與失效模式,沒有任何鏡頭、測試或文件——而 install-distribution 鏡頭問的是安裝當下,不是裝完之後那幾個月
- 備份與復原完全沒出現在 16 個鏡頭裡:圖譜 425 篇加六本帳只活在這一台 mac 的 clone 與 GitHub main 上,帳本是 append-only 但沒有任何校驗或簽章(replay 的 sha 閉包只驗自己凍結的那批)。「機器壞了」「誰誤刪 docs/」「git 歷史被 force push」的復原路徑,一句都沒有
- fail-open 沒有總量清單:scripts/lumos 有 104 處 except Exception,其中 59 處是裸 except Exception:。各鏡頭只挑自己碰到的幾條講(hook 的、pitfalls 的、config 解析的),沒有人做一份「哪些是刻意 fail-open、哪些是吞掉了該讓人知道的錯」的盤點——而這個 repo 的核心主張就是「降級要留痕」
- CI 從頭到尾只被當背景板:.github/workflows/ci.yml 只跟 main 的 push 與 PR、沒有 concurrency group(連續推兩次會整套重跑兩遍)、actions 用可移動 tag(@v4/@v5,版本發布計劃 [S7] 早就點名要 pin sha)、也沒有把 scenario_probe/slim-scan/lint-watch 這些自家儀器納入。16 個鏡頭裡沒有一個以 CI 為主體審過一次,它卻是「本機 hook 可繞、這裡是後盾」的那條後盾
- 中文檔名這條坑沒被當一等問題:git 的 quotePath 轉義在這次審查裡就讓一位審查者少數了 17 份 .err(把 3 份講成全部)。圖譜大量節點檔名是中文,而 Windows 消費端(Systems/native-windows-support)、tar/zip 交付、以及各種 grep/ls 統計腳本對中文檔名的行為沒有任何測試或筆記
- hook 注入的持續成本沒人量:cost-observability 問的是席位的 tokens,但每次 Edit/Write 由 impact-hook 灌進主 session 的字數、每次 SessionStart 灌的開場字數、一天累計多少,沒有任何一條發現量過——那是這套工具最頻繁、最不容易被察覺的花費,而且它直接吃掉主 session 的脈絡窗口
- 三支腳本幾乎沒有覆蓋也沒被審:scripts/external-seat.sh(外家席派工,test_lumos.py 全檔只提 1 次)、scripts/fetch-notesmd.sh(3 次)、scripts/graph-rename.sh(8 次)。第一支尤其要緊——它是審查流程的入口,壞了整條迴圈拿回來的證據都不可信,而它既不在 anchor 也幾乎沒有測試
- 「第二個維護者」這個角度沒有鏡頭:new-user-journey 問的是使用者,沒有人以接手者為主體問過一次——單檔 19k 行(拆檔已裁緩辦,而條件正是「等第二維護者」)、沒有 CONTRIBUTING、沒有 LICENSE、bus factor=1,而 CLAUDE.md 自稱主要讀者是下一個 session 的 AI。這是所有「該不該加治理」問題的隱含前提,卻從沒被單獨檢視
- docs/design/ 那四十幾份設計稿與圖譜的關係沒人審:它們被 docs/methodology 引用、但不在 vault 內、不受 doctor 管、沒有 status 欄也沒有 superseded 鏈(檔名日期停在 2026-06/07)。哪幾份已經被實作取代、哪幾份還是現行真相,今天無從判斷——而它們正是新 session 讀 methodology 時會被指過去的地方

## 主題詳情

### #1 公開 repo 沒有授權條款

- **編號**:F62、F66、F104;工量 S
- **為什麼**:這個 repo 是公開的,README 中英兩版都教陌生人 curl|bash 一鍵裝,工具還會把一份 scripts/lumos 複製進每個消費專案(點得出名字的有 mOrangePos、Landmark、KDS 加兩個交付庫)。沒有 LICENSE 的法律預設是「保留所有權利」——真正沒被涵蓋的正是這套東西的核心動作:複製進別人的專案、修改、再散布。同一張圖譜對「借進來的碼」反而嚴格記授權(ClawBench MIT、evidra Apache-2.0 才裁 borrow),入嚴出無。順帶:scripts/vendor/ 裡還躺著兩支別人的 MIT 程式(marked 12.0.2、3d-force-graph 1.80.0),也沒有任何標示。
- **做什麼**:人裁一次(工具鏈常見 MIT 或 Apache-2.0;若刻意不授權就把「刻意」寫進 README 邊界段),放 repo 根 LICENSE、README 中英兩版尾段各一行、slim/ 交付包一併帶,scripts/lumos 檔頭加 SPDX 註解,並在 LICENSE 或 NOTICE 記 vendor 兩支第三方 MIT。三條發現是同一件事,不要當三件做。不要照搬 REUSE 的逐檔表頭(治理過頭)。
- **PRIOR-ART**:最小解在 repo 根目錄一個檔;世界解=choosealicense.com + SPDX identifier + GitHub community profile 清單;裁定=borrow-design(照抄標準條款,只借「一檔+README 一行」那一層)

### #2 pre-commit 刪除守衛半盲跑:15 秒逾時是自己造成的

- **編號**:F18;工量 S
- **為什麼**:帳上有 46% 的 delguard 執行是「掃到逾時就降級放行」——不是守衛太嚴,是它拿著 git grep 去掃三十幾 MB 的審查卷證(.err 單檔 2MB)與 3.6MB 治理帳。守衛在半盲狀態下擋人,而降級記帳這件事本來就是為了讓人看見這種事。實測同一組指令排除 governance/ 與 docs/ 後,35 秒降到 1.3 秒。
- **做什麼**:_DELGUARD_EXCLUDE_DIRS 加 governance/ 與 docs/,同時在 pre-commit 的 should_exclude 補對應 case 行(既有漂移守衛會逐項比對,少一邊就翻紅),預算 15→5 秒;驗收看治理帳 degraded 佔比一週內趨近 0,t_delguard 85 條照跑。不要改成「只掃 code 副檔名」——那會把「全域消失」的語意改掉,是更大的行為變更。
- **PRIOR-ART**:最小解在 git grep 的 pathspec;世界解=pre-commit framework 的 files/exclude/types 過濾、ripgrep 預設略過大檔與二進位;裁定=borrow-design(每支 hook 只看它該看的檔)

### #3 doctor 收尾行說 0 issues,同一畫面上方有七段警告

- **編號**:F06、F15、F45、F100、F127;工量 S
- **為什麼**:今天實跑:上面列了 5 件回訪逾期(最老逾 4 天)、5 份驗證引用被翻案的決策、1 張零判定的連鎖單、1 條失效路徑、沒接 linter,尾行仍印「✓ 圖譜健康 — 0 issues」。人和 AI 都會停在那一行。軟提醒不進 rc 是既有裁定、不該動,但結論行比正文樂觀就是過度宣稱;而且 9/1 起 129 次 doctor 全部 issues=0,這幾件一件都沒被清掉。五條發現(五個鏡頭各撞一次)是同一件事。
- **做什麼**:只改輸出:保留「✓ 圖譜健康 — 0 issues (N 篇)」原樣(四處測試錨綁著「圖譜健康」與「篇)」兩個 token),後面接「· 另有 K 段提醒(回訪逾期 5、驗證引翻案 5;lumos doctor --verbose)」。計數要放在 warn 與 warn_soft 的共用層——Check F 走的是 warn([]) 空列表,只數 warn_soft 會漏它;「含…」子句要從各段既有 head 取,不要手寫第二份文字。rc、軟硬分級、每段 cap 3 全部不動。doctor-run 事件加 soft=/revisit_due= 是可選加項,別當賣點(gates= 已在)。
- **PRIOR-ART**:最小解在 doctor 收尾那一行字串;世界解=ESLint「✖ N problems (E errors, W warnings)」/ tsc / cargo 的錯誤與警告分開計數同行呈現;裁定=borrow-design(警告不改 exit code,但一定出現在最後一行)

### #4 暫停自主迴圈把五段週期觀測一起關掉了

- **編號**:F44、F91;工量 S
- **為什麼**:9/5 決定暫停派工,但 nags 空轉提醒與 14 天升級鏈、回放週跑、情境探針週抽、檢索考卷、backlog 每日衰減這五段都住在同一支 autonomous-loop.sh 裡,一起停了;而三處筆記白紙黑字寫著「便宜的日常段(治理日報、lint-watch、doctor --ci、回放週跑、探針週抽)照跑」,落地當下這句就是假的。監看的東西和被監看的東西同命,REVISIT 到期升級現在沒有出口——這是主題 3 那五件逾期沒人管的下游原因。第一次漏跑是 W37(09-07),backlog 衰減從 09-06 就停。
- **做什麼**:二選一:抽 governance/weekly-jobs.sh 由 wrapper 無條件呼叫(函式原碼搬過去不改),或把 LUMOS_AUTOLOOP_OFF 的判定移進 autonomous-loop.sh 選 gap 之前、wrapper 無條件呼叫它。守衛測試釘「OFF=1 時 bash -x 乾跑仍看得到 run_nags/run_replay/run_probe/run_exam」;三處文件(README審視五修_計劃、Systems/autonomous-iteration-loop、commands/08-自動跑的.md)同步改成實話。
- **PRIOR-ART**:最小解在 bash 函式擺哪一支腳本;世界解=一個排程單元只做一件事(crontab/systemd timer 一 job 一 unit)+ feature toggle 只包最小單元(Fowler, Feature Toggles);裁定=borrow-design(toggle 縮到真正要停的那件事)

### #5 更新通道的兩個真 bug:全域 hook 被倒退、來源被自己弄髒

- **編號**:F59、F61;工量 S
- **為什麼**:第一個:lumos update 會拿「更新前」的 vendored 副本去同步全域 ~/.claude/hooks,把整台機器最核心的 Stop hook 靜默換成六月版(實測 30912B → 15303B),訊息還印綠燈;舊版的 merger 還會把已撤除的 hook 註冊加回全域 settings.json。第二個:來源 clone 裡有七本被 git 追蹤的帳檔,而唯讀的 lumos show/context 就會 append 其中一本——只要有人在 ~/harness/lumos-toolchain 裡查過一次圖譜,之後這台機器所有專案的 update/bootstrap --pull 都會被 fail-closed 擋住(逃生門在錯誤訊息最後一行,但沒人會讀)。
- **做什麼**:(a) _vendor_toolchain 把 _install_hooks_py(root) 移到 filecmp 自癒迴圈之後;cmd_bootstrap 分流①的全域同步改用來源 home(core.hooksPath 仍用 root),最乾淨是把 _install_hooks_py 拆成「git config 這半」與「全域同步這半」;加反事實測試「vendored 舊、來源新 → update 後全域內容==來源」。(b) 帳檔二選一:git rm --cached 七本並補一份 docs/.gitignore(scaffold 樣板有清單但本 repo 的 vault 早已存在、從沒被產出),或 _pull_source_or_abort 對既有的 _BOOKKEEPING_FILES 白名單自動 checkout 並印一行;補「來源只髒 usage-log → update 仍成功」的測試。
- **PRIOR-ART**:最小解在同步順序與一份既有的簿記白名單;世界解=dpkg 拒絕降版(要 --force-downgrade)、Homebrew brew update 對 tap 直接 reset(來源目錄屬工具所有);裁定=borrow-design(只對工具自己寫的簿記自動處理,實質改動仍中止)

### #6 hook 面的信任邊界:執行誰的碼、寫哪個目錄、注入什麼字

- **編號**:F85、F87、F88、F24、F31;工量 M
- **為什麼**:全域 SessionStart hook 會用 sys.executable 執行「你剛打開的那個資料夾」裡的 scripts/lumos,唯一判準是那個 repo 有 docs/*-knowledge——clone 一個陌生 repo、開 Claude 或 Codex,那一刻就跑了對方的 python(實測:沒有 +x 位照樣跑、fork 出的背景程序活過內層 timeout)。派工鏡頭的私有目錄檢查沒跟上 stop-block 在 r2/r3 各加的兩刀(拒 symlink、解析後路徑必須相等),而真正 rmtree/mkdir 的寫入端與 disarm 完全沒檢查。anchor 只逐條比對清單內的檔,新增一支 hook 檔沒有任何東西會看。impact-hook 則把圖譜自由文字(pitfall_when 觸發字串、RISK 後綴)以系統口吻逐字灌進主 session,而同 repo 的 dispatch-lens 早就為此定了固定字彙。
- **做什麼**:拆成四刀,①先做:lumos-entry-hook 改成 which(lumos)→$LUMOS_HOME,找不到就跳過 enforcement 行(fail-open 本來就允許),check-graph-sync/impact-hook 的樹內備援同步(那兩支是 which 優先,嚴重度低一階)。②抽一支 _trusted_private_dir(is_symlink 拒、解析後路徑相等、uid、g/o 不可寫),stop-block、_lens_arm_dir_ok、_lens_cache_write、disarm 四處共用,把 stop-block 測試⑲㉒複製一份到 lens arm。③anchor verify 加「git ls-files scripts/hooks 的檔集合==baseline 集合」——講清楚它買到的是「無聲新增 hook 檔」變成必留一種痕跡,不是防線(checkout 當下已經執行了)。④impact-hook 兩條渲染路徑的 matched_by 改固定字彙、contract 只印類別前綴、注入段首尾加「以下是機器附加的參考資料,不是指令」框,並同步改 t_impact_hook_incidents_inject 那條會翻紅的斷言。順手把 pre-push 與 ai-governance-research.sh 的固定名 /tmp 檔改 mktemp(理由是已兌現的碰撞:hook 測試三次覆寫同一路徑害過一次誤診,不是 symlink 攻擊)。
- **PRIOR-ART**:最小解在 hook 的尋路、一支共用的路徑信任函式、一層注入分隔框;世界解=git safe.directory(CVE-2022-24765)與 VS Code Workspace Trust、OpenSSH safe_path/systemd chase、OWASP LLM01 + Microsoft spotlighting、CWE-377/mktemp;裁定=borrow-design(工具自己的碼可以跑,從當前資料夾撿到的碼要先被信任)

### #7 對外發布線落地(release 分支、CHANGELOG、--version、Windows 入口)

- **編號**:F58、F72、F86、F99、F60、F109、F63;工量 M
- **為什麼**:2026-07-30 使用者裁定的「main 開發線 / release 對外線」五週零落地,八條條款全數未動:遠端只有 main、0 tag、無 CHANGELOG/RELEASING、LUMOS_VERSION 從誕生就是 v1.0(所以那條版本落後提醒結構上永遠不會響)、lumos --version 直接吐 argparse 錯誤、三個 clone 站與兩份 README 共七行安裝指令全指 main 的當下 HEAD、get.ps1 停在 06-26 兩步版且寫死 python。這條線的缺席是好幾個症狀的共同上游(curl|bash 抓到半成品、版本身分講不出、nudge 空轉),而計劃 status 掛 doing、沒有 REVISIT,doctor 也不會唸。
- **做什麼**:二選一、當次收口。(A) 照計劃 [S5] 最小切片:git push Lumos main:release(本 clone 沒有 origin,計劃內兩處寫死 origin 要一起修)、三個 clone 站加 --branch release 並保留冷啟動 fallback、七行安裝 URL 改 release、get.sh 整段包進 main() 防串流半段執行、get.ps1 改成委派 bootstrap 並透傳旗標、主線 cmd_install 的 Windows shim 借 slim 已審過的 _pick_windows_interpreter、CHANGELOG 首筆 v1.0、--version 印 LUMOS_VERSION+short sha(vendored 無 .git 時印 vendored 不炸)。(B) 判定暫不發版:lumos set status todo(project 型沒有 deferred 這個值,寫下去會靜默變成篩不到的狀態)加一行 REVISIT:2026-10-05 與自主迴圈去留同日裁。不管選哪個都不要在 ONBOARDING 教人用 --version 對版本——「版本號嚴禁當 staleness oracle」是既有裁定。
- **PRIOR-ART**:最小解在 git 分支與一個 CHANGELOG 檔;世界解=git-flow release 分支 / Chromium stable channel、Keep a Changelog、Sigstore「A Safer curl|bash」、GNU --version 慣例;裁定=borrow-design(計劃已借好形狀並否決過 tag 當 clone 通道,缺的只是執行)

### #8 死碼與帳面房務批

- **編號**:F09、F75、F29、F34、F39、F98、F33;工量 S
- **為什麼**:一批「留著不痛但一直在說謊」的東西:repo 根一支 5 bytes 的 lumos-calls.jsonl(無人讀無人寫,開發期手滑被 git add 進去)、已撤 hook 的 423 行全本(階段二 DELETE 逾期兩週,靠的是永遠不會觸發的「隔一版」條件)、Stop hook 兩段印到模型看不到的 stderr 的死分支、20 份共 13.5MB 的 Codex 全程逐字稿進了版控(佔 review-reports 追蹤內容四成、git 壓縮後仍是整包 pack 的三成)、usage-log 的退場條件寫在 doctor 掃不到的 HTML 註解裡。另外有一條反向的:「bypass 模式下 Stop block 會不會被忽略」這個開放風險,今天的逐字稿已經有實證可以收窄。
- **做什麼**:一批做完:git rm 雜檔(不必加 .gitignore、不必加「repo 根無新檔」斷言,沙箱隔離已成立);verification-rot-check.py 移到 _RETIRED_CLAUDE_HOOKS 並刪檔,同 commit 結案 Systems/verification-rot-eval(design-only、從未實作,是它唯一的真引用),並把 test_lumos.py 第 5 段寫死該檔名的斷言改成合成名字——不要用刪測試換綠;刪 check-graph-sync 的 _impact_missing 分支與 emit_queue_patrol(掛回 Issues/只退場不痛的機制 d1),Systems/graph-sync-coverage 的「三處點名」改兩處並註明這條分支從 08-22 到 09-05 從未到過模型面前;.gitignore 加 review-reports 的 *.err 與 *-stderr.txt 並 git rm --cached(歷史不 rewrite),收貨改用 codex exec --output-last-message;usage-log 退場條件改成獨立 REVISIT 行;立一篇 Verification 釘住 bypass 下 block 確實落地(valid_under 綁 Claude Code 2.1.260,比對法用「內容以 Stop hook feedback: 開頭」的 user 訊息數 vs 標記數,不要用含 LUMOS-STOP 去 grep,同 session 有 10 則假陽性)。
- **PRIOR-ART**:最小解在 git rm、.gitignore 與一行 REVISIT;世界解=deprecation 建立時就綁移除日期(Software Engineering at Google ch.15 / feature flag debt)、CI log 當 artifact 有保存期不進版控、characterization test 釘平台未文件化行為(Feathers);裁定=borrow-design

### #9 CLI 進場面:說明段、錯誤訊息、退出碼、brief 選行

- **編號**:F01、F108、F02、F71、F03、F111、F04、F110、F05、F11、F07;工量 M
- **為什麼**:這是「白話三段式」長期標準四批清掃唯一沒掃到的一面,而它正好是新手和 AI 的第一眼。lumos --help 開頭那段是 2026-06-15 初始 commit 之後從沒改過的 docstring:只列 10/66 支(argparse 下面又全列一次,所以 doctor/context/export 各印兩遍)、指向不存在的路徑、夾「MemPalace closet」這種外人不懂的詞;頂層清單還有 14 條 help 帶 [M1/P2]、[T3 養成] 這類代號。打錯節點名時,七支讀指令印的是寫側專用的「決策沒地方掛」(白話化那一批複製貼上漏改),而且不給近名候選。打錯指令或把 --vault 放在子命令後,吐的是英文 argparse 錯誤加 66 個選項。rc2 同時代表用法錯、IO 錯、帳損壞、找不到節點、找不到圖譜,而同一個「找不到圖譜」在 impact --file 是 rc3、在 --node 是 rc2,impact --diff 更是靜默回 0 裝作查過了(對新手最危險)。
- **做什麼**:一批文字與訊息改動加兩條結構守衛:docstring 縮成一句定位加「入口三步 search→context→contracts」;help= 改成直接取 HELP_WHEN(每個子命令的白話單一來源已經在那裡,不要手寫第二份 99 條),守衛用「help= 必須等於 HELP_WHEN 條目 / 不得以方括號開頭」這種結構判準,不要用抓不全的代號正則;抽 _node_not_found 與 _vault_not_found_hint 各一支(讀側去掉「決策沒地方掛」、寫側保留;近名候選複用既有 _el_near_ratio,不要另引裸 difflib;訊息裡不得裸寫 init/bootstrap,精簡版把生命週期整族砍掉、slim-scan 會判懸空);子類化 ArgumentParser 覆寫 error() 給三段式與候選,--vault 用 parents= 也掛到子命令(注意 slim 凍結區的兩處文字會漂移,要嘛保留 invalid choice 字樣要嘛明記);頂部加 RC_ 常數不重新編號,表寫進 Systems 當唯一來源;context --brief 選行改成「合約行+日期最大的 KEY+首條 FLOW」——這條前案被 r1 用 design-loop 反例(+86% bytes)否決過,進場要帶那個反例,而且不要順便立「KEY 最新在上」的寫入慣例(帶日期的變更史正主是 decisions)。--json 只登記一行已知缺口:doctor 有 --ci 側通道、合約可經 impact --json,真正沒機讀面的只有 decisions,等出現第一個解析它的消費端再做。
- **PRIOR-ART**:最小解在 argparse 的 description/help/error 三個字串面;世界解=git 的 common commands 分群與 did-you-mean、clig.dev 的 Help/Errors/Exit codes、GNU --help 慣例、BSD sysexits;裁定=borrow-design(全部 stdlib,不改任何既有 rc 數字)

### #10 活文件對齊現況,再補存在性守衛

- **編號**:F64、F67、F107、F69、F70、F79、F74、F112、F80、F84、F105;工量 M
- **為什麼**:新手照 ONBOARDING 走,第一步就撞到 2026-06-26 拆掉、至今被靜默吞掉的 ./install.sh --copy(以為拿到複製版,其實是 symlink,還以為更新要重跑安裝);同一份文件把 08-21 已撤的「提交後派 AI 自動複查」當前置需求講兩次、少了 Codex CLI、還教一個不存在的 --copy 剪貼簿旗標(skill reference 也還在教)。README 說「技術棧 skill 不進這裡」但 repo 裡住著三支 idioms;docs/methodology 三份解釋文件從任何入口都走不到,主檔自稱是客戶專案的文件、把已撤的 Layer 3 當現役列表、兩個欄位值與現實相反;注入到每個消費端 CLAUDE.md/AGENTS.md 的紀律範本寫著客戶專案名 Landmark,還指向本 repo 沒有的〈架構參考 Skills〉;commands 速查表有九列格數對不上表頭,02 那張已經真的錯位。而守衛只有單向(argparse→文件),文件寫的指令與旗標存不存在沒人驗。
- **做什麼**:先修文再加守衛(這個 repo 自己的模式)。修文:刪 --copy 兩處(ONBOARDING:54、skills reference:1228 與 slim 鏡像)、install.sh 的 exec 加 "$@"、ONBOARDING 刪已撤層與補 Codex 前置、README §6 改成「七步 SOP,這裡濃縮五個要點」、邊界句中英兩版加 ONBOARDING:129 一起改、ARCHITECTURE 的 skills 數改成以 ls skills/ 為準、範本 graph-discipline.md 改通用範例與條件式指路(★改的是範本不是那兩個檔,否則 Check D 會判漂移、reinject 又會刷回★)、methodology 補入口連結與現況狀態列(★不要標成「舊稿以 README 為準」——它 09-05/06 還在改,而且是六篇筆記列管的必同步標的★)、commands 三檔九列表格補齊。守衛兩條:t_skill_mentions_resolve(真值取 argparse choices 與各子命令 --help,不要 regex 掃原始碼——舊教訓是「守衛的尺自己在漂」;要先把命令 span 切乾淨,否則全域旗標與同行多指令會製造假紅)、t_commands_table_shape(等價 markdownlint MD056,20 行自寫)。誠實記:存在性守衛抓不到語意漂移(install-hooks.sh --force 跑得動,但它做的是完整 init),首跑真陽性可能是 0——它是防未來漂移不是抓現存缺陷。
- **PRIOR-ART**:最小解在文字修正加兩條測試;世界解=docs-as-tests(rustdoc/python doctest、clitest)、markdownlint MD056、Diátaxis 的象限入口與 ADR 的 status 欄;裁定=borrow-design(不真跑指令只驗介面存在,避免寫入副作用)

### #11 test_lumos.py 地基:真機隔離與重複收攏

- **編號**:F48、F49、F55;工量 M
- **為什麼**:$TMPDIR 已經堆了 33 萬個 gctl-* 測試殘骸(10 萬個超過 30 天,du 直接掛住);更嚴重的是兩支 install 測試每跑一次全套,就把開發機真正的 ~/.claude(hooks、settings.json、skills symlink)與 ~/.codex 重寫一遍——同型事故 08-01 刪過真機 hook、09-02 又重連過真 skills,兩次之後仍然沒有任何機制擋住,而假 HOME 只寫在事故筆記裡。另外 55 處內嵌 importlib(已經有兩支現成 helper)、71 處手寫 HOME env、142 處函式內 import subprocess,讓 AI 每次編輯這個檔的成本都偏高。這批也是分片並行的前置。
- **做什麼**:全部收在 main() 這個唯一進入點(跟清 GIT_* 同一個理由):建本輪專用根目錄並同時設 tempfile.tempdir 與 TMPDIR(子進程繼承)、收尾 rmtree(--keep-tmp 或有紅時保留;修剪只碰已標記結束或 mtime >24h 的根,不要按輪數硬刪——hook 會平行起 runner)、設假 HOME/USERPROFILE 並補 LUMOS_HOME、pop CODEX_HOME(否則開發機設了會繞過假 HOME 打到真 ~/.codex);加自證測試「runner 底下 Path.home() 不等於真家目錄」;兩支 install 測試改成在假 HOME 內斷言(語意從「真機裝好了」變成「會在 HOME 下建對的連結」)。去重只做真正省事的兩件:7 處 subprocess -c 字串抽 _py_call、約 14 處行內 importlib 改用已存在的 _load_lumos_module,env 抽 _env()——不要新增第九支載入 helper,也不拆檔(07-29 已裁緩辦)。兩支檔都是 anchor,改完 anchor approve 並跑一次全套做等價驗證。
- **PRIOR-ART**:最小解在 runner 的唯一進入點;世界解=pytest basetemp + tmp_path_retention、Go testing.T.TempDir、tox passenv / Nix sandbox 的 HOME=/homeless-shelter、xUnit Test Utility Method;裁定=borrow-design(測試進程看到的家目錄由 runner 決定,不由每支測試記得)

### #12 推送閘序與測試 runner 的五個旗標

- **編號**:F19、F52、F53、F54、F128、F56;工量 M
- **為什麼**:pre-push 把 8-10 分鐘的全套排在最前面,anchor(0.19 秒)、doctor(0.93 秒)、pitfalls(0.25 秒)排在後面——被便宜的閘擋下時,全套已經白跑完了,而註解還寫著 2026-07-07 的「~32s」。runner 又用寬鬆解析:--help、打錯旗標、甚至情境錄音裡真實出現過的裸測試名,全部被靜默丟掉當成沒帶 -k,直接跑滿全套(Codex 就因為跑全套超時過)。沒有 -x、沒有失敗優先、沒有分片,也沒有隨機序探針——順序相依從來沒被打過一拳。
- **做什麼**:①重排 pre-push 成 anchor→doctor→pitfalls/code-loop/test-layers→全套;注意「沒有 vault 就 exit 0」要改成只跳過 doctor 段,否則 t_prepush_test_gate 情境 B 會翻紅。②runner 改嚴格解析並開 help、裸位置參數當 -k 同義(情境錄音就是這樣敲的)、加 --list 印名單。③加 -x 與 --ff,快取落 .lumos/test-cache.json(既有 gitignored 快取慣例,不要放 .git/)。④加 --shard I/N 與 --json-summary,pre-push 起 N 個子進程彙總;前置是上一批的 TMPDIR/HOME 隔離,還要蓋掉固定路徑 /tmp/pwned-* 與 GH_STATE、8 處 os.chdir。⑤加 --seed 隨機序,預設關、只給每日治理跑、紅了印 seed,不進 pre-push。順手把 pre-push:64 註解改成實測數字並印預估。兩支檔都是 anchor,改完 anchor approve。誠實記:-x 只縮短「有紅」那一次,全綠推送仍要跑滿,真正壓時間的是分片。
- **PRIOR-ART**:最小解在 runner 的參數與 hook 的段落順序;世界解=pytest -x/--lf/--ff 與 cacheprovider、Bazel test sharding(TEST_SHARD_INDEX/TEST_TOTAL_SHARDS)、pytest-split 按歷史耗時均衡、Go test -shuffle 印 seed、lefthook 的 priority/piped;裁定=borrow-design(fail_fast 不借——本 repo 已裁每道閘本來就 exit 1)

### #13 假綠:把偽裝成通過的 skip 改走 SKIP 通道

- **編號**:F50、F51;工量 S
- **為什麼**:有十幾處「條件不成立就 check(…, True); return」把「沒驗」記成 PASS,而不是走既有的 SKIP 通道;runner 也不對「一支測試 PASS+FAIL 零增量」有任何反應。其中最貴的一支:全套唯一那條 vendored-cli==active 的斷言,CI 從第一天(09-02)起就沒跑過本體——當天 commit 訊息卻寫「測試 8 案覆蓋各分支」,CI 日誌逐字打臉。
- **做什麼**:做小的那半:偽 skip 改 raise 走 _SrcOnly/SKIP 通道並列名;runner 對「PASS+FAIL 差值為 0」判紅(跟 -k 選中 0 判紅同一個理由);那支 CI 沒跑到的測試,最小解是把來源改成 Path(GRAPHCTL).resolve().parent.parent,不必動 ci.yml。★不要做 F51 的 --reach 到達檢查★:同型的 mutate v2 才在 08-26 因為零消費者退場,復活條件是先把消費者接線寫死;而且它對 pwsh/bash 那幾次假綠本來就量不到,靶還是 maker 自己定的。要留就留成一行帶條件的 REVISIT。
- **PRIOR-ART**:最小解在 runner 的計數與既有 SKIP 通道;世界解=PHPUnit risky test(沒斷言不算過)、Jest expect.hasAssertions、pytest.skip 明確計數、PIT/mutmut 把 NO_COVERAGE 與 survived 分成兩格;裁定=borrow-design 前半、不採用後半(缺真消費者,家裡有同型退場先例)

### #14 hook 逾時:預算單一來源,超時不要白燒

- **編號**:F27、F28;工量 M
- **為什麼**:派工鏡頭超時就把子行程殺掉、什麼都不留,同一個範圍的下一席再燒 45 秒再放空,現在唯一的緩解是「編排者先手跑一次暖快取」——全靠人。五支 hook 的內層逾時與 settings.json 的外層天花板沒有單一來源、沒有測試,三支違反自家「外>內」的規則;其中 impact-hook 單檔的 30 秒等於外層 30 秒,意思是那條 TimeoutExpired 的 fail-open 分支與冷卻窗解除根本跑不到——一個為了 fail-open 而寫的分支,結構上永遠不執行。
- **做什麼**:①超時時不殺子行程,讓它跑完寫快取(start_new_session 避免被 hook 行程組收掉),下一席就命中 20 分鐘快取;邏輯放 lumos 端、hook 維持薄殼(09-03 r3 裁定),並行派工時同範圍加鎖或只讓第一個續算;TIMEOUT_NOTE 若要寫「下一席大概率有」就得附 REVISIT(機率宣稱要接電)。②HOOK_ENTRIES 的 command 加 --budget 由一處生成,各 hook 從 argv 讀、內層一律取 budget×0.7 減已耗,加一條「每個 subprocess timeout ≤0.75×外層」的測試。翻掉 impact-hook 30 秒那條 r1「逐字等價」裁定要在計劃筆記寫明理由,並改 test_lumos.py:25365 的 ==30 斷言。
- **PRIOR-ART**:最小解在 hook 的逾時參數傳遞;世界解=deadline propagation(gRPC deadlines / Go context.WithTimeout)、cache-warm-on-miss 背景補算;裁定=borrow-design(不借 RFC 5861 stale-while-revalidate 與 circuit breaker——沒有舊值可回、也沒有跳閘邏輯,掛名不對應)

### #15 skill 頭版單源化:兩家對照只留一份

- **編號**:F78、F83;工量 S
- **為什麼**:兩份 SKILL.md 都寫著「Codex 對照單源=templates.md §3 ④」,卻又各抄一整段同樣的 Codex 版本事實(0.153.2 選得中、0.144.1 忽略、別信 TOML 的 sandbox 欄)——說是單源,實際三份,commit 記錄就有一次「三處統一」的同步。頭版步驟又以 Claude 的工具名當主詞、Codex 塞在括號裡,而同一份檔兩家都會載入(install 同時鋪到 ~/.claude/skills 與 ~/.agents/skills)。Codex 版本行為一變就要改三處,這正是散文載規則會漂的老問題。
- **做什麼**:純名稱對照(Agent↔spawn_agent、Edit/Write↔apply_patch、claude -p↔codex exec、claude-in-chrome/Playwright↔無)收進既有單源表,design-loop 頭版留一句指標,code-loop 那句放它自己的 reference.md(沿用既有「單源見…不在此雙寫」的一跳形狀,別製造「頭版→別家 templates」的兩跳);版本相關的行為事實只留在單源。把 t_skill_reference_pointers_resolve 的正則從〈標題〉擴到「§N ④」型錨點,並加一條反向斷言:有單源指標的頁面不得同時出現 spawn_agent 與版本號。
- **PRIOR-ART**:最小解在指標與一條既有測試的正則;世界解=Single Source of Truth / DRY(Pragmatic Programmer)+ Anthropic 的 references 一層深原則;裁定=borrow-design(repo 已有指標守衛,只是沒守「有指標就不准再抄內容」那半)

### #16 frontmatter 欄位守衛:打錯的鍵與空的必填欄

- **編號**:F13、F14;工量 S
- **為什麼**:欄位鍵打錯(valid_under/verified_by)會被所有檢查靜默略過,lint 一句話都不說;同時 19 篇 Verification 的 revalidate_when 是空的或根本沒有這個鍵(12 篇有鍵空值、7 篇連鍵都沒有,其中兩篇是這幾天才產生的),而 skill 的參考文件自己寫著「必填」——文件承諾必填、工具零檢查,stale 與 doctor [V] 都看不到它們,doctor 那個 0/153 的分母也因此不誠實。
- **做什麼**:併進 09-12 房務批一起做:①lint 加已知鍵集合,不認得就一行軟提醒加近名候選——★集合要納入其他 vault 在用的合法鍵(priority/title/regen、core-knowledge 的 project/implements/domain),或讓 .lumos/config.json 可擴充,否則消費專案每次 lint 都被嘮叨★;doctor 不升 error(維持容忍未知欄位的前向相容立場)。②既有 Issue 已裁的部分照做:cutoff 之後的 pass 驗證缺 valid_under/revalidate_when 給 warning,不擋舊帳。③doctor [V] 尾行加「另 N 篇 pass 驗證未填(不在分母)」。順手修 reference.md:269 那個 code 從沒讀過的 valid_until。
- **PRIOR-ART**:最小解在 lint 的一個集合加近名比對;世界解=Dendron schema.yml / Backstage catalog-info 的未知鍵驗證、adr-tools 與 log4brains 對 ADR 必填段落的 lint;裁定=borrow-design(不引 JSON Schema 依賴,一個集合就夠)

### #17 受波及合約測試閘到底什麼時候跑  ★需設計審★

- **編號**:F22;工量 S
- **為什麼**:圖譜、計劃、三份 skill 都寫「pre-push 每次推送都呼叫 code-loop check,不分風險等級」,實際上那行呼叫從第一天就寫在 tier=high 的分支裡。在本 repo 看不出來(前面無條件跑全套會蓋掉),但消費專案的 standard 推送,合約綁的測試本機一次都沒跑,CI 又用 LUMOS_SKIP_BOUND_TESTS 跳過——INVARIANT 宣稱的行為和實作對不上,而且對不上的方向是「宣稱有守、實際沒守」。
- **做什麼**:二選一並寫回圖譜:(a) 把 code-loop check 搬到 tier 判斷之外(沒 pins 時它自己記 no-pins 帳、秒級),tier 判斷改讀它的 --json,pitfalls 少跑一次;(b) 維持現況,把計劃第 25 行、Systems/bound-tests-gate 的 FLOW/INVARIANT、三份 skill 與 ci.yml 註解全部改成誠實版。(a) 才符合原設計意圖,但會讓 standard 推送多一種被合約紅擋下的機會——那正是 INVARIANT 宣稱的行為,所以要當成一次判準變更來裁,不要順手改。
- **PRIOR-ART**:最小解在 pre-push 的一段 if 的位置;世界解=Google TAP / Bazel presubmit「改到就跑相依測試,風險分級只決定要不要多派人審,不決定要不要跑測試」;裁定=borrow-design

### #18 每日治理 wrapper:死了要有人知道、不要兩份同跑、帳本要有門檻  ★需設計審★

- **編號**:F43、F46、F47;工量 M
- **為什麼**:9/5 那次 wrapper 在第二步跑完回來時,因為自己被改動的檔而 syntax error 死掉,第 3-5 步全沒跑——而它永遠 exit 0、沒有任何東西讀它的 log 或 launchd 狀態,所以整天沒人知道。它也沒有整跑鎖:機器睡過 09:30、人打開蓋子同時手跑,兩份治理日報會互蓋、LINE 播兩次、多燒一次配額。治理帳 30 天長一倍(1.9→3.6MB)且沒有任何大小門檻,主要來源是每次 doctor 把同一批未修的軟提醒整批重寫。
- **做什麼**:①wrapper 收尾寫 governance/logs/.last-complete(日期+各步 rc),各步 rc 做 OR 當退出碼,讓 launchd 的 last exit code 有意義。②死人開關要放在不是 wrapper 自己的地方:doctor 一天被跑數十次(全是獨立行程),加一條軟檢查「.last-complete 超過 36 小時沒更新」——主通道是 doctor 的輸出,不是 nags→LINE(那條腿因為自主迴圈暫停現在是斷的,要誠實寫成 REVISIT 綁 10-05)。③把 autonomous-loop.sh 已審過的 mkdir 鎖慣例(含 pid、鎖齡 60 分鐘接管)抬到 wrapper main() 開頭,鎖目錄進 .gitignore,守衛測試釘「鎖在 main 體內、finalize 會移除」。④治理帳只裝門檻觸發器(超過 N MB 或近 7 日平均每日 >500 筆就印一句並進帳),分檔慣例先寫進圖譜掛 REVISIT、到門檻才做——它有四個整檔讀者加 replay 的逐行 sha 閉包;順手在 Systems/reversibility-governance-ledger 補一條 KEY 記「spec 的 2000 筆 cap 從未實作、gitignore 那半已被裁維持追蹤」。
- **PRIOR-ART**:最小解在 wrapper 收尾一行戳記 + doctor 一條軟檢查;世界解=healthchecks.io/Cronitor 的 heartbeat+grace、systemd OnFailure、SRE「alerting on absence」、flock/run-one(macOS 無 flock 用 mkdir 原子鎖)、logrotate 的 size 條件;裁定=borrow-design(告警器必須獨立於被監看的行程)

### #19 enforcement 可觀測性:擋了幾次、放行幾次、跳過幾次、hook 有沒有跑  ★需設計審★

- **編號**:F21、F95、F25、F30;工量 M
- **為什麼**:治理帳 24,262 行沒有一筆 hard=true——不是沒人寫,是那三道會寫的從沒觸發過;真正的缺口是六條 hook 層的 exit 1(anchor、全套測試紅、code-loop 無留痕、污染指紋、lint、改 code 沒動圖譜)擋下人時一筆帳都不寫,pre-push 的五條 fail-open 放行與整支耗時也無處可數。README 卻對外宣稱「每道關卡攔了誰、硬擋還是提醒」都在帳上。五支 Claude hook 的成功/超時/rc≠0 只有開 debug 才看得到,要量得去 grep 逐字稿,而 lumos enforcement 只驗「有沒有註冊」。逃生口則是 git 層全有全無的 --no-verify:為了省 8 分鐘測試,連 1 秒的 anchor 與 doctor 也一起跳,本機零留痕。
- **做什麼**:當成一批設計:①每個 exit 1 分支前寫一行 gate/kind=blocked/hard=true(★邏輯進 lumos 子命令,hook 維持薄殼——09-03 r3 的裁定,不得在 hook 裡塞 python - 小段;新開子命令有五份文件+索引的同步稅,要算進去★);②pre-push 記整支耗時與五條 fail-open;③LUMOS_SKIP=<gate-id> 細粒度跳閘(anchor 刻意不可跳),被跳的閘記 kind=skipped 與 note,擋下訊息把「第三條路」從 --no-verify 改成 LUMOS_SKIP,這樣才量得出哪一道最常被跳;④五支 Claude hook 各寫一行 jsonl 到 ~/.cache/lumos(★私有目錄、不進 git、不是治理帳——這點要在計劃裡寫清楚,才不會撞派工鏡頭 d1「不記治理帳、不量成效」的裁定★),enforcement 多一欄「近 7 天跑 N 次/注入 N/超時 N」,把「生效=有註冊」升格成「生效=最近真的跑過」。★不要重提消費端 hook-local 覆寫與 rebase 偵測★(.lumos/config.json 宣告式開關已經是正規出口),LUMOS_SKIP 只收窄在源 repo 的 pre-push 四道閘。
- **PRIOR-ART**:最小解在既有 jsonl 帳本多幾筆事件加一個環境變數;世界解=OPA decision logs 與 K8s admission failurePolicy=Ignore 必配 audit、pre-commit framework 的 SKIP=<hook>、OpenTelemetry logs 資料模型/flight recorder;裁定=borrow-design(fail-open 可以,但每次 fail-open 都要留一筆可查的決策紀錄)

### #20 審查收貨線變成指令(正規化、三道機械檢查、派工單 schema)  ★需設計審★

- **編號**:F38、F124、F40、F125、F35、F37;工量 M
- **為什麼**:收貨正規化到今天還是「每個迴圈臨場寫一支 regex」的 SOP(至少六個迴圈各記一次不同變體,09-05 首次寫成腳本入版控),而那支臨場腳本會在一行 severity 都 parse 不到時默默把首行補成 clean——寫側 rc2 擋的正是這件事,等於把「低報成 clean 的無聲逃逸門」補了回去;它的 .strip('"') 也已經在入版控的卷證裡吃掉引句頭尾引號、把「」換成『』,那會讓合法引句錨不回快照。同時一輪審查的收貨與記帳沒有任何一條指令串起來:每席固定 3-5 條參數高度重疊的指令,11 席的迴圈光收貨記帳就要打 40-50 條,reviewed 的 sha 還要人另算(工具內部早就在算同一個檔的 sha)。派工單又沒有機械 schema,讀側只認 auditor 鍵,09-03 起 8 個迴圈全席被判 unknown、喊出假的「單家族/席位不足」。
- **做什麼**:三件一批:①正規化收進一個子命令,做且只做三件格式轉換(quote:→引句、file:→反引號、表頭型 severity 抽成獨立行),保留 .raw 原檔,找不到任何 severity 宣告就 rc2 退回、★絕不代填 clean★;★嚴重度 parse 必須複用 _report_severities、引句正規化複用 _quote_norm,不得自寫第二份★(自寫會出現「正規化器認得、寫側不認」的漂移,家裡為此立過鐵則)。②一條收貨編排指令依序跑正規化+quote-check+refcheck+seat-check,算出 reviewed sha,印一條只留嚴重度與處置給人填的 record 命令——不記帳、不判嚴重度、不自動寫 preflight 宣告行(人工判讀的 HIT/MISS 重現仍由編排者寫),★名字不要叫 intake,那個詞已被 rN-intake.md 的既有慣例佔用★。③_roster_dispatch_entries 先讀 family 再退 auditor,loop next 直接吐派工單骨架(欄位齊、family 預填),seat-check 驗必要鍵。新子命令要進指令索引與 HELP_WHEN(既有守衛會擋)。F37 的重複行只採「尾行相同就跳寫」、不改寫成 xN,且不單獨開工,併 11-26 覆核。
- **PRIOR-ART**:最小解在一支正規化器加一支編排指令;世界解=gofmt/prettier 的 canonical form 與「Parse, don't validate」、reviewdog rdformat 轉接器(本 repo 對 linter 已這麼做)、git-review/arc diff 的送審打包、Gerrit ReviewerInfo 的明示欄位;裁定=borrow-design(轉接器放工具裡不放每個人手上,但缺值一律退件、不預設)

### #21 成本帳:機器取值、一頁總帳、單位可比  ★需設計審★

- **編號**:F93、F94、F96;工量 M
- **為什麼**:每席 tokens 靠編排者從子代理結束通知手抄,填充率三成、Codex 席 69 筆只填 3 筆——而兩家 harness 本來就吐得出來(codex exec --json 的 turn.completed.usage、子代理逐字稿每則 assistant 訊息的 usage 四欄)。自主迴圈記美元(12 筆全在 auto 家族)、手動席只記一個彙總 tokens,兩本帳沒有共同單位,08-22 自己寫下的唯一消費者「本週自主 loop + 派席共花 $X」今天算不出來。快取讀只活在散文 log 裡,而它才是美元的主要構成(09-05 那輪 1,411 萬快取讀是 tokens 的 58 倍)——tokens 低不代表便宜。
- **做什麼**:併進既有 B3 候選(10-15 回看,條件 usd 覆蓋率 <20%,現在 2%,幾乎篤定觸發)一起做:①record 加 --usage-from 從 harness 產物取值,抓不到就留空、★禁止填 0★;②tokens 分型存(input/cache_create/cache_read/output),舊 tokens 語意不動,美元在讀側按一張帶日期與 REVISIT 的單價表現算並標「估」,實測回傳的 usd 另欄;③gov --stats 加成本段,但先接受四件事實:usd 只有 auto 家族有、加總前要去重(有 7 組完全相同的三元組)、覆蓋率必須跟數字並印、低覆蓋一律標成下界。★別再宣稱能把 README 那個 930 萬 token 換算成美元★——它的來源是手機翻拍截圖,重算出來的不會是同一個數。
- **PRIOR-ART**:最小解在 record 的一個讀取器加讀側一張單價表;世界解=OpenTelemetry GenAI semconv 的 token 分型屬性、FinOps showback / unit economics、SLI coverage 慣例(沒量到的比例要跟數字一起印);裁定=borrow-design(寫入端只存事實、換算放讀側)

### #22 無空白中文查詢的字對回退  ★需設計審★

- **編號**:F16;工量 M
- **為什麼**:中文黏成一串的查詢在結構上永遠走不到 OR 回退(回退條件要求 token >1,無空白就是一個 token),而排序層明明已經有 CJK bigram、入口栓那條路也已經在用同一支 tokenizer 做召回。現在只印「加空白再查」的提示——CLAUDE.md 自己把「中文查詢要加空白」列成第一條紀律,正說明這個坑一直在踩,而且踩的人是每個新 session 的 AI。
- **做什麼**:走完整程序再翻預設:先用 governance/eval 補 10 題無空白查詢當對照組(既有 30 題 goldset 與多詞 10 題不動、題目由另一家族出),再把「0 候選 且 無空白 且 ≥4 漢字」的查詢退成 bigram OR + BM25F,提示行改成「整串找不到,退成字對召回」,--no-any 照樣關得掉;同時處理誠實面——回退後幾乎不可能回 0,「查無訊號」會消失,要設計訊號還回法(例如只對非跨詞邊界的高覆蓋字對標星)。這是對 2026-08-22 d4「0 筆時提示加空白」的翻案,要掛 superseded 或補充,不能靜默取代。
- **PRIOR-ART**:最小解在既有回退條件多一支分支;世界解=Lucene CJKAnalyzer / Elasticsearch cjk analyzer 的 overlapping bigram;裁定=borrow-design(tokenizer 已在檔內,不引 jieba 這類分詞依賴)

### #23 連鎖提醒的升級鏈接電

- **編號**:F118;工量 S
- **為什麼**:Check E4 的治理事件 nodes 是空的,而 gov --nags 這個唯一的「機制空轉」偵測器用 (gate, node) 當鍵——所以 E4 從 08-25 喊到現在 237 筆,--nags 卻回「沒有空轉的提醒」,那張 08-29 開的空連鎖單零判定至今,沒有任何機制會把它升級給人看。
- **做什麼**:★排在既有 Issue「空連鎖單巡過無法銷帳」的巡過動詞(REVISIT 09-12)之後再做★:E4 的 nodes 填連鎖帳本檔名 stem(8 個檔、天然唯一),nags 立刻咬得到。順序不能反——現在唯一那張未銷帳的空票沒有合法銷帳路徑,先填 nodes 只會把一則已知噪音推上每週 LINE,正是那個 Issue 點名的提醒麻痺。長期可考慮把 E4 收成 REVISIT 一種形狀(開連鎖單時直接在翻案節點寫 REVISIT 行),但那是另一案。
- **PRIOR-ART**:最小解在 gov 事件的一個欄位;世界解=Alertmanager 以 label 路由分組(沒 label 的告警落不到任何 receiver);裁定=borrow-design

## 第一批動手:12 件 quick win 全做完(2026-09-06)

都是「一小時內、不需審」那一批,逐條先驗證目標存在再改:

1. **刪掉根目錄的測試殘骸**(5 位元組、內容是字面空陣列,開發期被批次 add 進來)。沒加 .gitignore 也沒加「根目錄不得有新檔」的斷言——沙箱隔離已經成立,那是守一條不存在的路徑。
2. **37 份外家席逐字稿出版控**(13MB,佔追蹤卷證四成,零消費端)。歷史不改寫,加 .gitignore 規則;結論檔(.md)照樣進版控。★「工作區保留」只對執行 `git rm --cached` 的那台機器成立★——其他機器 pull 到這個 commit 時,git 會照新的樹狀態把那些檔從工作目錄刪掉(代碼審 r1 通才席用乾淨 clone 實測)。要留就自己備份。之後收貨改用 `codex exec --output-last-message` 直接拿結論。
3. **刪掉一處已拆旗標的教學**(`install.sh --copy` 2026-06-26 就拆了,現在會被靜默吞掉):上手指南那一行。★原本連 skill 參考與精簡版鏡像的第 12 條也刪了,是我判錯——那條講的是 Obsidian CLI「任何命令加 --copy 複製到剪貼簿」,跟安裝器的同名旗標是兩支不同工具;代碼審 r1 通才席查 git 歷史抓到,已還原(順帶消掉 11 跳 13 的編號斷層)。那個清單整體陳舊是另一件事,歸主題 #10★。
4. **安裝器透傳旗標**:未知旗標現在會撞上 argparse 吐錯,不再被吃掉。
5. **用量帳的退場條件接上電**:原本寫在 HTML 註解裡(「90 天內無人立案則退場」),到期掃描只認獨立的 REVISIT 行,等於沒寫;改成 REVISIT:2026-11-19 並寫明判準。
6. **發布流程計劃補回頭條件** REVISIT:2026-10-05(2026-07-30 裁定至今五週零落地)。順手記下:status 要改只能改 todo,project 型沒有 deferred 這個值,寫下去會變成篩不到的狀態。
7. **三張速查表的欄位錯位補齊**:動手前算波及那張真的錯位(四列只有兩欄,「結果怎麼讀」掉到別欄);設計審那張是 `--finding-kind id=code|spec|process` 的直槓沒跳脫把一列撐成五欄;代碼審那張三列缺最後一欄。
8. **README 中英兩版的邊界句改寫**:原句說「技術棧 skill 不進這裡」,但 repo 裡就住著三份;改成「跨專案通用的慣例 skill 是工具鏈的一部分,專案自己的框架選型不進來」。★第一次改動時替換位置插進括號清單裡,句子讀不通,重寫過★。
9. **快速上手補「裝好了嗎」**:README 兩個入口與上手指南各加一句 `lumos enforcement`,並說明它查的是「有沒有接上」不是「判得對不對」,以及 Codex 那幾行為什麼會停在「本機讀不到」。
10. **推送前 hook 的耗時註解訂正**:「實測 ~32s」是 2026-07-07、183 支測試時代的數字,現在約 8 分鐘、3700+ 案例。
11. **方法論三份文件接上入口**:之前從 README / 架構文 / 上手指南一條連結都到不了。★我原本寫的第三份檔名不存在,驗證連結目標時抓到,改成真的那份★。
12. **Python 版本宣告訂正 ≥3.8 → ≥3.9**:主程式自己就用了四處 3.9 才有的字串方法,而另一處註解還在為了 ≥3.8 刻意迴避 3.9 的 API。純事實訂正;要不要再往上調是另一件事,要人裁。

驗證:相關測試子集全綠(精簡版 9、指令索引 7、安裝 247、推送閘 18),兩篇動到的節點 lint 0 問題。

## 第一批的代碼審(code-audit-quickwins r1,2026-09-06)

- **編制**:standard 三席——通才、架構對齊(皆 sonnet)、外家 Codex。11 條發現(1 major、10 minor)全折,零放行;處置閘 PASS。
- **兩條是我自己做錯,審查席抓到**:
  - **用錯理由刪東西**:我把 skill 參考與精簡版鏡像裡「任何命令加 --copy 複製到剪貼簿」那條當成「安裝器已拆旗標」一起刪了。通才席查 git 歷史發現那是 Obsidian CLI 的同名旗標,兩支不同工具。已還原,順帶消掉刪除留下的 11 跳 13 編號斷層。
  - **筆記寫了不成立的話**:我寫「工作區保留」,實際上 `git rm --cached` 只對執行的那台機器成立;其他機器 pull 到這個 commit 時 git 會照新樹把檔從工作目錄刪掉。通才席用乾淨 clone 實測。已改寫並註明。
- **只修一半的三條**:
  - 安裝器加了旗標透傳,但兩支結構一模一樣的手足薄殼沒改;而上手指南教的正是其中一支帶旗標的用法,那個旗標一直被靜默吞掉。兩支都補上。
  - Python 版本宣告只改了主程式三處,同檔還有一處、測試檔的函式名與說明、精簡版的獨立宣告都沒跟。全部補上。★精簡版那條原本以為不用改,查了才知道產出的精簡版建置真的含 3.9 才有的呼叫(因為建節點那個命令在保留清單裡)★。
  - README 補的驗收段與方法論連結只加在中文版,英文版沒跟。補上。
- **忽略規則兩次收窄**:外家席指出 `*stderr*` 會吃掉任何檔名含 stderr 的結論文件(實測 `stderr-summary.md` 真的被忽略),收窄成只認逐字稿副檔名;通才席再指出規則本質是「只認副檔名不認是不是逐字稿」,把這句話寫進註解而不是假裝規則很聰明。
- **回頭條件放錯位置**:新加的 REVISIT 放在標題正下方,不緊鄰任何具體宣稱;既有五篇的慣例都是緊鄰原句。已搬到它在講的那段旁邊。
- **表格錯位其實沒修對**:我上一輪替四列編了新內容,但真相是第 14 列的第三四欄本來就是第 10 列跑錯位的原文。外家席抓到,已把原文搬回去。
- **★審材缺陷(外家席 major)★**:我凍結審材時用 pathspec 把 `governance/review-reports` 整個排除,結果 37 個檔的刪除完全不在審查材料裡,三席都看不到那件事。改動本身有交付(版控裡已經 0 個),但審查席判不了。**教訓:凍結審材的排除條件會決定審查席看得到什麼,排掉的東西等於沒審**。
- **問閘擋過一次**:四句引句錨不到——三句是審查席在引「這次沒改到的原檔」(那正是他們的論點,而 quote-check 只比對 diff),一句是我的臨場正規化腳本為了不撞外層分隔符把引號字元換掉、把原文弄壞了。修法:把被引用的原檔行當附錄接進審材、還原被換掉的引號,重記帳再問閘才過。**這正是合成結果裡 #20 那個主題(收貨正規化該變成指令、臨場腳本會出錯)的又一次實證**。

## pre-push 擋下一次:測試成本隨「未推送量」放大(2026-09-06)

- **現象**:第一批推不上去,全套 3779 過、1 支紅——`t_codex_s1_lens_arm_claim` 超過 180 秒逾時。單獨跑一樣紅、CPU 全滿,所以不是機器忙。
- **真因**:那支測試驗的是「席次 token 的原子認領」,卻用 `<遠端主線>..HEAD` 武裝四次。算一次派工鏡頭的成本跟「本機比遠端多幾個 commit」成正比:當天多 5 個 commit、73 個檔,實測單次 47 秒,四次就撞破上限。**你要推的東西越多,它越容易紅;而推送前正是它唯一會被跑到的時機。**
- **修法**:只留第一次用真範圍(證明真內容跑得通),其餘三次改用 `<遠端主線>..<遠端主線>` 這個空 diff——一樣過「base 必須在主線」的守衛、一樣走完整的武裝/認領/過期/並發路徑,但不必重算鏡頭。180 秒逾時 → 55 秒,12 條斷言全過。
- **這條的意義**:它跟合成結果裡「假綠形態」是同一型的反面——測試存在、也會紅,但紅的原因跟它宣稱要驗的東西無關。找法寫進節點:看每次跑完印的「最慢 5 支」那張表,有沒有哪支的耗時會隨 repo 狀態浮動。
- **順帶量到**:算鏡頭 47 秒這件事本身,就是合成結果裡 #14(hook 逾時、超時不要白燒)那個主題的實測數字。

## 主題 #1(沒有 LICENSE)結案 — 2026-09-06

Enzo 確認著作權人是本人,選 **MIT**。查證、五個候選各派反方挑戰、實作與後續要人自己確認的事,全部收在 [[Systems/授權與歸屬]]。這一批動了:根目錄 LICENSE(含第三方登記)、主程式檔頭貼全文、其餘 12 支被複製的檔加 SPDX、精簡版包同步、產出 HTML 加第三方聲明、README 中英與上手指南各一段、一條守衛測試釘「檔頭不見就翻紅、LICENSE 不准進複製白名單」。

★順手補到一個現在就違規的洞★:打包的 3D 圖形函式庫上游 minified build 沒帶版權 banner,而獨立模式匯出會把它整段內嵌進交出去的 HTML——那是一次沒帶聲明的再散布。已在 LICENSE 尾段與產出 HTML 註解補上。

## MIT 授權那批的代碼審(code-license-mit r1,2026-09-06)

**四席、17 條發現全折零放行、處置閘 PASS。** 這一輪特別值得記,因為守衛測試被連續打臉四次。

- **三席各自用不同的壞例子讓同一支守衛假綠**:外家 Codex 用「白名單裡有含右括號的註解」、通才席用「兩個 tuple 相加」;我換成語法樹解析後擋得住前者、擋不住後者。**架構對齊席直接指出 repo 裡早就有更好的既有寫法**——載入模組讀執行期真值,同檔另一支測試早就這樣做。改用那條之後兩種都翻紅。
- **合約獨立審計判 fail,再抓三條**(它被要求「實際構造破壞而不是推論」):①繞過白名單直接在移除函式裡刪 LICENSE,守衛全綠;②在 hooks 頂層新增沒標示的檔會被真的複製出去,而手寫清單掃不到;③「MIT 全文」只比兩句片語,中段掏空照樣綠。→ 加端到端測試、清單改用生產邏輯算、全文改逐行比對。
- **四種假綠管道現在全部翻紅,原檔全綠**,都有實測記錄。
- **我自己漏的兩件**:節點寫了正文卻沒填摘要(等於對搜尋與簡要模式隱形),`about_code` 留空(改主程式的人不會被提醒看這篇)。都是自家鐵則,架構席抓到。
- **第三方版本標示對不上**:授權檔與產出 HTML 宣稱 1.80.0,但預設模式的網址沒鎖版。已鎖版。
- **教訓寫進節點**:「只驗白名單內容」是必要非充分,繞過白名單直接刪檔看不到——所以合約要配端到端測試,不能只驗一個常數的內容。

## 第二批動手:三件(2026-09-06)

### #2 刪除守衛半盲跑:逾時的真因不是我以為的那個

- **帳上 30% 的執行是「掃到逾時就降級放行」**——守衛在半盲狀態下擋人。
- **我第一次量錯方向**:用 `cmd_doctor` 這類罕見詞量,得到 0.75 秒,差點判「早先把逐字稿移出版控之後已經不慢了」。但帳上明明寫著「8 個 token 也逾時」,對不上。
- **回頭把帳讀完才看到真相**:成本跟★命中行數★成正比,不是 token 數。6 個 token 命中 835 行要 9.7 秒;10 個 token 命中 1615 行要 14 秒,而預算就是 15 秒;6 個 token 命中 0 行只要 0.3 秒。
- **換常用詞重測就重現了**:四個常用詞全 repo 命中 75587 行、7.17 秒;排除治理與文件兩夾後 7336 行、0.47 秒,**15 倍**。修完實測 8 個常用詞 1.09 秒。
- **語意面也更準,不只是快**:那兩夾是「講程式的文字」不是程式本身,符號被審查報告提到不代表它還活著。排掉之後判「已消失」更貼近事實,方向是更容易示警而不是更容易放過。
- 同步改了提交前守衛的排除清單(既有漂移守衛會逐項比對兩份清單),加一條測試釘住。

### #3 健康檢查收尾行不再比正文樂觀

- 實跑當天上面列了 5 件回訪逾期、5 份驗證引用被翻案的決策、1 張零判定的連鎖單、1 條失效路徑、沒接 linter,尾行仍印「✓ 圖譜健康 — 0 issues」。**五個鏡頭各自獨立撞到這件事。**
- **軟提醒不進判定是既有裁定,沒有動它**——只要求結論行把「還有幾段沒算進來」講出來。
- 計數放在兩個提醒函式的共用層:有一種檢查走「沒有逐條、只有一句」的路徑,只數其中一個會漏掉它。
- **試了兩版把各段標題截斷拼成一句,都很難讀**(「功能筆記從來沒被不知道背景的人重、筆記的 about_code 標」)。最後改成只給數字,細節上面每段都印過了。這一版寫進註解,免得以後有人再試一次。
- 治理帳的事件也帶上這個數字,可重算。測試釘住「收尾行講的段數必須等於實際印出的段數」,不是手寫。

### #8 死碼房務

- **刪掉已撤 hook 的 427 行殘骸**。它 2026-08-22 撤除時換成空殼保留(舊 session 的設定快照還註冊著它,一刀刪會讓那些 session 報錯),相容期兩週早就過了。
- **測試裡寫死該檔名的七處改成合成名字**——測的是「兩階段撤除」這個機制,不是那支檔。★而且相容期清單清空之後,原本的測試會因為「現在剛好沒有任何 hook 在相容期」而測不到東西=靜默失去覆蓋★,所以改成注入合成名字。
- **結案那個 design-only 的取代品節點**(從 2026-06 立案到現在從沒實作,而它要評估的對象已經不存在了)。明寫「不是做完了,是要評估的東西沒了」,而且★當初的問題仍然沒有答案★:圖譜內容會不會腐爛,今天沒有任何機制在管——完整性批評席也把這條列為這輪沒覆蓋到的第二項。
- **方法論文件裡那一整層標成歷史**,它原本還在把已撤的 hook 當現役在教。

## 第二批的代碼審(code-audit-batch2 r1,2026-09-06):我做出一個 blocker

三席 9 條全折零放行,處置閘 PASS。**這輪最重要的不是修了什麼,是我為什麼會做錯。**

- **★blocker:我把硬閘弄鬆了★**。刪除守衛的排除清單跟提交前守衛的豁免清單,有一條既有的漂移守衛逼它們逐字相同。我加了治理目錄到前者,為了讓漂移守衛過,就機械照抄到後者——**結果治理目錄底下 28 支真程式,全部從「改 code 沒動圖譜就擋」的硬閘掉出去**。審查席在乾淨副本實測重現:帶著我的改動可以直接提交,還原那一句就擋下來。
  - **根因不是粗心,是我沒問「這兩份清單是不是同一件事」**。它們語意根本不同:一份是「哪裡不算活著的程式」,一份是「哪些檔改了不必配圖譜」。既有的漂移守衛把它們綁在一起,反而誘導我照抄。
  - **修法**:拆成兩個常數,散文那份明令不得複製到硬閘,並在測試裡釘死「硬閘那一行不得含 governance」。
- **散文清單只認 repo 根**(外家席):原本任何深度同名目錄都排,消費專案的 `src/docs/parser.py`、`packages/governance/rules.py` 很可能是真程式。六種路徑逐一驗過。
- **兩支新測試都被打臉**:①只比對常數不驗行為——審查席把真正的排除判斷寫死成關閉,測試照樣全綠;改成餵真 diff 給解析器。②把所有警告行都當軟提醒——repo 一有普通壞連結就會在產品沒壞的情況下翻紅;改成不重複計硬問題,並實際造一個硬問題驗過。
- **測試污染來源 repo**(外家席):新測試會對來源 repo 跑帶記帳的健康檢查,每跑一次就在工作樹留一筆、帳本持續膨脹。改成原始碼層確認欄位有接上,並**誠實標明這條的證據層級**——值的正確性由畫面斷言涵蓋。
- **收尾行排版分岔**(架構席):用了全檔沒出現過的符號,又把指令接在句尾。改回既有慣例:提醒行用既有符號、指令獨立一行。
- **順手補上一個一直沒人守的洞**(架構席):那條漂移守衛只比對三份同源清單裡的兩份,第三份漏同步不會有任何測試翻紅——而那支檔自己的檔頭就寫著「兩邊不一致會產生幽靈 bypass」。現在三份都比。

## 第三批:#4 暫停誤傷、#5 更新通道兩個真 bug(2026-09-06)

### #4 暫停派工把五段週期觀測一起關掉了

- 開關寫在外層 wrapper、包住整支迴圈腳本,而那支腳本前半有五段便宜的週期觀測(檢索考卷、情境探針、空轉提醒與 14 天升級鏈、回放週跑、backlog 每日衰減)。三處筆記寫著「便宜的日常段照跑」,落地當下那句就是假的。
- **監看的東西和被監看的東西同命**——回訪到期的升級鏈因此沒有出口,那正是同一次審視裡「五件逾期沒人管」的上游原因。
- **裁定 (b) 不是 (a)**:合成席給了兩個選項,一是抽出獨立腳本、二是把開關搬進迴圈腳本。我選後者:不用搬函式(風險低),而且開關剛好只包住真正要停的那一段,符合世界解「toggle 只包最小單元」。
- 實跑驗證:六段觀測全部跑到、backlog 今天實際衰減了一天、派工段照樣停。守衛測試釘的是**相對位置**(所有觀測必須排在開關之前、wrapper 不得再包一層)——用位置而不是真跑,因為真跑會發通知、抽探針、燒配額。

### #5 更新會把全域 hook 換成舊版

- 全域同步跟「設定 hook 路徑」綁在同一支函式,而它排在檔案自癒迴圈**之前**——所以更新會拿更新前的舊副本去覆蓋整台機器的 hook。實測舊版是六月的,而且舊版的設定合併器還會把已撤除的 hook 註冊加回去。
- 修法:拆成兩支,設路徑留在原位、全域同步搬到自癒之後。反事實夾具實測:專案的是舊的、來源是新的,更新後全域那份等於來源。

### #5 來源被自己弄髒導致更新全被擋

- 唯讀的查詢指令就會附加一行到版控中的用量帳。**只要有人在來源目錄查過一次圖譜,這台機器所有專案的更新都被擋住**,而逃生門寫在錯誤訊息最後一行。
- **裁定不採用「把帳本移出版控」**——那些帳本本來就該進版控,是治理紀錄,`lumos gov` 讀歷史、回放凍結都引用它們。
- **第一版用暫存還原,實測會在帳本裡留下衝突標記**——兩邊都往同一個檔尾附加,還原必衝突,而帳本一有標記之後每次讀都炸。**那比原本擋住更糟。**
- **定案:聯集合併**。這幾本是 append-only 的 JSONL,正確解是把兩邊的行取聯集:本機那份讀進記憶體 → 還原到已提交版 → 拉 → 把本機獨有的行補回去。非 JSONL 的簿記檔(設定基準線是一份 JSON 物件)不能這樣併,照原路擋下並說明。
- **順帶抓到兩件**:①簿記白名單漏了兩本工具自己寫的帳(kill/signoff),補上;②暫存會建 commit 物件所以需要 git 身分,機器沒設全域身分時會靜默失敗——這條在改成聯集合併後不再相關,但當時是真的踩到。

## 第三批的代碼審(code-audit-batch3 r1,2026-09-06):兩個 blocker,而且我第一版的修法自己有 bug

三席 13 條全折零放行,處置閘 PASS。**這輪抓到的東西比前兩批更嚴重,因為錯在我為了修 bug 而寫的新程式碼裡。**

- **★blocker:資料會靜默遺失★**。聯集合併用「集合判有沒有」,而帳本是事件序列不是集合。審查席對本 repo 實際量:治理帳有 487 行內容完全重複、用量帳有 8 行,其中某筆查詢在同一秒出現三次是三次真的呼叫。遠端剛好也加了同樣一行時,本機那筆會被當成重複吃掉。改成用計數,而且**比較對象要是「拉之前的已提交版」不是「拉下來的內容」**——這一點是我自己補的重複行測試跑出 2 份而不是 3 份才抓到的。
- **★blocker:我的錯誤訊息在說謊★**。備份只存在記憶體,被中斷或寫回失敗就永久消失,而訊息叫人用 git 指令救——**未提交的內容從沒進過 git 物件庫,那句話是假的**。改成動手前先落磁碟備份,全部併回成功才刪,訊息改成指向真的備份路徑。
- **major:只修了一半**。一鍵安裝那條路仍呼叫舊的合併外殼,會拿可能很舊的專案副本覆蓋剛裝好的全域 hook,完整重現原 bug;而且我寫的 docstring 還指錯了誰是安全的呼叫者。
- **major:全新機器會在裝好當天燒配額**。外層改成無條件呼叫之後,沒有任何歷史的機器會立刻抽八題探針。改成第一次先蓋印記、下週開抽。
- **★major:我補強過的測試仍然假綠,審查席實測證明★**。把暫停區塊裡的離開動作拿掉、只留判斷和訊息,暫停就變成什麼都不做、派工每天照跑,而我的十二條位置斷言全部照過。改成:①判斷的身體裡必須真的有離開動作;②**真跑一次**,用金絲雀確認派工段沒被執行到;③**反面也跑**,證明金絲雀在開關關掉時抓得到——不然那條斷言可能是恆真的。
- 兩條 minor(白名單缺日期理由註解、測試改用子行程沒寫理由)也折了。

**這輪的教訓**:修 bug 寫的新程式碼,跟原本的程式碼一樣需要被審。三個 blocker 級的問題全部在我這次「修法」裡,不在原本的碼裡。

## 第三批推上去之後 CI 紅了一次(2026-09-06)

- **紅的是我新加的測試,不是產品**。夾具用一個裸倉庫當共同遠端,而我讓它 HEAD 指向 `main`——**本機的 git 預設分支是 main,CI 上是 master**。HEAD 指到不存在的分支時,複製出來是空工作樹、只印一行警告就過去了,於是夾具靜默壞掉、測試在後面用一個「找不到檔案」的例外表現,看起來像產品壞了。
- **修法兩件**:①建裸倉庫後明確把 HEAD 指到我們真的會推的分支;②**夾具建不起來要大聲說**——加一條「複製後拿得到檔案」的斷言,而不是讓它在後面丟例外。在模擬 CI 預設分支的環境驗過。
- **順手修 `ci-wait` 的誤報**:它等一個窗(30 秒)沒看到 run 就判「沒有觸發任何 workflow」,而家規明說 no-run 不算過。實測那次 14:02 推、14:15:46 才出現 run。改成連等三個窗才下結論,訊息也改成講「等了多久沒看到」而不是斷言「沒有觸發」。
- **★沒有完全診斷清楚,誠實記★**:那次 `ci-wait` 從 14:02 跑到 14:18 卻仍回 no-run,單靠「加等待窗」未必解釋得完(可能是查詢的分支/sha 條件、或 API 回傳延遲)。REVISIT:2026-10-06 看治理帳上還有沒有 no-run 出現;有的話要真的去追查詢那一段。

## CI 第二次紅:我改了預設行為,卻只跑了關鍵字子集(2026-09-06)

- **紅的是另一支測試檔**(自主迴圈那套,8 失敗 1 錯誤),不是我一直在跑的主測試檔。原因:我把派工段的暫停開關改成★預設開啟★,而那 132 支測試整組驗的就是派工段的行為——它們在「派工根本沒執行」的狀態下比對輸出,全部紅。
- **另有一個我引進的真 bug**:探針的「首次執行先不抽」守衛,在全新機器連 scenarios 目錄都還沒有時,附加檔案會炸。夾具正是那種狀態,所以順帶炸出來。已補建目錄並讓寫入失敗也不阻斷。
- **修法**:那組測試明示設定關掉暫停,不靠環境預設。**紅在環境預設而不是被測行為,是最難查的那種**,所以在測試裡寫明為什麼要明示。
- ★教訓★:專案規矩說「改完先跑相關子集、全套留給推送前的閘」,但**推送前的閘只跑主測試檔,另一支是 CI 才跑的**。我改的是預設行為,影響面不在關鍵字裡。以後動到預設值或開關語意,要把兩支測試檔都跑過再推。**這條當場修掉了**:推送前的閘現在兩支都跑(第二支只要 12 秒),各自紅了各自擋,並加測試釘死 [test:t_prepush_runs_both_test_files]。

## 主題 #20(收貨線指令化)★停案★ — 2026-09-06

走了完整設計審,五席一輪就把設計打穿:正確性 1 blocker+3 blocking major、邊界與失敗 1+3、外家 Codex 4 blocker、必要性 1 blocking major、架構對齊 2 minor。**我裁停案,不是修一修再跑一輪。** 完整裁定與六個理由在 [[Projects/收貨線指令化_計劃]]。

★這輪對我自己最有價值的三件★:
- **我把潛在風險寫成既遂事故**。低報事故實際為零(398 筆帳列首驗過),而急迫性正是我用來跳過「先驗證更小解」的理由。
- **病灶在我的派工詞,不在缺工具**。事實反方查證指出 09-05 那次三席吐錯格式不是模型天生行為,是我自己的派工詞要求的,正確格式早就寫在範本裡。
- **圖譜裡兩天前就有更小更對症的候選,我漏查**。我的圖譜攔截只比對了三天前的停案,漏掉同題材、更直接相關的那份調研。

改做三件更小的:①修派工詞 ②刪那支含「讀不到就補成乾淨」分支的臨場腳本 ③修錨定器把散文短括號當引句的假失敗。S3(派工單家族欄位)另立小案。

## 停案換來的三件,代碼審 r1(2026-09-06):第三件當場撤回

三席 12 條全折零放行,處置閘 PASS。**但這輪最重要的結果是「撤回」,不是「修好」。**

- **★第三件(補引句錨定的洞)撤回★**。我的修法既沒補起洞、又打壞既有卷證:
  - 外家席實測:不用巢狀,把編造的字放在第一個閉引號**之後**就照樣通過。我自己重現了。
  - 通才席另指出一種更容易無意寫出來的形態:引句裡有一個落單的收尾符號時,抽到的前綴括號數是 0 比 0,守衛完全看不出來。
  - **回歸實測**:帳本裡可讀的 613 組報告與快照,**148 組(24%)**會從通過變成判錯;通才席另從回放角度算出 114 組會被誤報成「邏輯漂移」。
  - **半吊子的修法比不修更糟**:給人「已經補起來了」的錯覺,同時把四分之一的歷史證據判成無效。改立事故筆記 [[Issues/引句錨定只驗前綴_後半可編造]],把四條結構性前提寫給之後真的要修的人。
- **★通才席教我一件我沒想過的事★**:改判準必須同時推進回放引擎版本,否則週跑抽查會把「規則升級」誤報成「邏輯漂移」。它實跑一個已凍結的迴圈,現場印出漂移訊息並 exit 1。
- **★我又犯一次今天早上才記下的錯★**:凍結審材時用路徑過濾排掉整個審查報告目錄,於是三席看不到我刪那支腳本的 diff——而那正是第二件的全部內容。架構席判 blocker,引的正是我自己早上寫的那句教訓。已重新凍結收進去。
- **第二件的守衛也改了**:原本靠檔名關鍵字(改叫 clean.py 就繞過、正當同名檔又誤傷),改成「卷證目錄裡不該有任何腳本」——卷證是證據不是程式。**誠實記:這條仍是目錄範圍的,把腳本放到別的目錄仍繞得過。**
- **說明書自相矛盾也修了**:新增的第 2 步說「收貨正規化這件事就不存在」,而沒改動的第 3 步還寫著「存席報告先正規化」。第 3 步改成「席報告原樣存檔,格式不對就退回該席重寫——編排者改席報告等於改證據」。

## 第四批:#13 假綠跳過、#15 說明書單源化、#16 開頭欄位守衛(2026-09-06)

### #13 把偽裝成通過的跳過改走正式通道

- 十處「條件不成立就印一條綠然後 return」全部改走既有的跳過通道,現在誠實顯示成 skip 而不是 pass。**最貴的一處**:全套唯一那條檢查工具是否為現行版本的斷言,CI 從第一天起就沒跑過本體,而當天的提交訊息寫著「測試覆蓋各分支」。
- **加一條機械守衛**:跑完卻一條斷言都沒有就判紅。理由跟「關鍵字選中零支判紅」一樣——**綠燈必須代表「驗過而且過了」,不能代表「什麼都沒發生」**。
- ★這句原本寫錯,代碼審 r1 訂正★:我當時寫「全套零命中,表示既有測試沒有零斷言的,改動安全」——**是錯的**。那次在 POSIX 機器上跑,五處「印 skip 後直接 return」的舊寫法根本走不到,所以掃不出來。真在 Windows 上跑,那五支會被我自己新加的守衛判紅,而它們本來就是合法跳過。三席代碼審獨立指出同一件事。
- **改成機械盤點**:寫了一支靜態掃描,逐支測試比對「任何 return 之前有沒有跑過斷言」,掃出 8 處(三處這批新改的 + 五處既有的),跟三席點名的不多不少。八處全部改走跳過通道,重掃 0 處。**掃描本身已落成守衛測試(含反面:刻意搭一支零斷言的假測試,掃描器要抓得到)**,往後不靠人工盤點。
- ★誠實記★:這台不是 Windows、又是來源 repo,所以那些跳過分支這次仍走不到;它們的行為要等在別的環境才驗得到。上面那個錯誤正是這件事的代價。

### #15 說明書單源化

- 兩份頭版都寫著「Codex 對照單源=範本」,卻各抄一整段同樣的版本事實——說是單源實際三份,版本行為一變要改三處。砍掉兩份的重複段只留指標,從三處變一處。
- **加守衛並反向驗過**:宣稱單源的頭版不得再出現版本號;把版本事實抄回頭版,守衛翻紅。
- ★代碼審 r1 訂正★:守衛原本寫死認 Codex 現在的版本形狀(0.1 開頭、三位數),**版本一過 0.199 這條守衛就靜默失效,而且要求單源檔必須命中的反面斷言會同時假紅**。放寬成任意三段式版本號又會誤中別的數字,所以改成鎖「同一行既有版本號、又在講 Codex」——被抄的那段內容本來就長這樣,不靠版本形狀猜。

### #16 開頭欄位打錯要出聲

- 鍵打錯(valid_unde / verifed_by)會被所有檢查靜默略過,那個欄位等於沒寫。加軟提醒與近名候選,實測提示正確。
- **照合成席的三個限制做**:只給提醒不升 error(前向相容立場)、清單可用設定檔擴充(別的 vault 有自己的欄位)、不擋舊帳。反面也驗:正常欄位不被誤唸、設定檔列進去就不再唸。
- ★代碼審 r1 折入兩條★:①已知鍵清單當初是「掃本 vault 428 篇出現過的鍵」建的,漏掉兩個工具真的會讀、但本 vault 剛好沒節點寫的欄位(跨專案升格參照、重建溯源)——被誤報時提示文字說「它不會被任何檢查讀到」,**這句話本身是假的**。正解是問工具認得哪些,不是問這個 vault 長怎樣,所以改成執行期併入工具既有的欄位常數,那兩份常數之後再加欄位這裡不必跟著改。②設定檔路徑寫死「往上兩層」,vault 巢得更深(monorepo 佈局)就算到錯的地方,**擴充口悄悄失效且不報錯**;改成從 vault 往上找設定檔本身,走到版控根就停,免得爬到家目錄撿到別的專案的設定。兩條都補了測試。
- ★我量錯兩次才對★:先用「同行為空」數出 78 篇缺回頭條件,實際那是 YAML 清單寫法、值在下一行;**正確數字是 0 篇空值、7 篇連鍵都沒有**,而合成席原本說的 12 篇空值也不對。數開頭欄位一定要把區塊式寫法算進去。

### 代碼審 code-audit-batch4(r1,3 席)

- **r1(2026-09-06,3 席:通才 / 架構對齊 / 外家 Codex):6 條 / blocking 5 / 全數折入,accepted 0。** 三席獨立指向同一條主線——我用人工盤點下的「零命中所以安全」結論是錯的,而且錯得有系統:在 POSIX 機器上驗不到非 POSIX 分支。
- 席報告與收貨留痕:`governance/review-reports/code-audit-batch4/`
- ★這輪的教訓★:**同一天內我第二次犯「只信一個來源」**(前一次是把清單寫法數成空值)。這次是「只在一台機器上跑=只有一個來源」。兩次的解法一樣:改成機械盤點,並把盤點器本身變成守衛。
- 收貨時有 2 句引言錨不回凍結快照,原因是它們引的是**既有碼**(用來說明「專案本來就有這個做法」),不在 diff 裡。逐句用真檔重現皆 HIT,留痕在收貨檔;不是編造。

### 兩家適配核對(Codex / Claude Code)

Enzo 2026-09-06 指出:這批優化要同時適配兩家。逐件核過,**不是靠推論,是逐條指出落點**:

| 這批改的東西 | 落在哪 | 兩家都吃得到? |
|---|---|---|
| 開頭欄位軟提醒、設定檔擴充口 | `lumos` 這支 CLI | ✅ 同一支程式,兩家都是敲它 |
| 跑完零斷言判紅、跳過通道 | 測試檔的執行器 | ✅ 由 git 的推送前閘叫起來,跟哪一家開的無關 |
| 單源紀律守衛 | 原本只掃 skills | ⚠️ **有破口,已補**(見下) |

- **skills 兩家共用**:安裝時把同一份來源同時連進兩家各自的 skill 目錄,已有機械守衛盯著(外方同名目錄不刪、解除時只清自己的)。所以寫在 skills 裡的規矩兩家都吃得到。
- **★補掉的破口★**:單源守衛原本只掃 skills 的頭版,漏了**兩家各自的入口檔**——Codex 讀專案根的 `AGENTS.md`(有 override 檔就只讀 override),Claude 讀 `CLAUDE.md`。版本事實抄進這兩個檔一樣會漂,而守衛看不到。已把三個入口檔納入掃描,並加三條反面斷言(入口檔真的在掃描清單裡、抄一行進去會被抓到)——**免得因為檔名寫錯掃了個不存在的檔,守衛假綠**。
- **另外機械核過**:這批 diff 裡所有提到家族名稱的地方,都只是在講「被抄的那段內容是關於 Codex 的」,**沒有任何一條是「只有某一家才走到」的執行分支**。所以其餘改動是結構上共用,不是我推論共用。

## 第五批:#11 測試地基——真機隔離(2026-09-06)

### 症狀先量到,不是照描述動手

- **真機被動**:那兩支 install 測試跑之前跑之後對照家目錄,**連結的 inode 從 37184038 變成 37197577**——是刪掉重建,不是只碰時間戳。Claude 與 Codex 兩家的 skill 目錄都中。指令留在下面,可以自己重跑。
- **暫存殘骸**:系統暫存目錄底下 **345,209 個** 測試殘骸(連 `ls` 都會卡)。

觀測方式(記下來,因為它就是「會對症狀翻紅的那道指令」):跑測試前後各記一次那幾個路徑的 inode 與時間,再 diff。修完之後同一道觀測要變成「沒差異」——這是驗收條件不是感覺。

### 修在唯一進入點,不在每支測試各自處理

理由跟這個檔案先前清 git 環境變數同一條:替代方案是「每支會碰家目錄的測試各自隔離」,那是幾十個呼叫點的簿記,**天生會漏——這個專案已經漏過兩次**(2026-08-01 刪掉真機 hook、2026-09-02 重連真 skills)。兩次之後「假家目錄是最低門檻」都只寫在事故筆記裡,沒有任何機制擋住。

關進去的東西:家目錄、暫存目錄(**父子進程都要**,測試大量用子進程,父隔離子沒隔離等於沒隔離)、還有那個會繞過假家目錄直接打到真 Codex 設定的環境變數。假家目錄裡先塞一份最小的 git 身分設定,免得測試裡的 git 指令噴錯。

### 加了自證測試

它驗的不是某支測試乖不乖,而是**整個執行器有沒有把現場關起來**——隔離被拆掉立刻紅,不必等到誰的開發機再被洗一次。含子進程那一面。

### 兩支 install 測試的語意變了,寫在它們自己的說明裡

它們現在驗「安裝會在家目錄下建對的連結」,**不是「這台機器真的裝好了」**——後者本來就不該由測試保證。順手補了 Codex 那邊 skill 目錄的斷言(原本只驗 Claude 那邊)。

### ★做的過程自己踩一個,而且它比原題目更值得記★

我把一個環境變數設錯了:那個變數叫起來像「lumos 的家目錄」,**實際是「lumos 來源 repo 在哪」**。設成假家目錄之後,有一支測試找不到來源就跳過了。

**全套照樣印「零紅」** ——是我去比跳過數字從 0 變 1 才發現。所以多加一條基準線:跑全套時跳過支數超過預期就出聲,訊息裡講清楚要先分辨「環境本來就跑不到」還是「有人把現場弄壞了」。

理由:**紅燈會叫你,跳過不會。** 「本來跑得到、現在跑不到」等於覆蓋悄悄少掉,而它在原本的輸出裡完全無聲。這跟同一輪做的「跑完零斷言判紅」是同一條原則的另一面——綠燈要代表驗過,**而不再驗的東西要有人喊**。

### 暫存修剪刻意保守

只清「已標記結束」或「超過一天沒動」的本輪型根目錄,而且不按數量硬刪——**因為 hook 會平行起執行器,刪掉別人正在用的目錄就是製造假紅**。既有那 34.5 萬個舊殘骸是另一種前綴,另外清掉。

### 這批沒做的(誠實記)

主題原本還列了去重(七處子進程字串抽共用、十幾處行內動態載入改用既有工具、環境變數組裝抽一支)。**這次沒做**——它們是可讀性收益,不影響行為,而這批的價值全在安全面。留在主題清單裡,不假裝做完了。

### #23 ★這次明文不做★

合成席自己寫了前提:必須排在另一件既有事項(回頭日期 09-12)之後。**現在做只會把一則已知噪音推上每週通知,正是那件事點名的「提醒麻痺」。** 順序反了會讓事情變糟,所以留待 09-12 那批一起做。

