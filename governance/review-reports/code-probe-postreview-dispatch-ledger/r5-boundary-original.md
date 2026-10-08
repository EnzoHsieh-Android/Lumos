severity: minor

## Finding BND5-01
severity: minor
blocking: 否
引句:「with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,」
file: `scripts/scenario_probe.py:75`

- 輸入:`--out` 的檔名長 250 到 255 bytes,其餘參數正常。
- 路徑:`main()` 跑完整批後呼叫 `_atomic_write_text`。暫存檔名是 `name + "." + 8 個隨機字元`,多出 9 bytes,超過 255 的檔名上限。
- 壞處:`NamedTemporaryFile` 丟出 `OSError: File name too long`。這發生在整批模型跑完之後,所以整份結果檔寫不出來。
- 重現與輸出:
  - 修後:呼叫 `_atomic_write_text(.../'a'*250, 'x')`,拋 `OSError [Errno 63] File name too long`。245 bytes 以內正常。255 bytes 也失敗。
  - 修前:`Path(d,'a'*250).write_text('x')` 和 255 bytes 都成功。
- 歸因:有證據的修復回歸。修前能寫、修後失敗,兩版都實跑過。
- 嚴重度自降為 minor。理由是真實場景的檔名通常不會這麼長,所以我沒給出會實際碰到的場景。

## Finding BND5-02
severity: minor
blocking: 否
引句:「mode = stat.S_IMODE(old.st_mode) & 0o666」
file: `scripts/scenario_probe.py:82`

- 輸入:`--out` 指向還不存在的檔,或指向符號連結。
- 路徑:`NamedTemporaryFile` 預設權限是 0600。新檔不會走 `fchmod`,因為 `mode` 是 `None`。目標是連結時 `lstat` 不是普通檔,`mode` 也是 `None`。
- 壞處:新檔變成 0600。修前 `write_text` 依 umask 得 0644。若同一份結果檔要給別的帳號或群組讀取,會讀不到。
- 既有普通檔:0664 會保留,這點正確。setuid 位元被 `& 0o666` 去掉,這是刻意的。硬連結會斷開,另一條連結仍看到舊內容 `a`。
- 實測:修後 new 檔得 `0o600`,連結目標得 `0o600`。修前 new 檔得 `0o644`。
- 歸因:有證據的修復回歸,屬權限語意改變。兩版都有跑。

## Finding BND5-03
severity: minor
blocking: 否
引句:「(f"\\x{ord(ch):02x}" if ord(ch) <= 0xff else f"\\u{ord(ch):04x}")」
file: `governance/eval/ablation_lumos_first.py:416`

- 輸入:含不可列印字元的外部文字,例如 U+E0001、U+3000、ZWJ,或字面上寫成 `\x1b` 的文字。
- 路徑:`text()` 先把字元換成 `\xNN` 或 `\uNNNN`,再被後面的反斜線跳脫規則加倍。
- 壞處:
  - 碼點大於 0xFFFF 時,`\u{:04x}` 不補成 `\U`。`U+E0001` 變成 `\ue0001`,和 U+E000 後接字元 `1` 分不開。
  - 真正的 ESC 與字面 `\x1b literal` 輸出相同,都是 `\\x1b literal`,轉換不可逆。
  - 全形空白 U+3000 被當成控制字元顯示成 `\u3000`。ZWJ 組合 emoji 被拆成 `👨\u200d👩\u200d👧`。
  - 在終端看到的是兩個反斜線 `\\x1b`,只有在 Markdown 渲染時才是一個。
- 實跑輸出已列。
- 歸因:有證據的修復回歸,新增的轉換本身引入了歧義。
- 這只是報表可讀性問題,不影響安全。

## Finding BND5-04
severity: minor
blocking: 否
引句:「return re.sub(r"([\\`*_\[\]()!|])", r"\\\1", html.escape(raw))」
file: `governance/eval/ablation_lumos_first.py:421`

- 輸入:`{"date": "https://evil.example www.x.com a@b.com ~~s~~"}`。
- 路徑:跳脫集合沒有涵蓋 GFM 的裸網址、`www.` 和 email 自動連結,也沒涵蓋 `~`。
- 壞處:實跑輸出為 `~~s~~ https://evil.example www.x.com a@b.com`,原樣保留。GitHub 類渲染器會把它變成可點連結。測試只檢查 `![` 和 `](`,所以抓不到這件事。這與修補聲稱的「外部文字只作字面文字」不符。
- 歸因:有證據的原有漏查。修前同樣沒處理,修補沒有加重它。

## 固定席逐條判定

- `codex-harness`、`design-loop`、`guard-kill`(牽連 ablation 與 probe):沒有破壞其合約。
  - 這次改的是輸出寫入方式、等待秒數和報表文字,不碰 guard kill 的 rc 優先序和 `--json` 純度。
  - 沒有觸及處置閘的 `.md` 審材規則。
- `lumos-cli-lifecycle`(re-inject 只覆蓋 sentinel 之間):不影響。`_confirm_tty` 只在 `os.open` 加了 `O_NOCTTY`,沒碰注入邏輯。
  - 對照 `LUMOS_TTY` 三種情形,修前修後行為一致:
    - 一般檔可開。
    - FIFO 可開。
    - 不存在的路徑拋 `FileNotFoundError`,被 `except OSError` 轉成 `return None`。
- `lumos-cli-read`、`測試假綠形態`、`bound-tests-gate`、`授權與歸屬`:不影響。
  - 沒動 search 濾網、授權白名單和 SPDX 檔頭。
  - 新測試 `t_probe_boundary_fifth_round_output_contracts` 的連結斷言有實際檢查連結本身被取代,不是空殼。
- 其餘「只列名」的節點未讀內文,不判。

## 修補三問

**① 原問題的修復效果有何行為證據?**
- 輸出連結:`_atomic_write_text` 先 `lstat`,再寫同目錄暫存檔,最後 `os.replace`。實測連結被取代,受害檔 `k` 沒被改。
- 等待秒數:`delay = min(300, 剩餘)`。迴圈條件是 `waited < wait_on_limit`,所以 `delay` 一定大於 0。逐值走過的結果:
  - `0`、負值:不進等待。
  - `1`:睡 1 秒。
  - `299`:睡 299 秒。
  - `300`:睡 300 秒。
  - `301`:先睡 300 秒,再睡 1 秒。
  - `600`:睡兩次 300 秒。
  - 非整數:argparse `type=int` 直接拒收。
- 控制字元:ESC 和 BEL 確實被轉成可見字面。
- 以上都是我直接跑函式或讀程式得到的,不是只靠作者的測試通過。我沒有跑全套,也沒有改動 repo。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 正常路徑成立。
- 目標是目錄時仍丟 `IsADirectoryError`,和修前同型,暫存檔也有清掉(`dd` 目錄旁沒殘留)。
- 檔名過長、新檔權限、硬連結,三處語意有變,見 BND5-01 和 BND5-02。
- 父目錄不存在、唯讀目錄、懸空連結、跨裝置:我沒實測。依程式讀:
  - 父目錄不存在、唯讀目錄:兩版都會在寫入或建暫存檔時失敗。
  - 懸空連結:會被取代。
  - 掛載點目錄:暫存檔與目標同目錄,`os.replace` 不會跨裝置。

**③ 新發現的案例在修前、修後各是什麼結果?**

| 案例 | 修前 | 修後 |
|---|---|---|
| 250 bytes 檔名 | 成功 | 失敗 |
| 255 bytes 檔名 | 成功 | 失敗 |
| 新檔權限 | 0644 | 0600 |
| 連結目標 | 受害檔被改寫 | 連結被取代 |
| 裸網址 | 保留 | 保留 |
| 不可列印字元 | 原樣輸出 | 被轉成字面,但有歧義 |

## 未驗範圍

- 沒跑 `ruff`。
- 沒跑真 CLI 或 `test_lumos.py` 子集,只直接呼叫函式與讀程式。
- 沒驗 `render_md` 在實際 Markdown 渲染器下的畫面,只驗字串。
- 沒驗掛載點、唯讀目錄、懸空連結的實際行為。
- 沒讀圖譜筆記的 diff 部分(749 行檔的筆記段)。
- 不提供整體無回歸保證。

max severity: minor
