severity: blocker

審查範圍:逐節讀完整份 r3 spec,並對照 `scripts/lumos` 現況。內部交叉引用(範圍編號、條款號、預期值表)核對無壞引用,下面的 finding 都在語意與程式碼現況不符。

1. 依覆蓋選出測試子集後,`_ChoiceKillRun` 的判定會把每個 `clause` 壞法記成「缺結果」。
   - 段落:範圍 2「回傳」、範圍 3「依覆蓋選測試與合併快篩」。
   - `add()` 在 `scripts/lumos:79202` 用「全部守的測試」建 `p["order"]`。
   - `finish()` 和 `on_row` 在 `scripts/lumos:79302` 附近要求 `len(rows) >= len(order)` 才當場判。
   - `_choice_kill_judge` 在 `scripts/lumos:78959`:`live` 裡只要有一支沒有列,就回 `no_result`「缺結果」。
   - spec 只說 guard-kill「照子集跑」,沒改 `order`、`finish` 或判定。
   - 重現:S1 的輸入(甲經過、乙沒經過)中,乙那支永遠沒有列。壞法會被記成 `no_result`,不是 `survived`。
   - 層級判讀的存活清單和 S1、S8 都收不到這個壞法。
severity: blocker
blocking: 是
引句:「`clause` 的行只跑經過的守的測試;`none` 的行不跑、直接記存活;`unknown` 的行跑全部守的測試。」

2. 準備物件在合併快篩關掉或合併基準不通過時不會被呼叫,spec 沒交代這幾條路。
   - 段落:範圍 2「準備物件」開頭。
   - `mctx` 只在 `merge is not None` 時建(`scripts/lumos:28479`),`_kill_merge_iter` 只在有 `merge` 時才進。
   - `--no-merge` 或 `LUMOS_SKIP_CHOICE_MERGE=1` 時整條路徑都不走。
   - `_kill_merge_ready` 回 None 時:指令形狀不支援、守的測試不足 2 支、名稱檢查沒過、時限不夠。
   - `_kill_merge_base` 回 None 時:基準量不齊、合併基準紅。
   - 這兩種情況下 `_kill_merge_iter` 都在 `scripts/lumos:29353` 直接 `yield from c.plist`。
   - 若把準備物件掛在「先量齊基準的同一個位置」(`_kill_merge_base` 內),這幾種情況都會整個跳過合批編譯、覆蓋和 `none` 判定。
   - `reach_why` 表沒有「合併關閉」這個原因,範圍 7 也只規定了 `--reach-only` 加 `--no-merge`。
   - 結果:`--no-merge` 加 `coverage:true` 的行為沒有定義。
   - 單一守的測試的平台組,理應可以做 `none` 判定與編譯檢查,卻會被「合併道不足 2 支」跳過。
severity: major
blocking: 是
引句:「guard-kill 在 `_kill_merge_iter` 先量齊基準的同一個位置呼叫它」

3. 換候選之後,`plan_of[loc]["x"]` 仍是候選 1,記到帳上的 `new_sha` 與 `row` 是無效壞法的身分。
   - 段落:範圍 2「回傳」、S17。
   - `finish()` 在 `scripts/lumos:79248` 用 `x["mutant"]["identity"]` 組事件,`x` 在 `add()` 時就定了。
   - spec 只說「換掉的配方(配方編號…含 `new` 一起算)」,沒說同步更新 `plan_of`、`rid_map` 和 `x`。
   - 實作後帳上會有:候選 1 的 `new_sha` 記成 survived 或 killed,同時有一筆 `invalid` 也指向它。
   - `_situation_rule_point_done` 用 `ident["new_sha"]` 做冪等比對,`choice-points` 卻顯示候選 2,兩邊對不上。
   - S17 只驗「交給 guard-kill 的是候選 2」,驗不到帳的身分。
severity: major
blocking: 是
引句:「準備物件 應 記一筆 invalid、換候選 2 再合批編一次、交給 guard-kill 的是候選 2」

4. 「覆蓋可信」的判準與「只分析壞法所在檔的類別」互相矛盾,`none` 幾乎出不來。
   - 段落:〈用詞〉覆蓋可信、範圍 2 的分析任務。
   - 可信 = 專案類別有紀錄數 > 0,但該數字來自只分析壞法所在檔的套件資料夾類別的那次分析。
   - 一支不碰這些類別的測試,紀錄數就是 0,被判不可信,於是所有行都是 `unknown`。
   - `none` 要求「每支守的測試都可信而且都沒經過」。因此只要有一支測試根本沒碰這個套件,就不會有 `none`。
   - S2、S12(預期 2 行 `none`)與依覆蓋省時間的效益都會落空。
   - S4 的斷路器也會因同一原因誤跳:一批不碰該套件的測試會被判成「設定沒生效」。
   - 實測的「345 對 0」是分析全部專案類別得出的,不是只分析壞法所在檔類別。
severity: major
blocking: 是
引句:「某支測試的覆蓋資料裡,至少一個專案自己的類別(平台根底下原始碼的套件)有執行紀錄。」

5. 斷路器「前 5 支」在時序上做不到。
   - 段落:範圍 2「斷路器」與「覆蓋基準跑完,一次 Gradle 呼叫…分析」。
   - 專案類別有紀錄數要等「覆蓋基準全部跑完」之後的那次分析才有。
   - 所以前 5 支覆蓋是否可信,在全部測試都已掛覆蓋跑完之後才知道,斷路器省不到任何時間。
   - 覆蓋失效時,169 支測試每支都已多花約 1.4 秒,卻沒有提早止損。
   - S4 的「前 5 支」不是前 5 支就能判的檢查。
severity: major
blocking: 是
引句:「斷路器:前 5 支(守的測試少於 5 支時就是全部)覆蓋都不可信,這次 run 關掉覆蓋、印一行原因,其餘照現在。」

6. 續跑快取存的「經過的壞法行」只對當時那批壞法有效,同一個 `at_sha` 換一批壞法會靜默誤判成 `none`。
   - 段落:範圍 2「續跑快取」。
   - 快取內容是「專案類別有紀錄數、經過的壞法行」,鍵是平台、測試名、測試檔 blob,效期是同一個 `at_sha`。
   - `_choice_kill_report`(`scripts/lumos:79361` 附近)的收尾訊息是「還有 N 個沒跑,再跑一次 lumos choice-kill」。
   - 第二次呼叫還是同一個 `at_sha`,但挑的是另一批壞法,或 `--only` 指到別行。
   - 這時快取裡沒有新行的紀錄,新行會被當成「沒經過」。判成 `none` 後不跑,直接記存活(`via: "cov"`),但實際可能被某支測試殺掉。
   - 這是最常走的重跑路徑,不只是 S6 的中斷情境。
   - 快取鍵缺「分析的行集合」,或快取只該存「基準」不存「經過的行」。
severity: major
blocking: 是
引句:「同一個 `at_sha` 再跑時直接取用,被中斷的 run 下次接著跑。」

7. `cov_sha` 在讀端與挑行時算不出來。
   - 段落:範圍 4(`cov_sha` 定義)、範圍 6「reach 有效」與「帶過去規則」。
   - `cov_sha` 由「經過或可能經過這一行的守的測試名與所在檔 blob」算,而哪些測試經過是覆蓋輸出。
   - `choice-points`、推送閘(讀 B 版帳)和 `_choice_kill_pick`(跑之前就決定要不要帶過去)都沒有覆蓋資料。
   - 帳上只有 `reach_clauses`,沒有測試名清單。
   - 「現在算出的值」所依據的測試集合無法重建,實作者只能各自猜,效果是 reach 永遠有效或永遠無效。
   - 結果:S8 的「cov_sha 不同 → 未分類」與 S21 的「cov_sha 變了 → 重跑」沒有一致實作。
   - 「這次也開覆蓋」在挑行階段也還不知道(斷路器、時間不夠都在跑起來之後才知道)。
severity: major
blocking: 是
引句:「reach 有效:最新一筆 reach 的 `cov_sha` 等於現在算出的值,而且 `reach` 不是 `unknown`。」

8. 合批編譯的「編不過」只靠錯誤的檔與行對回壞法,沒定義編不過卻讀不出檔與行的情況,也沒有先確認基準樹本身能編。
   - 段落:〈用詞〉合批編譯檢查、範圍 1(`compile_cmd` 預設)。
   - 沒有任何壞法時編譯本來就紅(依賴下載失敗、無關的測試程式編不過、Gradle 設定錯誤、逾時),輸出就沒有 `e: file:line`。
   - spec 規定這種「對不回」要整批改逐個編。但逐個編時每個壞法也會同樣失敗,而「元凶」的判準沒寫。
   - 若照字面把逐個編失敗者都記 `invalid`,每個候選都會無效,每行變成 `exhausted`,推送閘靜默放行整批改動。
   - Android 預設 `compileDebugUnitTestKotlin` 寫死 Debug 變體,但 `_choice_merge_shape` 允許任意 `test<變體>UnitTest`(含 flavor、純 JVM 的 `test`)。
   - 變體不符時,不是該任務不存在整批失敗,就是 flavor 原始碼集的壞法根本沒被編到。
   - 該行 `_KILL_COMPILE_RE`(`scripts/lumos:28191`)已有編譯錯誤判法,spec 沒說沿用。
   - 缺的是:先編一次不套壞法的基準樹;預設指令要從 `run_cmd` 的任務推變體與模組;不可歸因的失敗要判成「環境錯,不記 invalid」。
severity: major
blocking: 是
引句:「Android 預設 `./gradlew :<模組>:compileDebugUnitTestKotlin`」

9. 一個壞法造成的連鎖編譯錯誤,會被誤記到另一個合法壞法頭上。
   - 段落:〈用詞〉合批編譯檢查、天花板 7。
   - 例:壞法 A 改了回傳型別。呼叫端第 50 行的錯誤,剛好落在壞法 B 的行範圍。
   - 這時 B 被判 `invalid` 並換候選。B 的候選都用完時,該行 `exhausted` 而「比照乾節點不擋」,但那行其實有合法壞法。
   - 天花板 7 說的「對不回時本來就會逐個編」不涵蓋「對得回但對錯」。
   - 對回壞法後缺少單獨複驗(把被判 invalid 的壞法單獨編一次確認),就用候選用完來免擋,守衛會漏。
severity: major
blocking: 是
引句:「兩個壞法互相影響(一個讓另一個編得過或編不過)時,合批結果可能跟單獨編不同」

10. `invalid` 沒有綁編譯脈絡,`exhausted` 的行不會再被跑到,因此無法自我修復。
    - 段落:範圍 6「挑壞法」、〈用詞〉無效壞法、回退 2。
    - `skip` 取「這一行最近一次 run 的 invalid `new_sha`」,只靠 `(檔, 行指紋, new_sha)`,不看 `at_sha` 或周邊檔。
    - 編不編得過取決於型別脈絡,而行指紋不變。其他檔改了之後,原本無效的候選可能變有效。
    - `exhausted` 行和 `arid` 一樣「不產壞法、不跑」,所以永遠不會重驗,推送閘也不擋。
    - 「最近一次 run」沒有定義:沒有 invalid 的 run 不留標記,舊的 invalid 會一直當最新。
    - 回退 2 自己承認「刪不掉帳」。
    - 該把 `at_sha`(或編譯脈絡指紋)納入 `skip` 的有效條件,並讓 `exhausted` 行在 `at_sha` 變時重驗。
severity: major
blocking: 是
引句:「挑壞法:`_choice_pick` 多一個 `skip`(這一行最近一次 run 的 invalid `new_sha` 集合)」

11. 「14 天清檔」與 `_note_audit_work_dir` 現況不符,`choice-cov/`、`choice-layer/` 不會被清。
    - 段落:範圍 2「續跑快取」、範圍 8、回退 4。
    - `_note_audit_work_dir` 的清檔只刪最上層的 `*.md`(`scripts/lumos:56738` 的 `d.glob("*.md")`)。
    - `choice-cov/<at_sha>/` 的 `.exec` 和 `.json`、`choice-layer/*.json` 都在子資料夾,也不是 `.md`,永遠不會被清。
    - 覆蓋資料檔(每支一份)會無上限累積。
    - 子資料夾也沒有現成的符號連結守衛:`_note_audit_safe_dir` 只管單一路徑,spec 說的「符號連結拒用」要逐子層另做。
    - 回退 4 說「由 14 天清檔規則清掉」是錯的,必須新寫清檔。
severity: major
blocking: 是
引句:「(符號連結拒用、自帶 `.gitignore`、14 天清檔)」

12. 合併快篩對子集的判法與現有程式的合併道寫死不相容,spec 沒說怎麼改。
    - 段落:範圍 3「依覆蓋選測試與合併快篩」。
    - `_kill_merge_screen`(`scripts/lumos:29294`)用固定的 `mcmd` 與 `lane`,並以 `names=lane` 呼叫 `_choice_merge_classify`(`scripts/lumos:29316`)。
    - 子集合併呼叫只含部分測試,`classify` 會把其餘 lane 名字算成對不到,回 `unclean`「N 支對不到結果檔裡的名字」。
    - 這會讓子集快篩永遠不通過、全部退逐支,依覆蓋選測試的省時效益歸零。
    - `_kill_merge_in_lane` 與 `mg.survived`、`mg.kinds` 也要跟著子集重算。
    - spec 的「子集沒有自己的合併基準」只回答安全性,沒回答這些判定函式怎麼收子集。
severity: major
blocking: 是
引句:「`clause` 的行合併快篩用經過的測試組一條合併指令(照 `_choice_merge_cmd`)」

13. `reach_more` 無法由 `_gate_event_fit` 補數。
    - 段落:範圍 4 末條。
    - `_gate_event_fit`(`scripts/lumos:1884`)只從尾端丟清單並加 `reach_clauses_truncated` 旗標,不會更新 `reach_more`。
    - 照字面要由呼叫端在截完後自己重算 `reach_more`,而 spec 沒寫截完後的第二步。
severity: minor
blocking: 否
引句:「單筆事件超過 4096 位元組時照 `_gate_event_fit` 截 `reach_clauses`(`reach_more` 補數)。」

實務隱患逐類:
- 設定與環境:見 finding 2、8、10,合併關閉、編譯環境錯誤與變體不符沒有定義。
- 資源與檔案累積:見 finding 11。
- 重跑與快取正確性:見 finding 6、7、10。
- 併發、金流、對外送出、不可逆:無。這個工具是單人單機依序操作,覆蓋只在本機跑,治理帳只追加,spec 的「已排除」成立。

節點判讀(固定席):
- `Systems/guard-kill`:會影響 `cmd_guard_kill` 新增的 `prep` 參數。在 finding 2 的路徑下(合併關閉)「沒交時行為不變」成立,但「有交時」的位置與路徑未定。兩條 INVARIANT 的 rc 優先序與 JSON 純度本身不受影響,因為 spec 說不改殺傷力判定與回報上限;但 finding 1 若不修,依覆蓋選子集會讓 `no_result` 數量上升。
- `Systems/規格閘`:會影響推送閘的子原因拆分。擋不擋、回報上限與放行鍵未變,「子原因行數加總等於原本存活行數」成立,但 finding 10 的 `exhausted` 會讓一批行在推送閘靜默不擋。

總結:最高等級是 blocker,blocking 共 12 條
