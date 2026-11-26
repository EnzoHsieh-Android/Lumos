severity: blocker

我讀了 spec,並對照 `scripts/lumos` 查證。9 條 finding,其中 3 條 blocker、4 條 major、2 條 minor。

severity: blocker
blocking: 是
- 位置:〈做法〉3 第③層,「每個類別一段 `--tests '<類別完整名>'`」,接〈做法〉4 的 `_choice_merge_classify`。
- 問題:第③層送進分類器的名字是類別名,不是方法名。分類器要求每個名字在結果檔的完整名裡恰好對到 1 次。結果檔的完整名是「類別.方法」,類別名既不等於它,也不是以「. 加類別名」結尾,所以每個類別都對不到。
- 後果:輸入是「PR 沒改測試檔、改到正式碼」,也就是 S1 第二案。基準在乾淨樹上就會被判成「N 支對不到結果檔裡的名字」,結果是沒跑乾淨,不是通過。第③層因此永遠判不了。巢狀類別的 `$` 被換成 `.`、參數化測試的名字被截掉參數尾巴,這兩處也會讓名字對不上。
- 佐證:`_choice_merge_hits` 是「等於 m 或以 `.`+m 結尾」。`_choice_merge_classify` 的 `miss` 檢查會回 `unclean` 與「對不到結果檔裡的名字」。
- 引句:「改到的正式碼所在模組的全部測試類別(每個類別一段 `--tests '<類別完整名>'`)」
- file: `scripts/lumos:28904`(`_choice_merge_hits`)
- file: `scripts/lumos:28943`(`_choice_merge_classify`)

severity: blocker
blocking: 是
- 位置:〈做法〉4,「既有 `_kill_merge_apply` 套 → `_kill_run` 跑 → `_choice_merge_classify` 判 → `_kill_merge_restore` 還原」,對照 D6「不量單支基準」與 D7。
- 問題:`_kill_merge_apply` 與 `_kill_merge_restore` 的第一個參數 `c` 是 `cmd_guard_kill` 的內部狀態,spec 說不呼叫 `cmd_guard_kill`,`_review_judge` 就得自己造一個 `c`。`_kill_merge_apply` 讀 `c.baselines[...][4]`(每支單支基準的「不確定」旗標)、`c.mstate`、`c.override`、`c.wt_real`。spec 說不量單支基準,`c.baselines` 就是空的,第一個壞法就會 KeyError。
- 另一處:`_kill_merge_restore` 失敗時會寫 `c.results`。
- 後果:D7 說這幾支函式可以直接重用,但這個宣稱不成立。實作者得自己決定怎麼偽造 `c`。
- 佐證:`lane_unsure = any(c.baselines[...][4] for m in lane)`,位於 `_kill_merge_apply`。
- file: `scripts/lumos:29202`

severity: blocker
blocking: 是
- 位置:〈做法〉4,掃描用既有 `_choice_changed`,以及〈白話〉、D5 的「Kotlin、Java」。
- 問題:`_choice_changed` 經 `_kt_sit_hunks` 只收 `*.kt`。Java 正式碼被改的 PR 完全不產生選擇點,掃描結果是空的。
- 內部矛盾:D5 與〈用詞〉的測試類別規則寫了 Java 的 `@Test … void`,卻沒有寫正式碼是 Java 時的處理。報告也沒有寫「這個 PR 的 .java 沒掃」。
- 後果:輸入是 Java 為主的 PR,或 Java 與 Kotlin 混合的 PR。使用者看到「0 個存活點」,會當成「測試守得住」,但其實是沒掃。
- 佐證:`diff_range, "--", "*.kt"`,位於 `_kt_sit_hunks`。
- file: `scripts/lumos:41269`
- 另外,`_choice_is_test` 是依 at_sha 那棵樹的版面判測試檔。`_choice_changed` 目前的簽章已含 `at_sha`,spec 說要「加 `repo`、`at_sha` 參數」,但 `repo_root`、`at_sha` 早就是參數,spec 描述的改動與現況不符。
- file: `scripts/lumos:77926`

severity: major
blocking: 是
- 位置:〈做法〉1,`merge-base(基底, 頭)..頭` 與 `git fetch <remote> pull/<編號>/head`。
- 問題:spec 只 fetch 頭,沒 fetch 基底。`baseRefOid` 在 PR 已合併時是合併後的主線尖端,在使用者 repo 可能不存在。merge-base 算不出來,範圍就不存在。
- 其他輸入:PR 已關閉或已合併、頭提交被強推換掉(取 `headRefOid` 與 fetch 到的 `pull/N/head` 可能不同)、使用者本機有多個 remote。
- 缺的處理:spec 沒說已合併或已關閉的 PR 怎麼辦(審還是拒)、`headRefOid` 與 fetch 結果不一致怎麼辦。
- 後果:這幾種輸入下行為未定義,可能 diff 範圍錯誤或直接崩潰,而 spec 只寫「拿不到就停、印原因」。
- 補充:「remote 取 URL 指向這個 GitHub repo 的那個」沒定義怎麼從 PR 的 `url` 與 remote URL 對比(ssh、https、`.git` 後綴、大小寫),也沒定義 0 個或多個符合時怎麼辦。

severity: major
blocking: 是
- 位置:〈做法〉3 第②層,「PR 改到或新增的測試檔裡的測試方法」,以及〈用詞〉模組定義(`<模組目錄>/src/main/...`)。
- 問題一:第②層取的是「測試檔裡所有測試方法」,不是「PR 改到的方法」。大型測試檔被碰一行,整檔測試全進來。
- 問題二:模組定義只認 `src/main`。常見的 KMP 專案是 `src/commonMain`、`jvmMain`,測試在 `commonTest`、`jvmTest`。這些輸入的正式碼不在 `src/main`,第③層找不到模組,報告也沒說明降級行為。
- 問題三:一個 PR 跨多個模組,但 `--run-cmd` 只有一個 `:module:test` 任務。其他模組的壞法會在錯的模組的測試上跑,全部判存活,是假陽性。
- file: `scripts/lumos:77715`(`_gradle_module_parts` 只是從任務名取模組路徑,不是從正式碼路徑推模組)
- 補充:spec 把「`_gradle_module_parts` 判法」說成能從 `src/main` 路徑推模組目錄。實際上該函式是解析 Gradle 任務名,對應的是 `_gradle_module_candidate`,兩者不同。這是與程式現況不符的宣稱。

severity: major
blocking: 是
- 位置:〈做法〉2、`--run-cmd`、D5,配合〈做法〉3 的合併指令組裝。
- 問題:`--run-cmd` 帶奇怪字元(空白、引號、`&;|<>`、`$()`)時,`_choice_merge_shape` 只擋含 `{method}` 那一段的元字元,其餘部分原樣進 `sh -c`。
- 後果:`_kill_run` 以 `shell=True` 執行。`--run-cmd` 是使用者自己給的,風險有限。但 `.lumos/config.json` 的 `run_cmd` 來自對方 PR 頭提交,fork PR 帶 `--trust` 時或同 repo PR 時,PR 作者可控制整條指令,等於任意程式碼執行。
- 補充:〈實務隱患〉只講了測試程式碼,沒講設定檔裡的指令也是不可信輸入。D2 把 `isCrossRepository == false` 視為可信,帳號被盜或惡意的同 repo 分支 PR 只靠這一道。
- file: `scripts/lumos:28783`

severity: major
blocking: 是
- 位置:〈做法〉4,「`--max-seconds`(預設 1800)夾住;時限到了停在壞法之間」,以及〈做法〉6。
- 問題一:剩下時限為 0,或基準本身就用掉全部時限時,`_choice_merge_screen_cap` 回 `max(remaining, 1.0)`,也就是 1 秒。基準之後的第一個壞法會在 1 秒內逾時,被判成「跑不出結果」。spec 沒說這種情況要不要停,也沒說報告怎麼寫。
- 問題二:Ctrl-C。`_kill_run` 會 re-raise `KeyboardInterrupt`。spec 只說「收尾整個刪」,沒說已跑出的結果要不要輸出部分報告,也沒說套了壞法還沒還原的審查樹是否由 `_isolated_worktree` 的 `finally` 刪掉(可以刪)。
- 問題三:`--out` 不可寫或目錄不存在時,報告寫不出來,但測試與壞法已經跑完。spec 沒定義先檢查,也沒定義失敗時是否改印到 stdout。

severity: minor
blocking: 否
- 位置:〈做法〉6、`--comment`,以及 D4。
- 問題:PR 描述空白或超長時,回指第二層與報告的處理沒寫。描述超長會讓 `--body-file` 貼的整份報告超過 GitHub 留言的 65536 字元上限,`gh pr comment` 會失敗,spec 沒寫截斷或分則。S5 只驗「只貼一則」。
- 補充:`closingIssuesReferences` 回的是連結 issue 的編號與標題,不一定含內文,〈做法〉5 第②層說「連結 issue 的內文」,需要再多一次 API 呼叫,spec 沒列。

severity: minor
blocking: 否
- 位置:〈驗收條款〉S6 與〈實務隱患〉「`.git` 會變」。
- 問題:S6 說「審查樹已刪」,但 `_isolated_worktree` 在 `worktree remove` 失敗時(例如測試程序仍開著檔案)只是靜默失敗,再 `shutil.rmtree`。測試不會抓到殘留的 `.git/worktrees` 登記。
- 另一處:spec 在〈做法〉1 說不寫、不讀帳,但 `_isolated_worktree` 在使用者 repo 建工作樹,與記憶中「從乾淨 worktree 做事、不碰別人未追蹤檔」的使用方式無衝突,但使用者 repo 有進行中的 rebase 或 bisect 時 `worktree add` 的行為沒定義。
- file: `scripts/lumos:28095`

最高 blocker,blocking 7 條
