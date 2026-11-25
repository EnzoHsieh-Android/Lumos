severity: clean

這輪修補我沒找到可利用的洞。逐類看過的結果如下。

**①提示注入:已看,無**
- 新增的 `mg.plats` 原因、`merge_off`、`merge_unclean` 的鍵,來源只有兩種。一種是程式裡寫死的字串,例如「指令形狀不支援」「時限不夠」「基準量不齊」。另一種是 `_choice_merge_classify` 回的原因碼,而這些碼出自 `test_quality.JUnitRejected` 的固定代碼(`report_unparseable`、`report_too_deep` 等)、「結果檔讀不出來」,或只含數字的「N 支對不到結果檔裡的名字」。
- 結果檔的內容和測試名都沒有進到這些原因字串。惡意 JUnit 最多讓它落到某個固定代碼,拿不到自由文字的落點。
- `_kill_merge_breaker` 和 `_kill_merge_base` 印的 `why` 沒跳脫,但來源是上述固定集合,沒有攻擊路徑。
- 平台名全部經 `_kill_esc` 才印出。平台名當鍵寫進治理帳(JSON 序列化),不會被當成指令。
- 時限提示的 `--max-seconds X` 是用 `math.ceil` 算出的整數,不含外來字串。

**②讀寫與執行越界:已看,無**
- 這輪沒有新增檔案寫入或 shell 插值。`_choice_merge_clear` 的 `rmtree` 的目標 `rdir` 仍由 `_choice_merge_results_dir` 限制在工作樹內,這輪沒改。
- 沒看到新增的下載網址、環境變數覆蓋點或密鑰。patch 裡的網址只出現在筆記與計劃的引用文字。
- `LUMOS_SKIP_CHOICE_MERGE` 是既有旗標,只會把合併關掉、回到逐支跑,不會讓該擋的被放行。

**③非刻意的一步繞過:已看,無**
- 新欄位 `merge_kind`、`single_runs`、`merge_unclean`、`merge_off`、`ran_solo` 只用於統計和印字。`ran_solo` 不進殺傷力帳本(`_kill_log_rows` 沒寫它),`_ran_solo` 也從 `--json` 輸出剔除。判定仍只看 `_choice_kill_judge` 的 rows 和 verdict。
- 「先紅順序」(`_kill_merge_failed_first`)只改逐支的跑法順序。名單來自結果檔,比對寬鬆(完整名等於 m 或以 `.m` 結尾)。結果檔被污染最多讓某支測試先跑,每一支仍要真的逐支跑過才記 killed。survived 只有兩條路:快篩 pass(要求每支名字恰好對上一次、`rc==0`),或每支逐支都 survived。這兩條都沒被放寬。
- 一個壞法也合併:`n_mutants` 那道門拿掉後,survived 判定仍走同一套 pass 條件,沒有新的放行路徑。
- 時限門挪到最後:各個 `_kill_merge_off` 分支回 None,都退回逐支。這是保守方向,不會把該擋的放行。
- 中斷(`_KillHalt`)會記 `merge_off` 為「中斷」再往外丟。這只是記帳,不影響判定,而且中斷時未判完的壞法本來就不記帳。
- 沒有發現 shell 殘留環境變數、`PYTHONPATH`、新分支首推之類的新入口。

**範圍外附註:無**

涵蓋範圍:`r2-snapshot.patch` 的 `scripts/lumos` 與 `scripts/test_lumos.py` 的改動全段,以及筆記、手冊(含 `guard-kill.md`、`規格閘.md`、第二段計劃、`06-代碼審與推送.md`)。另外對照過 repo 內 `/Users/enzo/harness/lumos-choice-speed2/scripts/lumos` 的 `_secev_junit_facts`、`_CHOICE_MERGE_BASE_WHY`、`_kill_log_rows`、`_KillHooks`,以及 `scripts/test_quality.py` 的 `JUnitRejected` 代碼。`r2-repair.patch` 的內容已包含在上面的 snapshot 範圍裡。
