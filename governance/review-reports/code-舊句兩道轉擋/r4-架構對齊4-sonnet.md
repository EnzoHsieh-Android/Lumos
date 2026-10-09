severity: minor

我跑了一輪對照(沒動 repo)。在 `/private/tmp/claude-501/seat` 用 `git show a4d42fea…:scripts/lumos` 與 `git show 40f871bf…:scripts/lumos` 各取一份,在暫存樹上實測。修補本身沒有引入第二種做法或跨層直呼,只有一條「同族兄弟讀端沒跟上」的輕微不一致。

## A1 兄弟的工作目錄讀端仍是舊的「只看最後一層」寫法,跟這次修好的讀端與寫端不一致
severity: minor
blocking: 否

**這次修補做對的部分**:`_note_reread_wt_verdicts` 改走共用的 `_repo_path_unsafe(..., dirs=True)`,讀端跟寫端 `_note_audit_safe_dir` 判的是同一份,「上層 governance 是指到 repo 外的符號連結」現在會被擋。

**還沒跟上的同族讀端**:專案裡還有兩支讀「工作目錄裡的治理資料」的函式,只擋最後一層符號連結,不看上層。我在暫存樹造了 `repo/governance -> 外面資料夾` 實測:
- **筆記內容審的判定檔**:`_note_audit_load_verdicts(root, None)` 把外面資料夾裡的判定檔讀進來,檔名出現在回傳的 bad 清單。寫端 `_note_audit_safe_dir` 對同一資料夾是拒寫的。
- **漂移表態帳**:`_drift_load_acks(root)` 回傳外面帳檔的內容 `[{'path': 'a.md', 'kind': 'm1', 'line': 1}]`。同一個 root 上寫端 `_drift_ledger_path_err` 回「governance 是符號連結……不往裡寫」。

這是「讀的人跟寫的人答案不同」,跟這次修補要消除的是同一種不一致。

- **既有的對照寫法(讀端也走共用守衛)**:`scripts/lumos:13527`(`_retro_path_unsafe` 讀寫共用)、`scripts/lumos:38186`(`_drift_ledger_path_err`,註解寫「讀寫同一條規則」)、`scripts/lumos:34896`(修補後的 `_note_reread_wt_verdicts`)。
- **仍是舊寫法的兩處**:`scripts/lumos:33673` 的 `d = root / _NOTE_AUDIT_VERDICT_DIR`、`if not d.is_dir():`,以及 `scripts/lumos:37757` 的 `_drift_load_acks` 內 `raw = fp.read_bytes() if fp.is_file() and not fp.is_symlink() else None`。
- **修補原文**:

引句:「判斷走共用的 _repo_path_unsafe(dirs=True),跟寫端 _note_audit_safe_dir 同一份(代碼審發現:原本只看最後一層,」

這句話只對回頭重讀那一支成立;同族的另外兩支沒有同步。
- **歸因**:有證據的原有漏查,不是修復回歸。我對兩版的這兩個函式做 `diff`,輸出為空(a4d42fea 與 40f871bf 完全相同),修補沒碰它們。
- **為何不升 major**:修補沒有引入新做法,也沒有直呼不該呼叫的東西。這兩處的行為在修補前就是這樣,修補只是修好了其中一支。依 `PITFALL`「同族一次掃完」的精神,建議回頭掃或明講界線,但這不擋本次修補。

## 核對過沒有問題的對照
- **`_repo_path_unsafe` 回傳值的判法**:修補寫 `... is None and d.is_dir()`,既有呼叫端寫 `if bad:`(`_note_audit_safe_dir`,`scripts/lumos:34086`)。真值語意相同。
- **OSError 的接法**:修補在 try 內接 `OSError` 並當不安全(`files = []`)。這跟 `_note_audit_safe_dir`(回「建不了」)、`_drift_ledger_path_err`(回「查不了」)、`_retro_path_unsafe`(回 "dossier")一致:守衛本身出錯都視為不能用。
- **`ValueError` 沒接**:`_retro_path_unsafe` 多接 `ValueError`,另兩個呼叫端和修補都沒接。`root` 來自 `--repo` 命令列參數,不可能含空位元組,我認為沒有實際差異,不列。
- **額外檢查**:`d.is_dir()` 是因為 `dirs=True` 對「不存在的層」回 None,這個檢查負責排除不存在的資料夾。`_note_audit_safe_dir` 是自己 `mkdir`,所以不需要。合理。
- **`RecursionError` 的接法**:
  - 專案的既有做法是就地 `except (ValueError, RecursionError)`,至少有 `scripts/lumos:26588`、`:45785`、`:37751`、`:13564` 等十幾處。
  - 兄弟閘 `_note_audit_config`(`:33349`)與 `_drift_config_text_parts`(`:39150`)就地接,跟這個做法一致。
  - 回頭重讀保留 `_note_reread_json` 包裝,是修補前就存在的(a4d42fea 已有),有四個呼叫端,docstring 也寫了理由,不算修補新起的做法。
  - `_note_shape_config` 用 `except Exception`,是更早的第三種寫法,也不是這次造成的。
- **`_sh_quote`**:
  - 修補把 `_note_reread_add_cmd`、`_note_reread_cmdline` 的 `import shlex` 改成 `_sh_quote`(定義在 `scripts/lumos:446`)。
  - 專案裡直接 `shlex.quote` 的地方很多(如 `:13028`、`:15990`),但同一段回頭重讀程式內已沒有殘留的直接 shlex。
  - 修補的兩支都是「印給人貼的指令參數」,用 `_sh_quote` 沒有問題。
- **測試換 `json.loads`**:
  - 寫法是 `_j.loads = deep_loads` 加 `finally: _j.loads = orig`。
  - 對照 `scripts/test_lumos.py:59198`(`_os.replace = boom` / `finally _os.replace = real`)、`:7037`(`_os.fdopen`)、`:7079`(`_os.write`)、`:70661`(`tempfile.mkstemp`),是同一種「換模組屬性、finally 換回」的慣例。
  - 修補原本換 `sys.modules["json"]` 的寫法在測試總檔裡是孤例,換掉是對的。
- **`t_reread_cmd_quote_shared`**:用 `g["_sh_quote"] = ...` 加 try/finally,跟 `:64503`(`g["_nodehome_side"] = ctrl_c` / `finally ... = saved`)、`:64666` 同款。
- **新測試 helper**:`_deep_json_text()` 是新 helper,但同檔 `:65813`、`:65959` 仍內嵌 `"[" * 130000 + "]" * 130000`。這是純風格重複,依判準不列。

## 圖譜鏡頭(固定席節點)
我只用 diff 與程式本身判斷,沒有逐篇細讀節點全文。
- **`guard-kill`、`lumos-cli-read`、`lumos-cli-lifecycle`(★INVARIANT★)**:這份 diff 沒碰 guard kill 的 rc 優先序與 `--json` 純度、search 的 superseded 濾網、re-inject 的 sentinel 外位元組保留。不影響。
- **`存量漂移守衛`、`筆記內容閘`**:`_drift_config_text_parts` 與 `_note_audit_config` 對「巢狀太深」改走既有的「讀不成 JSON → 照預設 block」退路,行為與節點宣稱一致,不影響。
- **`reversibility-governance-ledger`、`pitfalls-code-loop`(★RISK★)**:修補沒有動到帳的寫入或風險分級,只動 `scripts/lumos` 裡回頭重讀與設定讀取的幾行。不影響。
- **`code-loop守衛main-direct盲區`**:牽連檔是 `pre-push` 與測試總檔。修補沒動掛鉤,測試只補強與換替身寫法。不影響。

## 沒核對的範圍
- **測試能不能真的翻紅**:沒有跑任何測試,也沒有做破壞測試,只讀了測試碼與對照既有慣例。
- **`parent-link` 那組測試**:把 `governance` 換成符號連結再換回,我只看了寫法與既有慣例是否一致,沒跑。
- **跨裝置 rename**:`rename` 在 `tmp` 與 repo 不同裝置時的行為不在架構對齊範圍。

最高等級:minor
