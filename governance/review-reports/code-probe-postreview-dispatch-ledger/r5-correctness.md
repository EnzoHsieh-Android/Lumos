severity: minor

## Finding COR5-01
severity: minor
blocking: 否
引句:「以同目錄暫存檔原子取代目標，避免跟隨既有目標符號連結。」
file: `scripts/scenario_probe.py:27`

- **輸入一:新檔權限。** `--out` 指向還不存在的路徑。
  - 路徑:`mode=None`,不進 `fchmod`。
  - 結果:`NamedTemporaryFile` 預設 0600,`os.replace` 後輸出檔變成 0600。
  - 修前 `write_text` 依 umask 產生 0644。
  - 影響:同機其他使用者或不同帳號的 CI 讀不到探針 JSON。
- **輸入二:`--out` 指向字元裝置。** 例如 `/dev/stdout`、`/dev/null`。
  - 路徑:`lstat` 不是一般檔,`mode=None`。
  - 之後在 `/dev/` 建暫存檔;非 root 得到 `PermissionError`,而且是整批跑完、寫報告的最後一步才炸。
  - root 執行則會用一般檔取代裝置節點(未實測,依程式路徑推得)。
  - repo 內沒有呼叫端用 `/dev/*` 當 `--out`,所以只影響手動用法。
- **重現。** 在兩版目錄執行 `python3.14 t1.py`(`/tmp/lumos-seat-work/code-probe-postreview-dispatch-ledger/正確性5-sonnet/t1.py`,對 `_atomic_write_text` 寫新檔、`/dev/null`、`/dev/stdout`、目錄)。
  - before 輸出:`newfile mode 0o644`、`/dev/null ok`、`/dev/stdout ok`、`dir IsADirectoryError`。
  - after 輸出:`newfile mode 0o600`、`/dev/null PermissionError ... '/dev/null.4w30khv1'`、`/dev/stdout PermissionError`、`dir IsADirectoryError`。
  - 目錄目標兩版行為相同,失敗後也沒留暫存檔(`os.listdir` 只剩 `new.json`、`dd`)。
- **歸因:有證據的修復回歸。** 兩版同一腳本結果不同。
  - `governance/eval/ablation_lumos_first.py` 的 `_atomic_write_bytes` 本來就有同樣的 0600 行為,所以新檔 0600 是延續既有慣例,不是新發明。
  - `/dev/*` 失敗則是這次新增的。

## Finding COR5-02
severity: minor
blocking: 否
引句:「return re.sub(r"([\\`*_\[\]()!|])", r"\\\1", html.escape(raw))」
file: `governance/eval/ablation_lumos_first.py:416`

- **輸入。** `meta["date"]` 或 `claude_version` 帶裸網址,例如 `https://evil.example/x` 或 `www.evil.example`。
- **路徑。** 這些字元都不在跳脫集合內,`text()` 原樣輸出。
- **壞在哪。** GFM 類渲染器會把它自動轉成可點連結。新增測試只檢查 `![` 與 `](`,所以測不到。這與測試名稱宣稱的「外部文字只作字面文字」不完全一致。
- **未實測。** 我沒有跑渲染器,結論依 GFM 自動連結規則推得,標 ⚠。
- **歸因:有證據的原有漏查。** 修前的 `text()` 同樣不處理,不是修補引入的。

## 逐項判定

- **本案 4a:`render_md` 跳脫順序。** 不會雙重跳脫。
  - 實跑結果:`it's` 變 `it&#x27;s`,`&` 變 `&amp;`,`<b>` 變 `&lt;b&gt;`。
  - `&`、`#`、`;` 不在 Markdown 跳脫集合,實體不會被再跳一次。
  - 控制字元先轉成 `\x1b` 字面,再把反斜線跳成 `\\x1b`,渲染後顯示為 `\x1b`。
  - 孤立 surrogate(`\ud800`)會變成 `\ud800`。修前寫檔會丟 `UnicodeEncodeError`,這是改善。
  - 一個小模糊:輸入裡真的有字面 `\x1b` 文字,和被轉換的控制字元顯示相同。
  - 衍生資料:repo 內沒有程式解析 `summary.md`,JSON 另寫,不受影響。
- **本案 4b:等待迴圈。** `delay<=0` 不會空轉。
  - 進入條件是 `waited < a.wait_on_limit`,所以 `delay` 必為正。
  - `--wait-on-limit` 的型別是 `int`,`delay` 不會是浮點。
  - 負數與 0 直接跳過等待。
  - `--wait-on-limit 1` 時只睡 1 秒,修前會睡 300 秒。
  - `waited` 仍跨題累計,行為與修前一致。
- **O_NOCTTY。** 用 `getattr(..., 0)` 保底。`/dev/tty` 本來就不能再成為控制終端,pty 與 `LUMOS_TTY` 路徑沒有行為差異。
- **be-api-compat:**
  - 輸出 JSON 的欄位與編碼沒變。
  - 差異只有權限(見 COR5-01),以及 `summary.md` 的文字多了反斜線(見 COR5-02 附近的實測輸出)。
- **be-authz:**
  - 無端點。
  - 與授權相關的只有 `--out` 符號連結不再被跟隨,是正向改善。
  - 殘留風險是 SIGKILL 後會留下 `out.json.<隨機>` 暫存檔。它不符合 `*.json`、`*.pending`、`*.candidate` 的 glob,下次讀取不受影響。
- **固定席節點:**
  - `lumos-cli-lifecycle`(★INVARIANT★ re-inject 只覆蓋 sentinel 之間、之外 byte-equal):不影響,diff 只動 `_confirm_tty` 的 `os.open` flag,沒碰 re-inject。
  - `design-loop`、`guard-kill`、`bound-tests-gate`、`測試假綠形態`:不影響。diff 沒有動處置閘、guard kill 的 rc 順序與 JSON 純度、綁定測試機制。
  - `測試假綠形態`:新增測試有補前置斷言(`claim_then_limit` 內 `check("供應商回上限前已真正 claim 最後一格"…)`),符合該合約。
  - `授權與歸屬`:不影響,沒有動 `_VENDORED_TOOLKIT` 或 SPDX。
  - 其餘節點(`codex-harness`、`lumos-cli-read` 等):不影響,沒有動到它們宣稱的行為。
  - 圖譜筆記本身我只讀了 snapshot,沒逐篇核對。
- **lint:** `ruff check` 兩檔共 44 個告警。未逐條對照 hunk,但這次新增的 hunk 沒有明顯的行為性告警,所以不列 finding。

## 修補三問

1. **原問題的修復效果。**
   - 等待預算:`--wait-on-limit 1` 在修前睡 300 秒,修後只睡 1 秒。證據是程式讀法加上新測試 `sleeping.call_args_list == [call(1)]`,我沒另外跑 before 版。
   - 符號連結覆寫:靠我自寫腳本確認 after 的寫入走 `os.replace`,不會寫進連結指向的檔。我沒跑 repo 的完整 `main` 測試。
   - 控制字元:靠實跑 `render_md`。
2. **相鄰路徑。**
   - 新檔權限由 0644 變 0600,`/dev/*` 目標由可寫變失敗(COR5-01)。
   - 目錄目標、既有一般檔(沿用原權限)、符號連結(換成一般檔)的行為合理。
   - 錯誤路徑上 `finally` 會清掉暫存檔(我只測了目錄目標,`os.listdir` 確認沒殘留;`PermissionError` 那條在建檔時就失敗,本來就沒有暫存檔)。
3. **同一案例修前修後。**
   - 新檔權限:修前 0644,修後 0600。
   - `/dev/stdout` 與 `/dev/null`:修前成功,修後 `PermissionError`。
   - 控制字元:修前 `\x1b` 原樣進報表,修後轉成可見字面。
   - 帶 `|` 的題號:兩版都正確跳脫。

## 未驗範圍

- **未跑:**
  - 沒跑 `scripts/test_lumos.py` 與 `scripts/test_autonomous_loop.py`;依規定不跑全套,這次也沒跑 `-k` 子集。
  - 沒實跑真實 `main()` 的 SIGKILL 殘留情境。
  - 沒測 root 取代 `/dev/null` 的情況,只靠路徑推論。
  - 沒核對 Windows 或 `fchmod` 不可用的平台,這兩個平台上 `os.fchmod` 缺失或失敗。
- **只讀未驗:** 圖譜 Verification 筆記只讀 snapshot 範圍,沒核對。
- **不保證:** 以上不是整體無回歸保證。

severity: minor
(max)
