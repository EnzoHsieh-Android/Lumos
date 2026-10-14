severity: minor

# 併發、資源與效能鏡頭(r3):結論

五項實測都沒有崩潰、表壞或誤擋。我只找到一條 minor:兩個 refresh 同時跑時會漏記測量值。依單人使用、AI 依序操作的威脅模型,這條可放行。實驗都在 `/tmp/lumos-seat-work/code-推送與CI提速-r3/併發資源-sonnet/` 的複本裡做,沒動 repo 根。

## 發現

severity: minor
blocking: 否

兩個 `lumos test-durations refresh` 同時跑,後寫的那個會覆蓋前一個的結果。它是先讀舊表,算完再整檔寫回,中間沒有鎖。另一個程序若在這段期間已合併、寫入並刪掉 run 檔,後寫的那個就只剩舊表,卻照樣印「✓ 耗時表更新」。

引句:「+    table = dict(tests or {})」

- 重現:`/tmp/lumos-seat-work/code-推送與CI提速-r3/併發資源-sonnet/race.sh`,舊表 20000 筆加 6 個 run 檔(共 18000 筆),兩個 refresh 同時跑。
- 預期:最後表有 38000 筆。
- 結果:兩輪各 12 次,第一輪有 4 次、第二輪有 3 次表只剩 20000、23000 或 29000 筆,run 檔全被刪光。
- 輸家的輸出是「原有 20000 支 → 現在 20000 支;這次合進 0 筆,讀完刪掉 6 個 run 檔」,rc 為 0。
- 它說「刪掉 6 個」是用 `len(runs) - kept` 算的,實際上是別人刪的。
- 損失:測量值掉了,下次分片稍不平均。耗時表本來就只是資料,不影響漏跑。計劃的 RETIRE-IF 看的是每台機器的耗時,所以不影響。
- 表從未被寫壞:12 次跑完表都能被 JSON 解析。`_write_lf` 是每次不同暫存名加 `os.replace`,是原子寫入。
- 沒有 Traceback:run 檔在列出後被刪,會走「略過讀不懂的 …」(訊息稍誤導),排序與刪檔都不崩。
- 歸因:有證據的原有漏查。主線 `1b83927e` 沒有這支子指令(`git show 1b83927e:scripts/lumos | grep -c cmd_test_durations_refresh` 得 0),所以不是修補造成的回歸。
- 建議:要擋就在讀表前拿鎖,或接受它。單人、依序操作下可放行。

## 五項實測

1. **每片載入整個主程式的成本。**
   - 清掉 `scripts/__pycache__` 後跑 `test_lumos.py --list --shard 1/16`。主線約 1.5 到 2.0 秒、493MB。修後第一次(冷)是 6.2 秒、704MB,之後(暖)約 1.55 秒、497MB。
   - 冷啟動多約 4.5 秒、約 210MB,CI 16 份各付一次。單獨載入 `lumos` 冷是 3.6 秒、272MB,暖是 0.06 秒、33MB。
   - 這筆開銷主線其實早就付了,只是被提前:很多 `t_` 測試與 `_docs_suite_select` 本來就會 `_load_lumos_inproc()`。完整跑 3/16 這片沒有看到額外劣化,不構成問題。

2. **份數極大。**
   - `--shard 1/100000000`、`1/1000000000` 和 `1/10^24` 都是 2.3 到 2.6 秒、約 495MB,和暖啟動基線一樣。`99999999/100000000` 乾淨回「擋下:一支測試都沒分到」,rc 為 1。
   - 直接量 `_shard_by_duration`(3700 個名字):n=16 為 0.01 秒,n=3700 為 1.56 秒,n=10^9 為 1.39 秒(實際只配 3700 份)。最壞是 O(測試數²),約 1.5 秒,不爆記憶體。
   - 200 萬筆的表呼叫 `_shard_by_duration` 只要 0.02 秒。
   - 空表會讓 `statistics.median` 丟 `StatisticsError`,但 `_read_durations_table` 先把空 tests 擋掉,走不到。

3. **兩個 refresh 同時跑、run 檔被刪。** 見上面那條 finding。

4. **正常推送會不會誤擋。**
   - 實跑完整的 `--shard 3/16`(127 支),結果 911 passed、0 failed、rc 為 0,開頭與結尾表雜湊都是 `19a95d9d`,沒有誤擋。這次因機器很忙跑了約 12 分鐘。
   - `--shard 2/2 -k t_runner_shard_by_duration` 也 rc 為 0,34 passed。
   - repo 裡 `scripts/hooks`、`.github` 沒有任何東西在測試期間改動 `governance/test-durations.json`。

5. **大表與超深巢狀。**
   - 深度 100 萬的 `[` 放在舊表或 run 檔裡,`RecursionError` 都被接住。舊表壞掉回「不是合法的 JSON」,rc 為 2,不覆蓋。run 檔壞掉只略過,不崩。
   - 150 萬筆的 run 檔刷新:8.9 秒、885MB,rc 為 0。這是人為的極端值,不是正常規模。
   - 刷新帶深巢狀舊表:1.6 秒、274MB。

## 固定席節點

- `Systems/測試假綠形態`、`lumos-cli-read`、`lumos-cli-lifecycle`、`guard-kill`、`design-loop` 的 INVARIANT 各自綁定的測試和行為(還原翻紅釘、search 排除規則、re-inject 保留、guard kill 的 rc 與 JSON 純度、處置閘第五步),都與耗時分片、refresh 無關。我沒看到這次改動碰它們,判不影響。
- `pitfalls-code-loop`、`reversibility-governance-ledger`、`loop-convergence-recording` 是 RISK 節點,牽連檔是 `scripts/lumos`。這次對 `scripts/lumos` 只加了簿記清單的一項和新子指令,沒動它們的邏輯,判不影響。
- 超出上限、只列名的節點我沒有逐篇讀,屬未驗範圍。

## 修補三問

1. **原問題的修復效果(r2 的巨大份數與 run 檔消失崩潰)有行為證據。**
   - 份數:輸入 `--shard 1/1000000000`,預期不吃記憶體,修後是 2.5 秒、497MB,rc 正常。
   - run 檔消失:修後的 refresh 對列出後消失的檔不崩。
   - 兩個修補點在修前版本我沒有實際跑,修前行為只靠 patch 註解的描述,沒有獨立重現。
2. **修補處的相鄰路徑仍成立。**
   - 空片:子集配分片時空片回 0。
   - 沒分到:全套沒分到時回 1。
   - 沒有表:退回照名字輪流分。
   - 格式壞的表:回 2。
   - 表在跑的期間被換掉:由結尾再讀一次比雜湊擋下。
   - 上面 5 項實測都走過這些路徑,沒有失敗。
3. **新發現(refresh 並發漏記)的修前與修後。** 修前沒有這支子指令,所以沒有可比的修前結果。它是新功能本身的原有缺口,不是修補引入的。

未驗範圍:多會談同時對真實 repo 跑 refresh,和 CI 實機 16 份同時冷啟動的真實牆鐘時間。

最嚴重等級 minor,blocking 共 0 條。
