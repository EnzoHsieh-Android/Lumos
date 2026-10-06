severity: major

# 通才審 Claude-mod第二批 r1(sonnet)

交叉引用:Systems/lumos事件帳、design-loop、記憶過期清掃、改檔前推播、lumos-cli-lifecycle、Projects/派工鏡頭注入_計劃 都存在;Systems/lumos-context 為新開,不算壞引用。

## F1 [第 4 項] 改 matcher 會讓既有安裝重複註冊,且 Codex 轉換壞掉
severity: major
blocking: 是 — 照 spec 做,舊安裝的 Edit/Write 每次推兩次筆記、Codex 端 apply_patch 失去 hook,且 spec 自稱「Codex 那邊不動」。
引句:「連同安裝端把觸發條件從 `Edit|Write|MultiEdit` 加上 `Bash`」
- `_equivalent` 比 matcher 字串全等(file: `scripts/merge-claude-settings.py:328`)。matcher 變成含 Bash 的新字串後,舊 `Edit|Write|MultiEdit` 那筆不等價,merge 走 `existing.append`,舊筆留在 settings.json。Edit/Write 同時命中兩筆,impact-hook 跑兩次(自癒去重也因 matcher 不同而不收)。spec 沒寫遷移(刪舊筆)。
- `_codex_entries` 只認 matcher 恰等於 `Edit|Write|MultiEdit` 才轉 `apply_patch`(file: `scripts/merge-claude-settings.py:271`)。改了字串後 Codex 得到原樣含 Bash 的 matcher,apply_patch 不再觸發。「Codex 那邊不動」與此矛盾,需另寫條款與測試。
- impact-hook 入口 `tool_name not in EDIT_TOOLS` 直接 return(file: `scripts/hooks/claude/impact-hook.py:777`),`extract_path` 只讀 `tool_input.file_path`(file: `scripts/hooks/claude/impact-hook.py:84`)。Bash 的 `tool_input` 是 `command`,spec 沒說要改這兩處、也沒說只認 code 副檔名與冷卻窗(TTL)對 Bash 目的路徑是否照用。
- 另一條 matcher 選項(獨立再掛一筆 `Bash` matcher)可避開前兩點,spec 沒比較。

## F2 [第 5 項 / S8] 記憶清掃 hook 拿不到會談編號,且「沒事也寫」與現有流程衝突
severity: major
blocking: 是 — S8 的檔名「按會談編號分檔」在現有 hook 實作不到,S7 對不上會談編號就整份不動,等於功能永不生效。
引句:「記憶清掃 hook 每次跑完(沒事也寫)把結果(會談編號、哪幾篇記憶檔、什麼原因)寫進 lumos 自己的快取資料夾」
- `main()` 不讀 stdin,參數只有 `--dir/--quiet/--budget`(file: `scripts/hooks/claude/memory-sweep.py:937`);SessionStart 的 `session_id` 在 stdin payload 裡,現在整支沒接。有 budget 時還走看門狗再起子行程(file: `scripts/hooks/claude/memory-sweep.py:944`),stdin/會談編號要跨兩層傳,spec 沒提。
- `if a.quiet and not (...): return 0` 在結果寫出前提前返回(file: `scripts/hooks/claude/memory-sweep.py:953`),「沒事也寫」要改這條流程;看門狗逾時被砍時結果檔寫不寫、寫部分結果算不算(「不完整」)沒定。
- 「什麼原因」沒有結構化來源:`Tally` 是 `lines` 自由文字加計數(file: `scripts/hooks/claude/memory-sweep.py:596`),沒有「檔 -> 原因」對映。要新增資料結構,不是只加寫檔。
- 範圍外一點:`HOME` 無、cwd 與記憶資料夾 slug 推導(`memory_dir`)和外掛端找索引怎麼對上同一專案,spec 只用會談編號對,沒驗證兩邊是同一個記憶資料夾。

## F3 [第 5 項] 執行順序未定時,功能可能整場不生效且無人察覺
severity: major
blocking: 是 — 順序是功能成立的前提,spec 把它丟給「實作前實測」,但失敗模式(整場零標記)無補救條款。
引句:「外掛先跑就讀不到檔、整份不動,不會標錯。」
- `prompt.context` 型別檔說「每個會談只算一次,直到 `$.ui.invalidate("prompt.context")` 或重讀」。若它先於 SessionStart hook,首輪結果必無檔,整個會談零標記直到壓縮;spec 沒用 `$.ui.invalidate("prompt.context")` 補(型別檔有),也沒有「讀不到檔」的可觀測訊號(S7 沒有 stderr/事件帳記錄),REVISIT 的指標也不量標記命中率。
- `instructionFiles` 是 optional,別的 hook 改過 `claudeMd` 文字時為 undefined(file: `/private/tmp/claude-501/bundled-skills/2.1.289/7074fcfbf99d3673806e406ebd90f7b5/plugin-authoring/types/claude-code.d.ts:8066`)。spec 只寫「改 instructionFiles 裡記憶索引那一份」,沒處理 undefined,也沒說用哪個 `kind` 認出記憶索引。
- 標記行加字會吃索引的載入上限(前 200 行或 25 KB,file: `scripts/hooks/claude/memory-sweep.py:379`);已接近上限的索引被標後,原本看得到的行可能被擠出。spec 沒量。⚠ 是否在上限前還是後截斷,型別檔未說。

## F4 [回退] 「拿掉清單與市集檔就會移除」與安裝碼不符
severity: major
blocking: 是 — 回退是 spec 的唯一退路,現況寫法回退不了。
引句:「把 `lumos-context` 從外掛清單與市集檔拿掉,下次 install / update 就會移除」
- 安裝端只做 ensure-install 與 uninstall 單一常數 `_LEDGER_PLUGIN`(file: `scripts/lumos:21921`、`scripts/lumos:22047`、`scripts/lumos:22074`),沒有「已裝但不在清單就移除」的路徑。清單拿掉後使用者機器上已裝的 lumos-context 留著;市集是 directory 來源,檔拿掉後還成為懸空外掛。
- S9 需要把單一常數改成清單,涉及 `_ledger_*` 一整串函式(用 `_LEDGER_PLUGIN` 判已裝、失敗提示 `_ledger_fail_hint`、手動指令 `_LEDGER_MANUAL` 皆單數),spec 沒列這些改動,也沒說 `uninstall` 只移除一個外掛失敗時另一個的處理。

## F5 [第 3 項 / S4] seat-check --events 的三個未定義
severity: major
blocking: 是 — 三處任一不定,S4 的測試無法寫成一個確定的紅綠。
引句:「抽報告裡 ``file: `路徑:行號` ``(新寫一套抽取;既有的只抽引句)與引句所在檔,列出席位從沒讀過的」
- 「引句所在檔」怎麼找:現有 seat-check 只把引句錨進派工 materials(file: `scripts/lumos:23536`);`--events` 沒有 materials 時要去哪搜、搜整個 repo?同一句多檔命中、引句來自凍結快照 /tmp 檔(如本次審查)時算哪個檔,spec 全未定。
- 路徑口徑:報告寫的 `file:` 是 repo 相對路徑,事件帳 `paths` 是絕對路徑,且 worktree 另記 `worktree` 欄(file: `mods/claude/lumos-ledger/hooks/register.ts:62`);相對轉絕對的基準(主 checkout 或 worktree)沒寫,誤判會是整批「沒讀過」。
- 席位對應:`seat-check` 現有簽章是 `report, dispatch`,席名來自 dispatch JSON 的 `seat`(file: `scripts/lumos:23523`),事件帳記的是派工詞第一行 `LUMOS-SEAT:` 後面整串(例 `Claude-mod第二批/r1/通才-sonnet`);兩者格式是否同一個值、`--events` 時 dispatch 還要不要給,沒寫。
- 會談範圍:`--events <會談編號>` 只收一個編號,而編排者的會談接續或 `/clear` 後事件分在多個資料夾(spec 自己在第 2 項說編號會變);席在舊編號、報告收在新編號時「找不到那一席」被當無事,未說是否多編號搜尋。

## F6 [第 3 項 / S5] 兩個欄位的判定來源未定
severity: minor
blocking: 否 — 屬實作細節,實測關卡已有安排,但條款本身不可驗。
- 「有沒有派工鏡頭附加段」靠什麼字樣判定未寫(附加段的固定標頭字串在 dispatch-lens-hook 裡,spec 沒引用)。agent.spawn 見到改寫前或後已排實測(做法要點有寫),但實測後的「判定字串」缺。
- 事件帳 `onSpawn` 只在 `next` 回來後記,被 deny 的 spawn 也進記(`denied`);S5 沒說被拒的派工要不要記席位標記。

## F7 [第 1 項 / S1] 「已附過就不重附」與 precompute 重用
severity: minor
blocking: 否 — 行為有退化但不致錯。
引句:「三種觸發都附,含預先計算 `precompute`;已附過就不重附」
- 「已附過」靠什麼偵測(附加段內的標記字串?)沒寫;使用者 `/compact <文字>` 恰含該字串時會被誤判已附。
- 型別檔說核心可重用已算好的摘要(`usage` 說明「core reused a summary already computed」)。若 precompute 先以附加段算好,之後使用者手動 `/compact 文字` 的指示可能被重用結果吞掉;spec 的「原文不變接在後面」在此路徑未涵蓋。⚠ 是否真重用,型別檔未明說。

## F8 [第 2 項 / S2、S3] 備案路徑沒進條款
severity: minor
blocking: 否 — 已有實測前置,但備案實際走時條款失效。
- S3 只寫讀 `LUMOS_SESSION_ID` 再 `CLAUDE_CODE_SESSION_ID`;備案(`CLAUDE_PID` 小檔)走起來時 lumos 讀的是檔,S3 與測試名 `t_session_id_prefers_lumos_env` 都沒涵蓋;小檔位置、清理、PID 重用造成讀到舊會談編號都未寫。`CLAUDE_PID` 是否在 Bash 環境可見也沒列入實測。
- `$.env.set` 名稱須是字串字面值且 `claude plugin validate` 會列出(型別檔 env 區);spec 沒寫宣告。次要:`turn.start` 只主會談,子代理內 Bash 讀到的值是否一致沒說。
- 現況核對:lumos 讀 `CLAUDE_CODE_SESSION_ID` 的確只有 handoff 一處(file: `scripts/lumos:46262`),「目前只有 handoff」成立。

## F9 [第 4 項 / S6] 寫檔形狀偵測的邊界
severity: minor
blocking: 否 — 只提醒型 hook、失敗即放行,錯判成本低。
- 規則只列 `>`、`>>`、`tee`、`sed -i`、`cp`/`mv` 目的端、heredoc;未提 `>/dev/null`、`2>&1`(最常見誤判)、`cd x && cat > rel` 的相對路徑基準、`perl -i`、`python -c`、`git checkout/apply` 等寫檔法;漏報與誤報口徑沒定。
- S6 寫「主會談」,但 hook 條款沒說如何排除子代理 Bash(payload 是否有 agentId 未查)。
- 回合內每次 Bash 都多一次 Python 啟動,spec 已列「實作時量」但沒設可接受上限或超標的處置(RETIRE-IF 也沒涵蓋這項)。

## F10 [RETIRE-IF / REVISIT] 撤除條件不可機械判
severity: minor
blocking: 否 — 屬審計品質,不影響設計是否成立。
引句:「核對引用一個月內零次抓到不實引用,而且收貨人工核對也沒抓到」
- 「收貨人工核對也沒抓到」沒有記帳來源(沒有欄位記人工抓到的次數),撤除條件無法判定。①「摘要器不照指示做」同樣沒有度量方法(事件帳只看得到壓縮事件,看不到摘要內容有沒有保住交棒狀態)。

## 各節狀態
- 範圍第 1 項:F7。
- 範圍第 2 項:F8。
- 範圍第 3 項:F5、F6。
- 範圍第 4 項:F1、F9。
- 範圍第 5 項:F2、F3。
- 不做:已讀,無 finding。
- 落點:已讀,無 finding(引用目標都在)。
- 條款 S1-S9:S1 F7;S2/S3 F8;S4 F5;S5 F6;S6 F1/F9;S7 F3;S8 F2;S9 F4。
- 回退:F4。

## 實務隱患逐類
- 併發:有。S8 快取檔多個同時啟動的會談各寫各的編號檔不衝突;但同一會談 SessionStart 看門狗與子行程各自寫、與外掛讀之間的競態靠原子換名可行,spec 已寫暫存再換名;未寫的是壓縮後重算時舊檔被覆蓋的讀寫順序(F3 同源)。
- 效能:Bash 每次多一次 Python 啟動(F9);標記行吃索引上限(F3)。
- 回滾:F4。
- 寫檔安全:快取資料夾路徑由 lumos 組、不從記憶內容推,方向正確;但資料夾位置、權限、「只留七天內」的清理由誰執行(哪支程式、什麼時機)沒寫。⚠ 清理刪檔屬新的刪除動作,與「不刪不改既有檔」的隱患自述(實務隱患 不可逆 一條)有出入,宜明說只刪自己快取。
- 提示快取:已列。
- 平行路徑:Codex 端(F1)、子代理的 Bash 與 compact(F7、F9)。

## 牽連節點
派工尾端沒有附 hook 牽連節點,無條目可判。

總結:最嚴重 major,blocking 5 條
