severity: minor

# 第 3 輪通才席審查(固定提交 1bb9609b)

我讀了 r3-code.patch 全部 hunk 和 r3-repair-review.patch,並追了呼叫者。審材外的檔我用 `git show 1bb9609b:scripts/lumos` 讀。我在臨時 clone 跑了 `-k arch_target_graduate`(26 通過)和 `-k arch_target_legacy`(9 通過)。我還做了一次變異檢查,見 finding 1。

## Finding 1:`_arch_legacy_check_lines` 的後備分支沒有任何測試守住
severity: minor
blocking: 否

引句:「pf_targets = _arch_target_split(_arch_target_changed_files(root, base, head), rules)」

- **失敗情境**:`pf_data` 沒有 `arch_alignment.targets` 時,會走這條後備路徑。我把它改成 `pf_targets = {}` 再跑 `-k arch_target_graduate_check_note`,結果還是 8 通過、0 失敗。
- **影響**:這條後備路徑改壞了,測試不會紅。
- **為什麼只列 minor**:這條路徑只在「有畢業的檔、卻沒有分級結果」時才走。正常流程下,畢業的改動檔一定會出現在 pitfalls 輸出的 `targets` 裡,所以後備路徑多半不會觸發。
- 歸因:有證據的修復新增(未判定是否回歸)。
- 查證命令:在 `scripts/lumos` 把該行替換成 `pf_targets = {}`,執行 `python3.14 scripts/test_lumos.py -k arch_target_graduate_check_note`。結果是修補後版 8 通過、變異版也 8 通過。修補前版沒有這條分支,所以沒有可比的結果。

## 八個角度的結論

1. **逐行**:沒有 major 以上的問題。
2. **被刪掉的行為(拿掉 `not h_warns`)**:沒有行為差異。
   - `_arch_targets_config` 只要有警告,回傳的規則一律是空清單(見 `scripts/lumos:57311-57335`)。
   - 呼叫端 `_arch_legacy_apply` 只在 `targets` 非空時才進來,`_arch_legacy_check_lines` 要 `rules` 非空才往下走,所以兩邊的 `rules` 都不是空的。
   - 在這個前提下,`h_rules == rules` 已經涵蓋「頂端版有警告」的情況:頂端有警告時規則是空,不會等於非空的 `rules`。
   - 這個結論也成立在 git 讀失敗時(`[]`,同樣不等於非空規則)。
3. **跨檔追蹤呼叫者(`_arch_legacy_check_lines` 改簽名)**:
   - 全檔只有 `scripts/lumos:57726` 一個呼叫者,已同步傳入 `pf_data`。
   - `rng`、`trusted`、`head` 與 pitfalls 分級用的是同一套函式(`_diff_range_ends`、`_trusted_decl_ref`)。
   - `disp_data` 與 `disp_range` 是成對決定的,所以 `pf_data` 對應的就是同一個範圍。
4. **重用**:畢業判定只有 `_arch_legacy_graduation` 一份,推送前分級、兩條派工鏡頭與說明行都走它。
5. **簡化、效率**:
   - 說明行改用已算好的目標檔,省掉一次 `git diff`。
   - doctor 的 NFC 轉換移到函式內,而且只在清單存在時才做,同樣沒有增加成本。
6. **修的深度**:`H2`(清單混非字串元素)與 NFD 的 doctor 測試都能對準各自的問題。`patch.object` 取代直接賦值,也消除了先前的模組污染。
7. **慣例**:沒有發現違反。

## 修補鏡頭三問

1. **原問題的修復效果,行為證據是什麼?**
   - doctor:`摘要只有一行`、`沒有宣告也印清單摘要`、`git 列出 NFD…不算已不存在` 三項都通過。
   - 說明行:`L` 與 `A2` 都在 `-k arch_target_graduate` 的 26 通過之內。
   - 清單形狀:`H2` 通過。
   - 以上都是修補後版的結果。修補前版我沒有另外跑,所以修補前的行為證據是未判定。
2. **修補處的正常、錯誤與相鄰路徑是否仍成立?**
   - 成立。
   - 正常:`A`、`A2`、`E`、`B` 以及 `K` 的相關測試通過。
   - 錯誤:`git 失敗`、`讀不懂`、`算不出` 的 doctor 測試通過。
   - 相鄰:派工鏡頭的 `A`、`B` 與設計審路徑的 `S11` 測試通過。
3. **新發現的同一案例,修前與修後各是什麼結果?**
   - 後備分支未被守住這件事,修前版根本沒有這條分支。
   - 修後版的變異檢查見 finding 1,是變異後仍 8 通過。

## 未驗範圍

- 沒有在真實 macOS NFD 檔名的 git 環境下端到端跑 doctor,只有函式層測試。
- 沒有模擬大型 repo 的效能和記憶體。
- `pf_data` 缺少 `arch_alignment` 但實際有畢業檔的組合,我沒有造出來。我認為正常流程到不了,但這是推論,沒有重現。

## 固定席逐條判定

- **`Issues/code-loop守衛main-direct盲區`**:不影響。這份 diff 沒碰 main-direct 守衛,只動架構對齊與舊檔清單的函式。
- **`Systems/lumos-cli-read`(★INVARIANT★ search 預設排除 superseded)**:不影響。沒有碰 search 的濾網。
- **`Systems/pitfalls-code-loop` ★RISK★**:不影響。`_arch_alignment_hints` 的輸出形狀沒變,只讀它的 `targets` 欄位。
- **`Systems/arch-alignment-lens`**:不影響。`arch-alignment-lens.md` 文字與修補後的行為一致,畢業只開宣告不動這一個口。
- **`Systems/design-loop` ★INVARIANT★**(處置閘第五步):不影響。設計審路徑傳 `head=None`,不畢業,此路徑沒有變動。
- **`Systems/測試假綠形態` ★INVARIANT★**(翻紅釘要有前置斷言):不影響。新測試的前置斷言和翻紅釘兩者都有。
- **`Systems/guard-kill` ★INVARIANT★**(rc 優先序、`--json` 純淨):不影響。沒有碰 guard kill 的 rc 優先序或 `--json` 輸出。
- **`Systems/reversibility-governance-ledger` ★RISK★**:不影響。沒有碰到可逆性治理帳本相關的程式。
- **其餘「超出上限」的節點**:只列名,不逐條判定。

最嚴重等級為 minor
