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
  - content: 第二批 mod 做三項:壓縮前保住交棒狀態、會談編號交給 lumos、核對審查員引用的程式檔有沒有真的讀過(縮小版);前兩項放新外掛 lumos-context,不放只觀察的事件帳。設計審第一輪後 Enzo 2026-10-06 裁縮小:原本五項另有 Bash 改檔前推筆記(拿掉:改觸發條件弄壞 Codex 轉換與舊安裝、列舉寫檔形狀違反「列舉補不完」既有決策、不是 mod 能力)與開場標出驗證不過的記憶(另開題:拿不到會談編號、要翻記憶清掃唯讀守衛、標記文字有注入疑慮)。更早考慮過:lumos 自己派代理(推送前的擋已逼編排者跑審查,Enzo 裁拿掉);壓縮後重新注入規矩(開場 hook 壓縮後本來就會再跑)。代價:第 1 項改模型看到的摘要指示;mod 介面是搶先版,改版可能壞。
    id: d1
    decided: 2026-10-06
    valid: true
  - content: "核對審查員引用的程式檔有沒有真的讀過:事件帳 spawn 事件記席位標記,seat-check 從事件帳核對 file: 引用——推翻派工鏡頭注入計劃開案決策裡的「不驗」,也部分推翻 seat-check 自己「repo 查證的 file: 引用一律合法」的設計(只對圖譜以外的檔、而且帳完整時才判);仍不量成效、不記派工詞有沒有鏡頭附加段。考慮過:①維持不驗(席位憑印象引用目前只靠人工抓);②連成效一起量(派工鏡頭計劃 2026-09-03 四份計劃死在想證明清單有用);③連引句與圖譜筆記一起核(引句要先找所在檔、筆記常由派工自動附上,事件帳都看不到,誤報多)。Enzo 2026-10-06 裁做縮小版。代價:只提醒不擋;沒帶路徑的搜尋算整個 repo 讀過,放行偏寬,另印條數。"
    id: d2
    decided: 2026-10-06
    valid: true
  - content: 記憶清掃 hook 改成每次把結果寫進 lumos 自己的快取資料夾(按會談編號分檔),外掛讀它在記憶索引行首加標記——部分翻案記憶清掃 2026-09-14 的「唯讀」設計:當年三輪 blocker 全落在寫進記憶檔(路徑穿越、符號連結、硬連結、檢查到寫入的時間差、撤章刪欄位),這次寫的路徑由 lumos 自己組、不從記憶內容推、不碰記憶資料夾,先寫暫存再原子換名。考慮過:①外掛在 TS 重做一份清掃(兩套判準會漂);②外掛直接叫 Python(外掛介面沒有執行外部程式的能力);③不做標記、只靠開場那段文字(就是現況,壓縮後模型常忽略)。編排者 2026-10-06 提案,交設計審檢視。代價:多一個寫檔點,要守住只寫快取資料夾。
    id: d3
    decided: 2026-10-06
    valid: false
    superseded_by: "#d1"
    ended: 2026-10-06
---
# Claude-mod第二批_計劃

白話:Claude Code 的 mod(外掛裡的函式掛鉤)能做到幾件設定檔 hook 做不到的事。這批挑三件:壓縮對話前叫摘要保住交棒狀態、把當下的會談編號交給 lumos、核對審查員引用的程式檔有沒有真的讀過。第一支 mod(事件帳 [[Systems/lumos事件帳]])只觀察;第 1、2 項會改模型看到的內容或環境,所以另開一支 `lumos-context`,不放進只觀察的事件帳外掛。設計審第一輪後縮小範圍(見決策 d1)。

PRIOR-ART: 最小解在 Claude Code 的外掛函式掛鉤。官方設定檔 hook 2026-10-06 核對原文:壓縮前那支只能讀到摘要指示、改不了(只能整個擋),壓縮後那支只能旁觀。外掛寫法、市集、測試沿用事件帳(核心邏輯可注入、`claude plugin test`、條款以測試標題開頭綁、Python 端掃外掛原始碼的結構測試)。審查員讀了哪些檔不另做觀察:事件帳已經逐筆記下每個子代理的 Read 路徑、Grep/Glob 的搜尋根目錄、Bash 指令前 500 字;記不到搜尋命中哪些檔,所以核對只做最窄的一層。`file:` 引用的抽取沿用 refcheck 的抽取函式。

RETIRE-IF: ①上線兩個月內 Enzo 仍得在壓縮後重講交棒狀態——摘要器不照指示做,第 1 項撤掉;②`CLAUDE_CODE_SESSION_ID` 在接續、`/clear` 後也跟著換(官方修好)——第 2 項撤掉;③收貨紀錄裡 `seat-check --events` 那一行連續一個月都是 0 條——第 3 項撤掉;④官方 hook 開始支援壓縮前改指示——第 1 項改走官方。

## 範圍

- **做**:
  1. **壓縮前保住交棒狀態**:新外掛 `lumos-context` 掛 `session.compact`,四種觸發(manual、auto、plugin、precompute)都在既有摘要指示後面附一段固定要求:逐字保留使用者在對話裡下的裁定與指示、目前在做的計劃節點與步驟、還在跑或剛收齊的審查席、還沒提交或還沒推的改動、待回覆的問題。附加段第一行是固定標記行 `[lumos-context 交棒要求 v1]`,指示裡已有這一行就不重附。子代理(輸入帶 `agentId`)附精簡版:保留它的任務與已得結論。
  2. **會談編號交給 lumos**:`lumos-context` 掛 `turn.start`,每個回合開始時用 `$.env.set` 設兩個值:`LUMOS_SESSION_ID` = `$.session.id()`,`LUMOS_SESSION_BASE` = 外掛當下看到的 `CLAUDE_CODE_SESSION_ID`。lumos 取會談編號時,只有兩者都不空、而且自己環境裡的 `CLAUDE_CODE_SESSION_ID` 等於 `LUMOS_SESSION_BASE`,才採用 `LUMOS_SESSION_ID`;否則用 `CLAUDE_CODE_SESSION_ID`。這樣在會談裡再開的 `claude -p` 子會談(它的官方編號是自己的,跟繼承來的 BASE 不同)不會讀到外層的編號。lumos 取會談編號的地方目前只有 `handoff` 排除接手者自己那一處,改成走同一個取值函式。
  3. **審查員引用的檔有沒有真的讀過(縮小版)**:
     - 事件帳的 spawn 事件多記一欄 `seat`:派工詞逐行找到的第一個 `LUMOS-SEAT:` 行後面那串(去頭尾空白、上限 200 字、被拒的派工也記),不記派工詞其他內容。
     - `lumos seat-check` 加 `--events <會談編號>`(既有的 `--ledger` 是越界帳,不共用):席位標記由派工單組成 `<派工單所在資料夾名>/<round>/<seat>`,在那個會談的事件帳找 `seat` 相同的 spawn,取最後一筆;沿 `child` 找那個子代理的事件。
     - 只核對報告裡 ``file: `路徑:行號` `` 形式的引用,而且只核對不在圖譜資料夾底下的檔(圖譜筆記常由派工時自動附上、或用 `lumos show` 讀,事件帳看不到)。引句不核對。
     - 判「讀過」:那個子代理對同一檔有 Read;或某次 Grep/Glob 帶的路徑是該檔或它的上層目錄;或 Bash 指令前 500 字裡出現該檔路徑;沒帶路徑的 Grep/Glob 算整個 repo 都搜過。只靠搜尋根目錄才算讀過的條數另外印出來,讓收貨人看得到放行有多寬。
     - 路徑比對前一律換成相對 repo 根的寫法:絕對路徑去掉這個 repo 任一工作目錄(`git worktree list`)的前綴;換不了的保留絕對路徑原樣比。
     - 帳不完整就不判,只說原因:找不到那一席、那個子代理沒有 `turn_end`(還沒跑完或還沒落盤)、那個會談的帳有寫入錯誤或壞行。外家席(Codex)沒有 Claude 事件帳,一律印「外家席不適用」。
     - 只提醒、不擋(恆回 0);印出的席位標記與路徑過事件帳讀取端同一道清理。收貨紀錄固定寫一行 `seat-check --events: N 條`。
- **不做**:
  - Bash 改檔前推筆記:設計審第一輪三席判必須改——改觸發條件會讓 Codex 那邊的轉換失效、舊安裝重複註冊;列舉寫檔形狀跟專案「列舉補不完、量結果」的既有決策相反;每次 Bash 多付 Python 啟動與寫帳。它也不是 mod 能力。
  - 開場標出驗證不過的記憶:拿不到會談編號、要翻記憶清掃的唯讀守衛、標記原因文字會把筆記內容放進更高信任的位置。另開題。
  - lumos 自己派代理(2026-10-06 本會談列的 mod 候選清單第 7 項,沒進任何計劃節點;Enzo 裁拿掉)。
  - 壓縮後重新注入規矩:lumos 三支開場 hook 沒設觸發條件,照官方文件壓縮後會再跑(未實測)。
  - 審查席隔離(另一條分支,停在代碼審第二輪)。
- REVISIT:2026-11-06 決定「開場標出驗證不過的記憶」要不要另開計劃(先解會談編號來源與注入框兩題)

落點:新開 `Systems/lumos-context`(管新外掛);其餘落在 [[Systems/lumos事件帳]](spawn 的 `seat` 欄)、[[Systems/design-loop]](`seat-check --events`,一行加連結回本計劃)、[[Systems/lumos-cli-lifecycle]](外掛清單)、[[Systems/lumos-cli-read]](`handoff` 取會談編號)。

## 做法要點

- 第 1 項的附加段固定一份文字放在外掛裡,不呼叫外部指令;原本就有指示(使用者打 `/compact <文字>`)時接在後面,不覆蓋。precompute 算的是當下的對話,真正壓縮時可能已過時——這是引擎行為,附加段只管要求,不保證新鮮。
- 第 2 項實作前先實測(手動,結果寫進驗證筆記):①互動會談裡 Bash 印 `$LUMOS_SESSION_ID`、`$LUMOS_SESSION_BASE`;②`/clear` 後再印一次;③`claude --resume` 接續後再印一次;④在 Bash 裡開 `claude -p` 印子會談看到的三個值;⑤`$.session.id()` 跟逐字稿檔名是否一致。①讀不到就整項停下回報,不走別的備案。
- 第 3 項的 `seat` 欄找法跟派工鏡頭 hook 找標記一樣逐行比對;實作前先確認派工範本會帶 `LUMOS-SEAT:` 行(審查席隔離那條分支定了這個標記與範本,哪條先上主線就由哪條加範本,另一條接上時合併)。
- 實作提交時,在 [[Projects/派工鏡頭注入_計劃]] 用 `lumos decision-add` 記一筆「不驗被本計劃 d2 部分翻案」,讓只讀舊節點的人看得到。
- 外掛清單:安裝端把單一外掛常數改成清單(`_LUMOS_PLUGINS`),另加「已退役外掛」清單:在裡面的名字已裝就移除。回退一個外掛 = 把它從清單搬到已退役清單。審查席隔離分支也做了同形狀的清單,後上主線的那條接上時合併。
- `lumos enforcement` 既有的事件帳外掛那一列,改成逐支列出外掛清單裡的外掛有沒有裝上,`lumos-context` 沒裝時看得到。

## 條款

外掛行為的條款綁在 `mods/claude/lumos-context/hooks/context.test.ts`,測試標題以條款編號開頭,用 `claude plugin test mods/claude/lumos-context` 在本機跑。

- [S1] 當對話壓縮(`session.compact`,四種觸發)時,外掛應在摘要指示後附上以固定標記行開頭的交棒要求段;原本有指示時接在後面、原文不變 [manual:claude plugin test mods/claude/lumos-context 的 S1 測試全綠]
- [S2] 當摘要指示裡已有交棒要求的固定標記行時,外掛應不再附 [manual:claude plugin test mods/claude/lumos-context 的 S2 測試全綠]
- [S3] 當壓縮的是子代理(輸入帶 `agentId`),外掛應附精簡版 [manual:claude plugin test mods/claude/lumos-context 的 S3 測試全綠]
- [S4] 當回合開始時,外掛應把 `$.session.id()` 設進 `LUMOS_SESSION_ID`、把當下的 `CLAUDE_CODE_SESSION_ID` 設進 `LUMOS_SESSION_BASE` [manual:claude plugin test mods/claude/lumos-context 的 S4 測試全綠]
- [S5] 當 lumos 取會談編號,而 `LUMOS_SESSION_ID` 與 `LUMOS_SESSION_BASE` 都不空、且 `CLAUDE_CODE_SESSION_ID` 等於 `LUMOS_SESSION_BASE` 時,應採用 `LUMOS_SESSION_ID`;其他情況應採用 `CLAUDE_CODE_SESSION_ID` [test:t_session_id_prefers_lumos_env]
- [S6] 當事件帳記 `spawn` 事件,應多記 `seat` 欄(派工詞第一個 `LUMOS-SEAT:` 行後面那串,上限 200 字;沒有就是 null),不記派工詞其他內容 [manual:claude plugin test mods/claude/lumos-ledger 標題以「第二批 S6」開頭的測試全綠]
- [S7] 當 `seat-check` 帶 `--events` 跑,報告裡圖譜資料夾以外的 `file:` 引用是那一席子代理沒讀過的檔時,應列出那幾條;讀過的不列;只靠搜尋根目錄才算讀過的另印條數 [test:t_seat_check_reads_from_events]
- [S8] 當那一席找不到、子代理沒有 `turn_end`、或帳有寫入錯誤或壞行時,`seat-check --events` 應只印不判的原因,不列任何一條,回 0 [test:t_seat_check_events_incomplete]
- [S9] 當 `lumos install` 與 `uninstall` 執行,外掛清單裡的每支(含 `lumos-context`)應各自裝上與移除;已退役清單裡的已裝外掛應被移除 [test:t_install_registers_context_plugin]
- [S10] 當 Python 端掃 `lumos-context` 的原始碼,應只出現 `LUMOS_SESSION_ID` 與 `LUMOS_SESSION_BASE` 兩個 `$.env.set`,沒有網路、寫檔與執行外部程式的呼叫 [test:t_context_plugin_files_valid]

## 回退

- 外掛:把 `lumos-context` 從外掛清單搬到已退役清單,下次 install / update 就會移除;lumos 讀不到 `LUMOS_SESSION_ID` 時本來就退回官方編號。
- Python 改動(取會談編號、`seat-check --events`、外掛清單)各自獨立,`git revert` 那段即可;事件帳的 `seat` 欄是多出的欄位,讀取端沒用到就忽略。

## 實務隱患

- 已排除:金流:不碰付款
- 已排除:對外送出:外掛不呼叫網路(S10 掃原始碼釘住);Python 端只讀本機事件帳與檔案
- 已排除:不可逆:外掛只附加摘要指示文字、設兩個環境變數,不寫檔;拿掉外掛即回到現狀
- 守衛面:第 3 項只提醒不擋;帳不完整時不判,不會用缺帳去誣賴席位
- 併發:同一外掛行程若同時服務多個會談,`$.env.set` 是行程層級,A 會談的 Bash 可能讀到 B 的值;S5 的 BASE 比對在這種情況會退回官方編號(官方編號在同一行程也相同時才會錯)——實作前實測第 ④ 步一併確認
- 效能:第 1 項只在壓縮時跑;第 2 項每回合兩次 `$.env.set`;第 3 項只在收貨時手動跑,讀一個會談的事件帳
