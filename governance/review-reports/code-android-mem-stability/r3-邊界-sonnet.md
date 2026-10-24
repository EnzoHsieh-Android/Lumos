severity: minor

我用修前版(44d93aba)和修後版(f0d41453)的 `scripts/lumos` 各取一份。我把它們放在 `/tmp/lumos-seat-work/code-android-mem-stability/邊界-sonnet/{old,new}/lumos`,用 python3.14 實跑。測試資料、假專案和腳本都在同一個目錄下,沒碰 adb 和裝置,也沒動 android-mem-stability 工作樹。

三條 finding 都是 minor,沒有 blocker 或 major。

## findings

截長 500 字會吞掉「類別名未還原」警語,類別清單也被砍掉

severity: minor
blocking: 否
引句:「_esc_clean(_macrobench_stab_detail(r), 500)」
- 歸因:有證據的修復回歸。
- 失敗場景:`java_growth` 的明細是「所有增長類別串起來,最後才接警語」。stability.json 的 `class_names` 是 `"raw"`(沒給 R8 mapping),又有 40 個類別各多 50 個。
- 預期:仍看得到警語「排除清單擋不到被改名的函式庫類別」。
- 實際:`_esc_clean` 截到 500 字,警語被砍光,類別清單只剩前 9 個,也沒寫總共幾個。
- 兩版對照:
  - 命令:`python3.14 <版>/lumos macrobench --repo repoA --stability grow.json`,工作目錄 `/tmp/lumos-seat-work/code-android-mem-stability/邊界-sonnet`,兩版退出碼都是 0。
  - 修前:輸出含「類別名未還原」1 次,列出 40 個類別。
  - 修後:輸出含「類別名未還原」0 次,列出 9 個類別,結尾是「…」。
- `strictmode` 也有同樣問題。120 筆 `DiskReadViolation` 會被截斷,看不出總數。
- 建議:警語放在清單前面,或截斷時印「共 N 項」。

`--json` 遇到孤立代理字元(lone surrogate)會崩潰,修補只補了文字路徑

severity: minor
blocking: 否
引句:「print(json.dumps(dict(res, configured=True, files=n_files), ensure_ascii=False))」
- 歸因:有證據的原有漏查。兩版都崩,修補只在文字輸出加了 `_esc_clean`。
- 失敗場景:stability.json 裡 `unreachable.reason` 是 `"bad \ud800 x"`,或 heap 的類別名含 `\ud800`,再加 `--json`。
- 預期:印出一行合法 JSON。
- 實際:`UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800'`,印出 traceback,沒有 JSON。
- 兩版對照:
  - 命令:`python3.14 <版>/lumos macrobench --repo repoA --stability sur2.json --json`(類別名版本是 `sur3.json`),兩版相同。
  - 同一份檔不加 `--json` 時,文字路徑正常,表示 `_esc_clean` 有效。
- 另一處同形:沒有結果目錄的分支也有一行 `print(json.dumps(dict(res, configured=cfg is not None), ensure_ascii=False))`。

結果檔的數字只擋 -1 和非有限數,其他負數與 0 都當有效值

severity: minor
blocking: 否
引句:「return None if not _macrobench_num(v) or v == -1 else v」
- 歸因:有證據的原有漏查。
- 失敗場景:`cycle_trace.frozen_frames` 是 -5,或 `max_main_block_ms` 是 -5。
- 預期:跟 -1 一樣列成「沒判」。
- 實際:`frozen` 判成通過。`unreachable` 的 `bytes` 和 `allocations` 為負數時也被收下,算出的差值不可靠。
- 驗證:這是用 `_macrobench_judge_stability` 對 `good.json` 逐欄改值得到的結果(`fz3.py`)。
- 現實風險:正常收集腳本用 COUNT 與 MAX,不會產生負值,所以只在檔案被手改或損毀時才發生。
- 順帶:`heap.classes_seen` 的數字沒有跟 before/after 實際內容對照。`before` 是 `{}` 而 `classes_seen.before` 是 3 時,仍判成有效。

## 邊界逐項結果(兩版都跑過,無例外)

| 項目 | 結果 |
|---|---|
| stability 設定段的 `warmup`、`cycles` | 輸入 0、-1、1.5、true/false、字串、空字串、空清單、null、NaN、Infinity、`{}` 都擋。10^19 和 100000 修前會收,修後擋。 |
| 輪數上限的兩側 | 設定檢查和 `java_growth` 判定都是 10000 收、10001 不收。結果檔 `cycles` 為 10001 或 10^12 會列成跳過,修前 10^12 會判通過,這點修補確實有效。 |
| stability 設定段其他欄位 | `category` 非 app/game、`max_record_s` 非 1 到 86400、`strictmode` 非布林、`adb_serial` 與 `mapping` 空字串都擋。`test_data` 為 null 等於沒寫;多餘欄位不擋,因為這段沒有未知欄位檢查。 |
| 門檻 check 條目 | 各欄位給 0、負數、布林、字串、`[]`、`{}`、null、10^400、NaN、Infinity、混型清單都擋或接受得合理。多餘欄位擋。`decided_at` 的 `2026-10-24\n`、全形數字、`2026-1-1` 都擋,`DATE_RE` 放行的結尾換行會被 `_rule_date` 擋下。 |
| 構造整份非法輸入 | 沒有例外,全部變成「沒判」。 |
| 輪數相關的放寬 | `min_per_cycle` 用 1e308 乘 10000 會變 inf,`java_growth` 恆判通過。這是人裁的門檻值,我不列為 finding,只記錄。 |
| vitals 分級邊界 | 3199 跳過,3200 到 4799 為 2.00 GB,4800 為 2.25 GB,18431 為 4.25 GB,18432 跳過。 |
| 「沒有 check 條目」提示(文字) | 有結果目錄加舊條目加 `--stability` 會印提示。沒有門檻檔也會印。不給 `--stability` 不印。 |
| 「沒有 check 條目」提示(--json) | 不印提示,stdout 維持純 JSON,符合預期。JSON 裡沒有欄位標示「沒東西可判」,消費者只能看到三個清單全空,這是設計上的缺口,不構成 bug。 |
| `--check-config` | 設定與門檻檔合格時回 0,兩版相同。 |

「讀不到不准當成沒事」這條統一規則有沒有漏網:`exits.new` 和 `strictmode.violations` 的元素型別、`unreachable.before/after` 的形狀、`cycles` 範圍,三處都補齊了,沒有例外。漏網只剩上面第三條的非 -1 負數。

## 三問回答

1. **原問題的修復效果**:
   - 輪數上限(設定檢查和 `java_growth`)。證據:10001 和 10^12 從修前的通過或收下變成修後的跳過或擋下。
   - `exits` 與 `strictmode` 的混型元素。
   - `unreachable` 的形狀。
   - 「沒有 check 條目」提示。證據:有 `--stability` 但門檻檔只有舊條目時,修前不印,修後印。
   - 以上我只對輪數上限和提示做了兩版同案對照;`exits`、`strictmode`、`unreachable` 的形狀修補只在修後版用 `fz3.py` 逐欄驗過,沒有兩版對照,所以這三項未判定。
2. **修補處的正常、錯誤、相鄰路徑**:
   - 正常路徑仍成立:`good.json` 加完整 check 條目,修後版 `native_unreachable`、`java_growth`、`peak_vitals`、`exits`、`strictmode`、`frozen` 都判通過,`instances` 因測試資料設計而判沒達。
   - 修補引入的新問題只有第一條,`_esc_clean` 500 截斷。
   - 相鄰路徑沒修到的是第二條 JSON 輸出路徑。
3. **新發現的同一案例兩版結果**:第一條修前保留警語、修後被截掉(回歸)。第二條和第三條兩版相同(原有漏查)。

**未驗範圍**:收集腳本本身(`android-stability-collect.sh`)和 `--update-baseline` 對真實結果檔的路徑沒跑;沒做大量輸入的效能檢查,只確認 40 個類別和 120 筆違規的輸出。

臨時目錄 `/tmp/lumos-seat-work/code-android-mem-stability/邊界-sonnet/` 還在,內含兩版程式、`fz*.py`、輸出檔和假專案 `repoA`,等編排者收貨後依規則刪除。

最嚴重 severity:minor;blocking 共 0 條。
