severity: major

## 一、分層與依賴方向

**大體對齊。**
- **共用函式的往下借法與鄰居相同。** 新指令往下借 `_spec_gate_judge_items`、`_isolated_worktree`、`_gov_rows_at`、`_nodehome_name_status` 這些共用函式,方向沒有反。
  - `_spec_gate_judge_items` 的 docstring 寫明「聚合、印出、跑不起來時怎麼辦都留在呼叫端」,新指令照這個分工。file: `scripts/lumos:15105`
  - 把樹準備從呼叫端抽成共用函式,是 `_isolated_worktree` 原本就走的路(guard kill 與修正關卡共用)。file: `scripts/lumos:26074`
  - `_h2_section_lines` 加選填參數而不另寫找節邏輯,符合它 docstring 的「找節邏輯不准長出第三套」。file: `scripts/lumos:13774`
- **材料裡的名字對不上程式。** 材料與派工單都寫 `cmd_fix_check`,程式裡只有 `cmd_loop_fix_check`,樹準備那段就在它裡面。實作者照字面找會找不到。file: `scripts/lumos:21873`
- **一處依賴來源沒交代。** 見發現 6,`_door_judge` 要的 `env` 材料沒講從哪來。

## 二、命名與錯誤處理

指令名 `pr-evidence`、`pr_evidence.gate` 的開關形狀與 `block|warn|off` 壞值當 block,都和鄰居(`note_shape.gate`、`lint_new.gate`、`room_guard.gate`)一致。不對齊的有下面幾條。

severity: major
blocking: 是
引句:「任何沒預期的例外都印原因、寫 `pr-evidence-skipped`、rc0——工具壞了不擋所有人,同推送前檢查的既有約定」
- **現況不一致。** 鄰居是命令本身回 0、1、2,由呼叫端決定出錯時放行或擋下,材料把呼叫端的決定搬進了命令。
  - 推送前掛鉤才是呼叫端放行:「其他非零 → 講一句這次沒檢查再放行」。file: `scripts/hooks/pre-push:716`
  - CI 明寫相反:「其他非零(參數錯、工具出錯)照原碼讓 CI 紅……兩邊刻意不同:CI 是最後一道後盾」。file: `.github/workflows/ci.yml:260-261`
  - 同類先例是沒預期的例外轉成擋下:`scripts/lumos:11035`(安全證據閘)。
- **材料的前提不成立。** 它說「同推送前檢查的既有約定」,但 `pr-evidence` 只在 CI 跑、沒有推送前那一端。
- **參數錯誤的處理也不同。** `--base`、`--head` 找不到時,鄰居回 rc2(`test-guard` 的 `scripts/lumos:50329`:「範圍有一端在本機找不到」回 2)。材料的 S4 把「算不出」整包併進 rc0。CI 變數為空或寫錯會變成永遠靜默放行。
- **工具出錯會無聲。** 現狀下 `pr-evidence` 自己有 bug 時 CI 會綠。留的 `pr-evidence-skipped` 事件寫在 CI 的暫存檢出裡,不會回到版控。

severity: minor
blocking: 否
引句:「寫一筆 `base-replay-failed` 事件(hard)」
- **事件命名和鄰居慣例不同。** 鄰居是 gate 等於命令名(`room-guard`、`lint-new`、`note-shape`),kind 用 `blocked`/`skipped`/`skipped-env`/`warned`/`passed`,原因放 note。見 `scripts/lumos:48846-48898`。
  - 材料只有 `expected-signed` 指定了 gate(`signoff`),其餘四個 kind 沒講 gate。
  - 沒寫要登記進 `_KNOWN_GATES`(`scripts/lumos:16574`)。不登記的話 `_gate_event` 會印警告並不寫(`scripts/lumos:1840`)。
  - 沒寫例行放行事件(`base-replay-proven`)走本機帳還是版控帳。慣例是「例行觀察」列進 `_GOV_LOCAL_PAIRS`(`scripts/lumos:1638`),沒列的預設進版控帳、偏吵。
- **有先例的部分。** 規格閘自己就有帶閘名前綴的 kind(`spec-gate-record`、`spec-gate-green`)。所以 kind 取名本身可以辯護,缺的是沒指定 gate 與分流。

severity: minor
blocking: 否
引句:「head 把它放寬(block 改 warn 或 off、warn 改 off)時改照分岔點那一版判」
- **讀設定的做法分兩族。** 擋人的閘(`lint_new` 放寬、`room_guard`、`note_shape`、`drift_check`)都是 `_nodehome_reader(...)` 讀位元組,再交各自的 `_xxx_config(text)`。`_lint_new_relax` 用 `_LINT_NEW_MODE_RANK` 比寬嚴。file: `scripts/lumos:39570-39585`
- **材料借了少數那族。** `_lumos_config_at_ref` 回 dict 加狀態,現有呼叫端是 review_roles、macrobench、目標架構這類非閘設定。file: `scripts/lumos:60011`
- **後果。** 它的產出餵不進 `_note_shape_config(text)` 那種吃位元組的讀法,材料也沒說放寬比較用哪張順序表。

severity: minor
blocking: 否
引句:「逾時用 `LUMOS_REPLAY_TEST_TIMEOUT`(讀不懂、不是正數、nan、inf 都用預設 900 秒)」
- **逾時變數長出第二個。** 現有 `_run_bound_tests` 已有每支逾時變數 `LUMOS_TEST_TIMEOUT`(預設 180 秒,0 是不限)。file: `scripts/lumos:69041`
- **解析寫法也是新的。** 鄰居是 `_confirm_tty_timeout`(`scripts/lumos:34220`)那種寫法,材料另立一套。
- **材料有講理由。** 冷樹第一次編譯會超過 180 秒,所以是有理由的分歧。

## 三、第二種做法

**1. 指令參數形狀。**

severity: minor
blocking: 否
引句:「lumos pr-evidence --base <提交> --head <提交> [--json]」
- **鄰居的做法。** `test-guard`、`room-guard`、`note-shape`、`drift check`、`push-range`、`bound-tests` 全都是 `--diff A..B` 加 `--repo`。範圍的驗證統一走 `_lens_range_ok`,它拒絕 `-` 開頭、`...`、空白。file: `scripts/lumos:64778`、`scripts/lumos:73474-73483`
- **新指令的缺口。** `--base`、`--head` 是全專案第一個兩旗標形狀,也沒提 `--repo`,繞過了 `_lens_range_ok`。未驗證的字串直接進 `git merge-base`,等於開了參數注入的口。
- **處理方向。** 用 `--diff` 形狀,或明寫為何不用並自行驗證不以 `-` 開頭。

**2. 分岔點的算法。**

severity: minor
blocking: 否
引句:「指令內部先算 `git merge-base <base> <head>` 當分岔點」
- **專案已有一族算分岔點的函式。** `_lens_fork_point`(`scripts/lumos:49716`,被 `_tg_start` 用)、`_lens_push_base`、`_push_range_start`、`_lens_default_base`(`scripts/lumos:65260`)。
- **它們的文件把「並存」當債。** `_lens_push_base` 的 docstring 寫「兩支並存到那三道驗過合過主線的形狀為止,收斂路記在 Issues」。`_lens_trusted_ref`(`scripts/lumos:60038`)還特地寫了為什麼不併進去。
- **新指令是第五支。** 明確給 PR 目標分支時,直接 merge-base 是對的,所以這條不一定錯。
- **缺的東西。** 材料沒寫為何不用現有那族,也沒像 `_lens_trusted_ref` 那樣分開處理 merge-base 的 rc1(沒有共同祖先)與其他失敗。⚠ 交編排者決定要不要補一句理由。

**3. 取門判定的 env。**

severity: minor
blocking: 否
引句:「用 `_note_text_at_rev` 讀 head 版本的計劃文字、`_note_from_text` 組成筆記物件(同 load_vault 的解析,不另寫一套)」
- **現況。** `_door_judge(env, note, text)` 的 `_door_linked_signals` 要查 `env.notes`(連到的節點有沒有合約或 risk 標籤)。file: `scripts/lumos:14007`
- **現有四個呼叫端。** 全都用工作目錄的 `Env(vault)`。
- **鄰居的做法。** 獨立指令(`test-guard`、`room-guard`、`security evidence`)都在 `Env(vault)` 之前分流,不載圖譜。要在任一提交上評估筆記,專案的單一做法是 `Env.from_texts`(`scripts/lumos:980`;`scripts/lumos:54208` 也在用)。
- **材料沒講 env 從哪來。** 有兩種可能:在 CI 的 pull_request 事件載入工作目錄的 `Env`(那是合併提交的圖譜,不是 head),或另造一份。前者的連結訊號會對錯版本,後者是第二條管道。⚠ 材料沒講清楚,交編排者。

**4. 表格拆格。**

severity: minor
blocking: 否
引句:「這支拆格寫成共用函式;專案裡另外兩處寬鬆的拆法用途不同、不改,寫回筆記時註明三者的關係」
- **已經有兩處寬鬆拆法。** `scripts/lumos:27561` 與 `scripts/lumos:51363`,都是 `strip("|").split("|")`。
- **新增第三套。** 這一支嚴格版是為了指紋穩定,有理由且已揭露。
- **屬於第二種做法。** 但仍是第三種拆格邏輯。

**5. 兩種「先紅」的證明方式並存,不列為不對齊。** 風險低走規格閘「現在跑一次必須紅」,風險高走 PR 檢查的分岔點重播。
- **材料已經處理。** 決策 d1、d7 白紙黑字,且共用 `_spec_gate_judge_items`、`_spec_gate_twoway_static`、`_clause_check_twoway`。
- **提醒一點。** 兩邊訊息的措辭要保持一致;共用的靜態檢查已經是同一份程式。

## 四、落點

**開新 Systems 家 `pr-evidence`(`--code scripts/lumos`)合理。** `room-guard` 與 `test-guard` 都是一個指令一篇、`about_code` 指 `scripts/lumos`,負責範圍開頭寫「負責 lumos X」。

severity: minor
blocking: 否
引句:「的 pull_request 事件加一步,呼叫 `lumos pr-evidence --base ${{ github.event.pull_request.base.sha }}」
- **CI 步驟的寫法和鄰居不同。**
  - 鄰居一律把事件值放進 `env:`,再用 `"$BEFORE..$SHA"` 帶雙引號,並加 `--repo .`(`.github/workflows/ci.yml:211-226`、`ci.yml:235-246`)。
  - 鄰居對 rc1 印 `::error::` 說明,其他碼照原碼讓 CI 紅(`ci.yml:219-225`)。
  - 材料是 `run:` 裡直接內插 `${{ }}`、沒 `--repo`、沒寫 rc 處理。
- **步驟放在哪個工作沒寫。** 現有的 lumos 檢查步驟全是 `if: github.event_name == 'push'`,這是第一個掛在 `pull_request` 的。
  - 它該放 `gates` 工作(`timeout-minutes: 20`,`ci.yml:177-180`),還是自己一個工作,材料沒講。
  - 材料說「整體上限交給 CI 工作的 timeout-minutes」,但冷樹重播兩棵 Android 專案可能超過這個數。

不對齊共 9 條,其中 major 1 條
