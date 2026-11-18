severity: minor

## k1 型錄 C-34 的判法欄仍寫「同 sbr.yml 的 value-pos」,實際規則已多排除分支位置
severity: minor
blocking: 否 措辭精度落差:照字面做不會出錯,只是三個月後的人會以為兩份規則判法相同。
引句:「`api.yml` `$R.let` 後接呼叫、回傳值有被用到(同 `sbr.yml` 的 value-pos)」
file: `skills/kotlin-idioms/checks-catalog.md:1701`
- 現況:`api.yml` 的 C-34 改用 `value-direct`,多排除了 `control_structure_body` 底下的分支。我在 87093835 用 `ast-grep scan` 跑了一份臨時檔:`when -> if (d) x.let{…}`(`a.kt` 第 4 行)不命中,`val a = when…`(第 2 行)與 `fun g2 = when…`(第 8 行)命中。可見 C-34 的「被用到」比 `sbr.yml` 窄。
- 預期:型錄的判法欄與計劃範圍 2 一致,寫「確定是值的位置」。
- 實際:型錄沒改,仍等同 `sbr.yml`。
- 歸因:未判定。修前 6cc9ad8c 的型錄同一行也是這句,這輪的 docs patch 沒碰它。這輪的修補(`value-direct`)讓落差更大,但 r1 加排除時就已經不一致。
- 驗證命令:`git -C /tmp/lumos-seat-work/code-選擇點第二批/合約-sonnet/repo show 6cc9ad8c:skills/kotlin-idioms/checks-catalog.md | grep -n "^| C-34"`
- 兩版輸出:修前的列文字與修後相同(型錄不在這輪 patch 內,我未逐字比對,只確認 patch 沒碰該檔)。

## k2 上線前實測筆記的 valid_under 釘在「2026-11-17 版」規則,規則已在 11-18 改過
severity: minor
blocking: 否 筆記的有效範圍描述過期,數字本身沒被推翻。
引句:「valid_under: ast-grep 0.51.2;第二批六列規則照 2026-11-17 版」
file: `docs/lumos-toolchain-knowledge/Verification/2026-11-17_選擇點第二批上線前實測.md:5`
- 現況:r2 修補在 87093835(2026-11-18)改了 `api.yml` 的 C-34、C-36、C-37 判法,命中集合變窄。這個提交是在 Verification 筆記之後的。
- 觸發條件:筆記的 `revalidate_when` 只列「加列、撤列」。規則窄化不會觸發重驗,所以上線門檻 a/b/c 的數字不會被重新確認。
- 缺口:門檻 a/b/c 的數字是用舊版 C-34 量的,新版沒有量過。
- 影響:變窄只會讓壞法數與輸出量降低,門檻方向安全。
- 歸因:未判定。我沒有重跑兩個真實專案的實測;在 87093835 工作樹上能確認的只有 `valid_under` 字面與規則現況不符。

## 其餘逐項核對:不影響或相符
- 計劃新增的 S6 預期值表列(else-if 鏈、`-1.coerceAtLeast(k)`)與 `choice-batch2.kt` 的 HIT/MISS 標記一致,也跟我自跑的 ast-grep 行為一致。
- 對照:樣本中 `if (c) go() else if (d) x.let` 為 MISS、`-1.coerceAtLeast(k)` 為 HIT、`-k` 為 HIT、`+2.5` 為 MISS。
- 鏡頭 2 與 3:RETIRE-IF 與 REVISIT 的日期 2027-01-17,跟 Verification「上線日 2026-11-17」及兩個月的算法對得上。
- 鏡頭 2 與 3:型錄〈統計〉寫「選擇點表:37 列」,「已撤列號:(無)」一行存在(`skills/kotlin-idioms/checks-catalog.md:1651` 與 `:1664`)。
- 鏡頭 2 與 3:`_row_key` 的 9 位上限與計劃 S8 描述無衝突。
- 鏡頭 3:這輪沒改任何 `★INVARIANT★` 行,綁定測試 `t_choice_samples_batch2`、`t_gov_stats_choice_by_row`、`t_choice_table_batch2`、`t_choice_table_missing` 在修後工作樹跑 `-k` 子集,各自通過(33、6、13、13)。
- 圖譜鏡頭:派工詞說鏡頭超時,我沒有補算,也沒有讀備份檔 `lens-r3.txt`。固定席逐條判未做,屬未驗範圍。
- 只判了文件改動與程式的對照,沒有逐 hunk 審程式。

## 三問
- ①原問題的修復效果:C-34 在 else-if、巢狀分支位置不再命中,`-1.coerceAtLeast(k)` 改為命中。
  - claim:這兩項修復成立。
  - input:臨時檔 `a.kt`(`when -> if (d) x.let{…}`)與 `choice-batch2.kt` 的對應列。
  - expected:`when -> if (d) x.let{…}` 不命中;`-1.coerceAtLeast(k)` 命中。
  - before:未跑(未開修前 worktree)。
  - after:第 4 行無 C-34 命中;樣本核對測試通過。
  - comparison:只有修後證據,修前行為未判定。
- ②相鄰路徑:`val a = when…`、`return x.let…`、`fun g2 = when…`、`val g = if (c) { x.let… }` 仍命中,沒有誤傷正常值位置。
- ③新發現的同一案例修前修後:k1、k2 都是文件字面問題,修前修後相同,未判定歸因,見各條。

最嚴重:minor;blocking 共 0 條
