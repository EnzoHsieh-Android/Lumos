severity: major

我只讀、沒改檔。這輪改法大致對齊:`_rg_methods`、`_strip_c_comments`、`_nodehome_cat_blobs_capped`、`_lens_git` 都真的重用,沒有再自建一套 Kotlin 辨識,也沒有讓配套模組自己跑 git。新加的部分裡,`tq/gate-config` 是第三種「同一次推送放寬設定」的做法,算 major;其餘是 minor。

## ① 分層與依賴方向

- 主流程方向對。`_codeloop_lint_new_step`(`scripts/lumos:67954`)呼叫 `_lint_new_verdict`(`scripts/lumos:38801`),再呼叫放在主程式的比對核心。這跟 Room 守衛放在主程式、`cmd_room_guard`(`scripts/lumos:48016`)呼叫 `_rg_*` 是同一層、同一個方向,沒有跨層直呼。
- 唯一的分層問題在 `tq/gate-config`。比對工具本來只該是「給兩端內容、吐候選」的純函式,現在卻要知道 `lint_new.gate` 這個屬於新增告警閘的設定鍵,變成比對工具反過來依賴閘。計劃裡的判定順序又先讀兩端設定來決定模式,同一份資料讀了兩次(見下面的 major)。
- `_lint_new_config(root, text=…, from_snapshot=True)`(`scripts/lumos:38429`)已經支援吃快照位元組,計劃沒說要用它。建議明寫。
- 治理帳的寫入點計劃沒指定。既有慣例是判定函式只回 dict,帳由 `_codeloop_lint_new_step` 這一層寫(`_gate_failopen`,`scripts/lumos:67962`)。留帳不要寫進 `_lint_new_verdict` 裡。
- 落點 `Systems/test-guard` 新開,跟 `Systems/room-guard` 並列是對的,見 ④。

## ② 命名與錯誤處理

對齊的部分:
- 指令名 `test-guard` 跟 `room-guard` 同一個形狀。
- 退出碼 0/1/2、終點找不到回 2,都跟 `_rg_range`(`scripts/lumos:47969`)一致。
- `_lens_range_ok` 的兩點寫法照用。
- 帳的種類字面值 `skipped`、`skipped-env`、`warned` 跟 Room 守衛一致:`scripts/lumos:47959`、`47983`、`48009`。
- 閘名 `lint-new` 已在 `_KNOWN_GATES`。
- `kind: guard` 掉進 `_lint_new_classify` 的 `hard_undone`(`scripts/lumos:38771`),會擋,結構上接得上。

不對齊的部分:

severity: minor
blocking: 否
引句:「舊紀錄沒有 `by` 欄的當人放的。」
佐證 file: `scripts/lumos:38721`、`scripts/lumos:42709`
- 這句跟現況不符。`_lint_waivers_add` 每筆都有 `by`,內容是 `$USER`(`scripts/lumos:38721`),不是沒有。
- Android 端到端驗收的 `by` 只收 `human`/`ai`,放行人另存在 `who` 欄(`scripts/lumos:42709`);`_e2e_waiver_ok`(`scripts/lumos:41923`)不認其他值。
- 照搬的話,舊的 `by: "enzo"` 會變成「不算數的放行」,或是兩種語意擠在同一個欄位。
- 另外,既有欄名是 `reason`/`ts`,端到端驗收是 `note`/`at`/`who`/`acked`/`acked_by`/`acked_at`。「照它的形狀」要明寫欄位對照和舊紀錄的遷移,不然會出現兩套詞彙。

severity: minor
blocking: 否
引句:「沒有互動終端、讀不到回答或答 n 都記 `by: ai`」
佐證 file: `scripts/lumos:42702`、`scripts/lumos:42706`、`scripts/lumos:33619`
- 計劃寫「照搬 `_e2e_waive_cmd`」,但這點不同。端到端驗收答 n(`ans is False`)是不放行、rc 1,Ctrl-C 也是 rc 1;計劃是答 n 仍放行並記 `ai`。
- 端到端驗收呼叫 `_confirm_tty(..., stdin_timeout=True)`,避免掛著虛擬終端的流程永遠等。計劃沒提這個參數。
- 端到端驗收的放行帳帶 `extra={"fingerprint", "by"}`;計劃沒說 `lint-new` 的 `waived` 帳要不要帶 `by`。

severity: minor
blocking: 否
引句:「健檢與推送前小結列出還沒人看過的 AI 放行(只提醒、不擋,跟端到端驗收一樣)」
佐證 file: `scripts/lumos:42525`、`scripts/lumos:68900`
- 端到端驗收的提醒還有一處:開場掛鉤有逐字複本 `_e2e_ai_pending_one`,並有測試盯兩邊一致(`scripts/lumos:42525`)。計劃沒有這一處。
- 推送前小結走 `_cl_say_e2e_notes`(`scripts/lumos:68900`),擋下和放行都印;`_cl_say_ok_extras` 只在放行時印。計劃沒說掛哪一個。
- 「跟端到端驗收一樣」要嘛補齊,要嘛明寫少了開場提示。

severity: minor
blocking: 否
引句:「`tq/` 候選改成最多印 50 條,每條印規則代號、檔案、完整原因」
佐證 file: `scripts/lumos:68943`
- 既有 `_cl_say_lint_block` 是前 8 條、訊息截 70 字、放行指令也只列前 8 條(`scripts/lumos:68943`)。同一道閘的同一則擋下訊息變成兩種格式,見 ③。

## ③ 第二種做法

severity: major
blocking: 是
⚠ 判不準,交編排者:計劃自己有內部一致性(放行走既有的 `lint-waive`),但同一類威脅既有兩種做法,計劃都沒引用。
引句:「這次改動把 `lint_new.gate` 改成 warn 或 off(`tq/gate-config`),這一次照 block 判」
佐證 file: `scripts/lumos:57737`
- 「同一次推送把設定放寬不算數」這件事,專案已有兩種處理:
  - 第一種:從可信版本讀宣告。`_lens_trusted_ref`(`scripts/lumos:57737`)和 `_trusted_decl_ref`(`scripts/lumos:57760`)讀起點和主線分岔點的設定,被推的分支自己改的不算。
  - 第二種:放寬要有核可。安全證據閘的 `security_evidence.gate=warn` 只有核可鏈上有有效的 `gate_setting` 才生效,否則照 block 判(`_secev_stage_chain`,`scripts/lumos:11085` 起)。
- 計劃走第三條路:把「改了設定」做成 `tq/` 候選,再用 `lint-waive` 放行。
- PRIOR-ART 和 r1 修正紀錄都沒提這兩個先例。
- 這條規則還把「閘的設定」塞進「測試作弊比對」,造成 ① 說的反向依賴。
- 建議:至少回答「為什麼不採第一種(從主線分岔點讀 `lint_new.gate`)」,或把它從比對工具移到閘本身。

severity: minor
blocking: 否
⚠ 判不準,交編排者:這是政策選擇,不是機制。
引句:「起點是空樹時,先試主線分岔點(`git merge-base <主線> <終點>`,主線用推送掛鉤既有的判法)」
佐證 file: `scripts/lumos:62474`、`scripts/lumos:48033`、`scripts/lumos:44087`
- 共用的 `_lens_push_base` 已經處理「全零起點或本機找不到時算分岔點」,並寫明「明寫空樹的起點照原意」。
- 現有三種空樹處理:
  - Room 守衛:不判,rc 0,記 `skipped`(`scripts/lumos:48033`)。
  - 筆記形狀擋:截到上線點(`_nodehome_clamp_base`,`scripts/lumos:44087`)。
  - 代碼審:整庫照比、照擋。
- 計劃是「照比、只印不擋、記 `skipped`」,又是一種。
- 「主線用推送掛鉤既有的判法」沒指名函式。`_lens_push_base`、`_push_range_start`、`_rg_fork_point` 三個都長得像,要指名。

severity: minor
blocking: 否
⚠ 判不準,交編排者:這是新語意,效果比鄰居嚴,但方向不同。
引句:「設定 off 或 `LUMOS_SKIP_LINT_NEW` 時,比對工具照樣在背後跑一次」
佐證 file: `scripts/lumos:38820`、`scripts/lumos:48031`、`scripts/lumos:44593`
- 鄰居的 off 是不執行:Room 守衛 `cfg[0] == "off"` 直接回 0、不記帳,筆記形狀擋的 off 也是不執行。
- 度量段的 `_metric_gate_off`(`scripts/lumos:4650`)也把 off 當「沒在跑」。
- 計劃讓 off 變成「仍執行、有候選才記帳」,是新的 off 語意。
- 好處是補上關閘不留痕的洞。代價是 off 的專案仍要付比對成本,而且 off 不再等於關掉。
- 建議在 `Systems/test-guard` 和 `Systems/pitfalls-lint-adapter` 明寫這個例外。

severity: minor
blocking: 否
引句:「自己用 `_lens_git` 跑 `git diff --name-status -z -M --no-ext-diff --no-textconv <起點> <終點>`」
佐證 file: `scripts/lumos:43687`、`scripts/lumos:43717`
- 既有的 `_nodehome_changes`(含刪除與改名,空樹起點可用)和 `_nodehome_name_status(raw, norm=False, codes=…)` 已經能解 `-z` 的 name-status。
- `norm=False` 就是為了拿去 `cat-file` 查 NFD 樹而設的。比對工具要拿路徑讀 blob,正好用得上。
- 計劃說「git 呼叫全部重用既有函式」,這條卻是再寫一個解析器。
- 計劃用 `_lint_new_changed_files` 刻意不收刪除當理由,這個理由站得住,但不等於要新寫解析器。

severity: minor
blocking: 否
引句:「指紋 = sha256(規則代號、檔案、身分、這是第幾個相同身分)前 16 碼」
佐證 file: `scripts/lumos:38673`
- `_lint_new_diff_claims`(`scripts/lumos:38654`)的指紋是 `sha256(k)[:16]`,不含序號;同一身分多出來的幾條共用同一個指紋。
- 計劃的指紋含序號,同一份放行檔裡會有兩種指紋規則。
- 計劃已說明原因(放行第一個不該順帶放第二個),結構上不衝突,但兩種規則要寫進 `Systems/pitfalls-lint-adapter`。

沒列為發現,但計劃要說清楚的幾處:
- `tq/too-large` 另設 5 MB / 10 萬行,不借 `max_file_lines`/`max_file_bytes`,計劃已寫明理由。
- `LUMOS_SKIP_LINT_NEW` 現況是「有設就算」(`scripts/lumos:38820`),鄰居是 `== "1"`。這是既有的不一致,不是這份計劃造成的。

## ④ 落點

- `Systems/test-guard` 新開是合理的,跟 `Systems/room-guard`(自己的節點、自己的負責範圍、`about_code` 指向 `scripts/lumos`)同一個做法。
- `Systems/test-quality-cli` 掛 0 份計劃,管標準文件和收證測試,放標準改寫和六條小修合適。`Systems/test-quality-multilang` 管 `test_quality_semgrep.py`,放 Semgrep 兩條規則合適。
- `Systems/pitfalls-lint-adapter`(管 `scripts/lumos`、沒寫負責範圍)是新增告警閘和 `lint-waive` 的家,補負責範圍和 KEY 例外合理。
- `Systems/pitfalls-code-loop`(20 行 KEY、沒寫負責範圍)計劃沒說要寫什麼進去。建議限定只放「代碼審檢查那一步怎麼接比對、小結印什麼」,避免它繼續變大。

severity: minor
blocking: 否
⚠ 判不準,交編排者:要不要為了回歸測試多掛一個家。
引句:「既有函式要擴充的三處(擴充時補 Room 守衛那邊的回歸測試)」
佐證 file: `docs/lumos-toolchain-knowledge/Systems/room-guard.md:8`
- `_rg_methods`、`_rg_method_end`、`_rg_annotations` 的家是 `Systems/room-guard`,但 `lands_in` 五篇裡沒有它。
- 依「改了程式要寫說明就寫進改到那支檔的家」,至少要在 `Systems/room-guard` 補一句「這三個函式被 test-guard 共用,改動要兩邊測試一起跑」。

不對齊共 9 條,其中 major 1 條
