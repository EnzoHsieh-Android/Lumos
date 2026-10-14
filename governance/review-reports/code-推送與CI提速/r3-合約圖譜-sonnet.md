severity: major

我是三個月後的接手人,逐句對了計劃、各筆記、文件和 ci.yml 註解。複本在 `/tmp/lumos-seat-work/code-推送與CI提速-r3/合約圖譜-sonnet/repo`,固定在 aea70018,沒碰主 repo。三支新測試(`t_runner_shard_by_duration`、`t_test_durations_refresh`、`t_ci_yml_speed_shape`)原樣都綠,`lumos lint` 三篇筆記都 0 問題。

做法是把各條款對應的實作逐處改壞,再跑綁定測試,共約 45 處。大部分改壞都會翻紅,但有幾處會讓條款宣稱的行為壞掉、測試照綠。

## 條款綁定測試抓不到的改壞

severity: major
blocking: 是
[S6] 三種換表情況只驗到一種。條款寫「被刪、被改、從無到有」,綁定的 `t_test_durations_refresh` 只造了「開頭沒表、結尾有表」。我把 `if _thash_end != _thash:` 依序改成下面三種,`t_test_durations_refresh` 都是 33 passed 0 failed:
- `if _thash is None and _thash_end is not None:`(只擋從無到有)
- `if _thash_end and _thash_end != _thash:`(被刪不擋)
- `if (_thash is None) != (_thash_end is None):`(被改不擋)

另外把 `_thash_end = "讀不懂"` 改成 `_thash_end = _thash`(結尾讀不懂當沒換),也是照綠。
失敗場景:跑到一半有人刷新或切分支換了表(被改),或刪了表(被刪),這一片不會 rc 2,聯集可能不等於全部卻全綠。這是計劃 S6 和實務隱患那段最在意的情況。
應該是:每種情況各造一組,至少「被改」和「被刪」要各有一組。
引句:「if _thash_end != _thash:」
歸因:未判定。`耗時表換了` 這串字不在修補差異裡,所以這條測試是修補之前就有的;S6 條款本身是修補才補上的。
查證:`grep -c "耗時表換了" /tmp/code-推送與CI提速-r3-repair.patch` 得 0。

severity: major
blocking: 是
[S2] 沒有耗時表時「照名字輪流分」沒有被驗到。我把輪流分那行改成 `if k % _n == 0`,等於只有第 1 片有測試,結果:
- `t_runner_shard_by_duration` 是 34 passed 0 failed
- 全部 `-k shard`(58 案例)是 58 passed 0 failed
- 全部 `-k t_runner`(117 案例)是 117 passed 0 failed

`-k t_prepush` 和 `-k t_ci_` 我沒跑完(`t_prepush` 逾時 300 秒),所以這兩組是否另有測試涵蓋我沒驗到,標 ⚠。
測試對沒表只斷言 `--shard 1/3 --list` rc 0,加上輸出裡有「沒有耗時表」這串字。
失敗場景:消費專案沒有耗時表,以及計劃〈回退〉說的「刪掉表就退回輪流分」,全靠這條路。它壞了(每片分到的內容不對),測試不會紅。
我另外確認過未改壞的版本是對的:沒表時三片各 683 支,聯集 2049 支、沒有重複。
引句:「tests = [t for k, t in enumerate(tests) if k % _n == _i - 1]」
歸因:未判定。
查證:在 aea70018 上改壞後跑 `python3.14 scripts/test_lumos.py -k t_runner`,輸出 117 passed, 0 failed。

severity: major
blocking: 是
[S4] 同一支測試沒有掃完同族的註解騙綠。筆記說這類問題已修(「先濾掉註解行再比」),但只有 shards 那段濾了註解行。`top` 那三條 concurrency 斷言是 `"…" in top`,沒濾。我把 ci.yml 的 `cancel-in-progress: ${{ github.event_name == 'pull_request' }}` 前面加 `#`,`t_ci_yml_speed_shape` 是 10 passed 0 failed。把整行 `group:` 改成註解也是 10 passed 0 failed。
失敗場景:PR 事件不再取消舊 CI(或 group 消失、workflow 不合法),測試照綠。
應該是:跟 shards 那段一樣,先濾掉以 `#` 開頭的行再比。
同族對照:把 group 改成 `ci-${{ github.ref }}` 會紅,所以字串本身有守,漏的只有註解這個縫。
引句:「check("只有 PR 事件取消進行中的工作", "cancel-in-progress: ${{ github.event_name == 'pull_request' }}" in top, top[-400:])」
歸因:未判定。這支測試的 concurrency 斷言在修補差異裡也有(`grep -c "只有 PR 事件取消進行中的工作"` 得 1),但我沒逐版本比對修前行為。

severity: major
blocking: 是
審計修正紀錄 r2 寫「測試補到每條條款改壞都翻紅」,跟上面三條打架,是內部說法不實。
引句:「測試補到每條條款改壞都翻紅,分片測試 59 秒降到 24 秒」
歸因:有證據的修復造成:這句話是修補差異新加的(`grep -c` 得 1)。
應該是:要嘛補上面三條,要嘛把這句收窄成實際範圍。

severity: minor
blocking: 否
[S1] 權重下限「0.05 秒」這個值沒被釘住。把 `_DURATION_FLOOR` 改成 0.06 或 0.04,`t_runner_shard_by_duration` 都是 34 passed 0 failed。改成 0.0 才會紅。測試只驗「有下限」,沒驗是 0.05。
引句:「_DURATION_FLOOR = 0.05」
歸因:未判定。

severity: minor
blocking: 否
[S2/S3] 布林被當成合法秒數。移除 `isinstance(v, bool)` 的排除後,`t_test_durations_refresh` 和 `t_runner_shard_by_duration` 都綠。函式說明寫「布林不算」,沒有測試造 `true` 當秒數。條款本文只列非負有限數字,所以只算說明與測試對不上。
引句:「if isinstance(v, bool) or not isinstance(v, (int, float)):」
歸因:未判定。

severity: minor
blocking: 否
[S3] 計劃〈做法〉說刷新「用主程式既有的原子寫入(暫存檔名每次不同)」,測試只驗了「舊的固定暫存檔名是符號連結不被跟著寫」和「沒留 `.tmp-wlf`」。把 `_write_lf(...)` 換成直接 `table_path.write_text(...)`,`t_test_durations_refresh` 是 19 passed 2 failed,所以有紅;但紅的原因是暫存檔相關斷言一起壞,不是原子性本身被驗到。這條屬於做法而非 [S] 條款,只提醒。
引句:「_write_lf(table_path, json.dumps({"version": 1, "tests": dict(sorted(table.items()))}, ensure_ascii=False, indent=1) + "\n")」
歸因:未判定。

severity: minor
blocking: 否
計劃〈做法〉寫「shards 工作在每一份的日誌開頭印開始時間」。但這份日誌寫進 `/tmp/shard-$i.log`,Actions 輸出只印 `tail -25`(紅時加失敗前後文)。日誌通常超過 25 行,所以開始時間不會出現在 Actions 畫面;結尾的「第 i 份耗時」是最後一行,看得到。耗時看得到,所以撤除條件量得到;只是「開始時間」這個交付項目看不到。
引句:「echo "第 $i 份開始 $(date -u +%H:%M:%S)"」
歸因:有證據的原有設計缺口。

severity: minor
blocking: 否
文件同步只改了數字。`reference.md` 的子命令全覽、`ARCHITECTURE.md` 的 CI 節點只改了數字或沒動,沒列 `test-durations`。總數有機械守衛(沒漏),分類清單沒守。`bound-tests-gate` 的 WHY 只寫分片與 concurrency,沒寫耗時表、刷新指令與簿記檔。三個月後的接手人從這個 Systems 節點找不到 refresh 的說明,要去讀計劃或 `commands/06`。
引句:「+## 3. CLI 子命令家族 (90 個頂層命令)」
歸因:有證據的原有慣例,不是這次回歸。

## 已核對、對得上的部分

- **摘要行格式**:`bound-tests-gate` 的 WHY(有 `[出處:]` `[因:]`)和 PITFALL(有 `[出處:]` `[根因:]`,`[修法:]` 與 `[test:]` 都有)、`測試假綠形態` 兩條 PITFALL 與 SEE 行,必有鍵都齊。第③型、第⑤型的編號與該筆記的定義吻合。
- **計劃的 REVISIT**:兩行日期格式正確;RETIRE-IF、PRIOR-ART、`lands_in` 都在。
- **S1 實測**:用真實耗時表跑 `--shard i/16 --list`,16 片聯集 2049 支、沒有重複,等於 `--list` 全部;每片都印同一個表雜湊(`19a95d9d`)。
- **逐項改壞都翻紅**(各自綁定的測試都紅):
  - `counts[j]` 平手取支數
  - 排序方向與同權重依名字排
  - 全表中位數(改成平均值)
  - 表雜湊前 8 碼與總支數
  - 壞表 rc 2
  - 刷新取最新(改成依檔名)
  - 小數三位
  - 保留舊值
  - 刪 run 檔
  - 讀完被改寫的 run 檔留著
  - 簿記檔清單
  - 「不是一般檔」檢查與空 tests 檢查
  - 超大整數與 NaN 檢查
  - 非來源 repo 不寫 run 檔
  - 紅、例外、逾時都記
  - CI 子殼層的 `exit $rc`、`set +e`、`rc=$?`
  - PR 與 push 的 group 鍵
  - S6 的整個結尾檢查
- **S2 帶 `--suite` 的空片算過**:改壞 `if not tests and _args.suite:` 時 `t_runner_suite` 有紅,所以有別的測試守,不算漏。
- **固定席節點**:
  - `測試假綠形態`(★INVARIANT★,要求還原翻紅釘配前置斷言):新增的三支測試都有 `★前置★` 斷言。上面三條 major 是「條款某些情況沒有造案例」,不是「前置斷言不成立」,所以對該合約的影響是新增的兩條 PITFALL 修法並沒有被全面套用。
  - `design-loop`(★INVARIANT★,計劃有 [SN] 時須有 `[綁定測試:有]`):計劃六條都有 `[test:]`,不影響。
  - `pitfalls-code-loop`、`reversibility-governance-ledger`、`loop-convergence-recording`(★RISK★,牽連檔 `scripts/lumos`):簿記檔清單是 pitfalls 與代碼審豁免共用的單一源。多一個耗時表只讓它不被當程式碼掃、不讓代碼審留痕失效,方向正確,不影響。
  - `lumos-cli-read`、`guard-kill`、`lumos-cli-lifecycle`:只因牽連檔重疊被列,改動沒碰到各自的合約行,不影響。
  - 超出上限只列名的節點:沒有展開判讀,標 ⚠ 未逐條判。

## 修補鏡頭三問

1. **原問題修復效果**:配對案例 R1 到 R6 我自己驗了這幾項。
   - R1:`--shard 1/100000000 --list` 約 1.4 秒,輸出「分到 1 支」,峰值約 496MB,看起來是載入測試的固定開銷;我沒在修前版本比對那 7.7GB。
   - R4:拿掉 `; exit $rc` 後 `t_ci_yml_speed_shape` 是 9 passed 1 failed。
   - R5:把刷新排序改成依檔名後 `t_test_durations_refresh` 是 32 passed 1 failed。
   - R2、R3、R6:我只確認對應測試存在且原樣是綠的,沒有逐案例重現修前行為。
2. **修補處相鄰路徑**:
   - 沒表的路徑(P2)結果正確,但沒有測試守(見第二條 major)。
   - 空片 rc 1(P3)和帶 `--suite` 空片算過都有測試守。
   - 換表 rc 2(P5)只守了一種情況(見第一條 major)。
   - P4 的 BOM 與保留舊值有測試守。
3. **新發現的修前修後差異**:我沒有在 22f6e132 上重跑改壞實驗,因此上面各條「歸因」多數標未判定。例外是審計紀錄那條,是修補差異新加的。

有 4 條 major(blocking 是),其餘 4 條 minor,blocking 共 4 條。
