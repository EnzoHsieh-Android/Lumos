severity: major

以下四問逐問答。第 1、3 問各有結構性不對齊,第 2、4 問只有命名與落點上的小差異。

## 問 1:分層與依賴方向

severity: major
blocking: 是
引句:「`lumos set <計劃> status done`:計劃有 `[evidence]` 條款或有〈待決問題〉一節時,先跑同一套交付檢查,沒過就拒絕」
`cmd_set` 是圖譜寫入原語(set/append/remove 等),它只動 frontmatter。它的守衛都是自己欄位的形狀:骨架欄不能刪、清單欄要有 value、白名單外的 key 一律回 2。本案讓它往上呼叫交付檢查,等於讀證據帳、比對程式內容指紋、再寫治理帳事件,是從寫入原語層直接呼叫判定層。
現行 `status done` 只有 lint 的值域與 enum 檢查,沒有任何指令在 `set` 裡跑語意檢查,所以這也是第一個先例。
file: `scripts/lumos:19692`(`cmd_set`)
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:41`(寫入原語的定位)
建議:把「done 擋不擋」放在規格閘或 `spec-trace` 那一層,`set` 只透過既有的共用判定函式問一句。

severity: major
blocking: 是
引句:「交付檢查每次擋下或放行都寫一筆治理帳事件(沿用 `_gate_event`)」
`cmd_spec_trace` 的 docstring 寫明「唯讀」。`--delivery` 要寫治理帳、讀證據帳,就把一支唯讀追溯指令變成了有副作用的閘。
既有的寫法是「做判定的子命令順便落帳」,但那些子命令本來就是閘:`spec-gate`、`code-loop`、`doctor --ci`。把閘塞進唯讀指令,等於改了 `spec-trace` 的角色。
`--delivery` 與 `set done` 又會各寫一次事件,而且計劃沒說兩條路徑誰記帳、會不會重記。
file: `scripts/lumos:8168`(`cmd_spec_trace` 的 docstring)
file: `scripts/lumos:1492`(`_gate_event` docstring:寫者是做判定的那一方)

## 問 2:命名與錯誤處理

severity: minor
blocking: 否
引句:「單列保證小於 4KB(既有追加寫法 `_ledger_append` 的上限),超過的欄位只留在原始檔目錄;追加用單次寫入,帳檔不存在時建立。」
- 同層的 `kill-log` 用 `open(...,"a")`,`ci-log` 用 `_jsonl_append_verified`(寫完讀回自驗,失敗回 2)。計劃要的「寫不進回 2」其實是 `_jsonl_append_verified` 的行為,不是 `_ledger_append` 的。
- `_ledger_append` 沒有 `O_CREAT`,docstring 明寫「建檔只屬觸發端」。它超過 4KB 是丟 `ValueError`,不截斷。這與計劃說的「帳檔不存在時建立」「超過的欄位留在原始檔目錄」兩處都對不上。
- 所以計劃若真用 `_ledger_append`,就得自己補建檔,還得在寫前先裁欄位。
file: `scripts/lumos:20557`(`_ledger_append`)
file: `scripts/lumos:10052`(`_jsonl_append_verified`)
file: `scripts/lumos:17527`(`kill-log` 的寫法)

severity: minor
blocking: 否
引句:「中斷時先寫帳再以 130 結束」
- 既有指令的回傳碼只有 0/1/2,全檔找不到 130 的先例。
- 這是新的第四種退出碼。
- 同一節說「FAIL 或 BLOCKED 回 1」,中斷這條卻回 130,同一個 BLOCKED 有兩種退出碼。
- 另外,`set done` 被擋的回傳碼計劃沒寫。既有 `cmd_set` 的所有擋下都回 2,而 `--delivery` 的沒過回 1,兩邊可能不一致。
file: `scripts/lumos:19692`(`cmd_set` 的擋下都回 2)

severity: minor
blocking: 否
引句:「形狀照棧別題庫 `_STACK_QUESTION_SPECS` 的條目寫法(`{id, stage, ask, when[]}`」
- 實際條目是 `{id, q, when, when_raw?, needs_backing?}`,問句欄叫 `q`,不叫 `ask`,也沒有 `stage`。
- 計劃說「照條目寫法」,欄位名卻換了。要嘛沿用 `q`,要嘛在計劃裡明講為什麼不同。
- 另外,題庫現在已有 `_PITFALL_QUESTIONS` 與 `_STACK_QUESTION_SPECS`,再加一張 `_REQUIREMENT_FACETS` 是第三張同類表。計劃已寫理由,結構上不算違規。
file: `scripts/lumos:26516`(`_STACK_QUESTION_SPECS`)
file: `scripts/lumos:26474`(`_PITFALL_QUESTIONS`)

## 問 3:第二種做法

severity: major
blocking: 是
引句:「內容一樣指紋就一樣,所以提交筆記、改帳本、壓提交、rebase 都不會讓證據過期」
這是第二種版本有效性判法,和 `_codeloop_record_valid_ex` 並存。後者看「同 sha,或祖先加中間只動簿記檔」。
- 新判法的排除範圍不同。引句:「排除知識圖譜目錄、`governance/`、`.lumos/` 與簿記名單後算 sha256」。這會整個排除 `governance/` 與 `.lumos/`。
- 既有判法只認 `_BOOKKEEPING_FILES` 與 `_BOOKKEEPING_DIRS`(code-loop、review-reports、replay 等子目錄)。`_codeloop_bookkeeping_code` 的註解還明寫「簿記資料夾底下的程式檔不算簿記」。
- 兩套規則會對同一次提交給出不同的「有效/失效」答案。例如 `governance/` 下新增一支腳本:指紋認它是簿記,代碼審留痕認它是程式。
- 計劃只說明了 d3 為什麼不綁 pass 狀態,沒說兩套判法為何不能共用,也沒說簿記名單的單一源怎麼維持。
- 計劃還說要把帳檔加進 `_BOOKKEEPING_FILES`,卻同時另算一份排除清單。這正是 `_BOOKKEEPING_FILES` 註解裡寫過的「兩處分開寫會漂移」。
- `ls-files -s` 已有 `_nodehome_git` 的呼叫先例,不用另寫。
file: `scripts/lumos:48870`(`_codeloop_record_valid`)
file: `scripts/lumos:48887`(`_codeloop_record_valid_ex`,含 `_codeloop_bookkeeping_code`)
file: `scripts/lumos:27097`(`_BOOKKEEPING_FILES`、`_BOOKKEEPING_DIRS` 及其註解)
file: `scripts/lumos:29280`(`ls-files -s` 的既有用法)

severity: major
blocking: 是
引句:「照破壞測試 `_kill_run` 的子程序寫法,但改掉它不合用的兩處」
這是第三份殺程序群組的子程序執行函式。`_kill_run` 與 lint 那支(27687 附近)各有一份 `killpg` 加 Windows 退路。
- 新函式改了三處:shell 換成參數清單、stderr 不再合併、改串流寫檔。這不是兩處,也沒說明是否抽共用的 killpg 部分。
- 沒有說明哪些部分與 `_kill_run` 共用,第二套會與它各自漂移。
file: `scripts/lumos:17169`(`_kill_run`)
file: `scripts/lumos:27672`(lint 的 Popen 加 `killpg`)

severity: minor
blocking: 否
引句:「`lumos init` 與 `lumos update` 把 `.lumos/evidence/` 加進忽略清單。」
- 先確認用法:`.lumos/` 目前放的是專案宣告檔(`config.json`、`lint.json`、`lint-waivers.json`),全部進版控,不放本機輸出。
- 本機執行期狀態的既有位置是 `governance/runtime/`,`init` 寫的是 `governance/.gitignore`,註解明寫「per-machine 的執行期狀態」。
- 本 repo 的 `.lumos/testmap.json` 是被忽略的產物,但那條只在本 repo 自己的 `.gitignore`,`init` 沒有處理。
- `init` 目前只寫 `docs/.gitignore` 與 `governance/.gitignore`,沒有根層的忽略清單,計劃說的「忽略清單」要新增第三處。
- 另外,doctor 對 `.lumos/` 做了捷徑與符號連結的防護(`scripts/lumos:4037`),往裡塞大量原始檔會讓那套防護的假設變複雜。
- 結構上能運作,只是和目錄既有用途不一致。
file: `scripts/lumos:23100`(`governance/.gitignore` 的寫入)
file: `scripts/lumos:8544`(`governance/runtime/` 的既有用法)

## 問 4:落點

severity: minor
blocking: 否
引句:「  - Systems/lumos-cli-read」
- `lands_in` 少了 `Systems/lumos-cli-lifecycle`。`init`/`update` 的忽略設定是它的職責(responsibility 寫明負責 init、update),計劃卻改了這兩個指令。
- 其餘大致合理:`pitfalls --stage` 進 `pitfalls-code-loop`,規格閘擋法進 `規格閘`,`set` 進 `lumos-cli-write`,`spec-trace` 進 `lumos-cli-read`,新指令各開新節點。
- ⚠ `_BOOKKEEPING_FILES` 與留痕判定的 home 在 `pitfalls-code-loop`,已列入;`gov` 統計接證據帳,本 repo 沒有單獨 Systems 節點明確擁有 `cmd_gov` 的載入清單(只在筆記內容審、anchor-integrity 等提到),所以哪一篇管它我判不準。
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:8`

總結:不對齊共 8 條,其中 major 3 條
