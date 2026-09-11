severity: major

### F4 根目錄的替代字元會讓 deinit 刪到另一個專案
severity: major
blocking: 是 — 解碼後的路徑直接成為刪除目標，會刪除使用者未指定專案的圖譜。
引句:「["git", "rev-parse", "--show-toplevel"], text=True, errors="replace",」
file: `scripts/lumos:12779` 以替代字元解碼專案根目錄。
file: `scripts/lumos:12799` 用解碼後的根目錄尋找圖譜。
file: `scripts/lumos:12852` 對找到的圖譜呼叫 `shutil.rmtree`。

1. 在使用 UTF-8 的 Linux 上，若專案目錄位元組為 `/repos/p-\xff`，另有已安裝 Lumos 的 `/repos/p-�`，從前者執行 `deinit --yes` 會選中後者並刪除其圖譜。
2. 以下唯讀單元重現模擬 git 輸出與已安裝狀態，攔截所有寫入入口：

   ```sh
   python3 -B -c '
   import ast, sys, io, os
   from pathlib import Path
   from unittest.mock import patch
   tree = ast.parse(Path("scripts/lumos").read_text())
   fn = next(n for n in tree.body
             if isinstance(n, ast.FunctionDef) and n.name == "cmd_deinit")
   g = dict(Path=Path, sys=sys,
       _lumos_src=lambda _: Path("/toolchain"),
       _selfdelete_risk=lambda _: False,
       _vault_in=lambda r: r/"docs"/"t-knowledge",
       _deinit_detect_installed=lambda _: True,
       _claude_block_present=lambda _: True,
       _deinit_unbar_gate=lambda _: None,
       _deinit_strip_claude=lambda _: None,
       _deinit_remove_vendored=lambda *a: None)
   exec(compile(ast.Module(body=[fn], type_ignores=[]), "<review>", "exec"), g)
   removed = []
   def git(*a, **k):
       return io.TextIOWrapper(io.BytesIO(b"/repos/p-\xff\n"),
           encoding="utf-8", errors=k.get("errors", "strict")).read()
   with patch("subprocess.check_output", side_effect=git), \
        patch("shutil.rmtree", side_effect=lambda p: removed.append(os.fsencode(p))):
       g["cmd_deinit"](yes=True)
   assert removed == [b"/repos/p-\xff/docs/t-knowledge"], removed
   '
   ```

3. 實測翻紅：`AssertionError: [b'/repos/p-\xef\xbf\xbd/docs/t-knowledge']`，新版回傳成功並選錯刪除目標；同一重現套用修改前函式則回傳 2、沒有刪除呼叫。

### F5 新守衛將變數形式的程式名稱誤判為其他程式
severity: minor
blocking: 否 — 已重現守衛退化，但本輪 scripts/lumos 的現有 git 文字呼叫均已帶 errors，尚未形成現有呼叫的漏修。
引句:「return "other"   # 例如 sys.executable:跑的是 python / 工具自己」
file: `scripts/test_lumos.py:9912` 清單首元素只要不是字串常值，就直接判為其他程式。

1. 將以下原始碼字串傳入 `_text_git_calls_missing_errors`，第五行確實是缺少解碼容錯的 git 呼叫：

   ```python
   import subprocess
   def f():
       exe = "git"
       cmd = [exe, "show", "HEAD:x"]
       return subprocess.run(cmd, capture_output=True, text=True)
   ```

2. 實測第二輪守衛回傳 `[5]`，第三輪回傳 `[]`，斷言 `guard(sample) == [5]` 當場翻紅。
3. 此判法把無法直接辨識的首元素當成已確認的非 git 程式，違反新增守衛「看不出來也要抓」的規則。

F3:修出新洞 — `_sp_run_text` 已修，移除修正後守衛會抓到第 942 行，但新判法新增了 F5 的漏判。

總結:最高 severity major,blocking 共 1 條