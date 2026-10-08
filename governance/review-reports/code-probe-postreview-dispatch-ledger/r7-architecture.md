severity: major

## Finding ARCH7-01
severity: major
blocking: 是
引句:「return f"⟦U+{ord(ch):04X}⟧"」
file: `scripts/lumos:16067`(`_kill_esc`)、`scripts/lumos:13553`(`_json_text_escaped`)、`scripts/lumos:11245`(`_esc_clean`)
- 既有:lumos 主程式把控制字元轉成可見文字有兩種固定寫法。
  - 要看得見且不丟資訊時,寫成 `\uXXXX`(`_kill_esc`、`_json_text_escaped`),類別組共用 `_PATH_SPECIAL_CATS`(`scripts/lumos:34338`)。
  - 只要不被終端執行時,換成空白(`_esc_clean`)。
  - `_esc_clean` 的 docstring(`scripts/lumos:11251`)明講「無損、看得見」的跳脫用 `_PATH_SPECIAL_CATS` 那組,兩種用途不併。
- 這次:`governance/eval/ablation_lumos_first.py:388-396` 的 `visible()` 原本走 `\xNN`/`\u`/`\U`,現在改成第三種 `⟦U+XXXX⟧`。
  - 它還要特判 `⟦` 本身(`:390`)才還原得回去,等於自己維護一套跳脫文法。
  - 判斷字元用 `isprintable()`、`Zs`,不是共用的 `_PATH_SPECIAL_CATS`,所以集合也不同。
- 隱患:專案裡「無損可見化」現在有 `\uXXXX` 與 `⟦U+XXXX⟧` 兩套,各自的字元集合與非 BMP 寫法都不同。
- 筆記的理由站不住:`ablation-lumos-first.md` 新增的 WHY(patch 第 23 行)只拿 `_esc_clean`(換空白)當對照,沒提 `_kill_esc` 這個真正的同類。
  - 它否決「反斜線序列」的理由是得把字面反斜線加倍。但 `_kill_esc` 就是反斜線序列,專案已接受那個取捨。
  - 若真要保留新寫法,筆記得改成對 `_kill_esc` 說明為什麼不用。
- 範圍:1 支程式(ablation 報表)、1 篇筆記。

## Finding ARCH7-02
severity: minor
blocking: 否
引句:「tmp_path = path.with_name(f".probe-out-{os.getpid()}-{secrets.token_hex(4)}.tmp")」
file: `scripts/lumos:19333`(`_write_lf` 暫存檔名)、`scripts/lumos:20431-20442`(帶上限的 O_EXCL 遞增序號)
- 結構一致:暫存檔用 `O_EXCL` 加 `0o666` 建立、讓 umask 自己生效;失敗時 `BaseException` 清暫存檔再重拋;最後 `os.replace`。這些都跟 `_write_lf` 同款(`scripts/lumos:19334-19346`)。r6 抓到的 umask 問題已經修回與 `_write_lf` 一致。
- 命名不同:`_write_lf` 是 `{name}.{pid}-{uuid8}.tmp-wlf`,探針是 `.probe-out-{pid}-{token}.tmp`。這是刻意為了不讓檔名超過 255 bytes,docstring 有說,我不算它第二種做法。
- 迴圈不同:探針多了無上限的 `while True` 加 `except FileExistsError: continue`。
  - `_write_lf` 沒有這種迴圈。
  - `scripts/lumos:20442` 的同類 O_EXCL 迴圈有上限 99 防異常迴圈。
  - 這個重試用的隨機名撞到的機率極低,但專案慣例是帶上限,這裡沒有。
- 另外:探針加了 `O_NOFOLLOW`(`_write_lf` 沒有),權限處理改用 `keep_mode` 加 uid、`st_nlink` 條件(`scenario_probe.py:92-93`),不是 `_write_lf` 的 `copymode`。筆記有交代理由,屬於需求不同。

## Finding ARCH7-03
severity: minor
blocking: 否
引句:「old.st_uid == _euid() and old.st_nlink == 1 else None)」
file: `scripts/test_lumos.py:9981`、`scripts/test_autonomous_loop.py:1588`(鄰居直接用 `os.geteuid()`,測試以 root 判斷跳過)
- 既有:專案其他地方直接呼叫 `os.geteuid()`,測試端用 `hasattr(os, "geteuid")` 或 `skipIf` 處理 root。
- 這次:`scenario_probe.py:27-29` 多包了一個只為測試換掉的 `_euid()`,測試用 `patch.object(mod, "_euid", ...)`(patch 第 370 行)。
- 這是命名與測試縫的寫法不同,結構沒問題。同檔的 `os.access` 與 `st_uid` 判斷沒有包同樣的縫,所以只有這一處有。

## 三問

**1. 分層與依賴方向:對齊。**
- 新碼放在 `scripts/scenario_probe.py` 的原子寫入、輸出檢查層(`_output_target_problem` 在 `:32`,`_atomic_write_bytes` 在 `:67`),`main` 呼叫它們。
- ablation 腳本從 scripts 匯入探針的原子寫入,這個依賴方向早就有(`ablation_lumos_first.py:29`,用 `sys.path.insert` 加 ROOT/scripts)。這次只是把本地的 `_atomic_write_text` 包裝刪掉、改成一起匯入,是收斂,不是跨層直呼。
- 沒有新增反向依賴。探針沒有去 import `scripts/lumos`,所以原子寫入有自己一份,不是這次才有的,而且程式裡有註明參照 `_write_lf`。

**2. 命名與錯誤處理:大致對齊,有 ARCH7-03 一處小差異。**
- 錯誤回傳:`OSError(errno.EINVAL, 訊息, 路徑)` 與 `PermissionError(errno.EACCES, …)`(`scenario_probe.py:85`、`:90`)是標準三參數形式,並改用 errno 常數取代原本的 13。`ablation_lumos_first.py:538` 也用 `errno.EACCES` 等常數,兩邊一致。
- `_output_target_problem` 回字串或 None,開跑前由 `main` 轉成 `print("✗ …", file=sys.stderr); return 2`,跟同檔 `:1131-1151` 的參數檢查一致。
- 日誌:沒有新增日誌通道。
- `⟦U+XXXX⟧` 的差異見 ARCH7-01。

**3. 第二種做法:有一處,在 ARCH7-01(`⟦U+XXXX⟧`)。**
- 暫存檔與 O_EXCL 的寫法與 `_write_lf` 一致,只在命名與迴圈上限有小差異(ARCH7-02)。
- 合併段(第 539 行以後)主要是把兩邊新增的條目並列。
  - MOC 清單、`codex-harness` 的 `verified_by` 與 PITFALL、`pitfalls-code-loop` 的 WHY 與 PITFALL、`skills/lumos-code-loop/SKILL.md` 新增的「五次修復試行」一條,都是疊加,沒有兩套互相競爭的流程。
  - SKILL.md 那條只指向 `reference.md` 與計劃筆記。
- 我沒看到競爭的流程說明。⚠ `skills/lumos-code-loop/SKILL.md` 的合併段在 patch 裡只截到標頭與一條新增項,上下文不完整,「有沒有第二套流程」我只能說在可見範圍內沒有,交編排者確認。
- 另外 `Verification/持久用量帳第五輪修補驗證.md:21` 仍寫「控制字元改成可見的 `\xNN`」。它不在這份 patch 的修改範圍內,屬歷史驗證紀錄。若 ARCH7-01 保留新寫法,可以順手標註已被取代。

總結:不對齊共 3 條,其中重大 1 條
