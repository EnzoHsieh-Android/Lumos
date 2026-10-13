severity: major

**問 1　分層與依賴方向**
- 歸屬掃描和 Unicode 判斷留在 `# 〈待決問題〉` 那一區，與原本的 `_pq_bad_char`、`_pq_scan` 同區，位置一致。
- `_pq_bad_char` 的 `elif` 分支仍用共用的 `_PATH_SPECIAL_CATS`，沒有另抄一組，這點對齊。
- 新增的 `_PQ_DICP_RANGES` 全表疊在共用類別之外，等於第二層「看不見字元」判斷。`_strip_zero_width`（`scripts/lumos:4995`）和 `_NOTE_REREAD_CTRL_CATS`（`scripts/lumos:35773`）各自又是另一組口徑。這是因為需求不同才分開，可以接受。
- 寫入拒絕放在 `load_raw_for_edit` 旁邊，與寫入原語同處，位置一致。
- 例外類別和邊界裝飾器放在 `decisions_items` 之後，離最早的使用處（`_signoff_read_original`）很遠，也離 `main` 很遠。專案其他常數與輔助函式都是先定義、再使用。
- `_PQ_BLOCK_HEADER_RE` 和 `_PQ_TOP_KEY_RE` 夾在函式中間定義，不像 `_PQ_ID_RE`、`_PQ_SUB_RE` 擺在區頭，擺放不一致。
- 裝飾器掛在 `main` 上不是跨層直呼，結構上對。

severity: minor
blocking: 否
引句:「class WriteBlocked(ValueError, RuntimeError):」
對照處 file: `scripts/lumos:9063`（使用處）與 `scripts/lumos:20327`（定義處）。
說明：類別定義離使用處約一萬一千行，鄰居慣例是先定義再用。

severity: minor
blocking: 否
引句:「_PQ_BLOCK_HEADER_RE = re.compile(r"^[|>](?:(?:[+-][1-9]?)|(?:[1-9][+-]?))?(?:[ ]+#.*)?$")」
對照處 file: `scripts/lumos:7080`（`_PQ_ID_RE`、`_PQ_SUB_RE` 擺在區頭的位置）。
說明：這兩個新常數擺在函式之間，和同區其他常數的擺法不一致。

**問 2　命名與錯誤處理**
- `WriteBlocked` 同時繼承 `ValueError` 和 `RuntimeError`，目的是讓既有只接其一的呼叫端不要整批中斷，用意可理解。
- 但專案目前並存兩種做法：最外層接一次（`main` 上的裝飾器，加上 `cmd_summary_line`、`_summary_line_locked` 拿掉自己的 try），以及各分派段自己接。
  - `guard` 段仍自己接 `(RuntimeError, OSError)`（`scripts/lumos:53365`）。
  - `_drift_fix_load` 仍自己接 `(ValueError, OSError, UnicodeDecodeError)`（`scripts/lumos:39813`）。
  - 全檔還有 136 處類似的 except。
- `_guard_dispatch` 的註解自己寫明「其他子指令群各自已有 try，沒有要全部改成這個形狀」，所以這輪的做法是新增第二種，不是統一。
- 同一條 `WriteBlocked` 在 guard 段由局部 except 輸出「擋下」，在其他段由裝飾器輸出，輸出同一句話但走兩條路徑。
- `cmd_signoff` 同一個函式內混用兩種做法：`_signoff_read_original` 直接丟 `WriteBlocked` 交給最外層，`_cmd_set_locked` 回 rc 的路徑仍在函式內處理。
- 符號連結檢查：`_write_symlink_reason` 與 `_drift_fix_load` 是兩份。
  - `_drift_fix_load` 自己先檢查 `path.is_symlink() or path.stat().st_nlink != 1`，隨後呼叫的 `load_raw_for_edit` 內部又會檢查一次符號連結。
  - 兩處訊息不同，而且硬連結檢查只在 `_drift_fix_load` 有，新的共用原語沒有。
  - 以上述 `scripts/lumos:39813` 為準，`_drift_fix_load` 的檢查實際上變成重複。

severity: minor
blocking: 否
引句:「class WriteBlocked(ValueError, RuntimeError):」
對照處 file: `scripts/lumos:53365` 與 `scripts/lumos:39813`。
說明：最外層統一接、各分派段自己接並存，成了兩種做法。

severity: minor
blocking: 否
引句:「why = _write_symlink_reason(path)」
對照處 file: `scripts/lumos:39813`。
說明：`_drift_fix_load` 保留了自己的符號連結加硬連結檢查，與新的共用原語重疊但不等價。

severity: minor
blocking: 否
引句:「用裝飾器保留 HEAD 的 `def main():` 開頭，並讓每個直接呼叫 main() 的入口都經過拒寫邊界。」
對照處 file: `scripts/lumos:51936`。
說明：
- 全檔函式層級的裝飾器只有 `@classmethod`、`@property`、`@contextlib.contextmanager`，而且全是方法或 context manager。
- 這是第一個用 `functools.partial` 包起來的邊界裝飾器。
- 上一輪因「裝飾器成了拿鎖的第二種寫法」被點名而撤掉，這輪是把同一形式換用在錯誤邊界，並非全新的需求。

**問 3　第二種做法**
- 判為 major。
- 專案已有三份 block scalar 讀法，三份的語意本來就不一致：
  - `parse_frontmatter`、`parse_decisions`、`fm_structure` 都只認 `("|", "|-", ">", ">-")` 這四個字面值（`scripts/lumos:543`、`19016`、`20057`）。
  - 它們的結束判準也不同：`fm_structure` 用 `startswith("  ")`，`parse_frontmatter` 用 `strip`，`parse_decisions` 用 `indent > key_col`。
- 這輪新寫的 `_PQ_BLOCK_HEADER_RE` 加 `_pq_block_scalar_errors` 是第四份：
  - 它接受縮排指示符（例如 `|2`）和標頭註解。
  - 既有三支讀法不會認這種標頭，會把它當成純量。
  - 於是同一份 frontmatter 裡 `pq_parse` 與 `fm_structure`、`parse_frontmatter` 對「哪裡是 block scalar」的判斷可能分岔。
- `_pq_decisions_section` 重寫了 `parse_decisions` 的項目與 `key_col` 歸屬邏輯，也是第二份，語意還更嚴。
- `_PQ_TOP_KEY_RE` 對應既有的 `TOP_KEY_RE`，字元集不同。
- `_pq_mapping_parts` 與 `_pq_unquoted_value` 重寫了冒號分隔和 `#` 註解判斷，沒有共用既有 `strip_quotes`（`scripts/lumos:468`）之外的輔助函式。
- 本輪沒有共用既有的 `fm_structure`/`parse_decisions` 做逐行歸屬，而是在待決問題區自帶一套文法。

severity: major
blocking: 是
引句:「_PQ_BLOCK_HEADER_RE = re.compile(r"^[|>](?:(?:[+-][1-9]?)|(?:[1-9][+-]?))?(?:[ ]+#.*)?$")」
對照處 file: `scripts/lumos:543`（`parse_frontmatter`）、`scripts/lumos:19016`（`parse_decisions`）、`scripts/lumos:20057`（`fm_structure`）。
說明：第四份 block scalar 判斷，比其他三份多認縮排指示符和標頭註解，同一檔案三份讀法對區塊邊界會判不同。

severity: major
blocking: 是
引句:「"""decisions 的最小文法：2 格 mapping 項、4 格子鍵、其自己的 block/list 值；每項 id=d加數字。"""」
對照處 file: `scripts/lumos:18983`（`parse_decisions`）、`scripts/lumos:20045`（`fm_structure`）。
說明：重寫一份決策歸屬掃描，有自己的 `block_col`、`nested_col` 狀態機，沒有共用既有逐行歸屬。

上一輪點名三項的收尾：
- summary-line 接錯位置：已收掉。`cmd_summary_line` 與 `_summary_line_locked` 內的 `try/except` 拿掉了，改由最外層接。
- `os.path.islink`：已收掉，`atomic_write_verify` 改走 `_write_symlink_reason`（內部用 `path.is_symlink()`）。
- 常數擺放：只部分收掉。`_PQ_DICP_*` 和 `_PQ_ALLOWED_FLAGS` 放在區頭，但 `_PQ_BLOCK_HEADER_RE`、`_PQ_TOP_KEY_RE` 又落在函式之間。

不對齊共 7 條，其中擋合併的 2 條
