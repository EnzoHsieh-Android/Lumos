severity: minor

## F1 同編號 `[S1]` 定義兩次時，第一條掛 `[manual:]` 且下一層寫了撤除，修後不再被列
severity: minor
blocking: 否
引句:「if r.get("state") == "manual" and not all(v.startswith("已撤除") for v in r.get("manual") or [])」
佐證: file: `scripts/lumos:7218` — `clause_bindings` 遇到同編號兩行都在行首定義時，回的 row 是 `state:"duplicate"`、`manual:[]`。
佐證: file: `scripts/lumos:31976` — `_ns_test_ref_lines` 的條款集合只看 `r.get("defined")`，duplicate 的定義行照樣算條款，所以 `[test:]` 那條路會列。
失敗場景：輸入是計劃檔裡 `- [S1] 當 x 時應 y [manual:開頁面目測一次]`，下一層 `  - 裁定:撤除`，檔案後面又有一行 `- [S1] 當 z 時應 w [manual:另一個說明喔]`。
- 走到 `_ns_tr_manual_clauses` 的過濾那行。
- `state` 是 `duplicate`，不等於 `manual`，第一條被濾掉，S20 不列。
- 同形狀改掛 `[test:test_alive]` 時，`[test:]` 路徑會列出該行。

同一份計劃的兩種標記因此口徑不一，S20 這張網漏了一條撤除候選。重複定義本身在處置閘與 spec-trace 會被擋，所以影響有限，但 S20 是散文撤除候選的唯一網。

歸因：有證據的修復回歸。以 /tmp 臨時 clone 跑同一支腳本 `/tmp/lumos-seat-work/code-撤除候選也看manual條款/正確性r2-sonnet/exp.py` 的 `dup_manual` 案例：
- 修前 069d6c64：`['Projects/P_計劃.md:8  條款仍掛 [manual:],下一層寫了撤除']`。
- 修後 280085c9：`[]`。
- 對照 `dup_test`，修前與修後都列出。
- 成因是 r1 改成「直接取 `clause_bindings` 的 state=manual」，duplicate 與 shadowed 兩種 state 因此漏掉。

## 其餘邊界走查（無 finding）
以下輸入都跑過，結果在修後版本，與 `[test:]` 路徑的行為一致，或是正確判定：
- **定義行在檔尾**：不列（沒有下一層），正確。
- **CRLF 換行**：列出。
- **標題式條款** `### [S1] …`：列出。
- **同行兩個 `[manual:]`，其中一個是 `已撤除,見 X`**：仍列出（`all(...)` 判定），合理。
- **全形逗號的 `[manual:已撤除，見 X]`**：不列，正確。
- **`[manual:]` 包在反引號裡**：不列，正確。
- **子行在圍欄內寫撤除、表格列式條款**：結果與 `[test:]` 路徑共用 `_ns_tr_sub_says_retire`，行為相同，不算新洞。

# 三問
1. **原問題（只掛 `[manual:]` 的條款被漏）的修復效果有證據嗎？** 有。
   - 命令：`python3.14 scripts/test_lumos.py -k doctor_s20`（修後 clone）。
   - 結果：`36 passed, 0 failed`，含 ①–⑧。
   - 這只證明案例通過，不單獨證明因果。
2. **修補處的正常、錯誤與相鄰路徑是否仍成立？** 大致成立，一處例外。
   - repair 案例：⑦ 太短的 `[manual:]` 不列，⑧ 同行 `[test:]` 加 `[manual:]` 只列一次。兩者在修後版本都有行為證據：測試通過，且 `[test:test_alive] [manual:…]` 同行只列 `[test:]` 一條。
   - preserve 案例：①–⑥ 與既有 `t_doctor_s20_prose_retire_*` 在修後全綠。
   - 例外是 F1，重複定義的 `[manual:]` 條款在修前會列、修後不列。
   - ⑦ 與 ⑧ 缺修前對照：修前版本不含這兩格，留未判定。
3. **新發現同一案例在修前、修後各是什麼結果？** 見 F1 歸因。
   - 修前：`dup_manual` 列出。
   - 修後：`dup_manual` 為 `[]`。

**圖譜鏡頭**：這份 diff 動的是 doctor 的 S20 提醒段（只提醒、不寫帳），沒碰事件帳、`[test:]` 綁定的 INVARIANT 判定、re-inject、search、處置閘、bound-tests、canary、guard-kill 的程式路徑。固定席節點判為不影響；牽連檔只有 `scripts/test_lumos.py`，修改的是新增的測試函式。

**角色卡**：沒附卡，略過。

總結：最高等級 minor
