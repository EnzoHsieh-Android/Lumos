severity: major

## 逐類掃過

1. 不可信輸入流到危險操作:已看,無。`_patch_file_changes` 新增的二進位分支(讀 `index` 行取新版 blob 雜湊、`GIT binary patch` 資料行)只做字串切割與 `hashlib.sha256`,取出的內容從未進 `open()`/`subprocess`/模板組裝,不構成路徑穿越或命令注入;bound-tests 新增的 `not_run`/`_no_run_cmd_reason` 只是把既有設定值印出來,不影響 `run_cmd` 實際怎麼被執行。
2. 登入與權限(審查閘繞過):見 G1。`_disposal_security_step` 本體(required-gated 席出席判定、留痕 sha 對帳、`_patch_file_changes` 覆蓋比對)這輪新增/修補的邏輯本身沒有找到繞過路徑——已用二進位與文字兩種輸入獨立重跑驗證,rebase 不誤判、內容改了指紋一定變。真正的洞在同一支檔案裡的鄰居函式。
3. 密鑰與個資:已看,無。這輪新碰的程式碼只操作模型名稱常數(`gpt-5.6-sol`)、檔名、severity、sha256,沒有寫入憑證或個資;測試檔裡沒有看起來能用的真帳密。
4. 加密與傳輸:已看,無。sha256 只作內容比對(完整性),沒有新增網路傳輸或憑證驗證邏輯。
5. 執行邊界:見 G1。Codex 席位 TOML 寫入邏輯(`_install_codex_agent`)這輪未被觸碰,只換了常數字串;bound-tests 執行 `run_cmd` 沿用既有 `_shlex.quote(method)`,這輪沒有新的注入面。
6. 行動端:本案無行動端程式,已看,無。
新依賴:已看,無。這輪只用到標準庫 `hashlib`/`shlex`,沒有新增第三方套件、沒有未鎖版本的依賴。

## Findings

### G1
severity: major
blocking: 是
引句:「`lumos loop next` 的 `disposal_cmd` 模板」
`_disposal_security_step` 這輪把補救指令的 `--loop {loop_id}` 改成 `--loop {_shlex.quote(loop_id)}`(見 r3-delta.patch 第 180 行的舊版 `--loop {loop_id}` 即本輪修掉的樣子),但同一支檔案裡 `cmd_loop_next`(這份 diff 也有改動,r3-snapshot.patch `@@ -8112,21 +8120,21@@`/`@@ -8310,21 +8318,21@@` 兩處)組出的 `record_cmd`/`disposal_cmd`/`disposal_gate` 三個字串(`scripts/lumos:8217`、`:8225`、`:8231`)仍是 `--loop {loop_id}` 原樣塞入、完全沒引號,而且這三個才是**每次**開審查輪都會印出來的主要建議指令(`record_cmd` 在文字模式與 JSON 都印;工具輸出白話三段式的慣例就是要編排者/代理人原樣照抄執行)。攻擊路徑:誰——能影響 loop 主題命名字串的人(操作者自己手誤、或主題名取自外部來源如自動化管線挑的 issue/分支名);從哪裡——`lumos loop next <loop_id>`,`loop_id` 是完全自由字串、無字元白名單(`ls.add_argument("loop_id")` 沒有 pattern/choices);送什麼——`loop_id` 夾帶 shell 特殊字元,例如 `code-x; touch /tmp/pwned #`;拿到什麼——只要有人依專案慣例把印出的 `record_cmd` 貼進終端機執行,`;` 之後的指令就會以執行者權限跑起來,等於任意指令執行。
file: `scripts/lumos:8217`
最小重現(已在本機實際執行,非推論):用 `loop_id = "code-x; touch /tmp/lumos_pwn_marker_12345 #"` 呼叫 `lumos loop next <該id> --tier standard --orchestrator claude --json`,回傳的 `record_cmd` 欄位原樣是
`lumos canary record caught|missed --loop code-x; touch /tmp/lumos_pwn_marker_12345 # --auditor <席> …`;
把這段文字丟進 `bash -c "$RECORD_CMD"`,`exit=0` 且 `/tmp/lumos_pwn_marker_12345` 真的被建立(等同任意程式碼已執行)。同一份 `loop_id` 帶進 `disposal_cmd`、`disposal_gate` 兩個欄位也是同樣未跳脫。
這證明本輪「補救指令裡的迴圈編號加 shell 引號」這個修法**沒有涵蓋它自己宣稱要解決的整個類別**——只堵了 `_disposal_security_step` 這一個失敗分支印的指令,`cmd_loop_next` 這三處(每輪開審必經的主線輸出)仍是同一個洞。r2 資安席報告把 `_disposal_security_step` 那個同構問題判成 minor/不擋(理由是「印給人看、loop_id 慣例上操作者自己命名」),但我在這輪能對同一個前提做出實際執行(見上方重現),而且 `record_cmd` 是每輪都會走到的常態輸出,不是只有失敗才出現的邊角分支,風險面比已修的那處更大,故升級為 major/擋。

## LUMOS-IMPACT 固定席逐條

- `design-loop.md`(處置閘第五步 ★INVARIANT★):不影響。`_disposal_clause_step` 本體這輪零改動,新增的第六步(資安席)與第五步互不共用狀態,合取關係只是並列多一項。
- `bound-tests-gate.md`(★INVARIANT★ 紅/懸空/偽證據/方法名不合法一律擋,無 run_cmd 不擋):不影響且不弱化。`_run_bound_tests` 裡 `if status != "real"` 的紅燈判定仍排在「有沒有 run_cmd」檢查之前,dangling/fake/bad-name 照樣先標紅;新邏輯只是讓「沒設 run_cmd 的平台」不再拖累「有設 run_cmd 的平台」被整批放棄,擋的範圍只增不減,合約守衛沒有變鬆。
- `canary-audit.md`(record/second 落盤與 second 不進 gate rc):不影響,兩個函式本體這輪未被觸碰。
- `guard-kill.md`(rc 優先序、`--json` 純度):不影響。`cmd_guard_kill` 唯一改動是把重複的 `test.run_cmd` 存在性判斷抽成 `_config_has_top_run_cmd()` 共用函式,`file=sys.stderr if as_json else sys.stdout` 的分流與 rc 判斷邏輯逐字保留。
- `slim-get-一行安裝.md` / `slim-install-安裝器.md` / `slim-uninstall-一行卸載.md` / `授權與歸屬.md`:不影響。這份 diff 沒有任何一個 hunk 落在 `.ps1` 產生、CLAUDE.md 注入、bin/manifest 安裝卸載、授權檔白名單相關函式,列進牽連檔只是因為整支 `scripts/lumos` 被改動。

## 總結
最高 severity 為 major;blocking 共 1 條(G1)。
