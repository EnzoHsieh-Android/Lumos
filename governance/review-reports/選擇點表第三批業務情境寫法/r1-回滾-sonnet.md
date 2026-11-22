severity: major

## rb1 回退會讓綁定測試翻紅,而且〈回退〉沒寫要改測試或條款
severity: major
blocking: 是(照〈回退〉做完,推送前全套測試會紅,實作者得自己判斷改測試還是改回退步驟,改測試檔還要先簽名)

- spec 段落:〈驗收條款〉S5、S6 與〈回退〉第 1、2 項。
- 問題:S5、S6 的綁定測試讀的是真型錄、真規則、真樣本。S6 把「型錄不含 `coroutineScope`」寫成通過條件。〈回退〉第 2 項整批撤掉時卻要把 `coroutineScope`/`supervisorScope` 加回「不收」清單,兩邊字面互相矛盾。S5 寫死每條第三批規則都要命中,但〈回退〉要刪掉 `samples/choice-batch3.kt`。〈回退〉沒有一句說要調整 S5、S6 的測試或條款。
- 單列撤掉也一樣。只撤 `coroutineScope` 或 `supervisorScope` 其中一列時,「不收」清單怎麼寫,spec 沒講,S6 也跟著失效。
- 失敗場景:撤掉第三批後跑 pre-push。`skills/` 與 `configs/` 不算純文件,會跑全套。`t_choice_table_batch3` 與 `t_choice_samples_batch3` 就紅。
- 對照:第二批的測試把撤列設計進去了,表裡沒有的列號直接跳過。第三批的 S5、S6 沒有照這個寫法。
- 引句:「整批撤掉:第 1 項對第三批每一列各做一次,刪掉 `samples/choice-batch3.kt`」
- 引句:「每條第三批規則 應 命中該命中的、不命中不該命中的」
- 佐證:file: `scripts/test_lumos.py:146516`(第二批 S6 測試,有 `if rid not in have: continue`)
- 佐證:file: `scripts/lumos:65827`(`_docs_only_file`:`skills/` 不在純文件白名單,走全套)

## rb2 整批撤掉漏了第二批〈回退〉有寫的善後項
severity: minor
blocking: 否(漏的是文件與註記,不會讓系統壞掉,但下一個 session 會看到沒有理由的狀態)

- spec 段落:〈回退〉第 2 項、〈範圍〉第 6 項。
- 問題:第二批〈回退〉第 2 項明列要改 Systems/kotlin規則包 的 `about_code` 與那條 WHY 行,第 1 項還要在說明段補撤列原因與日期。第三批的第 2 項只說刪樣本檔、加回「不收」,這幾件事都沒提。
- 失敗場景:整批撤掉後,`about_code` 還列著已刪的 `samples/choice-batch3.kt`。WHY 行還寫著「翻案 `coroutineScope`/`supervisorScope`」。「不收」清單加回這兩個字,卻沒有撤列理由與日期,下一個 session 可能再次提議翻案。
- 引句:「Systems/kotlin規則包 `about_code` 加 `samples/choice-batch3.kt`」
- 佐證:file: `docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md:195`(第二批整批撤掉的善後項)
- 佐證:file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:34`(`about_code` 現已列 `choice-batch2.kt`)

## rb3 撤列時已記的判定會外溢到同一行的別列,〈回退〉第 3 項只用「同第二批」帶過
severity: minor
blocking: 否(沿用第一版的「以行為單位」取捨,不會壞系統;缺的是提醒與人工重看步驟)

- spec 段落:〈回退〉第 3 項、〈實務隱患〉「已排除:不可逆」。
- 問題:外溢的不只放行。`_choice_disposition` 對 killed 與 waived 都當有效處置,對 survived 只要守的測試雜湊沒變就直接帶過去。撤列觸發條件是「等價」放行偏多。同一行 `x.firstOrNull { … } ?: d` 的放行是針對 `firstOrNull → first` 判成「等價」,撤列後該行改挑第二批的 `?:` → `!!`,那筆放行直接套上去,沒人檢視過。第二批〈回退〉第 3 項明寫會外溢,並說「要不要在撤列提交時把這些行列出來重看,由人決定」。第三批只留一句「照第一版續用」,這個提醒與步驟都沒有,而第三批的重疊行(`firstOrNull` 與 `?:`)比第二批更多。
- 引句:「已記的處置照第一版以 (檔, 行指紋) 為單位續用(同第二批〈回退〉第 3 項)。」
- 佐證:file: `scripts/lumos:78045`(`_choice_disposition`:「waived」與「killed」直接算有效處置)
- 佐證:file: `scripts/lumos:78305`(`_choice_kill_pick`:waived、killed 不重跑;survived 且守的測試雜湊沒變就帶過去)
- 佐證:file: `docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md:196`

## rb4 RETIRE-IF 寫「同第二批」,卻漏了「不適用」的算法
severity: minor
blocking: 否(只影響撤列的判準口徑,不影響系統運作)

- spec 段落:RETIRE-IF。
- 問題:第二批寫「不適用」算分母、不算分子。第三批改寫後少了這句,放行標籤卻有三種:`_CHOICE_WAIVE_LABELS = ("等價", "不是需求", "不適用")`。
- 失敗場景:某列有 5 筆放行,3 筆「等價」、2 筆「不適用」。「不適用」算分母時是 60%,不撤。「不適用」排除時是 100%,撤。第三批這種列(`firstOrNull` → `first` 遇到 `allWarningsAsErrors`)正好容易出現「不適用」。
- 引句:「RETIRE-IF: 同第二批:上線日(寫進第三批的 Verification)起滿兩個月」
- 佐證:file: `scripts/lumos:77987`
- 佐證:file: `docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md:32`

## 其餘各項已查,無 finding

- **型錄撤了、規則沒撤(或反過來)會不會擋所有 Kotlin 推送**:會,而且 spec 的宣稱成立。
  - `choice_tables` 預設帶 `rules_dir`,`_choice_rules_match` 兩個方向都報。
  - 報了就讓 `_choice_tables` 回「表壞」。
  - `_choice_push_scan` 在有 Kotlin 改動時擋下並記 blocked。
  - 型錄與規則都從同一個工具鏈根目錄讀,不會兩邊版本不一致。
  - toolchain 本身的 pre-push 因為走全套,會先抓到。
- **已撤列號**:型錄列與規則 id 都擋,格式有守(前導零、全形都擋)。整批撤掉時,`已撤列號:` 要列全部號碼,第二批機制可直接用。
- **`gov --stats` 依列號**:讀帳不讀型錄,撤掉的列號照印。預設窗口 90 天,蓋得住兩個月。
- **處置鍵**:(檔, 行指紋) 與型錄雜湊、列號無關。`_choice_catalog_sha` 只記備查,不會讓舊處置作廢。
- **三處擴充整批撤掉後走不到的宣稱**:現有 `api.yml` 的 `.方法名` 列都用 `$R` 沒用 `$A`。現有帶 import 的列都是方法名錨點,沒有「運算元起始加 import」的列。宣稱成立。
- **決策表互指**:決策表各列沒有寫 `C-` 列號,撤列不會留下懸空引用。
- **樣本目錄**:`_stack_changed_ok` 排除 `configs/ast-grep/*/samples/*.kt`,改樣本不會觸發選擇點那一道。
- **`check.py --catalog-only` 沒帶 `--sg`**:會退去找 PATH 上的 ast-grep,找不到只印「沒檢查到」。撤列的半套狀態(列、規則、標記)不靠 ast-grep 也查得到,不另列。
- **既有 `_choice_also` 呼叫與測試**:測試沒有直接呼叫 `_choice_also`、`_choice_api_edits`,只呼叫 `_choice_anchor`(簽名不變),擴充不會讓既有測試翻紅。

總結:最高嚴重度 major,blocking 共 1 條
