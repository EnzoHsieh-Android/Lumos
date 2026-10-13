severity: major

C 節的「沿用既有機制」大致成立:規格閘會真跑 Kotlin 測試、guard kill 能跑 Gradle、k6 門檻會回非零、spec-trace 看得到綁的測試在不在。有一處宣稱不成立(finding 1),其餘是 minor。

**逐項驗證(你點名的 6 項)**

- **(1) 規格閘跑 Kotlin 測試:成立。**
  - `cmd_spec_gate` 呼叫 `_run_bound_tests`,走 `kotlin-junit` 的預設指令 `./gradlew test --tests '*{method}'`。
  - 這個 profile 沒有 `_RAN_EVIDENCE`,所以不會被判 unproven,篩不到支數時只印有沒有跑過。
  - 風險高的計劃也會跑,但「紅綠只印不擋」。
  - 留痕寫的是測試名和 `n_red`,不存每支測試的綠燈結果。
  - file: `scripts/lumos:7800`、`scripts/lumos:23287`、`scripts/lumos:47978`、`scripts/lumos:8010`
- **(2) 推送前綁定測試閘:單支逾時成立,跑的範圍與 spec 寫的不同。**
  - 單支 180 秒成立(`LUMOS_TEST_TIMEOUT` 預設 180),規格閘與推送閘共用同一支 `_run_bound_tests`。
  - 但 `_bound_tests_for_diff` 只收被波及節點上 ★INVARIANT★ 合約的 `[test:]`,不收計劃條款綁的測試。
  - 見 finding 1。file: `scripts/lumos:47909`、`scripts/lumos:48117`
- **(3) guard kill-add / kill 在 Kotlin + Gradle 專案:能跑。**
  - kill 在 HEAD 的隔離 worktree 跑,要求 baseline 綠,用 `max(600s, floor)` 當 baseline 逾時,壞法那次逾時是 `max(baseline×5, 20s)`。
  - 歸因靠測試名出現在 FAILED 行附近,Gradle 的輸出格式符合。
  - 見 finding 3。file: `scripts/lumos:17298`、`scripts/lumos:17169`
- **(4) k6 門檻沒過回非零:成立。** 這是 k6 本身的行為,不是 Lumos 的。
- **(5) spec-trace 顯示綁的測試在不在:成立。** 懸空和壞名會標 ⚠,但不影響 rc。file: `scripts/lumos:8168`
- **(6) A 節新規則與 S1/S2、`--stage`:一致。**
  - S2 逐條列了阻塞不得延後、已驗的測試名要在本篇條款、編號重複。
  - `pitfalls` 的 `md` 參數本來就吃 spec 路徑且不需要圖譜,加 `--stage` 可行;規格閘直接讀〈待決問題〉也自洽。
  - 唯一的接線問題見 finding 4。file: `scripts/lumos:51378`

severity: major
blocking: 是(宣稱的「推送前再跑」在多數情況不成立,會讓 d6 的前提落空)
引句:「規格閘真跑一次並留痕,推送前綁定測試閘再跑」
推送前綁定測試閘只跑 ★INVARIANT★ 合約的 `[test:]`(file: `scripts/lumos:47909`),不跑計劃條款綁的測試。
計劃條款測試只有「風險低」的留痕才會在推送時重跑(`_spec_gate_push_scan` 只處理 `_rec_plan_risk(rec) == "low"` 的留痕,file: `scripts/lumos:8102`)。
風險判定預設為高,除非四類各有一行合格的已排除行(file: `scripts/lumos:7124`)。示範訂單系統若寫到「扣款」「對外」這類字(`PITFALL_CLASSES`,file: `scripts/lumos:26459`)就是風險高。
結果:冪等、故障恢復、功能這幾類條款測試,在推送時沒有任何閘重跑。只有綁在 INVARIANT 上的併發測試有。
建議:C 節改成明寫「只有 INVARIANT 綁的測試進推送閘;其他條款測試靠規格閘手動重跑」,或要求把這些測試也掛到合約上。

severity: minor
blocking: 否(S5 是 `[manual:]` 條款,且寫法有分歧)
引句:「規格閘的留痕裡這些測試都跑綠」
留痕只存測試名和 `n_red`(file: `scripts/lumos:8010`),不存每支測試的綠燈判定,所以「留痕裡跑綠」無從查證。
若示範計劃判成風險低,沒標 keeps 的條款測試在規格閘當下必須是紅的,綠了反而擋下(`_spec_gate_twoway_run_verdict`,file: `scripts/lumos:7257`)。「規格閘跑綠留痕」與風險低互斥,要綠只能走風險高或標 keeps。
建議:S5 改成「規格閘輸出顯示綠」,並寫明示範計劃走哪一種門。

severity: minor
blocking: 否(⚠ 我沒實測 Gradle,只依程式碼推斷)
引句:「資料庫帳密一律走環境變數與本機設定檔(忽略),不進版控」
`guard kill` 在 HEAD 的乾淨 worktree 跑(file: `scripts/lumos:17298`)。被 gitignore 的本機設定檔不會進去,配方與測試也必須先 commit。若測試依賴那個設定檔,baseline 會非綠,整條 abort。
建議:C 節補一句,示範的 kill 測試只靠環境變數或 Testcontainers 動態帳密。

severity: minor
blocking: 否
引句:「`lumos spec-gate` 不論風險高低都應回 1 並列出那一題」
`_spec_gate_front` 對沒有 `[SN]` 條款的風險高計劃會提早回 0(file: `scripts/lumos:7552`),`--no-run` 也會提早收(file: `scripts/lumos:7800`)。
新的阻塞檢查若接在這兩個出口之後,只有〈待決問題〉而沒條款的計劃就不會被擋,與 S1 矛盾。
建議:實作時把檢查放在條款綁定之前,並補一支只有〈待決問題〉、沒有條款的測試。

總結:最嚴重 major;blocking 共 1 條
