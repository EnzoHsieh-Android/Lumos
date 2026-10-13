severity: major

三問都附對照處。結論先講：1 條 major、2 條 minor，分層與依賴方向沒問題。

**問 1　分層與依賴方向：對齊**
- `_VAULT_LOCK_VAULTS` 和 `_vault_lock_held_for` 放在鎖層。位置在 `_VAULT_LOCK_HELD` 旁邊、`_vault_write_lock` 之前，由 `atomic_write_verify` 往下呼叫，方向是「寫入原語 → 鎖層」。
  - 對照：`scripts/lumos:19959`、`scripts/lumos:19963`、`scripts/lumos:20017`。
  - 測試以外已經沒有程式在鎖層外讀 `_VAULT_LOCK_HELD`。上一輪「讀鎖層私有狀態」確實收掉了。
- 包裝函式緊貼 `_*_locked`，順序是「拿鎖、再叫 `_locked`」，和鄰居一樣。
  - 對照：`scripts/lumos:15508` 的 `cmd_guard_plan` 接 `_guard_plan_locked`，`scripts/lumos:20145` 的 `cmd_set` 接 `_cmd_set_locked`，`scripts/lumos:16304` 的 `cmd_guard_bind` 同樣。
- `_vault_locked` 裝飾器已整支刪掉，鎖層和各指令沒有第二種寫法留下。
- `cmd_decision_amend` 只鎖讀改寫那段，放鎖外的 git 動作。這和 `cmd_guard_kill_add` 把 `_kill_add_after_lock` 放在鎖外是同一個思路（`scripts/lumos:17127`）。

**問 2　命名與錯誤處理：兩條 minor**

severity: minor
blocking: 否
引句:「            except RuntimeError as e:」
對照處 file: `scripts/lumos:53057`、`scripts/lumos:52878`。
- 這是 `guard bind` 和 `audit` 在分派層新加的 try/except，只接 `RuntimeError`。
- 鄰居的做法是 `except (ValueError, RuntimeError, OSError)`：`decision-amend` 和單節點決策指令在 `scripts/lumos:53057` 前後，`decision-reindex --all` 也是。
- 同一個 `guard` 區塊裡的 `plan`、`settle`、`abandon`、`kill-add` 同樣會拿鎖，但沒有這種包法。同一區塊出現兩種處理拿鎖逾時的寫法。

severity: minor
blocking: 否
引句:「def _decision_amend_locked(rel, path, did, field, text):」
對照處 file: `scripts/lumos:15517`、`scripts/lumos:16045`、`scripts/lumos:20260`。
- 其他 `_locked` 一律第一個參數是 `env`，這支沒有，只收 `rel, path`。
- 命名一半對得上：`cmd_guard_plan` 去掉 `cmd_` 變成 `_guard_plan_locked`，`cmd_set` 保留 `cmd_` 變成 `_cmd_set_locked`，鄰居本來就兩種。
- 這輪新加的 `_cmd_guard_bind_locked`、`_append_decision_ref_locked`、`_dref_remove_ref_locked` 都落在鄰居已有的兩種寫法裡，命名沒問題。

**問 3　第二種做法：裝飾器、手寫解析、讀鎖層私有狀態都真的收掉；仍有 1 條 major、1 條 ⚠ minor**

已收掉的：
- 裝飾器 `_vault_locked` 已刪。
- 改名解析改走 `_nodehome_git` 加 `_nodehome_name_status`，和 `scripts/lumos:27549` 附近一致。
- `_VAULT_LOCK_HELD` 不再被鎖層外讀。
- `cache["\0paths"]` 這類魔術鍵改成 `cache["nodes"]` 和 `cache["paths"]`，結構上沒有第二種做法。

severity: major
blocking: 是
引句:「        r = _lens_git(rr, "rev-parse", "--verify", "--quiet", "--end-of-options", rev + "^{commit}")」
對照處 file: `scripts/lumos:46656`。
- `_pq_push_remind` 裡的 `_is_commit` 是巢狀小函式，自己跑一遍 rev-parse。
- 專案已有 `_lens_full_sha`（`scripts/lumos:46656`），做的是同一件事：`rev-parse --verify -q --end-of-options <rev>^{commit}`，而且 `--end-of-options` 防 `-` 開頭的用意也一樣。
- 這輪的修正是 `_is_commit(base) and _is_commit(head)`；改成 `_lens_full_sha(rr, x) is not None` 即可，第二種做法就收掉。

severity: minor
blocking: 否
引句:「    return c in "\u200c\u200d\u00ad" or 0xE0020 <= ord(c) <= 0xE007F」
對照處 file: `scripts/lumos:35267`、`scripts/lumos:35281`、`scripts/lumos:11715`。
- ⚠ 判不準。`_pq_cf_ok` 在共用的 `_PATH_SPECIAL_CATS` 之上加了逐字元的放行名單。
- 鄰居調整共用組的做法，是在類別層級增減：`_NOTE_REREAD_CTRL_CATS = _PATH_SPECIAL_CATS - {"Cs"}`，或 `_path_special_chars(..., surrogate=False)`。
- 這輪有照既有慣例寫出「為什麼不用共用組整組」的理由（和 `scripts/lumos:11715` 同格式），所以不算違反慣例，只是新增了一種「字元級例外」的形狀。
- `_pq_bad_char` 本身也沒走 `_path_special_chars`。這是前一版就有的，不算這輪新增。

不對齊共 3 條，其中 major 1 條
