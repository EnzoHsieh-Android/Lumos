severity: major

我讀了被審的 r2 修訂稿和凍結提交的計劃筆記,對照 `/Users/enzo/orca/workspaces/lumos-toolchain/interview-gaps` 的 `scripts/lumos` 與規則包。我只讀、沒改任何檔,也沒建暫存目錄。以下的行號都出自 `scripts/lumos`,另有標路徑的除外。

## 1. 分層與依賴方向:有一處不對齊,兩處待釐清

整體放對了位置。

- **分級邏輯放進單一算法 `_pitfall_tier`。** file: `scripts/lumos:64523`。鄰居就是這樣做的。`pre-push` 掛鉤和 `code-loop check` 都經 `pitfalls --json` 取分級(file: `scripts/hooks/pre-push:566-577`),所以沒有人繞過入口。
- **行內忽略註解接進新增告警閘。** 它沿用 `_lint_new_diff_claims` 與 `_lint_new_key` 的指紋比差(file: `scripts/lumos:42830`、`scripts/lumos:42855`),也沿用 `lint-waive`,沒有另開放行流程。對齊。

不對齊的是「讀哪一版設定」,這條是 major。

- 稿裡寫「範圍起點那一版與終點那一版取聯集」。專案裡同一件事早有共用入口 `_trusted_decl_ref`,它退回「起點與主線的分叉點」那一版。file: `scripts/lumos:63651`、`scripts/lumos:63674`。
- `_trusted_decl_ref` 的說明明寫「分級、派工鏡頭、推送檢查、角色鏡頭共用」。
- 緊鄰分級呼叫處,`arch_targets` 就是這樣讀的。file: `scripts/lumos:65131-65132`。
- 已結案的事故 `Issues/角色鏡頭在起點不在主線時讀分支宣告` 記的就是這個坑。修補輪的起點是被審分支自己的提交,分支在上一輪把宣告改掉,下一輪就照改過的讀。
- 稿的「起點那一版」重新引進同一個坑。舉例:推送 1 把 `src/auth` 從清單拿掉,推送 2 起點已是沒有它的版本,改 `src/auth/Login.kt` 就判不成 high。
- 修法是起點側改走 `_trusted_decl_ref`,終點側再取聯集。聯集的「新加當次就生效」是合理的偏離,但起點側不該另選版本。

兩處待釐清,見第 3 問的 finding:
- 稿沒說「這次改到的檔」從哪來。鄰居 `_residual_tier_hits` 自己跑 `git diff --name-only -z --no-renames`。file: `scripts/lumos:64800-64802`。`_pitfall_tier` 收到的 `files` 已被副檔名、測試、vendored 篩過。file: `scripts/lumos:65147`。
- 工作樹模式的隔離沒說清楚,見第 3 問。

## 2. 命名與錯誤處理:鍵名對齊,讀不出的方向不完全一致

- **鍵名對齊。** `risk_high_paths` 是頂層、snake_case、字串清單,跟頂層宣告式清單 `arch_targets`、`review_roles` 同形。`*_paths` 的字尾跟 `shared_paths`、`include_test_paths` 一致。
- **200 項上限數字對齊。** 數字同 file: `scripts/lumos:44924`(`E2E_PATH_LIST_MAX`),但稿寫死 200,沒說複用那個常數。
- **理由字串對齊。** 檔名取 3 支加「等 N 支」,並經 `_plain_label` 清洗,跟 `_residual_tier_reasons` 一致。file: `scripts/lumos:64454`。

不對齊的有兩處,都是 minor。

- **讀不出的方向。** 稿說「JSON 解析失敗就判 high,跟殘留索引讀不出的方向一致」。實際上鄰居分得更細。
  - 起點索引內容壞掉不升級,只有 git 讀不出才升。file: `scripts/lumos:64811`。
  - 設定檔鄰居 `_arch_targets_at` 規定「原文沒提到這個鍵就當沒宣告」。file: `scripts/lumos:63684-63699`。
  - 照稿寫,沒宣告過 `risk_high_paths`、只是 `config.json` 多一個逗號的專案,每次推送都被判 high。
  - 稿也沒處理 git 讀不出的狀態。`_lumos_config_at_ref` 有 `ok/missing/unreadable/git-failed` 四態。file: `scripts/lumos:63624`。
- **新規則名和 `source` 值。**
  - 規則名 `lumos/inline-suppression` 是新前綴,既有內建規則用 `tq/<kebab>`。file: `scripts/lumos:42992`、`scripts/lumos:53252`。
  - `source: lumos` 是第三種寫法,既有是 `lint:<driver>` 與 `pitfalls-builtin`。file: `scripts/lumos:42377`。
  - 訊息把 `lint-waive` 的用法寫進去,但擋下輸出本來就逐條印放行指令。file: `scripts/lumos:41730`。

## 3. 第二種做法:一處 major,兩處 minor

**major:套件執行器解析另起一套。**
- 稿在命令切段之後另訂規則:`npx/bunx/uvx` 取「下一個非選項的詞」,`pnpm exec`、`yarn`、`uv run`、`python -m` 同理。
- 既有的「剝包裝詞」只有一處:`_SHELL_WRAPPERS` 加 `_detekt_skip_wrapper_opts`。file: `scripts/lumos:40311`、`scripts/lumos:40314`、`scripts/lumos:40329`。
- 鄰居逐個包裝詞寫明選項要不要吃值(`env -u X`、`nice -n N`)。稿的「下一個非選項的詞」沒有這層。`npx -p pkg tool`、`uv run --with x ruff` 會取錯詞。
- 切段與 `_cmd_basename` 的複用是對的:`_detekt_walk_segments` 的說明本來就寫「共用」。file: `scripts/lumos:40599`、`scripts/lumos:40588`。
- 不對的是套件執行器這層沒說要併進包裝詞表,字面讀起來是「切段外再自寫」。⚠ 稿沒指明實作落點,若實作時併進 `_detekt_strip_prefix` 的詞表就不算第二種做法,請編排者要求稿寫明。

**minor(⚠):讀某版設定的函式沒指名複用誰。**
- 稿的 PRIOR-ART 對路徑比對明指複用 `_e2e_norm`、`_e2e_under`,但讀設定那段沒指名。
- 既有三套:`_lumos_config_at_ref`(只收 ref)、`_residual_index_read_at`(`rev=None` 讀工作目錄,自帶狀態)、`_stack_questions_config`(只讀工作目錄)。
- 「終點是工作目錄」目前沒有現成的同態函式。若實作另寫一支,就成了第四套。

**minor:其他不指名處。**
- 鄰居把每種升級原因抽成 `_xxx_tier_hits` 加 `_xxx_tier_reasons`,分級函式只串接。file: `scripts/lumos:64454`、`scripts/lumos:64768`。稿是「在分級函式裡讀」,沒說抽成對。
- 比對前沒提 `nfc(_posix_norm())`。tier 鄰居比路徑前都先做這一步(file: `scripts/lumos:64652-64664`),`_e2e_norm` 只去空白、尾斜線、前導 `./`。file: `scripts/lumos:44906`。中文路徑在 macOS 的 NFD 與 git 的 NFC 會對不上。
- 清單每項沒說要不要過 `_e2e_relpath_err`(file: `scripts/lumos:44884`),`shared_paths` 是這樣驗的。
- 「對不到檔」那行輸出沒說走哪個通道。鄰居的慣例是 `--json` 加欄位並維持「沒宣告的專案輸出逐字不變」,或 stderr 的 `提醒:`。file: `scripts/lumos:65108`。

**minor(⚠):行內忽略註解掛在哪一層。**
- 稿說「只在推送範圍模式 `_lint_new_tools`」「每跑完一條命令」,又列「工作樹模式不做」。
- 但「每跑完一條命令」只能落在 `_lint_new_run_cmds`,而它同時被推送路徑和工作樹路徑呼叫。file: `scripts/lumos:43263`、`scripts/lumos:41607`。
- 稿也要求同一行跨命令去重,那得是跨命令的狀態,不是每條命令各算。
- 鄰居分流的做法是 `wcfg = dict(cfg, wt_argv=True)` 的旗標,或各自呼叫端另接。file: `scripts/lumos:41606`。稿沒選,實作時容易漏進工作樹模式。

**其餘對齊:**
- 規則例外跟 `kt-register-without-unregister` 的 Application 排除同一形狀:`not: inside: class_declaration`,有 `delegation_specifier` 搭 regex,加 `stopBy: end`。file: `configs/ast-grep/kotlin-android/rules/architecture.yml:293-299`。目標規則在 `configs/ast-grep/kotlin-android/rules/state.yml:176`,「任何一層外圍類別」和「兩個分支都豁免」都接得上。
- 路徑比對複用 `_e2e_under` 沒有另寫。`arch_targets`、`review_roles` 用 glob(`_config_glob_error`,file: `scripts/lumos:63588`),而 `risk_high_paths` 取 `shared_paths` 的整段路徑語意。兩種約定本來就並存,稿在「不做」裡講明不支援萬用字元,不算新做法。

## 4. 落點:大致對齊,一處不一致

- **`Systems/kotlin規則包`:對齊。** 負責範圍寫的是規則、樣本與型錄,且寫明「不負責新增告警閘判定」。規則例外、樣本、STATE-5 列放這裡正確。
- **`Systems/pitfalls-code-loop`:對齊。** `arch_targets`、`review_roles`、`stack_questions`、`lint_new`、`security_evidence` 的設定說明都在這篇(例:file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:237`、`:259`)。`risk_high_paths` 的說明也該落這篇。稿只提改「分級 KEY 行」,沒說要像 `arch_targets` 那樣寫一段設定鍵的說明。
- **`Systems/pitfalls-lint-adapter`:有一處不一致,minor。** 它的負責範圍(新增告警閘的檢查工具那一半加 `lint-waive`)剛好涵蓋行內忽略註解。但稿的 `lands_in` 列了它,範圍 5「跟著改的文件」卻沒列它要寫什麼。
- **使用者面文件:對齊。** `skills/lumos-code-loop/SKILL.md`、`06-代碼審與推送.md`、`docs/指令參考.md` 都已列入,跟 `arch_targets` 的文件落點一致。

## Findings

不對齊的有 7 條,下面逐條列:

1. 讀設定的起點側用「範圍起點」,不走 `_trusted_decl_ref`,重現已結案的 Issue。

severity: major
   blocking: 是
   引句:「範圍起點那一版與終點那一版(終點是工作目錄時讀工作目錄)的清單取聯集」

2. 套件執行器另訂「下一個非選項的詞」,沒併進既有包裝詞表和選項表。⚠ 稿未指明落點。

severity: major
   blocking: 是
   引句:「第一個詞是 `npx`、`bunx`、`uvx` 時看下一個非選項的詞」

3. 讀不出就判 high,沒做 `_arch_targets_at` 的「原文提到才算」,也沒分 git 讀不出和內容壞掉,卻自稱與殘留索引一致。

severity: minor
   blocking: 否
   引句:「設定檔讀得到但 JSON 解析失敗、或 `risk_high_paths` 不是字串清單、或超過 200 項 → 判 high」

4. 讀某版設定的函式、「改到的檔」來源、`nfc(_posix_norm())`、逐項路徑驗證、抽成 hits/reasons 對,稿都沒指名複用。⚠ 若實作另寫就升 major。

severity: minor
   blocking: 否
   引句:「分級函式 `_pitfall_tier` 在殘留索引那一步之後、風險型樣那一步之前,讀 `risk_high_paths`」

5. 行內忽略註解的注入位置會漏進工作樹模式,稿又說不做,也沒選旗標或另接呼叫端。⚠

severity: minor
   blocking: 否
   引句:「新增告警閘的推送範圍模式(`_lint_new_tools`)每跑完一條命令,就在改動前、改動後兩份快照上」

6. 新規則名前綴 `lumos/` 與 `source: lumos` 是新寫法,訊息還重複擋下輸出已印的放行指令。

severity: minor
   blocking: 否
   引句:「新加的行內忽略註解(<工具>)會讓檢查略過這裡:移除它,或用 lumos lint-waive <指紋> --note 寫明為什麼要忽略」

7. `lands_in` 列了 `pitfalls-lint-adapter`,但「跟著改的文件」沒列它要寫什麼;`pitfalls-code-loop` 也只提改 KEY 行,沒說要寫設定鍵說明段。

severity: minor
   blocking: 否
   引句:「`Systems/pitfalls-code-loop` 的分級 KEY 行(順序寫成:殘留索引、高風險路徑、風險型樣)」

不對齊共 7 條,其中 major 2 條。
