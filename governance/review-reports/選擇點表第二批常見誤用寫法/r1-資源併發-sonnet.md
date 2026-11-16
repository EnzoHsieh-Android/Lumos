severity: major

**實務隱患鏡頭(資源與時序)逐類**
- 掃描與挑壞法時限:見 finding 2。
- choice-kill 的 Gradle 次數:見 finding 1。
- 治理帳讀取成本:無。`gov --stats` 原本就整本讀帳,125714 筆、22.6MB,實測整個指令 3.0 秒。「依列號」只是在已載入的 `rows` 上多一個 Counter 迴圈,不增加 I/O。`row` 欄位已由 `_gov_row` 投影進統計列,不缺欄位。
- ast-grep 多兩三支規則檔:無。實測見 finding 3。
- 做到一半失敗:已有 `_ChoiceUnverifiable` 與 `unverified` 的提醒放行路徑,spec 沒新增失敗面。
- 併發與不可逆:無。已依指示不考慮兩個程序同時寫。

1. **choice-kill 的批次量與「缺紀錄」擋下,在 `?.`/`?:`/`.let` 加入後沒有上界**
severity: major
   blocking: 是,功能行為在實務上變成「大多數 Kotlin 改動都被擋,而且要跑多輪 Gradle」,spec 卻把它留給兩個月後的 RETIRE-IF。
   - 對應 spec 段:〈不做〉、〈實務隱患〉「掃描量」、RETIRE-IF。
   - 引句:「不改一行一個壞法、回報上限、乾節點、殺傷力判定與推送前那一道的規則。」
   - 問題:
     - 回報上限 `_CHOICE_CAP_PER_FILE`=7 只限制「存活」(`survivors`)被抽中的行數。
     - 其他原因照擋:沒帳的行回「缺紀錄」,跑不出結果回「跑不出結果」,不唯一和過期也擋。這幾類沒有上限。
     - 每一行有 `?.`、`?:` 或 `.let` 就多一個要跑的壞法。這三種是 Kotlin 最常見的語法,第一版 13–15% 的密度會明顯上升。
     - `cmd_choice_kill` 每次最多跑 30 個壞法(`_CHOICE_MAX_MUTANTS`)、總時限 1800 秒。每個壞法是「每支守的測試」各一條 Gradle 配方。
     - 一次改 100 個含 `?.` 的行,就要跑 4 輪以上 choice-kill,每輪都先付基準 Gradle。
     - 1800 秒對 Gradle 單次 60 到 120 秒的專案,實際只跑得完 15 到 30 個壞法。
     - 〈實務隱患〉預期 `.let→.also`、`$A!!` 編不過或等價的比例不低。`no_result` 照 `_choice_kill_pick` 的說明「一律重跑」,每輪 choice-kill 都佔用 30 個名額。每一行要靠人逐行放行才能推。
   - spec 缺的東西:
     - 沒有「每次推送的壞法行數、Gradle 次數、需人處置行數」的上界或度量。
     - RETIRE-IF 只看單列的「等價/不是需求比例」和「跑不出結果比例」,看不到「每次推送要多跑幾輪」的成本。
     - 〈範圍〉5 的「依列號」只統計比例,不統計每次推送的行數。
   - 佐證:
     - `scripts/lumos:78229`(`cmd_choice_kill` 的 docstring 與 `todo[:max_mutants]`)
     - `scripts/lumos:77656`(`_CHOICE_MAX_MUTANTS`=30)
     - `scripts/lumos:77657`(`_CHOICE_MAX_SECONDS`=1800)
     - `scripts/lumos:78323`(`_CHOICE_PUSH_REASONS`)
     - `_choice_push_judge`:只有 `survivors` 走 `_choice_cap_pick`,`by["缺紀錄"]` 直接進 bad。

2. **挑壞法時限(15 秒、整次共用、整檔丟棄)在密度上升後沒有驗收門檻,超時時放行**
severity: minor
   blocking: 否,超時走既有的提醒放行路徑,不是新增缺陷;但只寫「實作時量一次」沒有通過門檻,也沒有條款綁。
   - 對應 spec 段:〈實務隱患〉「掃描量」。
   - 引句:「推送前時限照第一版(`_KT_SIT_BUDGET`、`_CHOICE_PICK_BUDGET`);實作時在兩個真實專案重量一次掃描耗時。」
   - 問題:
     - `_CHOICE_PICK_BUDGET`=15 秒是 `_choice_compute` 一次算好的 `pick_dl`,所有檔共用。
     - `_choice_file_points` 逐行檢查 deadline,超時就 raise `_ChoiceUnverifiable`,**那一整支檔**被記成「挑壞法超過時限」,整支都不判。排在字典序後面的檔全部一起掉。
     - 第一版實測(2.4/5.1/5.9 秒)是 13–15% 的密度。第二批把有選擇點的行數推高。
     - 每個有壞法的行都跑 `_choice_identity`,其中 `_count_overlapping(text, old)` 是整檔 `str.find`。新增一支大檔或批量改動時是行數乘檔案大小的平方。
     - 我模擬 20000 行、0.77MB、每行唯一,只算 find 就 3.4 秒。第一版量到的 720KB 單檔 5.9 秒是在低密度下;密度翻倍後 ⚠ 可能逼近 15 秒,我沒有真實 Kotlin 專案可量。
     - 超時結果是「只提醒、記 unverified、放行」。最大、最需要守的新增檔反而最先掉出閘。
   - spec 缺的東西:沒有「超時比例」的驗收,S1–S8 都沒有大檔或高密度的條款。
   - 佐證:
     - `scripts/lumos:77431`(`_choice_file_points` 的 deadline 檢查與 raise)
     - `scripts/lumos:77496`(`_choice_compute` 的 `pick_dl`、`pick_timeout`)
     - `scripts/lumos:78320`(`_CHOICE_PICK_BUDGET` 註解的量測值)
     - `scripts/lumos:77315`(`_choice_identity`)

3. **ast-grep 多規則的掃描增量**
   已讀,無 finding。
   - 在 `/tmp/lumos-seat-work/選擇點表第二批常見誤用寫法/資源併發-sonnet/` 造了 1600 行的單檔,以及 40 檔各 100 行。
   - 掃描設定用現有 `rules-choice` 加上草擬的 `?.`、`?:`、`LaunchedEffect`、`remember` 四條規則。
   - 單檔實測:0.93 秒對 0.93 秒,持平。
   - 40 檔批次(並行):0.137 秒對 0.138 秒,持平。
   - 輸出筆數:4800 到 6000(單檔)、9600 到 12000(多檔),約 +25%。輸出量在 4.1MB 到 4.7MB,離 `_LINT_SARIF_MAX_BYTES`(64MB)很遠。
   - 規則數量的成本可以忽略。成本主要在 Python 端的挑壞法,見 finding 2。

4. **各節核對**
   - 〈白話〉、〈範圍〉1、2、4、6:已讀,無 finding。
   - 〈範圍〉3:「`?.` 列一行只挑一個節點」與 `_choice_pick` 的一行一壞法一致。已讀,無 finding。
   - 〈範圍〉5(統計):已讀,無 finding,成本見上。
   - 〈驗收條款〉S1–S8、〈回退〉、〈天花板〉:已讀,無 finding。資源面的缺口併入 finding 1、2。
   - 內部交叉引用:`_CHOICE_PICK_BUDGET`、`_KT_SIT_BUDGET`、`_choice_pick`、`_choice_file_points`、`choice-kill`、`gov --stats` 在 `scripts/lumos` 都存在,`configs/ast-grep/kotlin-choice/` 也在。

最嚴重 severity: major;blocking 共 1 條(finding 1)。
