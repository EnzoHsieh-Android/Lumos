severity: major

## F1 撤回紀錄與新欄位「舊讀法不認得就忽略」的宣稱與實際舊程式碼行為不符
severity: major
blocking: 是(消費專案還沒 `lumos update` 時,舊版 `loop escape --list` 會把撤回紀錄印成「手改帳?」的可疑列,而不是宣稱的無害忽略,會誤導排查、浪費調查時間)

引句:「已寫進帳的撤回紀錄與新欄位留著無害(舊讀法不認得就忽略)」

file: `scripts/lumos:9459-9474` `cmd_loop_escape` 的 `--list`(list_mode)是逐行讀 JSON、`by_loop.setdefault(str(r.get("loop","?")), []).append(r)` 直接把每一列(不論認不認得欄位)放進分組;顯示時 `wlabel = wsev if wsev in _SEV_W else f"非標準值 {_esc_clean(wsev, 20)}(手改帳?)"`(9466 行)、`sev_disp = sev if sev in _SEV_W else f"?{_esc_clean(sev, 12)}"`(9469 行)。撤回紀錄依 spec 第三節的設計不會有 `severity∈{minor,major,blocker}` 這種值(它是另一種紀錄形狀),舊版程式碼不會「忽略」它,而是會把它算進該 loop 的筆數(`len(rs)`)、且用「非標準值…(手改帳?)」的字樣印出來——對還沒更新的消費專案而言,這是主動的誤導(暗示帳被手改),不是宣稱的「無害忽略」。逃逸帳存放在 `env.vault.parent / ".escape-log.jsonl"`(每個消費專案自己的 docs 目錄下,scripts/lumos:9412),`lumos` 本體透過各專案各自的安裝/更新時機生效,不是所有消費專案會在同一天更新,這個情境會真的發生。
spec 第三節本身沒有為撤回紀錄定義任何欄位形狀(例如要不要帶 `loop`、要不要帶 `kind`),導致上面這個推演無法排除——不論撤回紀錄長什麼樣子,只要它落進 `--list` 的舊程式碼路徑,就一定會被當成一筆逃逸列印出來,不會被「忽略」。

## F2 「下一站接住」的站名清單漏掉正式程式碼已經在用的 `push-gate-unreviewed`
severity: major
blocking: 是(照 spec 字面實作 escape-stats,會把「被推送閘擋下、根本沒有漏出去」的列算成漏網或「站名不認得」,拉高看起來的逃逸率——這正是本案要修的那種「單位/分類算錯」的同類錯誤)

引句:「站名是 `實作`、`code-loop`、`push-gate` 的,代表往下一站就被接住」

file: `scripts/hooks/pre-push:311` 呼叫 `"$PY" "$GRAPHCTL" loop escape --auto --stage push-gate-unreviewed --severity major`,對應 `scripts/lumos:9356-9359` 的語意是「計劃被判成風險低、跳過審查,結果推送閘擋下」——這正是典型的「被下一站(push-gate)接住,沒有真的漏出去」個案,語意上比 `push-gate` 本身更貼近「接住」的定義。但這個字串跟 spec 列的三個站名精確比對(`實作`/`code-loop`/`push-gate`)都不相等,若照字面實作,`push-gate-unreviewed` 這個站名會落進「其他站名算漏網」或「不認得的站名」,而不是「下一站接住」。`scripts/test_lumos.py:33622,33626` 證實這個字串是正式測過、確實在用的階段值,不是理論上的邊界情況。目前帳上還沒有這個站名的真實列(用 `python3 -c "import json;from collections import Counter;print(Counter(json.loads(l)['stage'] for l in open('docs/.escape-log.jsonl') if l.strip()))"` 數出來只有 push-gate 1 筆、沒有 push-gate-unreviewed),但機制已經掛在 pre-push 常態觸發,累積後會被 escape-stats 誤算。

## F3 撤回紀錄本身被過濾到所有標準讀法都看不到,與「撤回清單可以查」「撤回本身也可以被看見」的宣稱矛盾
severity: major
blocking: 是(「撤回是否被濫用」這個守衛面宣稱唯一提到的緩解手段,實際沒有對應的指令/條款落實——沒有任何一條 [S1]–[S9] 要求存在一個「列出所有撤回紀錄」的讀法)

引句:「`_escape_rows_for` 過濾掉被撤回的列與撤回紀錄本身」

引句:「撤回本身也可以被看見」

file: `docs/lumos-toolchain-knowledge/Projects/逃逸帳對得起來_計劃.md` 第 45 行明講「所有讀逃逸帳的地方都要走這支」,而第 45 行同一句已經定義 `_escape_rows_for` 連撤回紀錄本身都濾掉;spec 第 87 行(實務隱患)又說「撤回清單可以列出來查」、第 90 行(已排除:不可逆)說「撤回本身也可以被看見」。這兩處宣稱互相矛盾:如果 `--list`、`gov --stats`、`escape-stats`、`rule-gap`、問閘尾的漏斗全部改走 `_escape_rows_for`(spec 明文要求全部改走),那麼撤回紀錄(理由、撤回者)就不會出現在任何一個現有的機讀或人讀指令輸出裡——唯一還能查到它的辦法是自己 `grep`/手開 `.escape-log.jsonl`。條款 [S1]–[S9] 沒有任一條要求提供「列出撤回歷史」的功能或測試,所以「撤回可以讓數字變好看,要留理由、撤回清單要能查」這個守衛宣稱,實際上沒有機制落地——理由留在帳上是真的,但「可以查」缺一個入口。

## F4 「撤回寫入包在既有的圖譜寫入鎖裡」對現況描述有誤,可能讓實作者漏掉替 --withdraw 加鎖
severity: major
blocking: 是(照字面理解會讓實作者以為手動記逃逸這條路已經有鎖覆蓋、不用特別處理,實際上目前完全沒有,--withdraw 若援引同樣假設就會漏鎖,造成撤回與撤回、或撤回與手動記帳之間的競態)

引句:「寫入包在既有的圖譜寫入鎖裡」

file: `scripts/lumos:9509-9535` 是 `cmd_loop_escape` 手動記帳(非 `--auto`)的寫入路徑,從產生 `rec` 到呼叫 `_jsonl_append_verified(log, rec, "token", rec["token"])` 全程沒有任何 `_vault_write_lock` 包裹。對照 `scripts/lumos:9342` 的 `_auto_escape`(`--auto` 路徑)明確 `with _vault_write_lock(env.vault):` 包住讀 existing、判、寫整段,且 9340-9341 行的註解正是在講「兩個程序同時寫,各自讀到還沒包含對方那筆的 existing,去重會被繞過」這個併發坑。spec 第 44 行講的「既有的圖譜寫入鎖」如果指的是這把 `_vault_write_lock`,那麼它目前只覆蓋 `--auto` 路徑,並不覆蓋手動記帳路徑——「既有」二字對手動記帳這條路不成立。`--withdraw` 在語意上跟手動記帳同屬「使用者互動式敲指令」的路徑,若實作者依 spec 字面理解「反正已經在鎖裡了」而不特別加鎖,兩個同時執行的 `--withdraw`(或一個 `--withdraw` 撞上一個手動 `loop escape <id> ...`)之間就沒有互斥——不是資料損毀等級的災難(單筆 `open('a')` append 本身在多數檔案系統下不會撕裂單行),但會讓「先讀撤回目標 token 是否存在」這類未來要加的檢查邏輯出現 TOCTOU 競態,而 spec 沒有提示這個落差。

已看,無:PRIOR-ART 提到的機制(`_escape_rows_for`、既有的圖譜寫入鎖、`_plan_for_loop`、`loop canary-stats` 的「一本帳一支統計子指令」形狀)在程式碼裡都查得到、命名與行為與 spec 描述一致;`loop_kind` 推斷規則第一節裡「代碼審自動記的歸 design、loop 欄故意寫成去掉 code- 的計劃名」對照 `scripts/lumos:8005-8011` 屬實(`derived = str(loop)[len("code-"):]`、`_auto_escape(env, "code-loop", ...)`),不是誤讀;S3 條款要求 `loop escape --list` 與 `rule-gap` 改走 `_escape_rows_for` 這件事本身,對照 `scripts/lumos:9434-9455`(--list 直接開檔讀)與 `scripts/lumos:20229-20244`(rule-gap 直接開檔讀)屬實,確實兩處都還沒走共用讀法;逃逸帳寫入鎖與圖譜合約的關係只涉及 `.escape-log.jsonl` 這本獨立帳本,不寫 `.canary-log.jsonl`,對照 `Systems/loop-convergence-recording` 節點宣稱的收斂判準(tail-K、canary caught/missed)沒有交集,不影響該節點宣稱的行為;逃逸帳讀寫的併發、效能、金流/對外送出/不可逆(撤回本身宣稱除外,見 F3)等實務隱患段落描述與程式碼現況相符,沒有另外發現的洞。

總結:最嚴重 severity 為 major;blocking 共 4 條。
