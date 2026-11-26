severity: major

審查範圍:`scripts/lumos` 的 choice-kill 覆蓋段落,加上兩篇圖譜筆記的 hunk。測試部分我只重跑了 `t_choice_cov_carry`(4 條全過)。其餘覆蓋測試我讀過程式碼,沒有重跑。我另外用 Python 對 `scripts/lumos` 的函式直接重現,結果見下面各條。exec 二進位讀者我對照 JaCoCo 的 `ExecutionDataWriter` 與 `CompactDataOutput`,另外自己造了檔案驗證。多頭 header、session 區塊、跨位元組的 varint、截斷檔、空檔這幾種都讀對。`_choice_cov_exception` 的幾種壞法形狀判得符合規格。

severity: major
blocking: 是
`scripts/lumos:79465`(`_choice_cov_robo`),後續在 `_CovBase.take`/`breaker`(約 79780–79810)。
引句:「out[n] = any("RobolectricTestRunner" in x for x in hit)」
失敗場景:Robolectric 的辨識只看「含該測試名的檔案裡有沒有字串 `RobolectricTestRunner`」。以下三種 Robolectric 測試都會被當成一般 JUnit:
- 用 `@RunWith(AndroidJUnit4::class)` 加 `@Config` 的(官方建議寫法)。
- 繼承自帶 Robolectric runner 的基底類別的。
- 方法名只出現在子類檔、runner 宣告在基底檔的。

走法:覆蓋設定沒生效時(規格自己舉的坑,`afterEvaluate` 寫法),這些測試的專案類別有紀錄數是 0。
1. `take()` 因為 `robo` 為 False,把 0 當可信,`why` 為空。
2. `breaker` 只累計 `robo` 為 True 的測試。`n_robo` 為 0 時 `need <= 0`,不會斷路。
3. `settle` 把它們全放進 `cand`,分析結果 `hits` 全空。
4. `_lines` 判成 `none`,`reach_done` 把每一行記成 `survived`、`via cov`,一支壞法都沒跑。

結果是整批行被錯記存活,擋住推送。這正是筆記寫的「不擋就會把全部行當成沒有條款經過」。
最小重現:`/tmp/lumos-seat-work/code-選擇點存活回指條款第一段/正確性-sonnet/exp1.py`。在 git repo 放一個帶 `@RunWith(AndroidJUnit4::class)` 的 `AT.foo_works`,和一個繼承 `BaseRoboTest` 的 `BT.bar_works`,呼叫 `_choice_cov_robo(t, [...])`。輸出 `{'AT.foo_works': False, 'BT.bar_works': False, 'RT.baz_works': True, ...}`。前兩支都是 Robolectric,卻被判成非 Robolectric。
這條要在覆蓋設定沒生效時才會咬人,但斷路器的目的就是防那種情況。目前的測試只用 `RobolectricTestRunner` 當 robo,沒有蓋到 AndroidJUnit4 或基底類別。

severity: major
blocking: 是
`scripts/lumos:79177`(`_choice_kill_pick` 新增的 `via == "cov"` 分支)。
引句:「if cov_sha_of is not None and evs[-1].get("cov_sha") == cov_sha_of(x):」
失敗場景:舊判法有一條防線,守的測試雜湊帶 `_CHOICE_TESTS_UNKNOWN`(測試所在檔找不到或查不完)就一律重跑,stderr 也這樣承諾(「上次存活的行這次一律重跑」)。`via cov` 的分支沒有這條防線。
走法:
1. `tsha` 含 `?`(unknown),或 `oids.get(檔)` 取不到。
2. `_choice_cov_sha(tsha, blob, new_sha)` 兩次呼叫都把同樣的 `?` 字串餵進雜湊,結果每次相同。
3. 守的測試內容無論有沒有被改,`cov_sha` 都相等,上次的 `via cov` 存活被帶過去不重跑。補了測試也不會重跑。

最小重現:`exp3.py`,同目錄。
- `via cov` 加 unknown 的 `tests_sha`,`_choice_kill_pick(..., cov_sha_of=lambda y: cs)[1]` 得到 `{('a.kt','ffff…'): 'survived'}`,被帶過去。
- 同樣的 unknown,把事件改成 `via run`,得到 `{}`,會重跑。

`t_choice_cov_carry` 沒有 unknown 的案例,所以測試抓不到。`choice-points` 的 `_choice_reach_valid` 也有同樣問題:雜湊相同就印「未判讀」。

severity: minor
blocking: 否
`scripts/lumos:79630`(`_measure`)與分析 init script(`_CHOICE_COV_ANALYZE`)。
引句:「_kill_measure_singles(c, todo, cb.cmd_of(todo), self.remaining, wrap=cb.wrap, after=cb.after)」
失敗場景:`lumosCovAnalyze` 任務沒有 `dependsOn` 編譯。隔離樹是全新 `git worktree`,沒有 `build/`。同一個 at_sha 第二次跑時,若全部測試的覆蓋資料都從續跑快取取得,`todo` 為空,樹上就沒有編譯過的類別。
- 分析找不到類別檔,每一行都 `total == 0`,全進 `nolines`。
- 每行被記成 `unknown`、原因「這一行沒有指令紀錄」。這個原因不在 `_CHOICE_REACH_TEMP`,所以 `--reach-only` 也不會重補。
- 例子:超過 `--max-mutants` 30 行的第二批,覆蓋加速全失效,而且 reach 紀錄被固定成永久 unknown。

未能重現,因為需要真的 Gradle,假 Gradle 不模擬編譯,所以 severity 自降一級。可考慮有快取時先編一次,或把「類別目錄不存在」列為暫時性原因。

severity: minor
blocking: 否
`scripts/lumos:79679`(`_analyze`)。
引句:「hits[n] = {back[i] for i in v if type(i) is int and i in back} if isinstance(v, list) else set()」
失敗場景:分析輸出 JSON 是 `{"hits": {}, ...}` 且 rc 為 0 時,每支測試的 `v` 都是 None。這裡一律當成「沒經過任何行」,每行判成 `none`,被錯記存活。缺鍵應該跟型別不對一樣視為分析失敗。目前沒有檢查 `hits` 是否涵蓋每個 `cand` 的序號。

### 圖譜固定席逐條判定

- `Systems/guard-kill.md`(★INVARIANT★ rc 優先序、`--json` 純淨):不影響。`cmd_guard_kill` 的 rc 計算與 JSON 輸出段落沒動,`prep` 不傳時行為不變。choice-kill 呼叫時 stdout 被 redirect,reach 的列印走 `self.out`。
- `Systems/lumos-cli-read.md`(search 排除 superseded):不影響,沒碰 search。
- `Systems/bound-tests-gate.md`:不影響。新事件 kind(`reach`、`reach-run`)不被 `code-loop check` 的綁定測試讀者讀到,`_choice_ledger_index` 仍只收 kind `choice-kill`。
- `Systems/lumos-cli-lifecycle.md`(re-inject):不影響。
- `Systems/測試假綠形態.md`(翻紅釘要有前置斷言證明現場成立):間接相關。新測試用假 Gradle 加翻紅釘,但沒蓋 AndroidJUnit4 與 unknown 雜湊兩個情境(見上兩條 major)。
- `Systems/design-loop.md`:不影響。
- `Systems/pitfalls-code-loop.md`、`Systems/loop-convergence-recording.md`:不影響。`LOOP_NOT_CLOSE_EVENTS` 補登了 `reach` 與 `reach-run`,和既有 choice-kill 的做法一致。

其他我走過、判定沒問題的地方:
- 舊程式讀新帳。`cov:` 前綴的 tests_sha 一定對不上,所以一定重跑。`_choice_ledger_index` 不收 reach 事件。
- `order` 改成子集後,`finish` 與 `_choice_kill_judge` 不會誤判缺結果。
- 合併快篩的子集判讀。
- `rmtree` 只刪 `choice-cov/` 底下較舊的非符號連結子目錄。

總結:最高等級是 major
