severity: major

## 1 rerun.sh 範本的三道「不准空轉」檢查,測試一道都沒單獨守住
severity: major
blocking: 是
引句:「if len(heads) != len(qs):」
歸因:有證據的修復回歸。這是修補新增的測試(t_android_evidence_rerun_refuses_empty)護不住它自己新增的檢查,不是行為變壞。修前 3461928 沒有這三道檢查;下面的突變只動修後版本。

失敗場景:
- 測試的三個案例(漏分號、標頭少空格、列了不存在的 Q9)都沒有任何 `expect`,所以任何一個案例都會被「沒有任何一條帶 expect」那一條擋成 rc 2。
- 拿掉「標頭數不等於解析條數」的檢查,三案例仍是 rc 2。
- 拿掉「manifest 列了 queries.sql 沒有的查詢」的檢查,案例 3 也仍是 rc 2。
- 真實的壞法是:多條查詢、都有 expect、只有最後一條漏分號;或 manifest 多列一個 Q。這時只有被拿掉的那道檢查能擋。

重現(在修後版本 1c3df999 的 clone 內做突變,reference.md 的 ```sh 範本改一行):
1. 把 `if len(heads) != len(qs):` 改成 `if False:`,跑 `python3.14 scripts/test_lumos.py -k android_evidence_rerun`,結果 `4 passed, 0 failed`。
2. 把 `if listed - set(qs):` 改成 `if False:`,同一指令,結果 `4 passed, 0 failed`。
3. 用突變 1 的範本跑真實收據:queries.sql 有 Q1(有 `;`、expect 正確)、Q2(expect=b:n=2、最後漏 `;`),manifest 只列 Q1,TP 換成會印 `"k","n"` / `"a","1"` 的假程式。
   - 原版範本:rc 2,印「有 2 個標頭、只解析到 1 條」。
   - 突變 1:rc 0,印 `OK  Q1 a:n=1`。Q2 被靜默丟掉,整份收據回 0。
4. 不用 `-k` 篩,這支測試在修前版本不存在,所以沒有修前紅綠可比。

file: `skills/lumos-android-evidence/reference.md` 範本內該檢查;測試在 `scripts/test_lumos.py` 的 `t_android_evidence_rerun_refuses_empty`
修法方向:每個案例至少一條帶有效 `expect`,讓每道檢查只能靠自己擋下。

## 2 非有限數測試只蓋了啟動類,滑動類兩個呼叫點改回舊函式測試照綠
severity: major
blocking: 是
引句:「stats = {s: float(v[s]) for s in MACROBENCH_PERCENTILES if isinstance(v, dict) and _macrobench_num(v.get(s))}」
歸因:有證據的修復回歸,同樣是修補新增測試的缺口,不是行為回歸。修後程式本身是對的:`_macrobench_read_one` 和 `_macrobench_entry_ok` 的滑動類分支都已換成 `_macrobench_num`。

失敗場景:
- 計劃 S10 要求「基準檔或結果檔的數字是 NaN 或 ±Infinity,不得拿它判不算退步」。
- `t_macrobench_rejects_nonfinite` 的基準檔與結果檔只造了啟動類(median/minimum/maximum)。
- 滑動類(P50/P90/P95/P99)的 NaN 完全沒測。
- NaN 的 P90 讓「現值 > 基準+容差」恆假,等於該情境永遠不算退步,正是修補要防的那一族。

重現:
1. 在修後 clone 把這兩處改回 `_secev_num`:`_macrobench_read_one` 的 sampledMetrics 那行,以及 `_macrobench_entry_ok` 的 `all(_macrobench_num(x) for x in v.values())`。
2. 跑 `python3.14 scripts/test_lumos.py -k macrobench`,結果 `158 passed, 0 failed`,沒有任何紅。
3. 同一個突變版本餵一份 `sampledMetrics.frameDurationCpuMs.P90 = NaN` 的結果檔。`--update-baseline` 顯示「基準已更新」並把 NaN 項收進基準。
4. 原版(未突變)程式對同一份檔回「讀不了:缺 P50/P90」,正確。

file: `scripts/lumos` 的 `_macrobench_read_one`、`_macrobench_entry_ok`;測試在 `scripts/test_lumos.py` 的 `t_macrobench_rejects_nonfinite`

## 3 超大整數讓 `_macrobench_num` 噴 OverflowError,門檻檔從「靜默收」變成 traceback
severity: minor
blocking: 否
引句:「return _secev_num(v) and math.isfinite(v)」
歸因:有證據的修復回歸,僅限門檻檔這條路徑。

失敗場景:
- 輸入是 JSON 整數字面值(不是浮點),例如門檻的 `"max": 1` 後面接 400 個 0。Python 讀成 int,`math.isfinite` 對它丟 `OverflowError: int too large to convert to float`。
- 計劃 S5 寫的是「不是有限的數字 → 回 2 並印第幾條」。實際是 rc 1 加 traceback,不是 rc 2。
- 修前版本對同一份門檻檔回 0,靜默收下。
- 設定檔 `tolerance_pct` 寫同樣的巨大整數,修前修後都是 traceback(`float(raw[k])`),屬原有。基準檔與結果檔因為有 try/except,修後會被正確當成讀不了。
- 實際機率低,只有手誤才會遇到。

重現:
1. 做一份 `.lumos/macrobench-thresholds.json`,把一條合法門檻的 `max` 換成 `1` 加 400 個 0。
2. 跑 `python3.14 scripts/lumos macrobench --repo <目錄> --json`。
3. 修後 rc=1 加 `OverflowError`,修前 rc=0。

file: `scripts/lumos` 的 `_macrobench_num`,被 `_macrobench_threshold_item_err` 呼叫且該處沒有 try 包住
修法方向:在 `_macrobench_num` 內 `try/except OverflowError` 回 False。

## 三問

**1. 原問題的修復效果有何行為證據?**
- NaN、±Infinity 在三處行為已驗:
  - 門檻 `max`/`min` 與設定檔容差的啟動類 NaN 被擋(`t_macrobench_rejects_nonfinite` 涵蓋)。
  - 基準檔與結果檔的滑動類 NaN,我用真實檔跑原版程式驗過:結果檔回「讀不了:缺 P50/P90」。
  - 基準檔的滑動類 NaN 路徑我沒單獨造檔驗。
- 漏分號、標頭歪、列了不存在 Q 這三個案例,範本都回非 0。但案例都沒帶 expect,證據只能說「至少有一道擋住」,護不住每一道(見 1)。
- 來源雜湊與解析改用同一份 bytes:我只讀了程式,沒造競態;作者自己也標了沒有競態測試。
- 日期、編號相關案例(2026-13-45、壞的排第 1 條)我只讀了程式,沒另跑。

**2. 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 正常路徑:跑了 `-k macrobench`(158 全綠)與 `-k android_evidence_rerun`(4 綠)。
- 錯誤路徑:見 1、2、3。
- 相鄰路徑:`_macrobench_num` 的四個呼叫點(`_macrobench_config_fields`、`_macrobench_read_one` 兩處、`_macrobench_entry_ok` 兩處)加上門檻檔,macrobench 區塊裡沒有漏掉其他讀數字的地方。區塊內 `_secev_num` 只剩 `_macrobench_num` 內部那一處呼叫。
- `_secev_num` 本身沒被改,資安證據閘不受波及。我沒另跑資安閘的測試。

**3. 新發現的同一案例在修前、修後各是什麼結果?**

| 案例 | 修前 3461928 | 修後 1c3df999 |
|---|---|---|
| 發現 3:門檻超大整數 | rc 0,靜默收下 | rc 1,traceback |
| 發現 3:設定檔超大整數 | 原有 traceback | 同樣 traceback |
| 發現 1、2:被突變的檢查 | 修前沒有這些檢查,也沒有這兩支測試 | 突變後測試照綠 |

發現 1、2 的證據是對修後版本做突變,沒有修前對照。

## 已驗與未驗
已驗:
- 圖譜鏡頭:派工詞說範圍算不出來,所以只就 diff 碰到的 `Systems/macrobenchmark-adapter` 判定。我讀了新增的 WHY 和 PITFALL 行,沒看到破壞既有合約。
- 新舊基準互讀:`source` 欄只寫入、不參與 `_macrobench_entry_ok` 與比對,舊程式讀新基準、新程式讀舊基準都不受影響。測試涵蓋沒有 `source` 的舊基準。

未驗:
- SKILL.md 與 reference.md 的裝置指令(adb、simpleperf)沒實跑。
- 競態(兩次讀檔之間檔案被換掉)。
- 資安證據閘測試。

暫存目錄已刪。

總結:這份報告最高嚴重度是 major
