severity: minor

## 結論(白話)
上輪的兩個修補都有效,沒有引入新問題。基準檔現在壞得再怪,也只會印「讀不了」而不會噴例外。重複情境的文字輸出也標對了。我只找到一條不阻擋的 minor,而且是修補前就有的漏查。

## H1:結果檔或基準檔裡出現 NaN,退步會被靜默吃掉
severity: minor
blocking: 否

引句:「return isinstance(v, (int, float)) and not isinstance(v, bool)」

- 位置:`scripts/lumos:8556`(`_secev_num`)。macrobench 的結果檔讀取與基準檔驗證都用它,它接受 Python `json` 讀成 float 的 NaN 與 Infinity。
- 失敗場景:結果檔的 `frameDurationCpuMs.P50` 是 `NaN`。`_macrobench_worse` 算出的 `delta` 是 NaN,`delta > tol` 恆為假,所以不報變慢。
- 若再跑 `--update-baseline`,NaN 會寫進基準,之後該指標永遠比不出退步。
- 另一個副作用:`--json` 會印出 `Infinity`,這不是合法 JSON。
- 歸因:有證據的原有漏查。修前修後輸出相同(見下方三問第 3 題)。
- 案例 claim:數值驗證應擋掉非有限數。
  - input:KDS 真結果檔,`P50` 改成 NaN、`P90` 改成 Infinity。
  - expected:NaN 當成壞檔,或至少要報出來。
  - case_source:我自己補的案例。
  - before:`P90 153.1 → inf` 列為變慢;NaN 的 P50 沒被報;`--json` 印出 `"current": Infinity`。
  - after:輸出與修前完全一致。
  - comparison:修補前後無差異,不是回歸。
- 這在真實 Macrobenchmark 結果裡極少見,所以只標 minor。

## 三問
1. **原問題的修復效果(repair)**
   - **基準檔壞形狀(G1/G3)**:同一份壞基準,修前跑 `-k macrobench` 的對照,修後逐例核對。

     | 輸入 | 修前 | 修後 |
     |---|---|---|
     | P99 為 null | rc=1,`TypeError` | rc0,印「基準檔讀不了」 |
     | 滑動類 P95 為字串 | rc0,比了 2 個情境,壞值被當成沒事 | rc0,印「基準檔讀不了」 |
     | 滑動類多出 `P75` 鍵 | rc0,照常比 | rc0,印「基準檔讀不了」 |

     「多出 `P75` 鍵」那一例,條款 S11 與修補說明的描述有出入:數字型的多餘鍵本身無害,是修補把驗證收得比必要的更嚴。這只影響手改的基準檔,測試也沒涵蓋這一例,我不當成 finding。
   - **重複情境(G2)**:我自己造的案例是同一情境出現在兩個結果檔。修後文字輸出標「重複情境,沒收」。測試 `t_macrobench_duplicate_scenario` 新增的兩條斷言對應這個行為。
   - **指令總數(B1)**:`-k docs_command_count` 通過,文件寫 94,與 argparse 一致。
2. **修補處的相鄰路徑(preserve)**
   - 修後 `python3.14 scripts/test_lumos.py -k macrobench`:84 passed、0 failed(含 S6 的 `t_macrobench_update_baseline_skips_failed`)。
   - 修前沒有跑 `-k macrobench`,綁定檔只寫了「60 條全綠」,這是作者自述,我沒有獨立重跑,留未判定。
   - 相鄰輸入都沒變:`entries` 為空、`entries` 是陣列、`device` 缺 `model`,修前修後相同。
   - 「新舊互讀」:修前版本寫出的基準只含 P50–P99 與三統計值,修後可讀回,沒有相容問題。
   - 文件的 `-k docs` 全套在我手上超時,沒等到結果,只確認了指令總數那一條,其餘留未判定。
3. **新發現的同一案例修前與修後**:只有 H1,結果如上,兩版相同,歸因為原有漏查。

## 已驗主張的證據
- **S12(重複情境,文字輸出)**:實作與測試都照條款文字。
  - 實作:`_macrobench_print` 對 `kind == "duplicate"` 用「重複情境,沒收」標籤。
  - 測試:斷言「重複」存在、「讀不了」不存在。
- **S11(基準檔壞形狀)**:實作與測試都照條款文字。
  - 實作:`_macrobench_entry_ok` 比對會用到的每個值都驗過,整份基準壞了就不比、`--update-baseline` 也不覆寫。
  - 測試:涵蓋八種壞法,各自檢查 rc0、無 traceback、印基準讀不了、更新不蓋掉。
- **文件鏡頭**:reference.md、INDEX.md、04-自檢與健康.md、ARCHITECTURE.md 寫的旗標(`--repo`、`--json`、`--update-baseline`)、預設值(`tolerance_pct` 10、`abs_tolerance` 1)與 rc(退步也回 0、設定壞回 2)都與程式一致。照文件做不會做出錯的操作。
- **測試品質**:`t_macrobench_corrupt_baseline_entry` 讓現況也帶滑動類指標,壞欄位真的會被拿去比,所以能抓到「比對時噴例外」。小瑕疵:`good` 變數第一次賦值沒被用到,只是死碼,不影響判斷。
- **表態記錄**:各題對這份 diff 都屬實(同步程式,無 async)。

## 未驗範圍
- 同一個檔案內有兩筆相同情境鍵時,後者靜默覆蓋前者,不報重複。條款 S12 只講「兩個以上的結果檔」,我也想不出 Macrobenchmark 真會這樣輸出,所以沒標。
- `results_dirs` 用絕對路徑或帶 `..` 的路徑、符號連結迴圈,都沒測。
- 圖譜鏡頭:固定席節點(`lumos-cli-read`、`測試假綠形態`、`design-loop`、`guard-kill`、`bound-tests-gate`、`lumos-cli-lifecycle`)所宣稱的合約,這份只新增 `macrobench` 子指令與其測試,我看不出會動到它們。我沒有逐條重跑它們的綁定測試。

總結:最高等級為 minor
