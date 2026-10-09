severity: minor

## Finding ARCH5-01
severity: minor
blocking: 否
引句:「def _atomic_write_text(path, content):」
file: `governance/eval/ablation_lumos_first.py:26`(同檔 :51 另有 `_atomic_write_text`;其餘既有實作 `governance/eval/retrieval_eval_multiword.py:235`、`scripts/lumos:14934`、`scripts/lumos:35341`、`governance/eval/refresh_labels.py:51`)
- 這份 diff 在 `scripts/scenario_probe.py` 新增的 `_atomic_write_text`,演算法跟 `ablation_lumos_first.py` 已有的 `_atomic_write_bytes` 逐行相同。兩支都是 lstat 取普通檔權限、`NamedTemporaryFile(dir=path.parent, prefix=path.name+".", delete=False)`、`fchmod`、`fsync`、`os.replace`、`finally` 清暫存。
- `ablation_lumos_first.py:55-58` 已經從 `scenario_probe` import 判準,並寫明「判準單一實作來源」。這個原子寫入卻沒有照做,多了一份同樣的拷貝,而不是留一份讓另一份 import。
- 全 repo 的原子寫入實作變成 6 種以上寫法(mkstemp 加 chmod、`O_EXCL` 加 `copymode`、`NamedTemporaryFile` 加 `fchmod` 等),repo 內沒有共用工具。新碼選的是 `ablation_lumos_first.py` 那一種,不算新發明。
- 判成 minor 而不是 major 的理由:沒有引入新的演算法,只是把既有演算法再抄一份。依嚴重度錨,「重複既有工具」可以升 major,但這裡沒有單一既有工具可以重複。⚠ 交編排者裁決:要不要把它算成「第二套」。

## Finding ARCH5-02
severity: minor
blocking: 否
引句:「return re.sub(r"([\\`*_\[\]()!|])", r"\\\1", html.escape(raw))」
file: `scripts/lumos:9765`(`_esc_clean`,另一種消毒控制字元的寫法);`governance/eval/ablation_lumos_first.py:70`(用 `isprintable()` 驗題號)
- `render_md` 的 `text()` 原本是 `html.escape` 加 `|` 跳脫和換行換空格。新版多做兩件事:非可印字元轉成 `\xNN`/`\uNNNN`,再用 regex 反斜線跳脫 Markdown 特殊字元。
- repo 裡沒有其他 Markdown 報表會做這個跳脫。`home_audit.py`、`retrieval_eval_multiword.py`、`rule_conflict_scan.py` 我 grep 過,都沒有 `html.escape` 或 `isprintable` 的跳脫碼。所以沒有同層對照,這是 repo 第一個 Markdown 文字跳脫器。
- 消毒終端控制字元在 repo 裡還有另一種寫法:`scripts/lumos:9765` 把控制字元換成空格並截斷。新碼改成轉成可見的 `\xNN`。兩者目的相同,做法不一致。
- 「題號用 `isprintable()` 拒收」(`ablation_lumos_first.py:70`)也是第三種做法。
- 沒有既有做法可對齊,所以不判 major。⚠ 交編排者:這是無對照的新慣例。

## 三問

1. **分層與依賴方向:對齊。**
   - 新碼都放在同層的 eval 腳本和探針腳本。`scenario_probe.py` 是底層,`ablation_lumos_first.py` 往它 import,兩者方向沒變。
   - `_atomic_write_text` 只在探針 `main()` 裡被呼叫(`scripts/scenario_probe.py:1314`),沒有跨層直呼。
   - `scripts/lumos` 只改了 `os.open` 加 `O_NOCTTY`,在原函式內。

2. **命名與錯誤處理:大致對齊。**
   - `_atomic_write_text` 與 `ablation_lumos_first.py:51` 同名,私有底線前綴也一致。
   - 錯誤處理(`finally` 清暫存、不吞例外)與 `ablation_lumos_first.py:26-47` 一致。與 `retrieval_eval_multiword.py:243` 以及 `scripts/lumos:14950` 的 `except BaseException` 加 unlink 寫法不同。這兩種寫法在 repo 裡本來就並存,屬於鄰居自己不一致。
   - `scenario_probe.py` 其餘寫檔仍用 `Path.write_text`(例如 :470、:617、:648),只有 `--out` 改成原子寫。這是刻意針對輸出符號連結,不算不對齊。
   - 日誌方式沒有改動。等待訊息的 `print(..., flush=True)` 沿用原寫法。

3. **第二種做法:有兩處,但都沒有單一既有工具可對照。**
   - 原子寫入:是 `ablation_lumos_first.py` 的拷貝,見 ARCH5-01。
   - Markdown 跳脫:repo 沒有同類先例,見 ARCH5-02。
   - 表態記錄 py-external satisfied、py-memory satisfied、py-parallel satisfied,我看不出這份 diff 與它們矛盾。上述發現屬於「重複既有」,不是效能或資源題,所以不寫成張力。

不對齊共 2 條,其中 major 0 條
