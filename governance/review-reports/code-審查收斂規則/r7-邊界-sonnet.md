severity: minor

已讀 `_residual_index_notes`、`_residual_note_hits`、`_residual_tree_paths`、`_doctor_residual_lines`、`_vault_slug_of(bare=True)` 與 `note_path` 的新寫法。我也跑了幾次實驗:
- 用 `unresolved` 值的壞形狀(空字串、整數、含換行、`[]`、`None`、字串型 `notes`)餵 `_residual_index_notes`。
- 把 `docs/knowledge`、`docs/x-knowledge`、大寫 `.MD`、非 `.md` 的檔名餵 `_residual_note_hits`。
- 對 5 處判斷各做一次破壞測試,每次清 `__pycache__`,各跑一組綁新增測試的子集。
- 這個 repo 的 `ls-tree` 約 13755 個檔,耗時約 0.1 秒。

**`unresolved` 值的壞形狀**:已讀,無 finding。除了空字串那一點(見下面 F3),其餘都走到「形狀不對」並叫人 `--reindex`,結果是安全的(判 high)。

**兩種圖譜佈局**:`docs/knowledge/` 與 `docs/<名>-knowledge/` 都被認得,`.txt` 不算。

**大寫副檔名**:`docs/knowledge/a.MD` 會被算成圖譜的檔,行為符合設計。

**F1:`.MD` 判斷沒被測試釘住(破壞測試存活)**

severity: minor
blocking: 否 — 這是測試覆蓋缺口,實際行為目前正確,也不會漏放行
引句:「gfiles = sorted(f for f in changed if f.lower().endswith(".md") and _vault_slug_of(f, bare=True) is not None)」
問題:把 `f.lower().endswith(".md")` 改成 `f.endswith(".md")`,5 組新增測試(`residual_note_unresolved_reason`、`path_checked`、`nfd_path`、`legacy_format`、`graph_file_any_vault`)全綠。程式刻意用 `lower()`,卻沒有任何測試用大寫 `.MD` 驗它。
具體失敗情境:日後有人把 `lower()` 拿掉,改到 `docs/x-knowledge/Foo.MD` 時「改到圖譜的檔」變成空,不會有測試紅。
佐證:``scripts/lumos: `_residual_note_hits` 內 gfiles 那行``

**F2:起點樹路徑的 NFC 正規化沒被測試釘住(破壞測試存活)**

severity: minor
blocking: 否 — 這是測試覆蓋缺口
引句:「return {nfc(x.decode("utf-8", "replace")) for x in r.stdout.split(b"\0") if x}」
問題:把 `_residual_tree_paths` 裡的 `nfc(...)` 拿掉,`t_pitfalls_residual_note_nfd_path` 等測試仍然全綠,所以這個測試沒讓「git 存 NFD 路徑」真的出現。實驗上,macOS 的 git 預設會把檔名轉成 NFC,在這台機器上走不到這條分支。
具體失敗情境:在 `core.precomposeunicode=false` 或 Linux 上,git 存的 NFD 路徑和 `nfc(p)` 對不上,會誤報「在起點版本裡沒有這支檔」。誤報只會升 high,不會漏放行,但現在沒有測試守這一段。
佐證:``scripts/lumos: `_residual_tree_paths` 的 return 那行``;測試 `t_pitfalls_residual_note_nfd_path`

**F3:`{"unresolved": ""}` 的理由句變成「解不出決策所在筆記:?」**

severity: minor
blocking: 否 — 只是顯示品質,判級(high)是對的
引句:「w = (f"解不出決策所在筆記:{_plain_label(v['unresolved'], 80)};重建索引修不好,」
問題:`isinstance(v.get("unresolved"), str)` 只擋非字串,空字串也過。`_plain_label("")` 出來是 `?`,理由句變成「解不出決策所在筆記:?;重建索引修不好」。
具體失敗情境:手改的索引寫 `{"unresolved": ""}` 時,「重建索引修不好」其實不實。因為圖譜若解得出,`--reindex` 就能修好,這句會誤導人去 `--remove` 掉殘留。
佐證:實驗輸出 `{'unresolved': ''} → 解不出決策所在筆記:?;重建索引修不好…`

**F4:標準獨立 vault 根(`MOC/`、`Systems/`、`Projects/` 在 repo 根)的專案,「不知道在哪篇」不再升 high**

severity: minor
blocking: 否 — 這種專案目前沒有殘留合約的證據,而且 `_vault_in` 的獨立 vault 根佈局(核心 repo)才受影響
引句:「「圖譜的檔」= 圖譜資料夾底下的 .md,資料夾照 _vault_slug_of(bare=True,認 docs/<名>-knowledge/ 與 docs/knowledge/」
問題:`_vault_in` 還認第三種佈局(repo 根有 `MOC/` 加 `Verification/` 或 `Systems/` 的獨立 vault)。`_vault_slug_of(..., bare=True)` 不認它,而上一版靠 `folders`(殘留指標的頂層資料夾)的啟發式能抓到這種。實驗:`_residual_note_hits({k: None}, {}, ["Projects/a.md"])` 與 `["Systems/a.md"]` 的 unknown 都是空,等於舊索引或解不出的殘留在這種佈局下改圖譜檔會靜默判 light。
具體失敗情境:核心 repo 這類專案有舊格式索引,改了存殘留決策的筆記,pitfalls 判 light,放行。
佐證:``scripts/lumos: `_vault_in` 約 26351 行``;實驗輸出

**已確認有效的測試**:
- 拿掉「起點樹路徑檢查」(`elif False`)會讓 `path_checked` 紅 3 條。
- 拿掉 `bare` 對 `docs/knowledge` 的支援,會讓 `graph_file_any_vault` 紅 2 條。
- 拿掉舊格式排除(`k[:5] + ((),) if k[:3] in legacy`),會讓 `legacy_format` 紅 2 條。

我留下的暫存現場(3 個 `gctl-run-*`)與實驗目錄都已刪除。

最高等級 minor,blocking 0 條。
