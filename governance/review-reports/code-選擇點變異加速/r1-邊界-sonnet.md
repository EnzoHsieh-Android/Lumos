severity: major

審查範圍是 pkgB:`scripts/test_lumos.py` 新增的合併快篩測試,加上計劃筆記。我在 `/tmp/lumos-seat-work/code-選擇點變異加速/邊界-sonnet/repo`(HEAD 22751fcce 的複本)改壞 `scripts/lumos`,每次只改一處,跑對應的 `-k` 測試,跑完用 git checkout 還原。三處改壞都是測試照綠。

## 1. 「結果檔合計超過 64 MiB」的防線拿掉,測試照綠
severity: major
blocking: 是
引句:「單檔超過 8 MiB 或全部加起來超過 64 MiB → 沒跑乾淨(`junit()` 只限巢狀深度不限大小,`system-out` 會整份進記憶體;」
file: `scripts/lumos:28837`

- 這道防線是記憶體保護,計劃做法 3 與〈實務隱患〉都寫了合計 64 MiB。
- 測試只驗單檔 9 MiB(`t_choice_kill_merge_junit_read`),沒有任何一支驗「每檔都沒超 8 MiB、合計超過 64 MiB」。
- 真實 Gradle 一個類別一個結果檔,64 支測試分散在許多類別時,「很多個各 7 MiB 的檔」是合理輸入。
- 重現:把 `or sum(sizes) > _CHOICE_MERGE_TOTAL_MAX` 刪掉,跑 `python3.14 scripts/test_lumos.py -k choice_kill_merge_junit_read`,輸出 `18 passed, 0 failed`。
- 建議補一案:例如 10 個各 7 MiB 的結果檔,斷言判「沒跑乾淨」。同一案順便補上單檔剛好 8 MiB 的邊界。

## 2. 套完壞法、開快篩前收到訊號時「還原壞法」沒有被驗
severity: major
blocking: 是
引句:「套完壞法、開快篩之前已收到第一個訊號時 應 還原壞法、不開快篩、不記帳;」
file: `scripts/lumos:29052`

- 驗收條款 S9 把「還原壞法」寫成必要行為,是不可逆類的守衛。
- 對應測試(`t_choice_kill_merge_interrupt` 最後一段)只斷言 `not _ckm_phase(calls) and rows == []`,即沒開快篩、沒有列。
- 它沒有讀回 `Vm.kt`,也沒有看工作樹裡的檔還是不是壞法版本。
- 重現:刪掉該處的 `_kill_merge_restore(c, target, r0)`,只留 `raise _KillHalt()`,跑 `-k choice_kill_merge_interrupt`,輸出 `6 passed, 0 failed`。
- 建議補一個斷言:在 `_KillHalt` 之後、工作樹被移除之前,檢查 `git status` 乾淨或檔內容等於原文。
- 做法:攔 `_kill_merge_restore` 看是否被呼叫,或在 patched 的 `_kill_after_write` 之外再包一層讀檔。

## 3. 合併快篩的逾時上限公式完全沒被驗
severity: major
blocking: 是
引句:「合併快篩**:刪結果資料夾、跑合併指令,逾時上限 = max(合併基準耗時 × 5, 下限)。」
file: `scripts/lumos:29056`

- 計劃做法 3 與〈實務隱患〉的「已知差異」都把「5 倍合併基準」當成有行為後果的規則。
- S7 只驗合併基準的上限(`_choice_merge_base_cap`),沒有任何一條驗快篩的上限。
- 重現:把 `max(m_el * 5, c.floor)` 改成 `c.floor`,跑 `-k choice_kill_merge`,輸出 `109 passed, 0 failed`。
- 原因:假 Gradle 的 `hang` 模式固定睡 60 秒,下限設 2 或 3 秒,所以「乘數」從來不是決定因素。
- 建議補一案:合併基準耗時大於下限,讓一個耗時介於 `下限` 和 `基準 × 5` 之間的快篩要通過,而不被誤判逾時。
- 不能只靠 hang 測試:改成 ×500 或 ×0 的實作,測試都分不出來。

## 4. 邊界值沒有恰好卡線的案例
severity: minor
blocking: 否
引句:「時限夠量齊**:剩下的總時限(`--max-seconds` 從 `t0` 算起的餘額)≥ 守的測試支數 × 10 秒 × 1.5。」
file: `scripts/lumos:28912`

- S19 的測試只驗 40 秒(不合併)和 60 秒(合併),門檻是 45 秒。
- 把 `<` 改成 `<=`,或把倍數 1.5 改成 1.2,兩案都不會紅。
- 同一類:被系統收掉的條件 `rc >= 128`(`scripts/lumos:28857`),測試只用 137 和 -9,沒有 128 與 127。
- 這些都是計劃明寫的界線。因為時間有流逝,單元層級才方便驗(傳入 `_KillMerge` 的 deadline 固定)。

## 5. 假 Gradle 與真 Gradle 的落差,只造成「該紅時沒紅」,不造成誤綠
severity: minor
blocking: 否
引句:「`write('<testsuite name="x.VmTest" tests="0"/>')`」

- 假 Gradle 把所有合併的測試寫進同一份 `TEST-x.VmTest.xml`、同一個 classname。
- 真 Gradle 一個類別一個檔,且 `--tests` 沒匹配到任何測試時會 rc 1 並印 "No tests found for given includes"。假的沒有模擬這一支。
- `big` 模式的 e2e(S4 第 5 案)只寫一個 testcase,另兩支對不到而判「沒跑乾淨」,所以這案其實測不到檔案大小檢查。
- 大小檢查只有 `t_choice_kill_merge_junit_read` 的單元案守著(見第 1 條)。
- 說這是 minor,是因為我沒能構造出「測試綠、真實情境錯」的具體輸入。

## 6. 基準階段「總時限到時」沒有測試
severity: minor
blocking: 否
引句:「基準階段收到第一個中斷訊號或總時限到時 應 在下一支基準之前停、記 run」

- 條款 S7 這句有兩個觸發條件,`t_choice_kill_merge_baseline_deadline` 只測 SIGINT。
- 總時限到時靠 `c.hk.between()` 內部的判斷,測試沒有任何一條讓期限在量基準中途到。

## 極端輸入對照(不另編 finding)

- 壞法數 0/1:`n_mutants < 2` 不合併,有 `--only` 單行案例守(S19)。
- 守的測試合併道剛好 2 支:S20 第一案是 a、b 兩支,有守;單支綠只有 1 支:S20 第二案有守。
- 連續 5 次的斷路器:S8 有守 5 與 6,以及中間夾通過、編不過、有失敗的情況。
- 測試名含空白或單引號:S1 有守;含逗號:`_test_name_ok` 擋下,有守。
- `--only` 指到已放行的行:S21 有守。
- `LUMOS_SKIP_CHOICE_MERGE` 為 0、空字串、true:S13 有守。

總結:最高嚴重度 major
