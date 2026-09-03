# r2 架構對齊審(主session鏡頭利用率_計劃,第 2 版整份重寫)

審材(凍結):`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/26a6b57a-9efc-4073-b845-c27e42a2fbb1/scratchpad/主session鏡頭利用率-r2.md`
只判「跟本 repo 既有做法不一樣」;不找 bug、不評風格。編號從 f9 起(f1–f8 是 r1)。

## 零、前輪 8 條驗收

| r1 | 判 | 依據(審材逐字) |
|---|---|---|
| f1 hook 直接 append usage-log(跨層) | **已改** | 「subprocess 呼叫 `lumos lens push …`」+「★hook 不自己開帳檔★(arch:hook 一律經 lumos 子命令;唯一直接寫帳的先例已撤)」。與 impact-hook / dispatch-lens-hook 「要圖譜領域的東西就 subprocess 叫 lumos」一致 file: `scripts/hooks/claude/dispatch-lens-hook.py:70-72` |
| f2 治理觀測事件塞檢索語料帳 | **已改** | 「(將建,檔名候選 docs/.lens-log.jsonl)」的獨立帳+「不進使用帳(它是檢索語料)」;`.usage-log.jsonl` 維持只由 `_usage_log` 寫 file: `scripts/lumos:7382-7392`。殘餘見 f9 |
| f3 `cmd` 值域裝事件類別 | **部分** | 欄位已改成 `kind`(對);值 `lens-push\|lens-tally` 仍不是既有 kind 的過去式動詞值域 → f12 |
| f4 一列多節點/無 node 破壞列形 | **已改(帶理由)** | 「事件形狀★一列一次推送★」並明寫「不沿用使用帳『一列一節點、cmd=子命令名』的形狀,因為這是另一本帳、另一種語意」——另開一本帳後這條自動消解 |
| f5 TTL 標記位置寫成家目錄 | **已改** | 現況段已改成「`<tmpdir>/lumos-impact-<session>/`」,與 `_ttl_marker_path` 一致 file: `scripts/hooks/claude/impact-hook.py:104-107` |
| f6 帳檔定位沒裁 | **部分** | 已裁「位置由 lumos 決定…hook 只傳 `--repo`」(方向對),但沒指名沿用哪一支定位函式,而既有帳寫者本身就有兩種 → f15 |
| f7 順序判定會逼出第二支逐字稿解析 | **已改判準、未裁歸屬** | 時間窗改「推送 ts 之後」、明寫獨立收集器不動 `collect_turn_actions` 回傳形態(對);但收集器該住哪一層、「共用 helper」共用到什麼,仍沒有機制 → f14(本輪唯一 major) |
| f8 重算腳本位置與掛勾 | **已改** | 「住 governance/eval/lens-utilization/,同席間覆蓋率那支 recount.py 慣例」,且與 REVISIT 綁定(「=REVISIT:2026-09-17 那天要跑的東西」);先例 file: `governance/eval/seat-coverage/recount.py:1-14` |

**8 條:5 條真改到、3 條(f3/f6/f7)只改一半,殘餘轉成本輪 f12/f15/f14。**

## 一、分層與依賴方向

新結構的主幹(hook 薄殼 → subprocess → lumos 子命令 → lumos 擁有帳檔)與 `dispatch-lens-hook.py` + `cmd_dispatch_lens` 的同日形態一致 file: `scripts/hooks/claude/dispatch-lens-hook.py:69-76`、file: `scripts/lumos:16594-16691`;`lumos lens push/tally` 兩層子命令有 `canary record` 先例 file: `scripts/lumos:17298`、file: `scripts/lumos:17305`;tally hook 不進 ANCHOR_FILES 與現況一致(只有會改寫子代理輸入的 dispatch-lens-hook 在內)file: `scripts/lumos:11404-11411`。以下兩條沒對齊。

### f9 登 gov 第八源缺兩樣既有源都有的東西:`gate` 字面值(有機械漂移釘)與 dedup 鑑別子

`lumos gov` 的每一源都吐一個 `gate` 值,且 `gate` 字面值受漂移測釘死——全檔 `"gate": "x"` 必須落在 `_KNOWN_GATES` 內,否則測試翻紅 file: `scripts/lumos:3467-3468`、file: `scripts/test_lumos.py:4179-4186`;去重鍵是 `(commit, nodes, gate, kind, token)` file: `scripts/lumos:3691`,canary 當年正是因為「同節點多次不該互吞」才特地補 `token` 當第 5 鑑別子 file: `scripts/lumos:3667-3676`。lens 事件沒有 commit、nodes 常同一組、kind 只有兩種,不給 token 就會整批折成一兩列——而分佈正是本案要的東西。設計只寫「`kind` 慣例」,沒給 gate 名、沒給 token。另有一處語意張力:審材自己在誠實界線寫「量測用,不是治理紀錄」,卻登進「治理事件時間軸 + 哪幾道閘沒響過」那份彙整 file: `scripts/lumos:3619-3623`。
引句:「登進 `lumos gov` 第八源(`kind` 慣例)」
severity: minor
blocking: 否

### f10 ⚠ 把「同一事件內的 hook 註冊順序」當成語意,既有註冊模型沒有這種相依

`HOOK_ENTRIES` 裡每個事件是一組彼此獨立的 command hook,各自一個 process、各自 fail-open,沒有任何一支的行為依賴自己排在誰前面(SessionStart 兩支、PreToolUse 兩支都沒有這種註解)file: `scripts/merge-claude-settings.py:33-108`。設計要求 tally hook「放在任何判斷之前」,並把理由掛在 check-graph-sync 的早退閘上——但那些 return 只結束它自己那個 process,跨 hook 本來就吃不到。照這句落地,等於在註冊表引進一條沒人維護、也沒有守衛的順序合約。標 ⚠:若這句的本意只是「不要合體進 check-graph-sync」(那一半是對的、也與現況一致),把順序要求刪掉即可,本條自動消失。
引句:「★放在任何判斷之前★(不與 check-graph-sync 合體,免得被它的早退閘吃掉、也免得污染它的兩個 list)」
severity: minor
blocking: 否

## 二、命名與錯誤處理

### f11 `lens` 與 `dispatch-lens` 各據一半:頂層命令是連字號兄弟慣例,`_lens_*` helper 前綴又已被佔用

本 repo 的同家族頂層命令一律連字號攤平——`ci-wait`/`ci-status`、`lint-check`/`lint-watch`、`dispatch-lens`,兩層子命令只給狀態機式的家族(`canary record/second`、`anchor verify/approve`)file: `scripts/lumos:17298-17305`。本案新增的是第三種:一個叫 `lens` 的兩層家族,和既有 `dispatch-lens` 共用「鏡頭」這個詞卻不同家族、不同語意(那邊是注入、這邊是記帳)。更硬的一點:`_lens_*` 這個 helper 命名空間今天整段屬於 dispatch-lens(`_lens_range_ok`/`_lens_git`/`_lens_cache_*`/`_lens_contract_*` 等 12 支)file: `scripts/lumos:16499-16592`,新子命令照慣例寫 `_lens_push`/`_lens_tally` 就會跟它混在一起,讀的人分不出哪支屬於誰。設計沒裁要合併成同一個 `lens` 家族、還是換名(如 `lens-log push`/`lens-util`)、也沒裁 helper 前綴。
引句:「經 lumos lens push/tally 子命令寫獨立帳 docs/.lens-log.jsonl」
severity: minor
blocking: 否

### f12 `kind` 的值域今天是過去式動詞/狀態詞,`lens-push`/`lens-tally` 是名詞、且把帳名抄進每一列

既有 kind 值:bypassed / warned / approved / signed / green / caught / missed / none / passed 這類過去式動詞或結論狀態 file: `scripts/lumos:3649-3685`。`lens-push`、`lens-tally` 既不是動詞,也把來源帳名重複寫進每一列——而來源在 gov 已由 `gate` 表達(見 f9)。對齊寫法是 kind = `pushed` / `tallied`,gate 另給一個名字。結構(append-only jsonl、ts 開頭)是對的。
引句:「`{ts: UTC Z, kind: lens-push|lens-tally, session_id, file, mode, pinned: [節點…]」
severity: minor
blocking: 否

### f13 薄殼 hook 的兩個既有錯誤處理慣例沒沿用:內外層 timeout 配對、`LUMOS_HOOK_DEBUG` stderr

同日那支薄殼把兩件事寫成硬慣例:①內層 subprocess timeout 必須明顯小於 `HOOK_ENTRIES` 宣告的外層(`INNER_TIMEOUT = 45` 對外層 60,註解直接掛事故)file: `scripts/hooks/claude/dispatch-lens-hook.py:22`、file: `scripts/merge-claude-settings.py:87-89`;②所有放行/失敗分支都經 `_debug()`,預設靜默、`LUMOS_HOOK_DEBUG=1` 才印 stderr file: `scripts/hooks/claude/dispatch-lens-hook.py:25-27`。設計對 tally hook 只寫「stdout 什麼都不印」——stdout 靜默是對的(且與 Stop hook 只走 stderr 的現況相容),但沒有 timeout 配對(Stop 事件現有宣告是 10 秒 file: `scripts/merge-claude-settings.py:97-108`,而 tally 要讀整份逐字稿),也沒說診斷走哪個管道;照字面「什麼都不印」落地,就是第一支完全不可觀測的 hook。
引句:「★stdout 什麼都不印★——印回給模型就是干預」
severity: minor
blocking: 否

## 三、第二種做法(收集器放 hook 還是 lumos;帳檔登記)

### f14 `collect_turn_touches` 放 lumos,但「共用逐字稿逐行迭代的 helper」在本 repo 沒有任何機制——落地必然是第二份逐字稿解析

事實三條:①`scripts/lumos` 今天完全不碰逐字稿(全檔零個 transcript 字樣),逐字稿知識只存在 hook 層——回合切點 `_is_real_user_input` file: `scripts/hooks/claude/check-graph-sync.py:86-104`、`collect_turn_actions` file: `scripts/hooks/claude/check-graph-sync.py:107-146`;②六支 hook 之間零跨檔 import,沒有共用模組、沒有 `__init__.py`,而且 hook 被複製到 `~/.claude/hooks/` 執行(`_hook_cmd`)file: `scripts/merge-claude-settings.py:15-23`,連 import repo 內的東西都做不到;③lumos 也不能反向 import hook。所以「共用 helper」在現況下沒有落點,實作只剩兩條路——新開一個共用模組(本 repo 沒有先例,且要一併解決 hook 的複製部署)或在 lumos 複製一份切點邏輯(=「本回合」語意兩份、日後各自漂移)。設計把「不改 `collect_turn_actions` 的回傳形態」寫清楚了(對,避免動 Stop 四道閘的輸入),但沒裁共用怎麼共用。同一段還隱含第二份 Bash 解析:既有 `extract_bash_file_paths` 只認 `{"rm","mv","cp","git rm","git mv"}` file: `scripts/hooks/claude/check-graph-sync.py:69`、file: `scripts/hooks/claude/check-graph-sync.py:218`,配套的 `_segment_command`/`_tokens_of`(shlex)也在 hook 檔內 file: `scripts/hooks/claude/check-graph-sync.py:178-186`,而 lumos 側今天只把 shlex 拿來 quote、沒有任何 Bash 指令切詞器——tally 要「任一 token 是圖譜根下的路徑」就得再寫一套切詞。
引句:「用★獨立收集器★ `collect_turn_touches(transcript)`→有序 [(ts, kind, path|cmd)](共用逐字稿逐行迭代的 helper,不改 `collect_turn_actions` 的回傳形態)」
severity: major
blocking: 是

### f15 「同一個定位函式」沒指名,而既有帳寫者本來就有兩種定位法,且設計自己的 0.1 秒預算把其中一種排除掉

既有兩種:七本帳的常規寫者走 `env.vault.parent`(`_usage_log` file: `scripts/lumos:7382-7392`、`_ci_log_path` file: `scripts/lumos:14864-14865`、gov 讀側 file: `scripts/lumos:3626`),唯一不經 env 的寫者 `_codeloop_gov_log` 直接用 `Path(repo_root) / "docs"` file: `scripts/lumos:16773-16784`——後者處理不了設計明寫要支援的 standalone vault(`_vault_in` 那個分支 file: `scripts/lumos:11375-11389`)。而 `env` 這條路要先 `Env(vault)` 把整個 vault 載進來(全檔註解實測 4.7 秒 file: `scripts/lumos:14229`),與設計自己在效能段寫的「lumos 啟動約 0.1 秒」互斥,等於 push 只能走 vault-free 路徑——那它就是第一個不經 `env` 又要處理 standalone 的帳寫者。指名一支(例如 `_vault_in(repo).parent`)就收斂;不指名,r1-f6 說的「長出第四種」原封不動。
引句:「★位置由 lumos 決定★(同其他帳:vault 的上一層,standalone vault 也走同一個定位函式」
severity: minor
blocking: 否

### f16 gitignore 只登記 init 的清單,但本 repo 的帳檔忽略其實落在根 `.gitignore`(ci-log 是兩處都有)

`lumos init` 產的是 `docs/.gitignore`,八本帳名寫在那裡 file: `scripts/lumos:11011-11013`;但本 repo 沒有 `docs/.gitignore`(不存在),`.ci-log.jsonl` 是靠根 `.gitignore` 第 10 行 `docs/.ci-log.jsonl` 被忽略——實測 `git check-ignore docs/.lens-log.jsonl` 目前 rc=1(不會被忽略)。設計的登記清單只點名「進 init 的 .gitignore 清單與 `_BOOKKEEPING_FILES`」,照這份落地,新帳在本 repo 會直接被 git 追蹤,「gitignored、同 ci-log」的宣稱在原生 repo 就先不成立。`_BOOKKEEPING_FILES` 那半是對的(ci-log 也在內 file: `scripts/lumos:12473-12475`)。
引句:「★gitignored★(同 `.ci-log.jsonl`;進 init 的 .gitignore 清單與 `_BOOKKEEPING_FILES`)」
severity: minor
blocking: 否

---

不對齊共 8 條,其中 major 1 條。
