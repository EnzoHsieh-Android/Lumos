severity: major

本席讀的是 `scripts/lumos` 在 5242975c 的樣子。對照用的行號都是那一版的行號。

**第一問:分層與依賴方向**

- 清單外鍵名規則留在待決問題那一區,而且用了共用的 `BLOCK_SCALAR_HEADERS`(`scripts/lumos:433`)。決策狀態機 `_pq_decisions_section` 與第四份 block scalar 判斷都已刪光,這兩項收掉了。
- Unicode 判斷(`_PQ_EMOJI_RANGES` `scripts/lumos:6953`、`_PQ_JOIN_CONTROL_SCRIPT_RANGES`)放在待決問題那一區,沿用 `_PQ_DICP_RANGES` 的手抄碼位表寫法。專案裡沒有另一份 emoji 表或文字系統表,所以沒有重複。`_PATH_SPECIAL_CATS`(`scripts/lumos:35765`)、`_esc_clean`(`scripts/lumos:12189`)、`_strip_zero_width`(`scripts/lumos:4998`)的用途是消毒或跳脫,和這裡的白名單不同。
- 寫入拒絕沒有放在寫入原語旁。`WriteBlocked`、邊界、`_write_refusal_reason` 都搬到 `scripts/lumos:9050-9084`,夾在 spec-trace 和 signoff 之間。它的主要使用處在 `load_raw_for_edit`、`atomic_write_verify`(`scripts/lumos:20374-20452`),隔了約一萬一千行。第 2 條對這點。
- 錯誤邊界掛在 `main` 上(`scripts/lumos:51942`)。這個方向沒錯,但接法有問題,見第 1 條。

**第二問:命名與錯誤處理**

- 「`WriteBlocked` 只由最外層接」不成立。裝飾器之外還有兩層接法並存,第 1 條說明。
- `_write_refusal_reason` 不是寫入拒絕的唯一一份,第 3 條說明。

**第三問:第二種做法**

- 上一輪點名的幾項:第四份 block scalar 判斷、第二份決策狀態機、drift 自己的連結檢查,都收掉了(drift 改走 `scripts/lumos:39824`)。
- 沒收掉的有兩項:兩種接法並存,以及 `WriteBlocked` 定義離使用處更遠。

---

severity: major
blocking: 是
引句:「def _write_blocked_boundary(func):」
對照處 file: `scripts/lumos:53359`、`scripts/lumos:53375`、`scripts/lumos:16010`、`scripts/lumos:20612`
說明:`WriteBlocked` 現在有三層接法。
- 第一層:`main` 上的裝飾器。上幾輪曾因「裝飾器成了拿鎖的第二種寫法」被撤掉,這輪又掛回來。
- 第二層:`main` 內 12 處分派段各加 `except WriteBlocked: raise`。這是新增的重複樣板,每個分派段都得記得寫,漏一個就悄悄走另一條路。
- 第三層:`cmd_*` 內部仍有大量 `except (ValueError, RuntimeError)` 在最外層之前就接走(例如 `scripts/lumos:16010`、`scripts/lumos:20612`、`scripts/lumos:21625`)。這些印的是各自的訊息格式,例如「⚠ 守衛節點已建好…」,不經過邊界。

所以「只由最外層接」並沒有統一,而是新增了一種接法。

---

severity: minor
blocking: 否
引句:「class WriteBlocked(ValueError, RuntimeError):」
對照處 file: `scripts/lumos:20374`
說明:上一輪點名「`WriteBlocked` 定義離使用處遠」,這輪沒有拉近,反而從 `load_raw_for_edit` 旁搬到 spec-trace 與 signoff 之間。`_write_refusal_reason` 也搬離了 `atomic_write_verify`(`scripts/lumos:20430`)。結構方向沒錯,位置比上一輪更不貼近。

---

severity: minor
blocking: 否
引句:「def _write_refusal_reason(path):」
對照處 file: `scripts/lumos:39536`、`scripts/lumos:10268`
說明:它不是寫入拒絕的唯一一份。
- `scripts/lumos:39536` 的 `fp.stat().st_nlink != 1`(同一支檔裡的另一個帳檔寫入守衛)自己查硬連結。
- `scripts/lumos:10268` 的 `_escape_log_guard` 自己查 `is_symlink`。
- 同族判準也不一致:`_write_refusal_reason` 用 `> 1`,`scripts/lumos:39536` 用 `!= 1`。

這些對象是帳檔而不是筆記,範圍可以不同。但新 docstring 宣稱「所有換檔／追加寫入共用」,實際上不是。

---

severity: minor
blocking: 否
引句:「def _pq_structure_marker_problem(raw):」
對照處 file: `scripts/lumos:7172`、`scripts/lumos:7201`
說明:同一區出現三份 anchor/alias/tag 偵測。`_pq_structural_value_problem` 有一份,`_pq_structure_marker_problem` 裡的 `item[:1]` 一份、`candidate[:1]` 一份,訊息文字逐字重複。`_pq_line_mapping` 的「剝 `- ` 加切 mapping」又是一套行讀法,和 `TOP_KEY_RE`、`LIST_ITEM_RE`(`scripts/lumos:11`)並存。block scalar 的結束規則也多了一種:`_pq_block_key_col` 用「縮排深於鍵所在欄」,而 `parse_frontmatter` 用「以兩格空白開頭」,`parse_decisions` 用 `key_col`。這些是同一個 YAML 子集的重複抽出,沒有收攏成一個小函式。

---

severity: minor
blocking: 否
引句:「print(f"擋下:{_esc_clean(str(exc), 1000)}", file=sys.stderr)」
對照處 file: `scripts/lumos:53361`、`scripts/lumos:53411`
說明:只有邊界清洗訊息。同一個 `main` 內的其他 `print(f"擋下:{e}")` 都直接印例外文字,沒有 `_esc_clean`。同一個「擋下」輸出有兩種消毒標準,這是新引進的不一致。

---

不對齊共 5 條,其中擋合併的 1 條
