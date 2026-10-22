severity: major

## 範圍與歸因界線
修補 e88e62b0 對照修前 d6eba6f4。我跑了 `python3.14 scripts/test_lumos.py -k macrobench`,結果是 60 條通過、0 失敗。實驗都在 `/tmp/lumos-seat-work/code-macrobench/正確性-sonnet/`:`lumos-before` 是修前版,`lumos-after` 是修後版。

## Findings

### G1 S11 的形狀檢查漏掉 P95/P99,基準的 P99 是 null 或字串時照樣噴 traceback
severity: major
blocking: 是

引句:「all(isinstance(v, dict) and all(_secev_num(v.get(s)) for s in MACROBENCH_SAMPLED_JUDGED)」

佐證行:
- `scripts/lumos:39523-39534` 的 `_macrobench_entry_ok` 只驗 P50 和 P90。
- `scripts/lumos:39491-39494` 的 `_macrobench_cmp_sampled` 用 `stat not in b` 判斷,所以 `P99: null` 會通過檢查,之後在 `_macrobench_worse` 做減法時出錯。

失敗場景:
- 基準檔裡 `frameDurationCpuMs.P99` 是 `null`,其餘欄位齊全。這是手改或寫壞的「型別不對」,S11 要求這種情況回 0 並印「基準讀不了」。
- `lumos macrobench --repo proj` 會在 `_macrobench_worse` 噴 `TypeError: unsupported operand type(s) for -: 'float' and 'NoneType'`,rc 為 1。
- 這個指令的合約是只提醒、恆回 0。

最小重現:先用 `lumos-before` 對 KDS 真結果檔跑 `--update-baseline` 產生基準,把基準的 `P99` 改成 `null`,再用兩版各跑 `macrobench --repo proj`。

歸因:有證據的原有漏查。S11 修補沒補到,但這個洞不是修補造成的。
- 修前:`lumos-before macrobench --repo proj` 噴 TypeError,rc 1。
- 修後:`lumos-after macrobench --repo proj` 噴同一個 TypeError。
- 兩版結果一樣,所以不是回歸,是修補沒蓋住 S11 所述的「任何一項型別不對」。

### G2 S12 的「不得說成讀不了」只在 `--update-baseline` 路徑做到,預設比對路徑仍印「讀不了」
severity: minor
blocking: 否

引句:「print(f"  讀不了 {f['file']}:{f['reason']}")」

佐證行:`scripts/lumos:39573-39583` 的 `_macrobench_print` 對所有 failed 項目都加「讀不了」前綴,沒有看 `kind`。

失敗場景:
- 同一個情境出現在 `out/a` 和 `out/b`。
- 用 `lumos-after macrobench --repo p2` 不帶旗標跑,輸出 `讀不了 out/b/x-benchmarkData.json:... 重複出現(也在 ...),兩份都不收`。
- S12 明講「不得說成結果檔讀不了」。

測試缺口:`t_macrobench_duplicate_scenario` 只檢查 `--update-baseline` 的輸出和 `--json`,沒有檢查預設文字輸出。把前綴改回去,測試仍然全綠。

歸因:有證據的修復不完整。
- 修前:update 路徑印「一個結果檔都沒讀成功」,比對路徑印「讀不了 … 也出現在」。
- 修後:update 路徑改對了,比對路徑仍印「讀不了 … 重複出現」。
- 所以是 S12 只修了一半,不是回歸。

### G3 `t_macrobench_corrupt_baseline_entry` 只覆蓋 metrics 的一種壞法
severity: minor
blocking: 否

引句:「data["entries"][key]["metrics"]["timeToInitialDisplayMs"] = {"median": 1000.0}」

失敗場景:
- 我把 `_macrobench_entry_ok` 的 sampled 檢查改成 `return True`,做成改壞版 `lumos-mut`。
- 基準檔刪掉 sampled 的 `P90`,`lumos-after` 印「基準檔讀不了,這次沒比」,改壞版卻印「比了 2 個情境」。
- S11 要求整份當讀不了,改壞版沒做到。
- 該測試只動 metrics,對這個改壞照綠。
- device 不是 dict、metrics 或 sampled 不是 dict 這幾條分支也沒測。
- 改壞版沒有噴例外,所以只算 minor。

歸因:未判定。測試是新加的,修前沒有對應測試可比。

## 已驗主張(同一案例證據)

### S11 / 新舊互讀(正常路徑仍成立)
- claim:修前版 `--update-baseline` 寫出的基準,修後版讀得回來,不會被新的形狀檢查誤判成壞檔。
- input:`lumos-before` 對 `governance/research/macrobench/2026-10-21-kds-emulator-benchmarkData.json` 跑 `--update-baseline`,產生 2 個情境的基準。
- expected:修後版正常比對。
- case_source:作者的 preserve 組 G2,加上我自己補的真結果檔。
- before:`lumos-before` 讀該基準印「比了 2 個情境,0 項變慢」。
- after:`lumos-after` 讀同一份基準印同樣的結果。
- comparison:相同,未誤判。

### S11 修復(metrics 缺 minimum/maximum)
- claim:基準缺欄時回 0 並印基準讀不了,更新時不蓋掉它。
- input:`t_macrobench_corrupt_baseline_entry` 的 `{"median": 1000.0}`。
- case_source:作者案例,我讀過程式路徑。
- before:修前缺欄會在 `outside = c["median"] > b["maximum"]` 噴 KeyError。這是看程式推得,沒有實際在修前版跑這個測試。
- after:修後 60 條測試全綠。
- comparison:這個案例已修,G1 和 G3 所述的案例沒蓋到。

### S12 修復(update 路徑)
- claim:重複情境不再說成「一個結果檔都沒讀成功」。
- input:`p2/out/a` 與 `p2/out/b` 放同一份結果檔。
- case_source:我自己造的案例。
- before:`lumos-before` 印「基準沒更新:這次一個結果檔都沒讀成功」。
- after:`lumos-after` 印「讀到的情境都重複出現在兩個以上的結果檔…」。
- comparison:update 路徑已修,比對路徑見 G2。

### G1 組 S5(負數與零基準)
- claim:新增的三個案例成立。
- input:-100→-95、-0.5→-0.2、基準 0 搭配 abs_tolerance 0.3。
- case_source:作者案例,我讀程式。
- before:修前五組舊案例全綠。
- after:修後同一個測試函式含新案例全綠。
- comparison:我從 `_macrobench_worse` 讀,負數基準用 `abs(base) * pct / 100`,零基準用 `abs_tolerance`,與測試期望一致。這一組我只讀了程式和測試,沒有另外實驗。

## 三問
1. 修復效果:S11 的 metrics 缺欄和 S12 的 update 路徑訊息有行為證據,且確實生效。S11 沒有覆蓋 P95/P99(G1),S12 沒有覆蓋比對路徑(G2)。
2. 相鄰路徑:修前版寫出的基準仍可讀;`entries` 為空 dict 時 `all()` 為真,視為可讀;測試改用 `_load_lumos_inproc()` 後 60 條全綠。
3. 新發現同一案例的前後結果:G1 和 G2 都是修前修後同結果(都有缺口,不是回歸);G3 未判定。

未驗範圍:NaN/Inf 的基準值、同一檔內重複 key、`results_dirs` 含符號連結或遞迴情況。

總結:最高等級為 major(G1 的 S11 漏洞是原有漏查,不是修補引入的回歸)。
