severity: minor

整合與知識同步鏡頭只找到一條 minor,其餘已核對的句子都成立。

## Findings

### 1. guard-kill 新 PITFALL「判法只算一份」綁的測試抓不到它要防的回歸
severity: minor
blocking: 否
引句:「PITFALL:判法(judged)在交出的列與收尾各記一份,交出列上那份沒有讀者、兩份可能不一致」
file: `scripts/lumos:29044`(`_kill_merge_emit` 組 survived 列的地方)
file: `scripts/test_lumos.py:146864`(`t_choice_kill_merge_ledger_counts` 用假的 `cmd_guard_kill`,列是測試自己造的)
file: `scripts/test_lumos.py:145635`(S12 斷言「交出的列沒有 judged」只在 `merge=None` 時跑)

失敗場景:這條 PITFALL 說「on_row 交出的列不帶 judged」,並綁 `t_choice_kill_merge_ledger_counts`。合併開著時,真的交列路徑沒有任何測試守這件事。

重現:在 after worktree 把 `_kill_merge_emit` 的 survived 列改成多帶 `"judged": "merged"`,四支測試全綠:

| 測試 | 結果 |
|---|---|
| `t_choice_kill_merge_ledger_counts` | 4 passed, 0 failed |
| `t_choice_kill_merge_all_survive` | 2 passed, 0 failed |
| `t_choice_guard_kill_new_params` | 5 passed, 0 failed |
| `t_choice_kill_merge_no_lane_chunk` | 2 passed, 0 failed |

修前版本我沒跑,這條歸因為未判定。這是舊問題,修補沒讓它變差,只是新 PITFALL 把它登記成「已有測試守住」。

影響不大:那份 judged 本來就沒有讀者。要補的話,在 S2 的端到端案例加一句斷言,看合併路徑交出的列不帶 `judged`。

## 已驗主張

**lint 與 spec-trace(在 after worktree 跑)**
- `lumos lint Projects/選擇點變異加速_計劃` 與 `lumos lint Systems/guard-kill` 都是 0 問題。
- `spec-trace` 24 條款,懸空 0、壞名 0、靠人 3、綁了 21。

**S22 成立**
- S22 和預期值表第 S22 列都成立,`t_choice_kill_merge_cap_wiring` 與 `t_choice_kill_merge_screen_cap` 在 after 版都綠。
- 呼叫端翻紅釘照寫的紅:
  - 快篩呼叫端改成 `max(m_el * 5, c.floor)`,`cap_wiring` 紅(2 passed, 1 failed)。
  - 合併基準呼叫端的 `max(mg.remaining(), 1.0)` 改成 `1e9`,同一支紅(2 passed, 1 failed)。
- 兩次改壞我都用 `git checkout` 還原,worktree 已移除。
- 引句:「判準:合併基準與快篩兩處」

**S23 成立**
- `_kill_merge_singles` 的判斷是 `remaining < 平均 × 未量支數 × 1.5` 才收手,所以「剛好等於時照量」成立。
- 預期值表算出來是 3.0 與 3.0 都照量(1×2×1.5、2×1×1.5),2.99 在第一支後就收手。
- 綁定的 `budget_edge` 與 `budget_reestimate` 在 after 版都綠。

**S24 與新 PITFALL 的 `_kill_merge_in_lane`(minor 觀察)**
- `_kill_merge_in_lane` 在 `_kill_merge_iter` 套壞法前就先看,沒有交集直接交逐支,所以敘述成立。
- `no_lane_chunk` 斷言的是「沒有合併呼叫、g2 交 abort、g2 不在 `mg.survived`」。
- S24 條款寫的是「`judged` 不是 merged」,而 judged 在 `scripts/lumos:78945` 由 `mg.survived` 算出,所以間接成立。測試沒有直接讀帳上的 judged,這點只是覆蓋精度,不另立 finding。

**綁定搬移一致**
- S4 去掉 `screen_cap`、S6 去掉 `reestimate` 與 `budget_edge`、S20 去掉 `no_lane_chunk`,分別搬到 S22、S23、S24。
- 引用這些測試的 PITFALL(104、106、108、110)都還對得上,`spec-trace` 無懸空。

**計劃其他段落**
- 整份計劃(`grep` 睡眠、端到端、`screen_cap`)沒有還在講已拿掉的「快篩睡 6 秒、總時限 3 秒」端到端案例。
- 「判法只算一份」的敘述與計劃〈列上的欄位〉那條(計劃第 123 行)一致。
- 引句:「S24] 當某個壞法的配方一支都不在合併道時,choice-kill 應 不套壞法開快篩、直接交逐支流程,這個壞法的 `judged` 應 不是 merged」

**未驗與不查的範圍**
- PITFALL 出處欄裡的「r3 通才 #1、邊界 #1」編號,無法在不讀上輪席報告的前提下核對。
- S7 與〈做法〉2 第 3 步寫合併基準上限是「剩下的總時限」,程式與 S22 是 `max(剩下總時限, 1)`。差別只在剩餘不到 1 秒時,計劃第 112 行已寫「最少 1 秒」,屬措辭精度,未立 finding。

**鎖檔與暫存**
- 鎖檔 `…2fa.json.warming` 不存在,不需要處理。
- 我在 after worktree 跑出紅的兩次測試留下兩個 `gctl-run-*` 現場,已用字面絕對路徑刪除。
- after worktree 已移除。
- 臨時目錄 `/tmp/lumos-seat-work/code-選擇點變異加速/整合-sonnet/` 已 `rmdir`。

總結:最高嚴重度 minor
