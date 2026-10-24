severity: minor

## 方法

我用 `git show f0d41453:scripts/lumos` 和 `git show 5fc4e715:scripts/lumos` 取出兩版,放在臨時目錄。每個案例的 repo 在臨時目錄裡造,用 `python3.14 lumos_{old,new} macrobench --repo … --stability … [--json|--update-baseline|--check-config]` 各跑一次。

沒碰 adb 和裝置,沒在工作樹動 git。完成後我刪掉了自己的臨時目錄。

另在工作樹跑了 `python3.14 scripts/test_lumos.py -k macrobench`,結果 169 passed、0 failed。這只代表現有測試沒被這次修補弄壞,不能證明下面的邊界案例被覆蓋。

## 發現

### F1 decided_by 的佔位判法只防得住「半形、同一行、兩邊都有角括號」的寫法

severity: minor
blocking: 否

引句:「    if not isinstance(by, str) or not by.strip() or re.fullmatch(r"\s*<.*>\s*", by):」

失敗場景:`decided_by` 填成下列寫法,兩版都回「macrobench 設定與門檻檔都合格」。用 `--check-config` 跑,「check 條目」和「舊寫法條目」各一份,結果相同。
- `<裁定\n的人>`(角括號中間有換行):`.` 不吃換行,所以 fullmatch 失敗。
- `＜裁定的人＞`(全形角括號)。
- `<裁定的人` 或 `裁定的人>`(只有一邊角括號)。

對照:`<裁定的人>`、`<Enzo>`、`  <x>  `、`<x> y>` 修後都被擋(舊版全放行)。`Enzo <e@x.com>`、`A<B` 修後仍放行,合法人名含 `<` 的情況不會被誤擋。空白字串兩版都擋,訊息是「缺 decided_by」。

評估:照抄範例的 AI 不會把括號換成全形或加換行,所以我只給 minor。換行那條只要加 `re.S` 就能補。

歸因:有證據的原有漏查。舊版對這些寫法本來就全放行,修補沒有讓它變差。

### 補充:舊寫法門檻條目也套了新的 decided_by 判法,合格的舊條目不會被誤擋

這一條只是回答「舊條目原本合格的會不會被擋」,不是缺陷。

- 舊條目 `decided_by: "Enzo"` 修後仍合格。
- 只有 `<…>` 佔位的舊條目,從放行變成被擋。這是預期行為。
- `decided_at` 與 `stat` 兩項的檢查順序對調了,只影響先報哪一個錯,不影響合格與否。
- `test_data` 現在也檢查 `device_model` 要是字串,舊版沒檢查。這是附帶的收緊,我沒有造案例實跑。

### F3 負數檢查擋掉了,但跳過原因的文字還寫「是 -1」

severity: minor
blocking: 否

引句:「    return None if not _macrobench_num(v) or v < 0 else v」

失敗場景:結果檔裡 `frozen_frames: -5`、`unreachable.after.bytes: -5`、`peak_anon_swap_kb: -5` 這種值。
- 舊版:`frozen` 判成達標,印出「凍結幀 -5 幀」,其餘兩項也被當成有效數字放行。
- 修後:三項都改列成「沒判」。這是修復有效。
- 但原因文字仍是「缺了、不是有限數或是 -1」,看不出是負數造成的,讀的人會去找 `-1`。

0 和 -0.0 兩版都照收,`-0.0` 印成「0 幀」,沒有問題。

歸因:有證據的修復回歸,輕微。兩版對 -5 的行為不同,新增的是文字不準。

### F4 --stability 結果檔的字串清洗改變了身分字串的比對

severity: minor
blocking: 否

引句:「        return _esc_clean(v, len(v) + 1)」

失敗場景:結果檔的 `scenario` 是 `s\t1`,門檻檔的 `scenario` 也是 `s\t1`。
- 舊版:兩邊相同,判成達標。
- 修後:結果檔被清成 `s 1`,判成「沒判」,原因寫「結果檔是情境 s 1,不是這條的 s\t1」。
- `device_model` 含控制字元時情況相同(`Pix\x07el` 對 `Pix el`)。

評估:真實的情境名和機型名不會含控制字元,風險很低。我標出來是因為「清完的字串跟原本不同時,判定會變」這件事確實發生了。清洗後鍵撞名的情況我沒有實跑。

歸因:有證據的修復回歸,影響面只有含控制字元的身分字串。

### F5 同一類孤立代理字元崩潰,在門檻檔的字串上還是崩

severity: minor
blocking: 否

引句:「    return _macrobench_stab_scrub(raw), None」

失敗場景:`macrobench-thresholds.json` 裡某條的 `contract` 是 `"bad\ud800x"`,再跑 `--stability … --json`。
- 兩版都以 `UnicodeEncodeError` 崩在 `json.dumps(..., ensure_ascii=False)`。
- 修補只清了 stability.json 的字串,門檻檔的 `scenario`、`contract` 沒清,而這兩個欄位都會被印出。

評估:這條要手寫或程式寫出孤立代理字元的 JSON 跳脫,在「單人、AI 依序操作、只用中英文」的威脅模型下機率很低。它是「同族一次掃完」的缺口,不是修補造成的。

歸因:有證據的原有漏查。兩版行為相同。

## 已驗屬實、沒有問題的項目

| 項目 | 兩版結果 |
|---|---|
| 巢狀深度 | 葉子在第 20 層時,修後放行;第 21 層修後被擋,訊息是「巢狀太深」。舊版 21 層也放行,所以範圍是變嚴。收集腳本實際最多 5 層(`exits.new[].type`),不會誤擋。`--check-config` 搭配過深的結果檔回 rc2,不存在的檔也是 rc2,兩版相同。 |
| 孤立代理字元(stability.json) | 舊版 `--json` 以 `UnicodeEncodeError` 崩,修後正常輸出。文字模式兩版都不崩,修後多出「1 筆:」。 |
| 明細改成先印警語與數量 | strictmode 0 筆時不進失敗行,達標也不印明細。1 筆印「1 筆:Violation0」。500 筆印「500 筆:…」,後面照舊被 500 字截掉,但數量留得住。java_growth 在類別名未還原且 300 類增長時,警語加「300 個類別增長:」排在前面,不再被截掉。0 個類別增長且未還原時印「(…)沒有類別增長」。 |
| `stability_unjudged` | 未給 check 條目時,下面五種情況的 `--json` 輸出都帶這一欄(舊版都沒有):門檻檔不存在、門檻檔只有舊條目、門檻檔是空清單、沒有 macrobench.json、有 results_dirs 但沒有基準。文字模式兩版都印警語。有 check 條目時兩版都沒有這一欄。 |
| `--update-baseline` 搭配 `--stability` | 修後文字模式先印警語再印更新結果(舊版也一樣)。 |

## 未驗範圍

- `--update-baseline --json` 同用時,輸出是文字而不是 JSON,所以沒有 `stability_unjudged`。兩版都有這個行為。我判斷它超出這輪修補範圍,只在此記錄。
- 有真實 Macrobenchmark 結果檔時的 `--update-baseline` 路徑我沒有造資料跑,只跑了「結果檔一個都沒讀成功」那條。
- `_macrobench_stab_scrub` 的遞迴在深度 20 內是安全的,我沒測超大寬度的檔案的效能。

## 回答三問

1. **原問題的修復效果**:有行為證據。負數判成達標、孤立代理字元讓 `--json` 崩、`--json` 少了 `stability_unjudged`、警語被截掉、`<裁定的人>` 佔位被放行,這五個症狀修前都重現,修後都解決。
2. **修補處的正常、相鄰路徑**:正常值(0、-0.0、合法人名、有 check 條目、5 層內巢狀)照舊成立。相鄰路徑裡,門檻檔字串的同族崩潰還在(F5)。
3. **新發現的案例在兩版的結果**:
   - F1:兩版相同,是原有漏查。
   - F3:兩版行為不同,修後的判定對、文字不準。
   - F4:兩版行為不同,是修補造成的小副作用。
   - F5:兩版相同,是原有漏查。

最嚴重 severity:minor,blocking 共 0 條。
