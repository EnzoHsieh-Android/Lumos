severity: minor

整體來看,這輪修訂把上一輪點到的「自寫第二套」大致收掉了:`_secev_sha` 改走 `_sha256_bytes`、`_secev_repo_root` 改走 `_secinv_repo_root`、`_dt_now_iso` 移除、讀帳改走 `_ledger_lines`、寫入合併進 `_jsonl_append_line_verified`。沒有 major,只有兩條 minor。引句取自 r2-repair-lumos-b.patch。

我沒讀到 python-idioms 的 SKILL.md,以下對照只以 7655a12d 版 scripts/lumos 為準。

## 問 1:分層與依賴方向

結論:一致,沒有跨層直呼。

- 所有新函式(`_secev_tools_read`、`_secev_chain_reminders`、`_secev_orphans`、`_secapr_confirm_human`、`_secapr_add_read`、`_secapr_add_check`)都放在 `_secev_*` / `_secapr_*` 區段,由 `cmd_*` 入口呼叫。
- `cmd_codeloop_security_approval_add` 拆成「讀 → 驗 → 確認 → 寫」四步,跟 `cmd_security_approvals` 拆出 `_secapr_payload_body` 的做法同形。
- 入口找 repo 根統一改用 `_secinv_repo_root(Path(repo) if repo else Path.cwd())`。對照 `scripts/lumos:7032` 的定義:它只照字面往上找 `.git`,跟 `_secinv_select_vault`、`_anchor_repo_root` 同一種判法。
- git 呼叫統一走 `_secev_git`,它包的是 `_lens_git_dl`(`scripts/lumos:9699`、`:57371`);`deadline` 一路往下傳。
- 帳檔寫入走共用的 `_jsonl_append_line_verified`(`scripts/lumos:17666`),沒有繞過。

## 問 2:命名與錯誤處理

結論:大致一致,有兩條 minor。

一致的部分:
- 錯誤輸出一律是「擋下:…」加 stderr,回傳碼 1/2 的語意沒變。
- 自驗失敗訊息改成 `{label}: 落盤自驗失敗…`,舊字串「canary record」留作預設 label,兩處呼叫的輸出沒變。
- `_secapr_add_*` 改成 `raise ValueError`,由 cmd 層印「擋下:」。這跟 `cmd_security_approvals` 吃 `_secapr_payload_body` 丟出的 `(OSError, ValueError)` 同形。
- `_secapr_confirm_human` 的 `except EOFError` 處理,對齊 `scripts/lumos:30852` 與 `_confirm_tty`(`scripts/lumos:33189`)的既有硬化。
- 治理帳讀法改成「`_ledger_lines` 切行加逐行 `json.loads`」,符合 `_ledger_lines` docstring(`scripts/lumos:19936`)寫的「帳檔切行唯一規則」。

不一致的兩條:

治理帳路徑寫死字面值,沒走 `GOV_LOG_NAME`
severity: minor
blocking: 否
引句:「led = Path(repo_root) / "docs" / ".governance-log.jsonl"」
這是改動所在函式裡的既有行,不是本輪新寫的。
file: `scripts/lumos:1633`(`GOV_LOG_NAME` 定義)與 `scripts/lumos:1652`(`_docs_ledger_path`)
對照:定義處註明「新碼用;舊碼的字面值照留」。同函式本輪新寫的讀法已改走 `_ledger_lines`,路徑卻還是字面值。
旁證:同樣寫法在 `scripts/lumos:20789`、`:38473`、`:60770`、`:62136` 也有,所以算專案內慣例漂移,不是本輪獨有。
歸因:有證據的原有漏查

共用寫入函式改用文字模式,但 docstring 說要原樣位元組
severity: minor
blocking: 否
引句:「with open(path, "a", encoding="utf-8") as f:」
file: `scripts/lumos:17666` 起的 `_jsonl_append_line_verified`
- 核可鏈與背書原本是 `open(path, "ab")` 寫位元組。抽成共用函式後,文字模式在 Windows 會把 `\n` 轉成 `\r\n`。
- 新 docstring 卻寫「要原樣位元組,不能讓這裡重新序列化」。
- 讀回自驗的比對 `got == text` 因為 `_ledger_lines` 認 `\r\n`,所以不會因此失敗。這條只是慣例與註解不符,不是 bug。專案有過 Windows 真機的前例(`scripts/lumos:30852`),所以標 ⚠。
歸因:有證據的修復回歸(由抽共用函式引入)

## 問 3:第二種做法與重疊

結論:沒有引入第二種做法。

- `_jsonl_append_line_verified` 沒有跟既有函式重疊,它就是從 `_jsonl_append_verified` 抽出來的本體。
  - `_jsonl_append_verified` 縮成包一層的薄函式(`json.dumps` 後轉呼叫)。
  - `_ledger_tail_needs_newline` 與 `_ledger_lines` 的用法沒變。
  - 新增的 `matches(got, d)` 回呼讓核可鏈、背書能原樣比對,是同一條路徑的擴充。
  - 我在 7655a12d 版 scripts/lumos 搜尋,找不到另一支同功能的「追加加讀回自驗」函式。
- `_secev_sha` 已換成 `_sha256_bytes`(`scripts/lumos:16891`),沒有並存的重複版本。
- `_secev_repo_root` 已刪,其呼叫點全改成 `_secinv_repo_root`。刪除的 `_dt_now_iso` 在 7655a12d 版已沒有其他呼叫者。
- `_secapr_confirm_human` 沒有複用 `_confirm_tty`,理由成立:後者是 y/N 加 `/dev/tty` 後備,這裡需要隨機確認碼,而且要求 stdin 與 stdout 都是終端,不能退到 `/dev/tty`。這是語意不同,不算第二種做法。
- 治理帳讀者有 `_drift_jsonl_iter` 系(只認 `\n`)與 `_ledger_lines` 系兩套,但 `_ledger_lines` 的 docstring 已明寫這是分開的兩系。新碼選了被標為「唯一規則」的那一系,沒有再生第三套。

不對齊共 2 條,其中 major 0 條
severity: minor
blocking 條數:0
