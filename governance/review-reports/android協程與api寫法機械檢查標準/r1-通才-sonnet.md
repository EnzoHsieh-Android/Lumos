severity: blocker

已讀完整份 spec。ast-grep 與 semgrep 本機未安裝,涉及它們輸出行為的宣稱只能讀程式碼推斷,不能實測。

**1. §5 回合結束檢查的預設預算讓整條檢查什麼都不跑**
severity: blocker
blocking: 是(預設設定下功能整個失效,會誤報「沒擋」)
引句:「預算預設 20 秒,可用 `.lumos/config.json` 的 `lint_new` 區塊新加的 `stop_budget_sec` 調」
- 既有判定函式在剩餘預算低於單條保底時,把命令記成「沒跑到」而不執行。
- 保底預設是 30 秒,所以 20 秒的預算從第一條命令起就判成預算不足。
- spec 又規定工作樹檢查對「沒跑到」的命令只列出、不擋。
- 結果:預設設定下 ast-grep 一次都不跑、永遠 rc0。S5 要靠 `--budget` 調大才測得紅,測試抓不到預設值的問題。
- spec 沒說 `stop_budget_sec` 要不要連帶蓋掉保底。
- file: `scripts/lumos:38498` 保底 `per_cmd_floor_sec` 預設 30。
- file: `scripts/lumos:39125` 迴圈裡 `left < cfg["per_cmd_floor_sec"]` 即記為 undone。
- file: `scripts/lumos:38689` 設定鍵白名單只含 `budget_sec`、`per_cmd_floor_sec`、`max_file_lines`、`max_file_bytes`,新鍵 `stop_budget_sec` 不加進這個迴圈會被靜默忽略。

**2. §5 沒說新道插在鉤子哪裡,既有提早 return 會讓它在最常見情境被跳過**
severity: major
blocking: 是(S6 沒覆蓋這些路徑)
引句:「專案有 `.lumos/lint.json`、工作樹上有未提交的程式碼檔時,跑工作樹檢查」
- 既有 `main()` 有四個提早 return:
  - 沒有圖譜根目錄(`find_graph_root` 回 None)。
  - 這一輪沒有檔案或 Bash 動作。
  - 動過圖譜(`graph_touched`)就在擋停分支之前 return 0。
  - 同一批檔第二次出現(`printed_key` 去重)就 return 0。
- 新道若接在擋停分支旁,本 repo 與任何「改 code 同時動筆記」的回合都不會跑 lint。
- 沒有 `docs/*-knowledge` 的消費專案,即使有 `.lumos/lint.json` 也不會跑。
- spec 的「兩道各自判」與這個既有流程衝突,沒定義位置。
- file: `scripts/hooks/claude/check-graph-sync.py:999` 沒有圖譜根就 return。
- file: `scripts/hooks/claude/check-graph-sync.py:1029` `if graph_touched:` 後直接 return 0。
- file: `scripts/hooks/claude/check-graph-sync.py:1054` 同批檔去重 return 0。

**3. 告警訊息被截成 120 字,「訊息裡已有標準寫法」不成立**
severity: major
blocking: 是(§2、§5 的核心賣點:錯誤訊息帶修法)
引句:「加每條規則訊息(訊息裡已有標準寫法與型錄編號)」
- SARIF 解析把每條告警的 message 截斷到 120 字元(v1、v2.1 兩路都是)。
- 型錄的標準寫法常是程式碼片段(例:`coroutineScope { val a = async { … } … }`),加上 `[編號]` 與「錯在哪」前綴後必被截斷。
- 被截斷的訊息正是要放進 decision:block 給模型看的那段。
- ast-grep 規則的 `fix`、note 等欄位完全不會進 claims。
- spec 沒要求調整這個截斷,S6 只驗「原因含規則訊息」。
- file: `scripts/lumos:38434` `message_text = (...)[:120]`。
- file: `scripts/lumos:38446` v2.1 分支同樣 `[:120]`。

**4. 共用工作目錄:別的會談的未提交改動會被算成本會談的新增告警**
severity: major
blocking: 是(`~/.claude/CLAUDE.md` 明載同一 repo 可能同時有別的會談)
引句:「基準取 HEAD、現在版讀工作樹的檔(含未追蹤但沒被忽略的檔)」
- 工作樹檢查把整個工作樹相對 HEAD 的差異都算進來。
- 並行會談 B 的 kt 改動會讓會談 A 在收工時被擋。
- A 依規矩不該碰別人的檔,擋停原因要求「先修」,等於無解;只能靠放行或 `LUMOS_STOP_LINT_OFF`。
- 既有的圖譜擋停是靠措辭「清單不保證是你這一輪改的」處理,而本案的擋停是硬性要求修告警,spec 沒處理這個差別。
- file: `scripts/hooks/claude/check-graph-sync.py:795` 擋停原因的清單已寫明「不保證每支都是你這一輪改的」。

**5. 快照暫存目錄在消費專案不會被 gitignore,會被工作樹檢查自己撿進去**
severity: major
blocking: 是
引句:「基準取 HEAD、現在版讀工作樹的檔(含未追蹤但沒被忽略的檔)」
- 新增告警閘把快照解到 `.lumos/lintbase-<隨機>/{base,head}/`,裡面是改動 kt 檔的完整副本。
- 只有本 repo 的 `.gitignore` 有 `.lumos/lintbase-*/`。
- 在 scripts/lumos 與 hooks 裡找不到任何寫入 gitignore 的程式碼,所以消費專案不會有這行。
- `.lumos/lint.json` 與 `lint-waivers.json` 要進版控,所以 `.lumos` 整個不能被忽略。
- 因此(a)並行會談在跑時留下的快照、(b)強殺後 24 小時內的殘留,都會成為「未追蹤、沒被忽略」的 kt 檔。
- 這些副本會被工作樹檢查當成新檔掃描,每個都被算成新增告警。
- 既有的圖譜擋停也會把它們列成「未提交的程式碼檔」。
- file: `scripts/lumos:38966` 清殘骸只清超過一天的。
- file: `scripts/lumos:39101` `tempfile.mkdtemp(prefix="lintbase-", dir=str(root))`。

**6. §4 的「終點是提交時一字不變」與判定函式現狀衝突,spec 沒說怎麼選工作樹終點**
severity: minor
blocking: 否(目前只有一個呼叫點,且是使用者手動帶單一參考點才會中)
引句:「判定函式多收工作樹終點,但終點是提交時走原路徑、結果一字不變」
- 既有行為:`_diff_range_ends` 對單一參考點(如 `HEAD~3`)回終點 None,判定函式遇到就回 env-unavailable 並自動放行。
- spec 若用「終點 None 即工作樹」來實作,`code-loop check --diff <單一參考點>` 會從放行變成真的掃工作樹,結果就變了。
- 若另加參數,spec 也沒寫簽名。
- file: `scripts/lumos:32069` `_diff_range_ends`。
- file: `scripts/lumos:39065` `if not base_ref or not head_ref:` 即判 env-unavailable。
- file: `scripts/lumos:67822` 唯一呼叫點。

**7. §8 手冊要「改動已提交就對 merge-base 到 HEAD 跑」,但沒有任何指令能這樣跑**
severity: major
blocking: 是(手冊步驟無法執行)
引句:「改動已提交就對 merge-base 到 HEAD 跑新增告警閘」
- §4 只定義 `lumos lint-new --worktree [--budget 秒]`,沒有範圍參數。
- §8 又排除了 `code-loop check`。
- 該 repo 的代碼審手冊要求「凍結前先把手上的改動提交」,所以走到派席那一步時,改動幾乎一定已提交、工作樹是乾淨的。
- 此時 `--worktree` 掃不到任何東西,必然回 clean。
- 結果:手冊第一步在實際情境下是空檢查,「乾淨才派審查席」形同虛設。
- file: `skills/lumos-code-loop/SKILL.md:19` 「凍結前先把手上的改動提交」。

**8. §7 `code-loop pass` 沒有範圍、沒有座標,判定函式也不能只抽兩道**
severity: major
blocking: 是
引句:「對同一版本跑新增告警與表態兩道判定(就是推送檢查裡那兩道的同一支判定函式)」
- `pass` 子命令只有 `--note`,沒有 `--diff`、`--at-sha`、`--branch`。
- 表態判定要吃 `pitfalls --diff --json` 的輸出(適用題清單),還要主線 merge-base 重算。
- 它們內嵌在 `_codeloop_guard_verdict` 裡,沒有獨立入口。
- 整個函式呼叫會在 tier=high 且尚無留痕時被「沒有留痕」那一步擋下,這正是 pass 要寫的東西。
- 所以 pass 要自己重跑 pitfalls 並複製 3.5、3.6 兩段邏輯,spec 沒說怎麼做。
- `pass` 與 `skip` 共用同一段程式,檢查要加在哪個分支也沒寫。
- file: `scripts/lumos:70779` `pass` 與 `skip` 只註冊 `--note`。
- file: `scripts/lumos:68594` `if subcmd in ("pass", "skip"):` 共用寫留痕邏輯。
- file: `scripts/lumos:68031` 新增告警步驟是 `_codeloop_guard_verdict` 的內嵌步驟。

**9. 「每列都接電」是標籤,不是接線;166 列的「告警帶寫法」在批一、批二根本沒有線**
severity: major
blocking: 是(違反使用者要求:怕寫了但完全沒參考)
引句:「(使用者 2026-11-05 要求:每列都要接,沒接電的列不收)」
- 我用程式解析型錄 473 列,數出以下結果:
  - 級別只有 A 的有 168 列,其中 166 列接電方式只有「告警帶寫法」。
  - 這 168 列的實測狀態全都不是「規則 <id>」,規則包沒有守它們。
  - A 級是現成第三方規則(detekt、Android Lint),訊息不能帶 `[編號]` 與標準寫法。
  - 這些規則要等批四才接進流程。
  - 語意類 106 列的表態、盲判、行為測試要等批三、批五。
- S3 只驗標籤字串存在,不驗接線。
- spec 天花板 §2、§3 承認了一部分,但用詞(每列都接、沒接電不收)與實況矛盾。
- file: `skills/kotlin-idioms/checks-catalog.md:832` 統計節自述「被規則包守到的列數:181」,473 列中不到四成。

**10. S3 對語意類的要求與型錄自己的規則矛盾,條款一落地就紅**
severity: minor
blocking: 否(實作時測試即能暴露,但條款應先改對)
引句:「語意類 應 含「表態對程式」與「盲判席」」
- 型錄口徑寫「只剩業務判斷的 D 級只寫表態對程式,名稱後標(人裁)」。
- 實際有 3 列(ARCH-54、DATA-62、DATA-68)只有「表態對程式」,沒有盲判席。
- 照 S3 字面,`t_kotlin_catalog_rows_wired` 會在 3 列上紅。
- file: `skills/kotlin-idioms/checks-catalog.md:477` ARCH-54 接電方式只有「表態對程式」。
- file: `skills/kotlin-idioms/checks-catalog.md:557` DATA-62 同樣。

**11. 新增告警閘只掃非測試檔,型錄 TEST 主題的規則在閘裡是死的**
severity: major
blocking: 是(spec 宣稱 TEST 主題有 18 列被規則包守到)
引句:「當對規則包每條規則的壞例樣本跑 ast-grep 時,應 每個壞例都被該條規則命中」
- 閘的檔案篩選會排除路徑中有 `test/` 或 `tests/` 目錄段的檔,Android 的 `src/test/...` 就是。
- 閘在掃描前用它過濾要掃的檔(`code_pairs`),所以規則樣本全過、實際推送時單元測試檔的告警一條也看不到。
- 例子:`kt-test-thread-sleep`(TEST-28)、runTest 相關列。
- 型錄統計顯示 TEST 主題有 18 列被規則包守到。
- S1~S9 沒有一條驗「規則命中的檔會被閘送進掃描」。
- file: `scripts/lumos:58390` `_stack_changed_ok` 排除 `_PITFALL_DIFF_TEST_PAT`。
- file: `scripts/lumos:39076` `code_pairs = [(a, b) ... if _stack_changed_ok(a)]`。
- file: `scripts/lumos:37574` 該 regex 含 `(?:^|/)tests?/`。

**12. 136 條 warning 只在樣本上驗過,卻要進不分等級的擋人閘**
severity: major
blocking: 是
引句:「做不到零誤報的降 hint;要型別、跨檔、綁名字的不寫」
- 型錄統計規則包 211 條(error 35、warning 136、hint 40)。
- 新增告警閘不分等級,warning 一律擋推送、擋停、擋 pass。
- spec 自己承認誤報率「目前只在樣本上驗過」,真機量測是 REVISIT 到 2027-03。
- S9 只在一個實驗專案複本跑一次。
- 「降 hint」的判準是作者主觀的「做不到零誤報」,沒有量測門檻。
- 同一誤報在三個入口(擋停、pass、推送)各被擋一次;放行是逐指紋的 `lint-waive`,規則改一個字就失效。
- RETIRE-IF 是三個月後才看放行紀錄。

**13. §6 改檔前推列:沒命中既有影響就不推;Codex 路徑沒有寫入內容;三列取哪三列沒定義**
severity: major
blocking: 是
引句:「改檔前影響鉤子在目標是 `.kt` 檔、而且要寫進去的內容(既有那支取 Edit/MultiEdit/Write 寫入內容的函式)含〈情境決策表〉某列的觸發字時」
- 既有鉤子在沒有任何 chunk 時直接 return 0。新 .kt 檔或沒有筆記命中的檔,影響結果為空,spec 的「在既有輸出後面加」就沒有後面可加。
- 決策表 20 列的觸發字很泛(`async`、`map`、`launch`、`Job`、`collect`、`first`、`delay`、`onClick`、`navigate`、`insert`……),幾乎每次編輯 Kotlin 都命中多列。
- 超過三列時取哪三列,spec 沒定義。`old_string` 與 `new_string` 都併進比對文字,刪掉壞寫法也會觸發推列。
- Codex 的 apply_patch 不在 Edit/MultiEdit/Write 三個工具內,取不到寫入內容,Codex 完全不推,與 Claude 行為不一致。
- spec 沒說鉤子在消費專案如何找到 `skills/kotlin-idioms/checks-catalog.md`(鉤子是獨立檔、只信任 lumos 腳本路徑)。
- S7 沒有覆蓋 Codex 路徑與零命中情境。
- file: `scripts/hooks/claude/impact-hook.py:893` `if not chunks or all(c.startswith("(多檔") ...): return 0`。
- file: `scripts/hooks/claude/impact-hook.py:417` `extract_delta_text` 只處理 Edit、MultiEdit、Write。

**14. 環境不可用的放行每輪記一筆帳,會弄髒追蹤中的治理帳並灌水統計**
severity: minor
blocking: 否
引句:「環境不可用(工具沒裝、跑不出結果)rc0 並印原因」
- 既有放行路徑一律呼叫 `_gate_failopen`,對 `docs/.governance-log.jsonl` 追加一行;該檔是追蹤檔。
- 若 `lint-new --worktree` 沿用,每個沒裝 ast-grep 的專案每回合都在工作樹新增一行帳。
- 這些帳會被 `_lint_new_autopass_count` 當成自動放行次數統計。
- 若為避免這個而不記帳,放行就看不見。spec 沒決定。
- file: `scripts/lumos:66900` `_gate_failopen` 寫 `fail-open` 事件。
- file: `scripts/lumos:39160` `_lint_new_autopass_count` 統計 `lint-new` 的 `fail-open` 事件。

**15. 每輪都跑的成本與強殺殘留,spec 只講「毫秒級」**
severity: minor
blocking: 否
引句:「ast-grep 對幾支檔是毫秒級;detekt 這類慢工具也在同一份宣告裡時,用預算截斷」
- 鉤子外層逾時是 40 秒,內層可用只有約 28 秒(`_inner_budget` 取 0.7 倍減已耗)。
- 既有的 git status、impact 點名等呼叫已佔去一部分;spec 的 20 秒預算沒扣這部分。
- 工作樹檢查每個 Stop 都重算整個未提交集合:建快照、逐檔 `git show`/複製、跑命令、清理。
- 沒有「內容雜湊相同就跳過」的快取。這一輪沒碰 kt 檔但前面還有未提交的 kt 時,一樣整套重跑。
- 鉤子被 40 秒逾時 SIGKILL 時,finally 不執行,`.lumos/lintbase-*` 留一份副本。
- 子命令以 `start_new_session` 執行,不會被一起殺,會留下孤兒程序。
- file: `scripts/merge-claude-settings.py:121` `"check-graph-sync.py": 40`。
- file: `scripts/hooks/claude/check-graph-sync.py:712` `_inner_budget`。

**16. 防無限擋:續做那輪新增的告警沒人看;每批各一個名額沒有上限**
severity: minor
blocking: 否
引句:「同一會談、同一批告警只擋一次,用它自己的會談標記檔(檔名含那批的雜湊」
- 被擋後的續做那輪,`stop_hook_active` 為真所以不擋,續做時新增的告警要到下一個使用者回合才被檢查。
- 之後「換了一批 應 再擋一次」,每批各佔一個標記檔,一個會談可以被擋任意多次。
- 標記目錄只有 7 天懶清理,沒有每會談上限。
- 這是修一條冒一條的 AI 會遇到的路徑。
- file: `scripts/hooks/claude/check-graph-sync.py:895` `if payload.get("stop_hook_active"):`。

**17. 宣告範本裡的 `<toolchain>` 在 CI 與其他機器沒有對應,CI 會靜默放行**
severity: minor
blocking: 否
引句:「ast-grep scan --config <toolchain>/configs/ast-grep/kotlin-android/sgconfig.yml --format sarif {LINT_FILES} > {LINT_SARIF_OUT}」
- `.lumos/lint.json` 進版控,但 `<toolchain>` 是每台機器不同的路徑。
- 既有 detekt 範本寫成 `$HOME/harness/lumos-toolchain/configs/...`,同樣依賴本機安裝位置。
- CI runner 沒有這份路徑與 ast-grep 時,spec §回退的說法是「報設定檔找不到 → 判環境不可用 → 自動放行」。
- 那麼 CI 這道閘在消費專案默默失效,與「CI 照樣會擋」的預期相反。
- spec 沒說 CI 怎麼取得規則包。
- file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:125` 既有 detekt 範本用 `$HOME/harness/lumos-toolchain/configs/detekt/android.yml`。

**18. 用詞與現況對不上:light 檔、「四十條」、API-1 的規則、好例數**
severity: minor
blocking: 否
引句:「light 是代碼審查迴圈的輕量檔(一到兩席、最多兩輪,見 lumos-code-loop 手冊)」
- 手冊寫 light「只派一席架構對齊」,且 light 不計輪次(「舊的不帶輪次循序單審、light、舊迴圈不記」)。沒有「最多兩輪」。批三依賴這個定義。
- file: `skills/lumos-code-loop/SKILL.md:12` 與 `skills/lumos-code-loop/SKILL.md:67`。
- 引句:「2026-11-04 初稿的四十條表(API-1~13、FLOW-1~7、STATE-1~6、CO-1~6、UI-1~3)已併入型錄,編號沿用」。括號內加總是 35 條,型錄 PLAN 列也寫「40 條」,型錄統計寫「沿用既有編號 35 列」,spec 內部互相矛盾。
- file: `skills/kotlin-idioms/checks-catalog.md:832` 統計寫 35 列。
- API-1 型錄寫「規則 kt-sequential-independent-await(hint):規則包樣本裡沒有它會命中的壞例,未實測」。這與 spec 範圍 2「每條至少兩個壞例、兩個好例」及 S1 矛盾,也與 spec「要綁變數名的那幾條用 semgrep」矛盾(API-1 的判準正是「第二句沒用到 a」,要綁名字)。
- STATE-1 的規則 kt-nonatomic-state-update 寫明「規則包沒有它專屬的好例」,同樣違反「每條至少兩個好例」。

**型錄抽樣**(九個主題各抽 2 列)
- 標準寫法與接電方式合理的:FLOW-4、STATE-3、CO-35、CO-7、ARCH-8、PERF-27。
- API-21、API-10、TEST-6 的接電含「行為測試或正向約束」,但實測狀態是「未測」或「—」,批一、批二沒有承載。
- UI-47、DATA-28、DATA-5 級別為 A,規則來源是 Android Lint 或 detekt,訊息帶不了型錄編號,是 #9 的實例。
- TEST-38 的判準是「build.gradle 缺 `animationsDisabled`」,要靠 ast-grep 判「缺少某物」且檔案是 Groovy gradle。`.lumos/lint.json` 以副檔名分派,且 ast-grep 規則包是 Kotlin 專用,這列的接電實際上不成立。
- STATE-27 的 hint 級規則標了「Android Lint 實跑命中」,可信。

**固定席節點逐條判**
- `Systems/linter精選目錄`:節點內沒有合約行。本案加的是宣告範本與規則包說明。不影響既有行為。唯一相關的引用是 #17 的範本路徑依賴,已列為 finding。
- `Systems/效能檢核目錄`:沒有合約行。本案不改它的題庫或表態判定,只引用。不影響。
- `Systems/棧別提問表態閘`:沒有合約行。本案 §7 讓 `code-loop pass` 也呼叫表態判定,但不改判定本身。對既有行為不影響,實作缺口已列在 #8。

**實務隱患逐類**
- 併發:有隱患,見 #4(多會談共用工作樹)、#5(快照目錄互相被撿進掃描)、#16。同一會談兩個鉤子同時跑:擋停名額用 O_EXCL 檔佔位是安全的,但兩道共用輸出時的退還名額邏輯 spec 沒寫。
- 效能:有隱患,見 #1、#15。
- 資源:有隱患,見 #5、#15(強殺殘留、孤兒程序、SARIF 暫存檔)。
- 回退:基本成立(新檔刪除即可)。但回退段落對「規則包不存在時判環境不可用」的說法與 #17 的 CI 靜默放行同源。
- 金流、對外送出、不可逆:spec 已排除,查證屬實,無隱患。

總結:最嚴重 blocker,blocking 共 11 條(#1、#2、#3、#4、#5、#7、#8、#9、#11、#12、#13),其餘 7 條為 minor 非阻擋(#6、#10、#14~#18)。
