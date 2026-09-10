severity: major

### F1 整個 hook／template 目錄被排除，漏掃消費專案自有程式
severity: major
blocking: 是 — 專案自己的風險改動被降成 standard，避開高風險審查要求。
引句:「return r in _VENDORED_TOOLKIT or any(r == d or r.startswith(d + "/") for d in _VENDORED_DIRS)」
file: `scripts/lumos:13139` 以目錄前綴直接判定檔案歸屬
file: `scripts/lumos:12978` 既有流程明確允許並保留這兩個目錄中的使用者自有檔

1. 消費專案自己的 `scripts/hooks/my_hook.py` 加入未關閉的 `open()`，會被當成 Lumos 安裝檔略過。
2. 以下唯讀測試只替換 git 輸出；預期兩處都為 high，實測依序為 high、standard，斷言翻紅。

```python
import runpy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

f = runpy.run_path("scripts/lumos")["_pitfall_diff_collect"]
for p in ("src/my_hook.py", "scripts/hooks/my_hook.py"):
    diff = f'--- /dev/null\n+++ b/{p}\n@@ -0,0 +1 @@\n+fh = open("x")\n'
    with patch("subprocess.run",
               return_value=SimpleNamespace(returncode=0, stdout=diff)):
        result = f("A..B", Path("/tmp"), no_lint=True)
    print(p, result["tier"])
    assert result["tier"] == "high"
```

### F2 lint 診斷繞過排除規則，vendored 檔仍會撐高分級
severity: major
blocking: 是 — 啟用 lint 的消費專案仍會因工具自己的檔案被判 high。
引句:「if (cur_file and _stack_changed_ok(cur_file, _skip_vendored)」
file: `scripts/lumos:17628` added 仍收錄被排除的檔案
file: `scripts/lumos:17704` lint 診斷只依 added 行號過濾，未套用 vendored 判別

1. 新排除只作用於內建 regex；專案宣告 Python lint 後，工具 hook 的診斷仍進入最終 claims。
2. 以下注入一筆 lint 診斷，預期 standard，實測 high；未執行外部 linter。

```python
import runpy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

f = runpy.run_path("scripts/lumos")["_pitfall_diff_collect"]
g = f.__globals__
p = "scripts/hooks/claude/_hookevent.py"
g["_lint_load_config"] = lambda _: {"py": ["lint {LINT_SARIF_OUT}"]}
g["_lint_aligned"] = lambda *a: True
g["_lint_run_and_parse"] = lambda *a: (
    [{"file": p, "line": 1, "source": "lint:fixture"}], True)
diff = f'--- /dev/null\n+++ b/{p}\n@@ -0,0 +1 @@\n+fh = open("x")\n'
with patch("subprocess.run",
           return_value=SimpleNamespace(returncode=0, stdout=diff)):
    result = f("A..B", Path("/tmp"))
print(result["tier"], result["claims"])
assert result["tier"] == "standard"
```

### F3 set 產生的純量無法再用 remove 清除
severity: major
blocking: 是 — 新的合法寫入流程會產生既有刪除入口無法處理的欄位。
引句:「fm[a:b + 1] = [f"about_code: {v}"]」
file: `scripts/lumos:10919` 帶值 remove 呼叫只接受清單的編輯函式
file: `scripts/lumos:10942` 不帶值 remove 又因 about_code 位於 LIST_KEYS 而拒絕

1. `set` 後，帶值 `remove` 拋出 scalar 型別錯誤，不帶值則回 rc2，且 `set ""` 也被新存在性檢查拒絕。
2. 以下只在記憶體保存欄位，預期 set→remove 成功，實測最後一行拋出 `ValueError: about_code 是scalar型欄位`。

```python
import runpy
from pathlib import Path
from types import SimpleNamespace

m = runpy.run_path("scripts/lumos")
g = m["cmd_set"].__globals__
state = ["---", "type: system", "about_code: []", "---", "# N"]
g["load_raw_for_edit"] = lambda _: (state[:], 1, 3)
g["atomic_write_verify"] = lambda p, lines, *a: state.__setitem__(
    slice(None), lines)
env = SimpleNamespace(vault=Path.cwd())
assert m["cmd_set"](env, "N.md", "about_code", "scripts/lumos") == 0
assert m["cmd_remove"](env, "N.md", "about_code", "scripts/lumos") == 0
```

### F4 既有欄位覆寫跳過引號處理，會寫出無效 YAML
severity: major
blocking: 是 — 合法 POSIX 檔名能通過工具自驗，卻破壞筆記的 YAML 欄位區塊。
引句:「fm[a:b + 1] = [f"about_code: {v}"]」
file: `scripts/lumos:10824` 已有欄位時直接插入原始值
file: `scripts/lumos:10587` 既有 fmt_scalar 會替含冒號加空白的值加引號

1. 專案存在 `src/a: b.py` 時，空範本被寫成 `about_code: src/a: b.py`，標準 YAML parser 會拒絕整段欄位。
2. 以下保留真正的寫前自驗，只替換檔案存在狀態與最終寫入；預期 YAML 解析成功，實測 `Psych::SyntaxError` 並使斷言翻紅。

```python
import runpy, subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

f = runpy.run_path("scripts/lumos")["_set_about_code"]
g = f.__globals__
state = ["---", "type: system", "about_code: []", "---"]
g["_vault_repo_root"] = lambda _: Path("/virtual/repo")
g["load_raw_for_edit"] = lambda _: (state[:], 1, 3)
output = []
class Captured(Exception): pass
def capture(path, text):
    output.append(text)
    raise Captured()
g["_write_lf"] = capture
with patch.object(Path, "exists",
                  lambda p: str(p) == "/virtual/repo/src/a: b.py"):
    try:
        f(SimpleNamespace(vault=Path("/virtual/repo/kg")),
          "N.md", "src/a: b.py")
    except Captured:
        pass
line = output[0].splitlines()[2]
print(line)
r = subprocess.run(
    ["ruby", "-ryaml", "-e", "YAML.safe_load(ARGV[0])", line],
    capture_output=True, text=True)
print(r.stderr)
assert r.returncode == 0
```

### F5 存在性檢查放行 repo 外路徑，也未統一儲存格式
severity: minor
blocking: 否 — 欄位可成功寫入，但與後續使用的 repo 相對路徑對不上。
引句:「if not v or not (root / v).exists():」
file: `scripts/lumos:10814` 未檢查解析後的路徑是否位於 repo 內
file: `scripts/lumos:19527` 讀側只移除 ./，不轉換絕對路徑或折疊 ..

1. 唯讀攔截最終寫入實測，`/etc/hosts`、本 repo `scripts/lumos` 的絕對路徑，以及 `scripts/../scripts/lumos` 全部通過真正的寫前檢查。
2. 後兩者建立的 about_code 計數鍵都不是 `scripts/lumos`，因此正常的相對路徑查詢拿不到對應的排序加分。

### F6 新事故筆記把排序欄位誤記成波及連結入口
severity: minor
blocking: 否 — 用途記載與實際行為矛盾，會誤導後續修復及驗收。
引句:「改那個檔的時候才找得到這篇。」
file: `docs/lumos-toolchain-knowledge/Issues/健檢技術棧那段撞到多平台設定就整支中斷.md:86` 將找得到筆記歸因於 about_code
file: `scripts/lumos:19520` about_code 僅替已進候選集的節點加分
file: `scripts/lumos:1456` S4 明示 about_code 不建連結，波及計算認正文路徑

1. 本文及新增測試註解把壞 about_code 描述成波及計算失聯，但修正欄位本身不會建立缺少的正文連結，也不能證明合約測試重新被納入。

### F7 唯一寫入口的宣稱與仍可使用的 append 矛盾
severity: minor
blocking: 否 — 文件宣稱的存在性保障未涵蓋另一個公開寫入口。
引句:「about_code 的唯一寫入口(2026-09-10)。」
file: `scripts/lumos:10533` about_code 仍在 append 白名單
file: `scripts/lumos:10888` append 直接編輯欄位，未執行路徑存在檢查

1. 對仍為 `about_code: []` 的範本，`append <節點> about_code src/missing.py` 仍能寫入不存在的路徑，因此 set 並非唯一入口，新增存在性檢查也不是欄位的統一保障。

風險掃描清單：誤報 — `scripts/lumos:17562` 的 `open(...)` 位於 docstring，沒有開啟檔案控制代碼。

總結:最高 severity major,blocking 共 4 條
