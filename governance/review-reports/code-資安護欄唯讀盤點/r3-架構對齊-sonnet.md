severity: minor

# 架構對齊席 r3 報告(security list 修補鏡頭,aadf6b07 → 84a58aee)

**結論:** 沒有 major。r2 提的第二套有界讀已收斂成唯一一份 `_read_fd_capped`,輸出也統一走 `_secinv_show`。剩 3 條 minor,都是結構正確、細節不一致。

## 問 1:分層與依賴方向

新碼位置和呼叫關係大致與鄰居一致,沒有跨層直呼。

- `_vault_safe_read_rel` 改呼叫 `_read_fd_capped`,後者與 `_retro_read_bytes` 共用(lumos_after.py:776、16776、16800)。
- `_secinv_vault_problem` 的逐層檢查呼叫既有的 `_repo_path_unsafe`(lumos_after.py:6700,定義在 39340),沒有另寫 realpath。
- `_secinv_collect` 改走 `env_text(env, rel)`(lumos_after.py:1016),不再直接讀私有欄位 `env._texts`。
- 決策快取沿用 `_pq_decision_target(..., cache=)` 的 `"paths"` 格(lumos_after.py:8968)。
- `_secinv_select_vault` 仍用 `_vault_in(all_candidates=True)`(lumos_after.py:28688),沒有另寫候選規則。

### finding 1:`_read_fd_capped` 的位置

標題:共用有界讀放在回顧檔區塊,底層的 `load_vault_safe` 往後依賴它。
severity: minor
blocking: 否
引句:「+def _read_fd_capped(fd, limit):」
file: `scripts/lumos:16776`(修後)。`_regular_own_fd` 在 `scripts/lumos:1639`,`load_vault_safe` 一族在 700 到 830 行。
- 說明:最早載入的安全讀取層,依賴一個定義在 16000 行之後、跟 `_retro_read_bytes` 同區的 helper。
- 這只是放置位置的問題:函式在呼叫時才解析,不會出錯。名稱沒有 `_retro_` 前綴,所以不誤導。
- 歸因:有證據的修復造成,但單一版本就看得出,不需要兩版對跑。
- 建議:搬到 `_regular_own_fd` 附近。

## 問 2:命名與錯誤處理

- 擋下訊息統一走 `擋下:` 前綴加 `_secinv_show`,與鄰居的 `擋下:` 形狀一致(lumos_after.py:21225)。
- 新錯誤種類 `errors_truncated`、欄位 `omitted_by_kind` 沿用 `_vault_issue(kind, node, **kw)` 的形狀(lumos_after.py:870)。
- `_SecinvErrors(list)` 有先例 `_ResidualAsks(dict)`(lumos_after.py:21195)。
- 回傳碼 0/2 未動。

### finding 2:決策表快取多開一格

標題:`_secinv_decision_problem` 另開一格決策表快取,與 `_pq_decision_state` 的 `"nodes"` 快取並行。
severity: minor
blocking: 否
引句:「+    table = cache.setdefault("decision_tables", {})」
file: `scripts/lumos:9019`。`_pq_decision_state` 的 `cache.setdefault("nodes", {})` 存的也是「每篇的決策」,註解寫「每篇的決策(nodes)與路徑索引(paths)各放一格」。
- 說明:同一份資料(每篇的決策)現在有兩種快取格式,一種存決策 dict 清單,一種存 `by_id → [valid 字串]`。
- security list 需要分辨「編號不唯一」,`_pq_decision_state` 只回第一筆,所以不能直接呼叫它。但可以共用 `"nodes"` 格,再在取用端做 `by_id`。
- 歸因:有證據的修復造成。修前每次都重新呼叫 `_node_decisions`,沒有快取;這次新增的是第二種快取格式。
- 行為:`-k seclist` 326 個全過,結果等價。

### finding 3:`.git` 判定有兩種寫法

標題:repo 根的判定,`_secinv_repo_root` 與 `_secinv_select_vault` 對 `.git` 用了不同判法。
severity: minor
blocking: 否
引句:「+        if os.path.lexists(str(d / ".git")):」
file: `scripts/lumos:6733` 的 `if (d / ".git").exists(): break`。
- 說明:專案已有至少 5 份各自的 repo 根尋找函式(`_vault_repo_root`、`_cochange_repo_root`、`_anchor_repo_root`、`_lens_repo_root`、`_repo_root_from_env`),新增第 6 份符合「各自一份」的現況,所以只算 minor。
- 但同一個功能裡,`.git` 是否存在有兩種判法:`lexists` 會把懸空的 `.git` 連結算進去,`.exists()` 不會。
- 這兩個函式對懸空連結的 `.git` 判斷可能不同。我沒有就這個場景實跑,所以不主張它造成行為差異。
- 歸因:有證據的修復造成(`_secinv_repo_root` 是這次新增)。

## 問 3:第二種做法

- R6 的核心「第二套有界讀」已經收斂,沒有引入新的第二種做法:
  - 修前 `os.read(fd` 在 `scripts/lumos` 出現 4 處,修後 3 處。
  - 檔案物件式的讀取(`_LENS_SPEC_MAX_BYTES`)屬另一種介面,不算同族。
- `_trusted_private_dir` 的 docstring 補了例外說明,與 `load_vault_safe` 註解互相指引,既有「dirfd 版邊際價值低」的決定有交代。

## 證據與已驗範圍

**已驗(兩版同一案例):**

| 項目 | 命令 | 修前 | 修後 |
|---|---|---|---|
| R6 單一有界讀 | 對 300000 位元組檔呼叫 `_retro_read_bytes(f, limit=100)` | `(None, '超過 256KB(至少 65536 位元組)')` | `(None, '超過 256KB(至少 101 位元組)')` |
| 無上限讀取 | `_retro_read_bytes(f, limit=None)` | 300000 | 300000 |

- 修後的「至少 N 位元組」更貼近上限,拒絕判定一致。
- 訊息裡的「256KB」是寫死的,和傳入的 limit 無關。這是修前就有的,不是修復造成。
- preserve:修後 `-k retro` 為 357 passed,`-k seclist` 為 326 passed,0 failed。

**未驗:**
- 修前的 `-k` 測試我沒跑,所以「修前紅、修後綠」的守護測試因果沒有主張。
- R1 到 R5、R7 的行為正確性不在本席鏡頭內。

不對齊共 3 條,其中 major 0 條(最嚴重 severity:minor,blocking 0 條)

已移除兩個臨時 worktree。
