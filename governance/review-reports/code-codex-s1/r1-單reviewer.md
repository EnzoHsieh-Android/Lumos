# code-codex-s1 r1 單reviewer 審查報告

審查對象:`governance/review-reports/code-codex-s1/r1-snapshot.patch`(commit `eaf4583`,對照 `aeb0aea..HEAD`,1280 行)。
逐 hunk 讀完整份 diff;每條 finding 都用真的程式碼(對照到確切 commit `eaf4583` 的檔案內容,不是工作樹目前的版本——見下方「重要背景」)跑過,不是憑讀碼猜測。

**重要背景(不算 finding,但影響怎麼讀這份報告)**:審查途中發現本機工作樹在這份 snapshot 之上,已經有**尚未 commit** 的修正,而且那批修正的註解直接寫著「code-codex-s1 r1 外家 #3」──看起來是另一位外部審查員(Codex)已經先發現了跟本報告 F2/F3/F4/F5 幾乎一樣的問題,正在被吸收。這代表本報告以下四條不是嚴謹度過頭的猜測,而是已經被另一條獨立管道證實的真問題。**本報告的每條 finding 仍然只對 `eaf4583`(snapshot 凍結的那個版本)下手驗證,不採用工作樹裡還沒進 commit 的內容。**

固定席鏡頭(圖譜):本次派工詞只留了 `LUMOS-IMPACT: aeb0aea..HEAD` 這一行原樣,後面沒有接到任何「必看——這 N 篇…」固定席清單,也沒有接到「圖譜沒有釘到節點」備援段——換句話說鏡頭這次沒注入任何東西(不是 0 篇有備援段那種,是完全沒有後續文字)。因為沒有清單也沒有備援段可對照,固定席逐條判這部分沒有材料可答,如實記在這裡,不臆測原因。

---

## Findings

### F1:多檔 patch 的預算迴圈,把 Claude 單檔路徑的 subprocess 逾時從 30 秒偷偷改成 20 秒

severity: major
blocking: 是
file: `scripts/hooks/claude/impact-hook.py:541`(逾時算式),`scripts/hooks/claude/impact-hook.py:60`(`APPLY_PATCH_BUDGET_SEC = 20.0` 定義)
引句:「timeout=min(30.0, max(3.0, left))」

失敗場景:舊版 `main()` 對 Claude 的 Edit/Write/MultiEdit 單檔一律用 `subprocess.run(..., timeout=30)`(diff 裡明確刪掉這行)。新版不分是 Claude 單檔還是 Codex 多檔 patch,一律先跑進同一個「總預算 `APPLY_PATCH_BUDGET_SEC=20` 秒」的迴圈,單檔情況下 `left≈20`、`timeout=min(30, max(3, 20))≈20`——**單檔逾時實際上從 30 秒縮到 20 秒**,跟 S1 實作紀錄自己寫的「Claude 單檔路徑要逐字等價(既有 81 測全綠)」不符。我實際 mock `subprocess.run` 跑一次單檔 Claude Edit,量到傳進去的 `timeout` 是 `19.99999887496233`,不是 30(重現腳本在 scratchpad,呼叫 `m.main()` 後檢查 mock 收到的 kwargs)。既有 81 測沒抓到是因為那些測試的 mock runner 只記錄 `cmd`(argv),沒有人斷言 `timeout` 這個關鍵字值,所以「逐字等價」的宣稱其實沒有被任何測試守住。在真實環境裡,如果一次 `lumos impact --file` 查詢原本要 20–30 秒之間才回(大 repo 常見),這個改動會讓它比以前更常撞到逾時、更常靜默不注入(fail-open 沒有錯誤訊息,除非開 `LUMOS_HOOK_DEBUG`)。

---

### F2:`dispatch-lens --claim` 併發認領時,席次編號用「剩餘 token 數回推」會撞號

severity: major
blocking: 是
file: `scripts/lumos:17219`(`remaining = len([p for p in d.glob("tok-*") if p.suffix != ".claimed"])`)、`scripts/lumos:17221`(`seat = seats - remaining`)
引句:「seat = seats - remaining」

失敗場景:`os.rename` 本身是原子的,兩個行程搶同一個 token 檔不會重複拿到同一份鏡頭文字這件事沒錯。問題在**認領成功之後算「這是第幾席」的方式**:每個行程各自 rename 成功後,再獨立去 `glob` 目錄算「還剩幾個沒 claim」,然後用 `seats - remaining` 反推自己是第幾席。如果兩個行程幾乎同時各自 rename 成功,而其中一個行程算 `remaining` 的時間點落在「兩邊都已經 rename 完」之後,兩邊算出來的 `remaining` 會一樣,於是**兩個不同的子代理會拿到同一個「第 k/N 席」字串**(token 本身不重複,只有顯示出來的席號重複)。我用兩個 thread、在其中一個的 `os.rename` 之後插入同步點逼出這個交錯,對照的正是 `eaf4583` 那份 `scripts/lumos`(不是工作樹已修的版本):兩邊都拿到 `"seat": 2`、文字都印「第 2/2 席」。這條鏡頭的唯一用途就是「領錯席時以這行對照」(程式碼自己的註解),編號一旦會撞,這個對照功能在併發情境下(也就是這個功能本來就是為了服務的「一次派多個子代理」情境)會失靈。測試裡「5 個並發認領 3 席→恰 3 ok 且席次 1,2,3 不重複」能過,只是這次交錯的時間窗沒被踩到,不代表這個保證真的成立——見 F6。

---

### F3:Codex 逐字稿裡 `exec_command` 用「無引號 key」(`{cmd:"…"}`)時,bash 指令抽不到

severity: major
blocking: 是
file: `scripts/hooks/claude/check-graph-sync.py:110`(`_CODEX_EXEC_CMD_RE` 定義)
引句:「_CODEX_EXEC_CMD_RE = re.compile(r'"cmd"\s*:\s*"((?:[^"\\]|\\.)*)"')」

失敗場景:這個正規式要求 JS 物件字面值裡的 key 一定要帶雙引號(`"cmd":"…"`)才抓得到。但 Codex 真實吐出來的 `custom_tool_call` input 常常是 JS 語法的無引號 key(`{cmd:"echo A", workdir:"/x"}`)或跨行縮排形(`{\n  cmd: "echo B",\n  ...\n}`)。我把這兩種形式餵進 `eaf4583` 版的 `collect_turn_actions`(對照 `git show eaf4583:...check-graph-sync.py`,不是工作樹已修版),兩種都回傳空的 `cmds`(`[]`)——完全沒抓到指令。工作樹裡尚未 commit 的修正把正規式改成 `(?<![\w$])["\']?cmd["\']?\s*:\s*"..."`,並在 commit 訊息等級的測試註解裡直接寫「今日逐字稿 30/61」用的是無引號形——如果這個比例真實,代表這份 snapshot 版本對將近一半的真實 Codex 逐字稿會**靜默漏掉**該回合實際跑過的 bash 指令。這支 hook 的唯一目的是「改了 code 有沒有寫回筆記」的收工檢查,指令抽不到不會讓 hook 出錯或崩潰,而是安靜地少偵測到——正是這種檢查最怕的失效模式(看起來正常運作,其實漏了一半)。

---

### F4:輪次邊界只認 `event_msg/user_message`,漏掉 `response_item/message role=user` 這種標記法,會把上一輪的指令一起算進本輪

severity: major
blocking: 是
file: `scripts/hooks/claude/check-graph-sync.py:153`
引句:「if obj.get("type") == "event_msg" and p.get("type") == "user_message":」

失敗場景:`collect_codex_turn_actions` 從逐字稿尾端往回掃,遇到這一行判定「到上一次真人輸入為止」才停止收集,超過這個邊界的內容不該算進「這一輪」。但 Codex 的使用者輸入不是每次都用 `event_msg/user_message` 表示,有時是 `response_item` 型、`type=message, role=user`(OpenAI Responses API 的常見形狀)。我把一段「兩輪、只用 `response_item/message role=user` 分隔、完全沒有 `event_msg/user_message`」的逐字稿餵進 `eaf4583` 版程式,預期只該回傳第二輪的 `echo NEW`,實際回傳 `['echo OLD', 'echo NEW']`——上一輪已經跑完的指令被誤算進這一輪。這會讓 Stop hook 的「這一輪改了什麼」判斷把已經處理過(可能筆記也已經補齊)的舊動作重新算進來,產生對不上號的提醒或錯誤地擴大這一輪的改動範圍。

---

### F5:`dispatch-lens --arm` 跟 `--claim` 同時給,不會被擋,會靜默照 argparse 的檢查順序只執行 `--claim`

severity: minor
blocking: 否
file: `scripts/lumos:18574`-`18575`
引句:「return cmd_dispatch_lens_claim(repo=args.lens_repo, as_json=args.lens_json)」

失敗場景:`main()` 對 `dispatch-lens` 子指令的分派是一串 `if`:先檢查 `args.lens_claim`,是就直接回傳,完全沒檢查是否同時給了 `--arm`。實測 `lumos dispatch-lens --arm main..HEAD --claim --repo .` 對 `eaf4583` 版執行,rc=0、印出「(沒領到席:not-armed)」——`--arm` 整個被忽略,不會武裝、不會報錯,呼叫者以為武裝成功但其實什麼都沒發生。實務上編排者跟 hook 各自只會單獨呼叫 `--arm` 或 `--claim`,誤用機率低,所以列 minor 不列 major;但如果編排腳本手滑打錯旗標組合,錯誤是完全靜默的,不容易在測試裡發現。

---

### F6(測試品質,非功能性 bug):併發測試真的是併發,但沒有可靠證到 F2 宣稱的「席次不重複」

severity: minor
blocking: 否
file: `scripts/test_lumos.py:1152`(對照 `eaf4583` 內對應行,新增測試 `t_codex_s1_lens_arm_claim` 的並發段)
引句:「procs = [_sp.Popen([sys.executable, GRAPHCTL, "dispatch-lens", "--claim", "--json", "--repo", str(repo)], env=env, stdout=_sp.PIPE, text=True) for _ in range(5)]」

說明(依派工詞「本案特定鏡頭」要求逐項回答):
1. 三個新測試(`t_codex_s1_impact_apply_patch` / `t_codex_s1_lens_arm_claim` / `t_codex_s1_graph_sync_codex_transcript`)逐條檢查過,斷言都是釘死的具體值(列表相等、seat 數字相等、字串前綴相等等),沒有找到永真斷言。唯一一條只驗「不炸」不驗內容的是 `check("s1-cgs: cmd 進 extract_bash_file_paths 不炸", isinstance(...), "")`,但它的名字跟目的本來就寫明只驗不炸,不是掛羊頭賣狗肉,不算問題。
2. 並發測試是真並發:5 個 `subprocess.Popen(...)` 在同一個 list comprehension 裡先全部啟動(`Popen` 本身不阻塞),之後才逐一 `communicate()` 收輸出——不是「起一個等一個」的序列化寫法。這部分做對了。
3. 但「真並發」不等於「可靠踩到 F2 的競態視窗」。F2 的撞號需要「兩個行程的 rename 都做完之後,才輪到其中一個去算 remaining」這種特定交錯,靠 5 個 real subprocess 自然啟動的時間差去賭,大機率賭不中(這也是為什麼這條測試目前是綠的)。測試通過只能證明「這一次跑,沒有觀察到撞號」,不能證明「席次不會撞號」——這正是這次派工詞要我特別確認的地方:測試沒有可靠釘住它聲稱要釘住的行為。

---

## 固定席鏡頭逐條判

本次派工詞裡的 `LUMOS-IMPACT: aeb0aea..HEAD` 這行後面沒有接任何固定席清單,也沒有接「圖譜沒有釘到節點」備援段——鏡頭這次完全沒有注入內容,無材料可逐條答,如實記錄、不臆測。

---

## 總結

本輪最高嚴重度:**major**(F1、F2、F3、F4)。
blocking 條數:**4**(F1、F2、F3、F4;F5、F6 為 minor、不 blocking)。
