severity: clean

我讀了 patch 裡 `scripts/lumos` 的全部改動,涵蓋 `_nogo_skip_lines`、`_door_judge`、`_door_rule_fingerprint`、`_clause_block_sha`、`_spec_gate_record`、`_spec_gate_push_stale`、`_spec_gate_print_door` 和 doctor 的前 30 份計數。也對照 `--door-rule` 的輸出路徑。工作樹跑了 `-k door`(21 個)、`-k spec_gate`(166 個)、`-k nogo`(63 個)、`-k small_change`(15 個),全部通過。我沒有另外造最壞輸入實測。

各項回歸檢查如下,都已讀,無 finding:

- **舊留痕不會變過期:** `_clause_block_sha` 在 `nogo_skipped` 為空時,算出來的指紋跟改動前完全一樣。舊的風險低留痕在推送前重判,不會因為這次改動變過期。
- **不會把原本判高的計劃判低:** 沒有「不做」清單的計劃,判定結果跟改動前相同。沒有「不做」節的既有計劃不會被改判。
- **doctor 前 30 份歸零是照計劃裁定的行為:** `_DOOR_RULE_VERSION` 從 1 升到 2,doctor 的前 30 份改成只數 `door_rule` 等於現行版本的留痕。這會讓前 30 份從零重數,是照計劃裁定做的。blocker 與 push-gate-unreviewed 兩項仍看全部,沒有被這個篩選弄丟。
- **版本檢查與指紋的取捨:** `inputs_sha` 目前只寫進留痕,沒有其他地方讀它。`inspect.getsource` 取不到原始碼時,退回位元組碼的做法只影響凍結打包的情況。
- **新版留痕的提示:** 推送前遇到版本比本機新的留痕會多一段「先更新 lumos」的提示,判定結果不變。
- **`--door-rule` 輸出格式沒變:** 仍是 `door_rule=… inputs_sha=…` 兩欄。

小備註:放在 `## 不做` 清單裡的 [S] 條款行,即使含危險詞也會被跳過。這是計劃明講接受的「精準不放寬」取捨,我不算 finding。

最高等級 clean,blocking 0 條。
