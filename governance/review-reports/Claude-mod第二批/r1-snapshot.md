---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-06
tags:
  - type/project
  - status/doing
  - scope/agent-dag
lands_in:
  - Systems/lumos-context
decisions:
  - content: 第二批 mod 做五項:壓縮前保住交棒狀態、會談編號交給 lumos、審查員有沒有照實讀、Bash 改檔前推筆記、開場標出驗證不過的記憶;壓縮前與記憶標記放新外掛 lumos-context,不放只觀察的事件帳。考慮過:①連 lumos 自己派代理一起做(推送前的擋已逼編排者跑審查,自動派只多省一點額度,Enzo 裁拿掉);②壓縮後重新注入規矩(官方會談開始 hook 壓縮後本來就會再跑);③Bash 改檔前推筆記用 mod 做(官方 PreToolUse 做得到,另寫 TS 是第二種做法)。Enzo 2026-10-06 裁。代價:三件會改模型看到的文字,可能讓提示快取失效一次;mod 介面是搶先版,改版可能壞。
    id: d1
    decided: 2026-10-06
    valid: true
  - content: 審查員有沒有照實讀:從事件帳核對席位讀過的檔與報告引用,另記派工詞有沒有帶到派工鏡頭附加段——推翻派工鏡頭注入計劃開案決策裡的「不驗不記」;仍不量成效(有沒有因此審得更好)。考慮過:①維持不驗(席位偽造或憑印象引用目前只靠人工抓);②連成效一起量(派工鏡頭計劃 2026-09-03 四份計劃死在想證明清單有用,不重蹈)。Enzo 2026-10-06 裁做。代價:只提醒不擋,寬口徑判讀過會漏報。
    id: d2
    decided: 2026-10-06
    valid: true
  - content: 記憶清掃 hook 改成每次把結果寫進 lumos 自己的快取資料夾(按會談編號分檔),外掛讀它在記憶索引行首加標記——部分翻案記憶清掃 2026-09-14 的「唯讀」設計:當年三輪 blocker 全落在寫進記憶檔(路徑穿越、符號連結、硬連結、檢查到寫入的時間差、撤章刪欄位),這次寫的路徑由 lumos 自己組、不從記憶內容推、不碰記憶資料夾,先寫暫存再原子換名。考慮過:①外掛在 TS 重做一份清掃(兩套判準會漂);②外掛直接叫 Python(外掛介面沒有執行外部程式的能力);③不做標記、只靠開場那段文字(就是現況,壓縮後模型常忽略)。編排者 2026-10-06 提案,交設計審檢視。代價:多一個寫檔點,要守住只寫快取資料夾。
    id: d3
    decided: 2026-10-06
    valid: true
---
# Claude-mod第二批_計劃

白話:Claude Code 的 mod(外掛裡的函式掛鉤)能做到幾件設定檔 hook 做不到的事。這批挑五件跟 lumos 治理直接有關的:壓縮對話前叫摘要保住交棒狀態、把當下的會談編號交給 lumos、核對審查員有沒有照實讀過它引用的檔、用 Bash 改檔前也推筆記、開場載入記憶時把驗證不過的條目標出來。第一支 mod(事件帳 [[Systems/lumos事件帳]])只觀察;這批有三件會改模型看到的內容,所以另開一支 `lumos-context`,不放進只觀察的事件帳外掛。

PRIOR-ART: 最小解在 Claude Code 的外掛函式掛鉤。官方設定檔 hook 2026-10-06 核對原文:壓縮前那支只能讀到摘要指示、改不了(只能整個擋),壓縮後那支只能旁觀;會談開始那支在壓縮後也會跑、能補內容,lumos 三支開場 hook(入口、CI 狀態、記憶清掃)沒設觸發條件,照官方文件壓縮後會再跑一次(未實測)。所以壓縮後重新注入規矩不必用 mod,mod 獨有的是「壓縮前改摘要指示」。外掛寫法、市集、測試沿用事件帳(核心邏輯可注入、`claude plugin test`、條款以測試標題開頭綁)。審查員讀了哪些檔不另做觀察:事件帳已經逐筆記下每個子代理的工具呼叫與路徑,lumos 讀它即可;但事件帳只記 Read 的檔、Grep/Glob 的搜尋根目錄、Bash 指令前 500 字,記不到搜尋命中哪些檔。

RETIRE-IF: ①上線兩個月內,壓縮後的交棒狀態仍要人重講、或摘要指示從沒被用上(事件帳看得到壓縮事件)——摘要器不照指示做,這段不值得維護;②`LUMOS_SESSION_ID` 跟 `CLAUDE_CODE_SESSION_ID` 在接續、`/clear` 後也一致(官方修好)——第二項撤掉;③核對引用一個月內零次抓到不實引用,而且收貨人工核對也沒抓到——第三項撤掉;④官方 hook 開始支援壓縮前改指示或改記憶內容——對應那項改走官方。

## 範圍

- **做**:
  1. **壓縮前保住交棒狀態**:新外掛 `lumos-context` 掛 `session.compact`,在既有的摘要指示後面附一段固定要求(三種觸發都附,含預先計算 `precompute`;已附過就不重附)——逐字保留使用者在對話裡下的裁定與指示、目前在做的計劃節點與步驟、還在跑或剛收齊的審查席、還沒提交或還沒推的改動、待回覆的問題。主會談與子代理都附(子代理附精簡版:保留它的任務與已得結論)。
  2. **會談編號交給 lumos**:`lumos-context` 掛 `turn.start`,每個回合開始時用 `$.env.set` 把 `$.session.id()` 設進 `LUMOS_SESSION_ID`;lumos 需要會談編號的地方(目前只有 `handoff` 排除接手者自己那一處)先讀它,沒有才退回 `CLAUDE_CODE_SESSION_ID`。後者在會談接續、`/clear` 後會停在舊值(2026-10-06 本會談實測:接續後環境變數仍是接續前的編號)。
  3. **審查員有沒有照實讀**:事件帳的 spawn 事件加記派工詞第一行的席位標記(`LUMOS-SEAT:` 後面那串)、有沒有派工鏡頭附加段、派工詞長度,不記其他內容;`lumos seat-check` 加 `--events <會談編號>`(既有的 `--ledger` 是越界帳,不共用),用席位標記找到那一席的子代理,抽報告裡 ``file: `路徑:行號` ``(新寫一套抽取;既有的只抽引句)與引句所在檔,列出席位從沒讀過的。只提醒、不擋,印進收貨流程。
  4. **用 Bash 改檔前推筆記**:擴充既有的改檔前推筆記官方 hook(PreToolUse),連同安裝端把觸發條件從 `Edit|Write|MultiEdit` 加上 `Bash`,讓它也認 Bash:指令裡有寫檔形狀(`>`、`>>`、`tee`、`sed -i`、`cp`/`mv` 的目的端、heredoc 寫檔)時,對目的路徑做同樣的推送(Bash 沒有改前改後的文字,查詢詞只用路徑)。Codex 那邊不動。不用 mod:官方 hook 做得到,mod 只省每次啟動 Python 的開銷;既有的推送邏輯、測試與預算都在 Python 那支,另寫一套 TS 是第二種做法。
  5. **開場標出驗證不過的記憶**:記憶清掃 hook 每次跑完(沒事也寫)把結果(會談編號、哪幾篇記憶檔、什麼原因)寫進 lumos 自己的快取資料夾,按會談編號分檔、只寫不讀記憶檔以外的路徑(見決策 d3);`lumos-context` 掛 `prompt.context`,改 `instructionFiles` 裡記憶索引那一份的內容,用索引行裡的檔名連結對到記憶檔,在那幾行行首加上 `⚠ 已過期或與圖譜對不上:<原因>`。只加標記,不刪內容;開場、壓縮與 `/clear` 後重算時都會跑。
- **不做**:
  - lumos 自己派代理(2026-10-06 本會談列的 mod 候選清單第 7 項,沒進任何計劃節點;Enzo 2026-10-06 裁拿掉:推送前的擋已經逼編排者去跑審查,自動派只多省一點額度)。
  - 壓縮後重新注入規矩:官方會談開始 hook 壓縮後本來就會再跑,CLAUDE.md 與記憶索引壓縮後也會重讀。
  - 審查席隔離(另一條分支,停在代碼審第二輪)。
  - 改寫或刪除記憶內容:只加標記,真相仍在圖譜。

落點:新開 `Systems/lumos-context`(管新外掛);其餘落在 [[Systems/lumos事件帳]](spawn 事件欄位)、[[Systems/design-loop]](`seat-check`)、[[Systems/記憶過期清掃]]、[[Systems/改檔前推播]]、[[Systems/lumos-cli-lifecycle]](安裝端觸發條件與外掛清單)。

## 做法要點

- 第 1 項的附加段固定一份文字放在外掛裡,不呼叫外部指令;原本就有指示(使用者打 `/compact <文字>`)時接在後面,不覆蓋。
- 第 2 項:`$.env.set` 只影響之後啟動的程式,型別檔不保證已開的 shell 看得到。Bash 工具若沿用一個早就開好的 shell,可能讀不到新值——實作前先用 `claude -p` 實測(派一個回合,Bash 印 `$LUMOS_SESSION_ID`,再 `/clear` 或接續後印一次);讀不到就改成外掛把編號寫進以 `CLAUDE_PID` 為名的小檔(`CLAUDE_PID` 在接續後不變),lumos 讀檔。
- 第 3 項判「讀過」的口徑寬:同一檔有任何一次 Read、或在某次 Grep/Glob 的搜尋根目錄底下(沒帶路徑就算會談工作目錄底下全部)、或出現在 Bash 指令前 500 字裡,就算讀過。寧可漏報不誤報;那一席有 Bash 指令被截斷時,結果標「可能誤報」。席位自己再派的子代理不算進來。
- 第 3 項實作前先實測:派工鏡頭 hook 用 PreToolUse 改寫派工詞,事件帳在 `agent.spawn` 看到的是改寫前還是改寫後。看不到附加段,就把「有沒有鏡頭段」從條款拿掉、在決策 d2 註明,席位標記照記。
- 第 5 項的標記只對結果檔裡列名的記憶檔;結果檔不存在、格式不對、或會談編號跟 `$.session.id()` 不同,就整份不動。快取資料夾只留七天內的檔。記憶清掃 hook 跟 `prompt.context` 誰先跑型別檔沒說,實作前實測;外掛先跑就讀不到檔、整份不動,不會標錯。
- 第 4 項實作時量:不帶寫檔形狀的 Bash 多付一次 Python 啟動要多久,量到的數字寫進驗證筆記。

## 條款

外掛行為的條款綁在 `mods/claude/lumos-context/hooks/context.test.ts`,測試標題以條款編號開頭,用 `claude plugin test mods/claude/lumos-context` 在本機跑。

- [S1] 當對話壓縮(`session.compact`)時,外掛應在摘要指示後附上交棒要求段;原本有指示時接在後面、原文不變;子代理附精簡版 [manual:claude plugin test mods/claude/lumos-context 的 S1 測試全綠]
- [S2] 當回合開始時,外掛應把當下會談編號設進 `LUMOS_SESSION_ID`;`/clear` 換編號後下一個回合應換成新值(Bash 讀得到要等 `claude -p` 實測過;讀不到就改綁 `CLAUDE_PID` 小檔的備案) [manual:claude plugin test mods/claude/lumos-context 的 S2 測試全綠]
- [S3] 當 lumos 需要會談編號時,應先讀 `LUMOS_SESSION_ID`,沒有才讀 `CLAUDE_CODE_SESSION_ID` [test:t_session_id_prefers_lumos_env]
- [S4] 當 `seat-check` 帶 `--events` 跑,報告的 `file:` 引用或引句所在檔是席位從沒讀過的,應列出那幾條;讀過(Read、搜尋根目錄底下、Bash 指令前 500 字裡出現)的不列;事件帳找不到那一席時說清楚、不擋 [test:t_seat_check_reads_from_events]
- [S5] 當事件帳記 `spawn` 事件,應多記派工詞第一行的席位標記、有沒有派工鏡頭附加段、派工詞長度,不記其他內容 [manual:claude plugin test mods/claude/lumos-ledger 標題以「第二批 S5」開頭的測試全綠]
- [S6] 當主會談用 Bash 寫檔(重導、`tee`、`sed -i`、`cp`/`mv` 目的端、heredoc 寫檔),改檔前推筆記應對目的路徑推送,跟 Edit/Write 同一套;只讀的 Bash 不推 [test:t_impact_hook_bash_writes]
- [S7] 當載入記憶索引且同一會談的清掃結果檔列了某幾篇,外掛應只在對到那幾篇的索引行行首加上過期標記;結果檔不存在、格式不對或會談編號不同時應整份不動 [manual:claude plugin test mods/claude/lumos-context 的 S7 測試全綠]
- [S8] 當記憶清掃 hook 跑完(含沒有發現),應把會談編號、記憶檔與原因寫進 lumos 快取資料夾裡以會談編號命名的檔;不寫進記憶資料夾或其他路徑 [test:t_memory_sweep_writes_machine_result]
- [S9] 當 `lumos install` 與 `uninstall` 執行,外掛清單應含 `lumos-context`,各自裝上與移除 [test:t_install_registers_context_plugin]

## 回退

- 把 `lumos-context` 從外掛清單與市集檔拿掉,下次 install / update 就會移除;第 2、3、4、5 項的 Python 改動各自獨立,`git revert` 那段即可;記憶清掃的結果檔是衍生資料,刪掉不影響任何東西。

## 實務隱患

- 已排除:金流:不碰付款
- 已排除:對外送出:外掛不呼叫網路;Python 端改動只讀本機事件帳與檔案
- 已排除:不可逆:只附加文字與標記、設環境變數;唯一的寫檔是 lumos 快取資料夾裡的衍生結果,不刪不改既有檔;拿掉外掛即回到現狀
- 守衛面:第 3 項只提醒不擋;第 6 項沿用既有推送 hook 的預算與失敗即放行
- 效能:第 1、5 項只在壓縮與開場各跑一次;第 2 項每回合一次 `$.env.set`;第 4 項每次 Bash 都多一次 Python 啟動,只在帶寫檔形狀時才查圖譜(數字實作時量)
- 快取:第 1、5 項會改模型看到的文字,可能讓提示快取失效一次
REVISIT:2026-11-06 用事件帳比對上線前後同長度會談的快取命中,確認第 1、5 項有沒有讓快取多失效
REVISIT:2026-11-06 用事件帳數這一個月壓縮次數、seat-check 抓到幾條沒讀過的引用、Bash 改檔推送次數,看哪項沒用上
