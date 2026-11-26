severity: blocker

我讀完整份 spec,並對照 `scripts/lumos` 的函式逐項核對。審查期間沒有改動任何檔案。

severity: blocker
blocking: 是
- 位置:做法 3 第③層(每個類別一段 `--tests '<類別完整名>'`)加上做法 4「`_choice_merge_classify` 判」。
- 問題:第三層送進 `_choice_merge_classify` 的 `names` 是類別名。classify 判通過前要求每個 name 在結果檔裡恰好對到一個「測試方法完整名」。類別名永遠對不到方法完整名,所以所有壞法都被判成 unclean(「N 支對不到結果檔裡的名字」),不會判通過。
- 具體輸入:PR 沒改測試檔(第三層,S1 第二半),某個壞法其實沒被任何測試抓到。
- 結果:有失敗的壞法會判成 fail(被抓到)。真正存活的壞法被判成 unclean,歸到「跑不出結果」,不進存活清單。報告的存活點數變成 0,整條第三層退化成「永遠看不到存活」。
- 佐證:
  - file: `scripts/lumos:28943`,`miss = [m for m in names if _choice_merge_hits(fulls, m) != 1]`,`miss` 非空就回 `"unclean"`。
  - file: `scripts/lumos:28915`,`_choice_merge_hits` 只認「等於 m,或以 `. 加 m` 結尾」。
  - spec 的 S3 與預期值表只測「全過就存活」,沒有測類別粒度。

severity: major
blocking: 是
- 位置:做法 3 第②層(測試方法)加上做法 4。
- 問題:classify 要求每個方法名恰好對到 1 個完整名,第二層會有兩種判錯。
  - 參數化或重複測試(`@ParameterizedTest`、`@RepeatedTest`,`KOTLIN_TEST_RE` 會收):`_choice_merge_fullname` 把參數尾巴去掉後,同名的案例會對到多個。命中數不是 1,整批壞法都判成 unclean,存活漏報。
  - 兩個測試類別有同名方法(例如各有 `shouldReturnEmpty`):`--tests name` 會同時選到兩支,同樣命中數 ≠ 1,存活被吞掉。
- spec 沒有交代:
  - 沒有呼叫 `_name_collision_reason` 或任何撞名判斷。
  - 沒有規定第二層要用「類別.方法」限定名。
  - 沒有規定撞名時怎麼辦。
- 佐證:
  - file: `scripts/lumos:28943`
  - file: `scripts/lumos:28895`(`_choice_merge_fullname` 去掉 `[`、`(` 之後的尾巴)
  - file: `scripts/lumos:74595`(`_name_collision_reason` 在既有路徑上用)

severity: blocker
blocking: 是
- 位置:D7、做法 4 「重用合併快篩的套壞法、組合併指令、跑、判讀、還原那幾支函式;不經 `cmd_guard_kill` 與 `_ChoiceKillRun`」。
- 問題:`_kill_merge_apply` 與 `_kill_merge_restore` 的第一個參數 `c` 是 `cmd_guard_kill` 內部建的現場物件。spec 沒有定義要自己造哪些欄位。
- 用到的欄位:`c.wt`、`c.wt_real`、`c.mstate`(`unsure`、`r`)、`c.override`、`c.results`、`c.plat`、`c.baselines`、`c.run_cmd`。`_kill_merge_screen` 另外用到 `c.hk`、`c.merge_failed`、`c.merge_back`、`c.sh`、`c.floor`、`mg`。
- 與 D6 直接矛盾:`_kill_merge_apply` 裡 `lane_unsure = any(c.baselines[_run_cmd_expand(...)][4] for m in lane)`,會對 lane 每支測試取單支基準。D6 與做法 4 明說「不量單支基準」。
- 具體輸入:任何有選擇點的 PR。
- 結果:直接 `KeyError`。若為了不炸而塞假的 `baselines`,`[4]`(基準的時間戳不確定旗標)就是假值,時間戳保護失效,可能吃到舊編譯快取而誤判存活。
- 同類問題:`_kill_merge_emit` 也讀 `c.baselines[...]`,spec 沒提它是否被重用。
- 佐證:
  - file: `scripts/lumos:29202`(`lane_unsure` 那行)
  - file: `scripts/lumos:29270`(`_kill_merge_emit` 讀 baselines)
- 另外,`sh["rdir"]`、`sh["tq"]` 不是 `_choice_merge_shape` 的回傳值(那支回 `s/e/seg/eq/parts/task/pdir`)。spec 沒寫誰來算結果資料夾(`_choice_merge_results_dir`)與 `tq`。

severity: major
blocking: 是
- 位置:D5「Kotlin、Java;JUnit 的 `@Test`」,以及做法 4 的「掃描:既有 `_choice_changed`、`_choice_compute` 加 `repo`、`at_sha` 參數」。
- 問題:與程式現況不符,有兩處。
  1. `_choice_changed` 底層的 `_kt_sit_hunks` 只 diff `*.kt`(`_ns_diff(..., "--", "*.kt")`),Java 正式碼完全不掃。純 Java 的 PR 會得到零個選擇點,卻被報告成「沒有存活點」,看起來像全被守住。spec 的 Java 支援只加在 `KOTLIN_TEST_RE` 的測試名端,選擇點端沒有。
  2. `_choice_changed` 與 `_choice_compute` 早就有 `repo_root`、`at_sha` 參數,而且 `cmd_choice_points` 已有 `repo=` 參數。spec 寫「加參數」「掃描兩支函式新加的參數預設值」(落點、回退節)是在改已存在的簽章。落點宣稱與現況對不上。
- 佐證:
  - file: `scripts/lumos:41269`
  - file: `scripts/lumos:77926`
  - file: `scripts/lumos:78563`
  - file: `scripts/lumos:78655`
- 另外,spec 說要「加一條同形的 Java 規則」,但 `JAVA_TEST_RE` 已存在:file: `scripts/lumos:6081`。

severity: major
blocking: 是
- 位置:做法 4 第一步「基準不是通過 → 把失敗的測試拿掉再跑一次」,以及報告(做法 6)。
- 問題:
  - 被拿掉的測試,對應守的壞法就沒人守,會被報成存活。報告開頭的欄位清單(做法 6)沒有「基準拿掉了哪些測試」。讀者看不出這個存活點其實是「抓它的那支測試被拿掉了」,這是漏報。
  - 第三層是整個類別一段,結果檔只能挑出失敗的方法,拿不掉單一方法(`--tests` 只能排除類別,或要另外做 `-PexcludeTests` 之類)。spec 沒說怎麼做:是整個類別拿掉,還是拿掉單一方法。
  - 只跑一次基準,flaky 測試在壞法跑時隨機失敗,會被判成「被抓到」。判斷方向是把存活判成被抓到,與立場相符。spec 完全沒提重跑或穩定性檢查。
- 佐證:spec 〈實務隱患〉「基準不過」只講「拿掉失敗那支重跑一次」,沒有報告欄位。

severity: major
blocking: 是
- 位置:做法 2 與做法 3(`run_cmd` 只有一個 Gradle 單元測試任務),以及第三層「改到的正式碼所在模組」。
- 問題:`_choice_merge_shape` 只收恰好一個 Gradle 單元測試任務(帶模組路徑,例如 `:app:testDebugUnitTest`)。PR 若改到別的模組(例如 `:core`)的正式碼,第三層組出的是 `:core` 的測試類別,但 run_cmd 的任務固定是 `:app:...`。
- 具體輸入:Android 多模組專案,壞法在 `:core`,測試也在 `:core`,config 的 `run_cmd` 指向 `:app`。
- 結果:
  - 任務找不到這些測試,沒有結果檔,判 unclean 或 compile(不會誤判存活)。
  - 真正的風險是 PR 也改了 `:app` 的測試時,被選中的測試只有 `:app` 那幾支。`:core` 的壞法對它們幾乎一定存活。這是假存活,而且報告不會說「測試其實不在對的模組」。
- spec 沒有定義「怎麼為不同模組換任務」,也沒說拿不到的模組要怎麼報告。第三層的「所在模組」只算類別,沒有換 `run_cmd` 任務這一步。
- 佐證:file: `scripts/lumos:28783`,`_choice_merge_shape` 只回單一 `task` 與 `pdir`。

severity: major
blocking: 是
- 位置:做法 5 第①②層(回指階梯)。
- 問題:
  - 第①層「行內反引號路徑或節點 `about_code` 含存活點所在檔」→「回指那一行」。一個大檔的家(例如某個 ViewModel 的 Systems 節點)通常有多條 ★INVARIANT★ 與 `RULE:`,about_code 一含該檔,全部都符合。spec 沒說取哪一行、取全部還是取最近的。具體輸入:存活點在 `FooViewModel.kt` 第 42 行的 `>=`,節點 `about_code` 含該檔,有一條合約講的是別的函式的重試次數。這會回指到不相干的合約。
  - 第②層「存活點所在檔名或所在函式名字面出現」:函式名常是一般單字(`get`、`run`、`update`、`parse`、`add`),檔名如 `Utils.kt`、`Util`、`Result.kt`,一定會在 PR 描述裡字面出現。回指到不相干的那一句。spec 雖寫「語意待人判」,但回指層與原文照樣放進報告,會誤導作者。
  - `RULE:` 沒有檢查「有效」條件(`[since:]` `[retire:]` `[confirmed:]` 近半年、非 superseded)。已作廢或過期的規則也會被回指,與專案 CLAUDE.md 對 RULE 效力的規定不一致。
  - 圖譜來自 PR 頭(審查樹),作者可以改。spec 沒提這點(單人信賴模型下可接受,不另標)。

severity: minor
blocking: 否
- 位置:做法 3 末句「超過既有長度上限 → 照類別名排序截到上限內」。
- 問題:字母序截斷會很容易把「正好測被改的正式碼」的類別截掉(例如 `FooTest` 對 `Foo.kt`,排在字母序後面)。結果是被改的類別沒被涵蓋,存活點變多,全是假存活。
- 報告雖然列出沒涵蓋的類別,但存活點本身沒標「所在模組有未涵蓋類別」。建議改成:先放名稱與被改檔對應的類別。
- 佐證:file: `scripts/lumos:28800`,`_choice_merge_too_long` 的本來設計是「不分批」。

severity: minor
blocking: 否
- 位置:做法 4 判定步驟,對照既有函式。
- 問題:spec 沒提 `_choice_merge_clear(rdir)`(每次跑之前刪結果資料夾)。不清的話,上一個壞法或基準的 `TEST-*.xml` 會留著,讀到過期結果。classify 靠 `rc != 0` 擋住了大部分情形,但壞法讓 Gradle 判 up-to-date 時(例如壞法被編譯快取吃掉),舊的通過結果檔配 rc 0 會判成存活。這是既有程式已處理的邊界,新執行器很容易漏掉。
- 佐證:file: `scripts/lumos:29080`,以及 `_kill_merge_screen` 在 `scripts/lumos:29308` 呼叫它。

severity: minor
blocking: 否
- 位置:做法 1 `git fetch <remote> pull/<編號>/head`,以及用詞「範圍是 `merge-base(基底, 頭)..頭`」。
- 問題:只 fetch 了頭提交。`baseRefOid` 若不在本機物件庫(PR 基底分支已移動、本機沒拉過),`merge-base` 會失敗。spec 沒寫要一併 fetch 基底提交,也沒寫失敗時怎麼處理。
- ⚠ 這是環境相關,我沒有實測。

最高 blocker,blocking 8 條
