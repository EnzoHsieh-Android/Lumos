severity: major

## 對照範圍

我讀了計劃、前掃紀錄、`dispatch-lens-hook.py`、`_hookevent.py`,以及 `lumos` 裡的 `cmd_update`、`_sync_global_hooks`、`ANCHOR_FILES`。全程只讀,沒跑任何東西。

## Findings

severity: major
blocking: 是 — RETIRE-IF 與 REVISIT 要數的東西,現有掛鉤事件欄位記不到,到期那天照字面判不出來
引句:「數一次掛鉤事件裡帶 `LUMOS-REPO:` 且通過檢查的次數與被拒的次數」
問題:
- 事件只有 `ts, hook, kind, repo, fp, note` 六欄,`kind` 只准 ok、timeout、error。`repo` 欄是掛鉤行程的 cwd 所在 git 根,也就是會談目錄,不是 `LUMOS-REPO:` 的目標。
- 「通過」要記成 `mark("ok", note)`,而 `ok` 是預設值,一般情況不寫 note。計劃做法 4 只寫「記一筆掛鉤事件」,沒指定 kind 與 note 格式,通過那條路根本沒有記帳點。
- 「是否等於會談目錄」要比 realpath,事件裡沒有這個欄位,note 也沒規定要帶。
- `_hookevent.py` 檔頭明寫「不記『注入 N 次』」,並引派工鏡頭案的 d1「不擋不驗不記不量」。計劃沒有處理這個與既有裁定的衝突。
- `mark` 只有單一欄位,同一次執行後寫的會蓋掉前面的。被拒若記成 `error`,會跟鎖失敗、範圍算不出來混在同一類,要靠 note 字首才分得開。
- 帳本在 `governance/runtime/hook-events.jsonl`,被 gitignore 蓋掉,記在各自的 cwd 根底下。計劃要求每個工作開獨立工作樹,收尾又按全域規則刪暫存工作樹,那份帳會跟著消失。
- 超過 512KB 就只留最後 2000 行。八到九週後,與所有 hook 共用的這份帳大概只剩一小段,「連續 8 週」沒有逐週分桶可看。
- RETIRE-IF 的「都等於會談目錄」在從沒用過這個標記時也是空真,到期會當成該撤除。
- RETIRE-IF 的第一個條件(Claude Code 帶出子代理工作目錄)沒有任何探測手段。
- 回頭看的條件只量「有沒有人用」,量不到「附錯 repo」的傷害。實務隱患的風險二(指錯 repo 時附上錯的節點)沒有任何訊號。這等於退回的觸發條件沒有儀表。

具體失敗:2026-12-15 REVISIT 到期,編排者打開帳本。有 `LUMOS-REPO:` 的派工若被記成 ok 且沒有 note,就和沒用標記的混在一起,通過數是 0 或無法判斷。被拒的數字摻著真正的錯誤。哪個工作樹的帳還在也不確定。最後只能憑感覺判,違反 CLAUDE.md 鐵則 4(寫不出可量的回頭條件,就是該處理而不是承認)。

建議:計劃要寫死記帳格式。例如一律 `mark("ok"|"error", "repo_marker pass same_as_session=0|1")` 與 `"repo_marker reject <代碼>"`,並明講這是對 d1 的有限鬆綁。同時要寫逐週彙總的來源,以及用 `LUMOS-REPO:` 數量為 0 時 RETIRE-IF 不算成立。

佐證:
- file: `scripts/hooks/claude/_hookevent.py:35-37` KINDS 與上限
- file: `scripts/hooks/claude/_hookevent.py:62-76` 事件欄位
- file: `scripts/hooks/claude/_hookevent.py:111-124` `mark` 單槽
- file: `scripts/hooks/claude/_hookevent.py:26-27` 不記注入次數的裁定
- file: `scripts/hooks/claude/dispatch-lens-hook.py:422` repo 取自 `CLAUDE_PROJECT_DIR` 或 cwd
- file: `.gitignore:36` `governance/runtime/`

---

severity: major
blocking: 是 — 回退段「對舊掛鉤無害」是假的,退回後會出現計劃自己否決過的「靜默用錯的樹」
引句:「舊掛鉤看不懂、原樣留在派工詞裡,不影響其他標記」
問題:舊掛鉤確實不報錯,但後果不是「無害」。
- 舊掛鉤沒有任何分支看 `LUMOS-REPO:`,一律在 `CLAUDE_PROJECT_DIR` 或 cwd 算。
- 做法 4 的原話是「不退回會談目錄算(退回會用錯的樹,比沒附更糟)」。退回後的舊掛鉤做的正是這件事,而且派工詞上明明寫著 `LUMOS-REPO: <目標>`,編排者與審查席都會以為它被遵守了。

具體失敗:
- 回退後,正在跑的審查迴圈或消費專案裡存著的派工詞仍帶 `LUMOS-REPO:`。
- 會談在 A,審的是 B 的分支,標記是 `LUMOS-IMPACT: main..HEAD` 這類兩端在 A 也解得開的範圍。
- 舊掛鉤在 A 算出一組看似合理的牽連節點,附進派工詞。
- 這一組是 A 的圖譜,不是 B 的,而且沒有任何說明行提醒。
- `LUMOS-SPEC:` 只收相對路徑時,A 剛好有同名計劃也會誤命中。

另外,全域複本 `~/.claude/hooks/` 是被 `copy2` 立即換掉的。Claude Code 每次呼叫都重新執行那支檔,所以同一輪派工中前半席走新掛鉤、後半席走舊掛鉤,固定席節點不一致。

建議:回退要有明確步驟,而不只一句「還原提交」。例如回退版掛鉤至少對帶 `LUMOS-REPO:` 的派工詞附一行固定說明(「此版不處理 LUMOS-REPO,節點是在會談專案算的」),或規定回退時先停掉進行中的迴圈、再同時回退範本。

佐證:
- file: `scripts/hooks/claude/dispatch-lens-hook.py:418-430` 舊掛鉤只認 IMPACT 與 SPEC,repo 一律取會談目錄
- file: `scripts/hooks/claude/dispatch-lens-hook.py:26-27` 兩個標記的正規式
- file: `scripts/lumos:24984-24987` 全域複本是 `copy2` 覆寫

---

severity: minor
blocking: 否 — 回退在單人環境做得到,但步驟缺漏會讓退回不乾淨,並留下殘局
引句:「消費專案 `lumos update` 取回舊掛鉤後要重新 `anchor approve`」
問題:
- 全域複本由「最後一次跑 install 或 update 的專案」的 vendored 版本寫入(`_sync_global_hooks` 用該專案的 `scripts/hooks/claude/` 當來源)。
- 只要有一個消費專案還沒 `lumos update`(或用了 `--no-pull`、`--allow-stale`),它下一次 update 或 init 就會把新掛鉤重新蓋回 `~/.claude/hooks/`。回退不是一次到位,要等所有消費專案都更新過才算。
- 錨點基線是消費專案各自一份。更新到舊掛鉤後 `anchor verify` 會擋推送,而且「永遠不可跳」。計劃只提了「重新 approve」,沒列出誰來逐個專案做。
- 事件帳的 `fp` 是掛鉤檔指紋。換版後,`enforcement` 會把舊指紋的 ok 事件判成 stale/unknown,直到下一次實際派工才恢復。
- 做法 8 把 3 處舊 WHY 標了 `[status:superseded]`、`[被取代:...]`,指向本計劃。回退段沒說這些要不要復原。若只還原程式提交而圖譜筆記留著,舊裁定會顯示被一個已撤回的計劃取代,形成懸空指向。
- 本計劃功能提交後還有「記錄代碼審通過」的帳本提交,回退提交本身也算改了錨點檔與測試檔,同樣要過 pitfalls 與審。

建議:回退段補一份清單,依序是還原程式與範本、復原三處 superseded、各消費專案 update 與 approve、確認 `~/.claude/hooks/` 的指紋。

佐證:
- file: `scripts/lumos:24961-24987` 全域 hook 同步
- file: `scripts/lumos:24307-24330` `cmd_update`
- file: `scripts/lumos:25740-25748` `ANCHOR_FILES` 含此掛鉤
- file: `scripts/lumos:23315-23345` 以 `fp` 判活

---

## 已讀,無 finding

- 做法 2 的信任檢查順序,先擋再跑 git。這和回滾無關。
- 緣起與實務隱患的金流、對外送出、不可逆三條排除理由。
- 驗收 S1 到 S6 對回滾沒有新增問題。

## 總結

最高等級是 major,共 3 條 finding,其中 blocking 2 條(RETIRE-IF/REVISIT 量不到,回退「無害」不成立),另 1 條 minor 不阻擋。
