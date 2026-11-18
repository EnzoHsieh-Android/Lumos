severity: major

## g1 C-34 在 else-if 鏈與巢狀 if(陳述位置)裡仍收回傳值沒人用的 `.let`

severity: major
blocking: 是 判準:r1 c1 的修補聲稱「不確定就不收」,但漏掉一個常見寫法。測試樣本沒有這個形狀,所以測試抓不住。計劃範圍 2「只收回傳值被用到的」這條必要行為會被破壞。

- 輸入:作為陳述寫的 `if (a) {…} else if (b) { x.let { show(it) } }`。這是很常見的 Kotlin 寫法。
- 路徑:`api.yml` 的 C-34 `value-used` 用 `inside: {kind: control_structure_body, inside: {kind: if_expression, matches: value-pos}}` 判斷。
- 壞在哪:`else if` 裡的內層 if_expression,它的父節點是外層 if 的 `control_structure_body`,不是 `statements`。所以 `value-pos` 第一支 `not: {inside: {kind: statements}}` 判它為真,也就是被誤判成「值被拿去用」。外層 if 其實是陳述,值沒人用。
- 預期:不命中,因為 `let`→`also` 在回傳值沒人用時必然等價。
- 實際:命中。這會產生一個等價變異,只能靠放行處理,而這正是第二批要避免的情況。
- 其他同族形狀:
  - 無大括號的 `if (a) if (b) x.let { show(it) } else 2` 也命中。
  - `if (a) x.let{..} else if (b) x.let{..}` 的第二個 `.let` 也命中。
- 樣本 `choice-batch2.kt` 只放了單層 if、for、while、when,沒有 else-if 鏈或巢狀 if 的 MISS 標記,所以 `t_choice_samples_batch2` 全綠。
- 重現:
  - 檔案內容(`t2.kt`):
    ```
    fun f(a: Boolean, b: Boolean, x: Int) {
        if (a) {
            go()
        } else if (b) {
            x.let { show(it) }
        }
    }
    ```
  - 指令:`ast-grep scan --rule configs/ast-grep/kotlin-choice/rules-choice/api.yml --json=compact t2.kt`
  - 修後(6cc9ad8c):`C-34 5`,即第 5 行命中。
  - 修前(eebb8459):`C-34 5`,結果相同。
- 巢狀無大括號的形狀(`t.kt`)也量過。修前第 3 行命中 2 次,修後命中 1 次,第 2 行命中。這代表 r1 c1 的修補只收掉一部分,沒有收掉這一類。
- 歸因:有證據的原有漏查。修前修後都命中,不是這次修補造成的;但修補聲稱已收斂的範圍沒有涵蓋它。
- 修法:`value-pos` 不該只看「不在 statements 裡」。if 在 control_structure_body 內時,要遞迴判斷外層 if 是否本身是值。

引句:「所以 value-used 另外排除沒大括號的 if/for/while/when 分支(control_structure_body 的直接子節點,只有 if/when 本身當值用時才算;」
file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml`(C-34 的 `value-used` 規則,`inside: {kind: control_structure_body, inside: {kind: if_expression, matches: value-pos}}` 那兩行)

## 固定席逐條判與三問

- 固定席節點判定(各席資料裡 impact 列出的 kotlin規則包、bound-tests-gate、guard-kill、lumos-cli-lifecycle、測試假綠形態、lumos-cli-read):
  - 這些是 ★INVARIANT★ 或家節點,綁的測試與這次改動(規則檔、check.py 的撤列號判讀、gov 統計的依列號段)無直接牽連。
  - 我沒有跑這些綁定測試,所以只能判「推測不影響」,不能算已驗。
  - kotlin規則包是這批 check.py 與 api.yml 的家。diff 裡的筆記本體不在程式 patch 內,我沒核對有沒有同步寫回,**未判定**。
- residual-ask 殘留段:鏡頭自己說算不出來。程式 patch 沒有動殘留索引或問答編號,我判不影響,但沒法逐條核對治理帳,**未判定**。
- 三問:
  1. 原問題的修復效果,以下是我實際驗過的:
     - 無大括號分支的 `.let`、`-1`/`'c'` 字面值:樣本測試 `t_choice_samples_batch2` 25 個全過。
     - 時區比較與全形冒號:`t_gov_stats_choice_by_row` 5 個全過、`t_choice_table_batch2` 12 個全過。
     - 其中只有 else-if 這條我有兩版對照證據(見 g1)。其餘各項只有修後通過,沒有修前結果,所以只能說「修後綠」,不能說已證明修好。
  2. 修補處的相鄰路徑:else-if 鏈(g1)仍壞。`val z = if (c) x.let{..} else 0` 與 `val r = if (a) { x.let{..} } else 0` 仍正確命中,我在 t.kt 驗過。
  3. 新發現的同一案例:修前、修後都命中,不是修補造成的回歸。
- 沒驗的範圍:
  - G5 巢狀 300 層與 1MB 輸出量線性成長,我沒跑。
  - NUL 的中文字 byte 位置,我沒跑。
  - 引數錨點的右括號行,我沒跑。
  - 其餘 test_lumos 測試我沒跑,只跑了上面三組。

最嚴重:major;blocking 共 1 條
