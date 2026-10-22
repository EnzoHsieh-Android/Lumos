severity: minor

## 總結:最高等級為 minor

這次修補把「每幀超時 P90 -1.7→-0.9」的誤報去掉了,新測試也守得住這件事。兩條 finding 都只是測試漏洞或殘留,不會讓程式做出錯的行為。

## Findings

### M1:啟動類路徑沒有測試守住新的容差下限
severity: minor
blocking: 否

歸因:有證據的原有漏查。修補一併把容差下限帶進啟動類,但新測試沒有補啟動類的案例。

引句:「delta, tol = _macrobench_worse(metric, b["median"], c["median"], cfg)」
file: `scripts/lumos:39480`(`_macrobench_cmp_metrics`)

- **輸入**:啟動類指標基準中位數小於 10(例如 5)。容差下限只在 `|基準|×10%` 小於 1 時才生效。
- **要守的行為**:5 → 5.8 的 0.8 差距要被下限放過;5 → 6.2 才算退步。
- **改壞方式**:我在臨時副本把 `_macrobench_cmp_metrics` 改回舊公式(基準非 0 只用百分比),跑 `python3.14 scripts/test_lumos.py -k macrobench`,結果是 92 passed, 0 failed。
- **測試現況**:新增的 `t_macrobench_nonpositive_baseline` 斷言與 `t_macrobench_real_tablet_lab` 只走到滑動類。實機啟動值是 216 和 571,下限根本沒作用。
- **為什麼是 minor**:因為正式碼兩處共用 `_macrobench_worse`,只有蓄意只改啟動類那一處才會漏,所以降到 minor。
- **修前/修後(兩版同一輸入)**:啟動類 5 → 5.8,修前 tol=0.5 會報退步,修後 tol=1 不報。這個差異沒有任何測試釘住。

### M2:每幀超時跨零規則不看容差,正常抖動跨過 0 仍會誤報
severity: minor
blocking: 否

歸因:有證據的原有漏查。兩版行為一致,不是修補造成的。

引句:「crossed = MACROBENCH_ZERO_CROSS.get(metric) == stat and b[stat] <= 0 < c[stat]」
file: `scripts/lumos:39494`(`_macrobench_cmp_sampled`)

- **輸入**:基準 P90 = -0.85,這是 `3-base-again` 的實測值,現行測試用的是 `1-base` 的 -1.69。重跑 P90 = +0.05,差距 0.9,比新容差 1 還小。
- **走到的行為**:`crossed` 為真,不看差幅,照樣報 `zero_crossed` 退步。
- **兩版結果**:我用同一個比對函式跑,修前和修後都回 `[('P90', True)]`。
- **對照**:同一個指標 -1.69 → -0.85(差 0.84)修後不報,但 -0.85 → +0.05(差 0.9)會報。
- **為什麼算漏洞**:修補要解的就是「正常抖動被報成退步」,而這條路還是會誤報。
- **為什麼不升級**:計劃明寫「每幀超時從準時變成掉幀不看差幅」,這是設計選擇;文件和程式一致,所以只列 minor。
- **尚未判定**:跨零要不要也套容差下限,這是設計取捨,我不替它下結論。

## 三問與已驗主張

### ① 原問題的修復效果

- **claim**:正常重跑不再誤報。
- **input**:實機三份檔。基準取 `1-base`,現況取 `3-base-again`,每幀超時 P90 從 -1.685 變 -0.851。
- **case_source**:`governance/research/macrobench/2026-10-23-lab-tablet/`,我另外用 Python 讀過數值。
- **before**:把修前的 `scripts/lumos` 配上現行測試檔,跑 macrobench 測試共 89 passed、3 failed。失敗的有 `t_macrobench_real_tablet_lab` 的「正常重跑 → 一項都不報」,實際輸出 `frameOverrunMs P90 baseline -1.685 current -0.851 delta 0.834`;另有 `t_macrobench_nonpositive_baseline` 兩條。
- **after**:`python3.14 scripts/test_lumos.py -k macrobench` 在修後版本全數通過;我在完整副本上跑是 92 passed、0 failed(那份副本只做了 M1 那一處改壞)。
- **comparison**:新測試修前紅在「正常重跑」那一條,符合本案特定鏡頭的預期;三份檔真的走到誤報那一項。
- **獨立核對**:測試註解的手算數字和實檔一致。啟動中位數 216.07 → 571.14 → 223.12,P90 超時 -1.69 → 3.65 → -0.85,P50 超時 -3.6 → -1.0 → -3.42,幀 CPU P90 4.71 → 10.15 → 4.69。

### ② 修補處的正常、錯誤與相鄰路徑

- **啟動類**:兩道門(超過容差、且超出基準最大值)沒變。基準 216、容差下限 1 時,+355 仍被抓到。
- **容差設很大**:例如 abs 設 100,啟動 +355 仍會報。這是設定的結果,文件說明得清楚。
- **容差設很小**:下限退回成比例主導,行為和舊版一致。
- **基準為 0**:容差 = max(0, abs) = abs,和舊版一致,不會除以零。
- **基準為負**:取絕對值算比例。`-100 → -95` 不報,`-100 → -85` 報(新增的斷言釘住)。
- **越大越好的指標**:`delta` 方向在 `_macrobench_worse` 裡反過來,容差部分不變。
- **不可逆/新舊互讀**:基準檔格式沒動,舊基準可直接讀。
- **副作用**:任何基準小於 10 的指標,容差下限都蓋過 10% 的比例。例如幀 CPU P90 基準 4.7 要慢過 1ms(約 21%)才報。文件有寫明是下限,不算不一致。
- **M1、M2**:見上。

### ③ 同一案例在修前、修後

- `-1.69 → -0.85`:修前報退步,修後不報。
- `-0.85 → +0.05`:兩版都報(M2)。
- `-0.05 → +0.02`:兩版都報(M2)。
- 啟動類基準小於 10:修前、修後行為不同,但沒有測試釘住(M1)。

## 圖譜鏡頭

固定席節點都在宣稱 `scripts/lumos` 與測試的共通合約:search 預設排除 superseded、guard kill 的 rc 與 JSON 純度、`re-inject` 保留 sentinel 外內容、`bound-tests` 閘、`design-loop` 處置閘。這次改動只動 `_macrobench_worse` 一行、`macrobench` 區塊的註解、一支新測試和文件,都不碰那些行為。我沒有發現破壞宣稱行為或合約的證據;這些合約綁的測試我沒有逐支跑。

## 文件一致性

- 計劃 S5、`Systems/macrobenchmark-adapter.md`、`skills/lumos-project-notes/reference.md` 對容差的描述互相一致,也和程式一致(`max(|基準|×百分比, abs_tolerance)`)。
- 照文件設定的結果符合預期。
- 唯一要注意的是下限對基準小於 10 的指標會壓過比例。文件寫的是「下限」,不算不一致。
- 未驗範圍:我沒有重新跑 pre-push 閘和 `lumos doctor`。

## 清理

我已刪掉測試副本 `m/`、`t/` 與 `gctl-run-xkmuvopu` 現場。`/tmp/lumos-seat-work/code-macrobench/正確性-sonnet/` 底下還剩 `lumos-before`、`lumos-after`、`lumos-mut`、`p.py`、`base-before.json`、`p2`、`proj`、`__pycache__`。其中 `lumos-after`、`lumos-mut`、`p2`、`proj` 我完全不記得自己建過,可能是先前席留下的,我沒動;`lumos-before` 和 `p.py` 是我這次建的。
