severity: major

1. 另寫了一份「取 git common dir」,沒用既有的 `_lens_git` 和 `_events_root`
severity: major
blocking: 是
引句:「r = subprocess.run(["git", "-C", str(p), "rev-parse", "--path-format=absolute", "--git-common-dir"],」
file: `scripts/lumos:25567-25576`(`_events_root`);`scripts/lumos:45955-45967`(`_lens_git`)
- `_events_root` 做的是同一件事:`_lens_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir", timeout=3)`,而且它同樣在 `enforcement` 開場被呼叫。
- 新增的 `_common` 巢狀函式把命令、逾時處理、`returncode` 判斷、`strip` 全部重寫了一遍。
- 專案裡 `_lens_git` 是 git 呼叫的統一入口,只回傳 None 或結果。新碼改用 `except Exception`,逾時定成 10 秒。`_events_root` 刻意把逾時壓到 3 秒,並註明「enforcement 每次開場都跑,git 卡住時只讓這一列退回原根」。`enforcement_status` 本來就是在這個預算內跑的,新碼卻放大到每個工作樹最多 10 秒。
- 這個函式一次要解兩個路徑(`root` 和 `other`),最壞情況會是 20 秒。
- 建議:改成 `_lens_git(p, "rev-parse", "--path-format=absolute", "--git-common-dir", timeout=3)`。若想連「取上一層」也共用,就拆出一個共用的 common-dir helper,讓 `_events_root` 也呼叫它。

2. 比對兩檔內容另寫 `_same_bytes`,沒用專案已用的 `filecmp`
severity: minor
blocking: 否
引句:「return Path(a).read_bytes() == Path(b).read_bytes()」
file: `scripts/lumos:22815-22828`(`_vendored_pending` 用 `filecmp.cmp(s, t, shallow=False)` 做逐位元組比對);`scripts/lumos:46967`(另有一處 `lock.read_bytes() == data`)
- 專案裡沒有名叫「比對兩檔」的現成 helper,只有 `filecmp.cmp(..., shallow=False)` 這個慣用法。所以我判 minor,不判 major。
- 結構上沒越層,新函式放在 `_hooks_path_*` 旁邊,位置合理。
- 差別在記憶體:`read_bytes` 會把兩份檔整個讀進記憶體,`filecmp` 不會。pre-commit 和 pre-push 都是小檔,影響很小。
- 錯誤處理也不同。`filecmp.cmp` 遇到 OSError 會直接拋出,新碼吞掉回 False。這份吞例外的寫法在 `enforcement_status` 外層的 `try/except` 裡反而多餘,而且 `add(layer, "unknown", str(e))` 的路徑本可以接住它。

3. 命名與模組級 import 與鄰居不一致
severity: minor
blocking: 否
引句:「def _hooks_path_sibling_worktree(root, val):」
file: `scripts/lumos:22034`(`_hooks_path_is_ours(root: Path, val: str) -> bool`)
- 同一組的 `_hooks_path_dir` 和 `_hooks_path_is_ours`、旁邊的 `_deinit_unbar_gate(root: Path) -> int`,都帶型別註記。新增的兩個函式都沒有。
- 新函式回傳 `Path | None`,卻沒標。
- `_same_bytes` 這個名字太通用,檔案裡另有 `_same_local_path`、`_same_decision` 等同前綴函式,語意各異,容易讓人誤會它是共用工具。

**逐問回答**

**問 1,分層與依賴方向。** 新碼放在 `_hooks_path_is_ours` 旁邊,位置對。`enforcement_status` 呼叫它,方向也一致。刻意不放寬 `_hooks_path_is_ours`,理由寫在 WHY 筆記裡,我認可。
- 不一致的是依賴對象:同檔已有 `_events_root` 和 `_lens_git` 這條「取 git common dir」的路徑,新碼不依賴它們,自己直呼 `subprocess`(見 finding 1)。
- 層⑥、⑦也沒有越層的呼叫。
- 新增的 `sib` 提前算出,以及在迴圈裡 `continue` 另走一支,與 `_enforcement_prepush_gated` 當初「為了不加 `enforcement_status` 分支數而拆出去」的做法相反。這在 `enforcement_status` 內多加了一個分支,但屬結構偏好,不列為 finding。

**問 2,命名與錯誤處理。**
- 命名與型別註記見 finding 3。
- subprocess 呼叫參數 `capture_output=True, text=True, errors="replace", timeout=...` 與鄰居一致。
- 但 `except Exception` 和 `timeout=10`,與 `_lens_git` 的 `except (OSError, TimeoutExpired)` 和 3 秒預算不同(見 finding 1)。
- 測試用 `_sp`/`_tf`/`_sh` 別名、`_need_src`、`check(...)` 和 `gctl-` 前綴暫存目錄,都與 `t_hooks_path_forms_all_recognized` 一致。測試最後 `rmtree` 清理也符合慣例。

**問 3,第二種做法。** 有,見 finding 1,這是 major。「判兩個路徑是否同一 repo / 取 common dir」在 `_events_root` 與 `_lens_git` 已有統一做法。
- 查過的 grep 命中點:`git-common-dir` 在 `scripts/lumos` 只出現兩處,即 `_events_root`(25567-25570)和這次新增(22047、22055)。
- 比對兩檔內容的 `filecmp` 和 `read_bytes() ==` 各有既有用法(finding 2)。
- 兩處都可以沿用既有做法,不需要新增。
- python-idioms skill 在 `/Users/enzo/.claude/skills/python-idioms`。我沒有逐條對照,所以這份回答不依賴它。

不對齊共 3 條,其中 major 1 條
