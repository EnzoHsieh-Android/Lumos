severity: major

只讀,沒有動 repo。沒有做實驗,也沒有建暫存目錄,所以沒有東西要刪。結論都來自讀 `scripts/lumos` 和 `scripts/hooks/pre-push`。

**已讀,無 finding 的節**
- `residual` 加進 `INV_TAG_RE` 後,既有呼叫點沒有被改壞。我逐一讀了 `_kill_find_contract`、`guard audit` 定位與重審、`_kill_rm_rewrite`、`_guard_formal_line`、`strip_test_refs`、`_clause_body_of`。
  - 它們都只拿來剝標記後比對或當子字串,而 `[residual:Projects/a_計劃#d12]` 裡的 `/`、`#` 都落在 `[^\]]+` 內。
  - 唯一有副作用的是計劃條款行(`_clause_body_of`)裡寫在反引號中的 `[residual:…]` 也會被剝掉。這只影響文法檢查的輸入,無害。
  - `guard audit` 重審本來就只替換 `[audit:]` 那一段(`scripts/lumos:18746`),所以殘留標記天然保留。
- `cmd_loop_escape` 的 `--residual-ref` 互斥面與 `_escape_withdraw(others=…)` 路徑,計劃寫的處理跟程式的形狀對得上,已讀,無 finding。
- `_pq_decision_state` 回 `ok` / `superseded` / `missing` / `bad`,跟計劃用的語意一致,已讀,無 finding。
- 決策內容支援多行 block,所以「一行 `checker:`」可行,已讀,無 finding。

severity: major
blocking: 是 — 計劃要求的「這條分支有有效留痕」缺少實作所需的輸入,照字面做會在非 HEAD 推送、已有 skip 留痕、tag 推送時判錯,也會吞掉訊息
引句:「要求這條分支有有效的代碼審留痕」
問題:
- `spec-gate --push-check` 只收 `RANGE` 和 `--repo`(`scripts/hooks/pre-push:429`),沒有分支名,也沒有被推的 sha。
- 而 `_codeloop_record_valid(repo_root, rec_sha, marker_sha)` 要的 `marker_sha` 是被推的頂端。代碼審留痕是綁 remote_ref 目的地加被推 sha 的,所以 `code-loop check` 才有 `--branch`、`--at-sha`。
- 照計劃字面做,只能退回 checkout 分支和 HEAD。
- 計劃沒寫:`skip` 留痕算不算;只認 `pass` 是否排除 light 層級的 pass。
- 計劃也沒寫:`_spec_gate_push_check` 內有 `if not plans: return 0`、`bad is None: return 0` 兩條早退(`scripts/lumos:9064` 一帶)。
- 計劃沒定這一步放在哪。放在這兩條之後,多數推送(沒碰風險低計劃)會整個略過。
- rc1 時,hook 固定印「風險低計劃的條款測試沒全綠…」(`pre-push:443-446`),使用者看不到擋下的真正原因。
- hook 這段的逃生說明講的是 `skip` 可解,可是 push-check 若只認 `pass`,按指示做仍擋。
- CI 沒有呼叫 `push-check`(`.github` 下搜不到),`--no-verify` 後 CI 也補不回。
具體失敗情境:
- 使用者在別的分支 checkout,執行 `git push origin HEAD:feat-x`(`HEAD:別名` 是 hook 明文處理的形狀)。
- push-check 去查 checkout 分支的留痕,可能誤放行,也可能誤擋。
- 擋下時畫面是「條款測試沒全綠」,與真因無關。
佐證:file: `scripts/hooks/pre-push:429`;file: `scripts/lumos:50536`;file: `scripts/lumos:51492`

severity: major
blocking: 是 — 「主線版」在直推主線時等於被推的頂端,S6 保證的「同一提交拿掉標記也躲不掉」失效;主線算不出時的行為沒定義
引句:「讀主線版是為了同一個提交把標記拿掉、改程式也躲不掉」
問題:
- 計劃沒定義主線版怎麼取。既有函式 `_mainline_ref`(`scripts/lumos:47409`)在沒設 upstream 時退到本地 `main` / `master`。
- 它的 docstring 自己寫:推主線時本地 main 就是要推的頂端。
- 直推 main 時,「主線版圖譜」就是被推的新版。同一個提交把 `[residual:]` 拿掉再改程式,就看不到殘留。
- 新分支首推、沒有 upstream、淺 clone 時,`_mainline_ref` 回 None。`_drift_tree_env` 也可能回 None,例如 git 失敗或 60 秒逾時。
- 計劃只寫「沒有圖譜的專案什麼都不做」,沒寫「算不出主線」要擋還是放行。
- 沿用本函式「算不出就 fail-open」的慣例,守衛會在最需要它的情境靜默消失。
具體失敗情境:
- 直推 main:提交 A 刪掉某條合約的 `[residual:]`,並改它守的程式。主線版取到的就是 A 自己,沒有殘留,放行,不需要任何代碼審留痕。
- 另一種是新分支首推:沒有 upstream 時主線算不出,整道閘無聲略過。
佐證:file: `scripts/lumos:47409`;file: `scripts/lumos:37609`

severity: major
blocking: 是 — 用 rename 繞過檔案比對,守的程式改了也不被要求代碼審
引句:「這次推送範圍改到的檔只要在那些節點的 about_code 裡」
問題:
- push-check 的 `touched` 來自 `git diff --name-only RANGE`,沒有 `--no-renames`(`scripts/lumos:9071`)。現代 git 預設偵測 rename,只列新路徑。
- 主線版 about_code 列的是舊路徑,比對不到。
- 計劃要比對的是「主線版節點 about_code」對「本次範圍檔」,卻沒說要處理 rename。
- 計劃說「含綁定測試所在的檔」,但綁定測試所在檔要靠測試索引解析。索引讀的是工作樹的 `.lumos/config.json`,而不是主線版的,計劃沒處理這個版本差。
具體失敗情境:
- 同一個提交把 `scripts/foo.py` 改名成 `scripts/foo2.py` 並修改內容。
- `touched` 只有 `foo2.py`,主線 about_code 只有 `foo.py`,放行,殘留合約守的程式被改了,沒有代碼審。
佐證:file: `scripts/lumos:9071`;file: `scripts/lumos:8788`(`_spec_gate_push_candidates` 用 `_impact_home_map` 查家,同樣吃 `touched`)

severity: major
blocking: 是 — 「不准換人重問」是這套機制抗賽跑的主要對策,但完全沒有機械痕跡
引句:「不再問第二次、不換代理重問」
問題:
- 第一個代理說「測得到」這件事不寫進任何帳或決策,只存在對話裡。
- 編排者要記殘留,只要自己再派一個代理,挑到說「測不到」的那個,把它的模型與日期填進 `--checker`,寫入指令就會放行。
- 寫入指令只驗「決策裡有一行 `checker:` 且等於 `--checker` 的值」。兩邊都是編排者自己填的,驗的是自洽,不是有沒有被否決過。
- 計劃的風險段把「偽造」列為接受風險,但這裡不需要偽造,只是重跑。
- 「不准換人重問」被當成對策寫進守衛面,實際上只是散文。
具體失敗情境:
- 代理甲回「這能用現有設施測到」。編排者不補測試,另派代理乙,乙回「測不到」。
- 編排者用 `--checker 乙的模型/日期` 寫入殘留。
- 所有檢查通過,事後帳上看不出甲曾經說過測得到。
- 可行的機械痕跡:派第二個代理前先在帳或決策記一筆「已問」,寫入殘留時要求有且只有一筆「已問」,且判定為測不到。

severity: minor
blocking: 否 — 驗收條款寫了做不到的翻紅條件,但不影響設計正確性
引句:「拿掉保留的那段實作時,這支測試應翻紅」
問題:
- `guard audit` 現在就是只換 `[audit:]` 那一段、天然不碰別的標記(`scripts/lumos:18746`)。
- 沒有「保留殘留」的那段實作可拿掉,要紅只能靠改寫成整行重組。
- 這條條款在實作時會變成無法驗收的承諾。
- 建議改成「`guard audit` 改寫整行後仍含 `[residual:]`」之類可實測的條件。

severity: minor
blocking: 否 — 成本與前置過濾沒寫,單次影響有限
引句:「沒有圖譜的專案不會有殘留,這一步什麼都不做」
問題:
- 有圖譜的專案,每次推送都要把主線整份圖譜讀進記憶體(`_drift_tree_env` 路徑,另外有 60 秒上限)。
- 計劃沒寫先用 `git grep` 或一次 `cat-file` 先篩有沒有 `residual:`。
- 主線上沒有任何殘留是絕大多數推送的常態,卻要付整份載入的成本。
- 其中包含只改文件的推送,因為早退位置沒定。

最高等級 major,blocking 共 4 條(另有 2 條 minor、非 blocking)。
