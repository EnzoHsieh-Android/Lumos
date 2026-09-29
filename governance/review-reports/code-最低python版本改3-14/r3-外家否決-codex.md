severity: major

## F1 非釘選候選仍可把假 Python 當成 launcher，讓掛鉤假綠

severity: major  
blocking: 是 — 假 launcher 能令應阻擋的 pre-commit/pre-push 檢查直接回 0，安裝器也能未安裝卻成功退出。  
引句:「# (post-commit 直接把程式交給它跑,不經 lumos 驗;設成 /usr/bin/true 會假成功、漏寫跳過帳);不合格就記下原因往下找,」  
file: `scripts/hooks/pre-commit:72`

1. 新探針只驗證 `LUMOS_PYTHON` 分支；`python3.14`、`python3.15`、`python3.16`、`python3`、`python`、`py` 仍只信 `command -v`，不要求絕對路徑，也不驗證真是 Python。七份 launcher 都相同。

2. `pre-commit`/`pre-push` 接著只要求該候選執行 `lumos python-path` 時回 0 且最後一行非空。假候選印出 `/usr/bin/true` 後，後續所有 lumos gate 都由 `true` 執行並成功放行。

3. 最小重現：

```sh
launcher="$(sed -n '/# ── python-launcher begin/,/# ── python-launcher end ──/p' scripts/hooks/pre-commit)"
resolver="$(sed -n '/# ── python-314 begin/,/# ── python-314 end ──/p' scripts/hooks/pre-commit)"
LAUNCHER="$launcher" RESOLVER="$resolver" REPO_ROOT="$PWD" /bin/bash -c \
'python3.14(){ printf "%s\n" /usr/bin/true; }; eval "$LAUNCHER"; eval "$RESOLVER"; unset LUMOS_PYTHON; _lumos_py314; printf "launcher=%s\nLUMOS_PY=%s\n" "$_LUMOS_ANY_EXE" "$LUMOS_PY"; "$LUMOS_PY" "$REPO_ROOT/scripts/lumos" doctor --ci; printf "gate_rc=%s\n" "$?"'
```

輸出：

```text
launcher=python3.14
LUMOS_PY=/usr/bin/true
gate_rc=0
```

4. `t_hooks_block_without_python314` 新增的 ⑦b 只覆蓋釘選分支，沒有對其餘候選做同一個「絕對路徑＋Python 記號」翻紅測試，因此原始假成功根因仍存在。

## F2 Windows 目前目錄檢查會被 symlink 的 realpath 繞過

severity: major  
blocking: 是 — repo 根的候選 symlink 可被當成合法直譯器執行，正中「執行到不該執行的檔」。  
引句:「if os.path.normcase(os.path.dirname(os.path.realpath(found))) == here:」  
file: `scripts/lumos:127`

1. 判斷候選是否位於目前目錄時，程式先對 `found` 做 `realpath`。若 `/repo/python3.14.exe` 是指向 `/repo/tools/evil.exe` 的 symlink，檢查比較的是 target 所在的 `/repo/tools`，因此放行 lexical location 就在 repo 根的候選。

2. 放行後 `_py_probe` 會執行該檔。它只需印出形如 `OK <絕對路徑>`，就能控制重跑目標並造成命令假成功。

3. 以下用 mock 精確模擬 Windows `shutil.which` 找到 CWD symlink、`realpath` 指向子目錄，直接呼叫本版 `_py_which`：

```sh
/opt/homebrew/bin/python3 -c 'import runpy,os,shutil; from unittest.mock import patch; m=runpy.run_path("scripts/lumos",run_name="lumos_review"); f=m["_py_which"]; old=os.name; os.name="nt"; rp=lambda p:"/repo/tools/evil.exe" if str(p).endswith("python3.14.exe") else "/repo"; p1=patch.object(shutil,"which",return_value="/repo/python3.14.exe"); p2=patch.object(os,"getcwd",return_value="/repo"); p3=patch.object(os.path,"realpath",side_effect=rp); p1.start(); p2.start(); p3.start(); print(f("python3.14")); p3.stop(); p2.stop(); p1.stop(); os.name=old'
```

輸出：

```text
/repo/python3.14.exe
```

4. 位置判斷必須使用 `found` 的 lexical absolute parent；解析 target 可另做存在性檢查，但不能拿來決定候選是否源自目前目錄。

## F3 uv 非零退出仍被誤報成正常找不到版本

severity: minor  
blocking: 否 — 解析結果不變，但錯誤分類違反本輪修正聲稱，會把壞旗標、權限或損壞安裝導向錯誤排查。  
引句:「return None, "uv 找不到 3.14"」  
file: `scripts/lumos:184`

1. `_py_uv_find` 只把 `TimeoutExpired` 與 `OSError` 分成執行失敗；凡 uv 真正啟動後以非零碼退出，一律丟棄 stderr 並回報「找不到 3.14」。

2. 例如舊版 uv 對 `--system` 回 `rc=2, stderr="unexpected argument"`，本版實際結果仍是：

```text
(None, 'uv 找不到 3.14')
```

3. 這與新增 docstring「執行失敗、逾時、正常回答但沒有 3.14 分開」不一致；非零退出至少要保留回傳碼及 stderr，只有確定的 no-match 才能報找不到版本。

## F4 Claude 自家目錄判斷只是後綴比對，外部同名掛鉤仍會被探測

severity: minor  
blocking: 否 — doctor Q 是軟提醒，但會重新產生本輪原本要消除的外部掛鉤誤報與額外執行。  
引句:「if (base in ours and (d.endswith("/.claude/hooks") or d == codex_dir)」  
file: `scripts/lumos:19951`

1. 規格要求 Claude 掛鉤位於當前使用者的 `~/.claude/hooks`；`d.endswith("/.claude/hooks")` 卻接受任意 `/tmp/foreign/.claude/hooks`、其他使用者家目錄，以及 Codex 設定中的 Claude 路徑。

2. 例如設定命令為 `/missing/python3.13 /tmp/foreign/.claude/hooks/impact-hook.py` 時，檔名命中 `ours`、目錄後綴也命中，`_hook_python_problems` 會執行第一段探針並要求重跑 Lumos install；install 不會改動該外部命令。

3. Claude 與 Codex 的目錄條件也沒有依 `fam` 分開，因此兩家的路徑可交叉命中。應精確接受目前 `home/.claude/hooks`、`${HOME}/.claude/hooks`，或該次掃描對應的 Codex hooks 目錄。

## 其餘 hunks

- `get.ps1`：已看,無 finding。
- 七支 shell 檔經 `bash -n`：已看,無 finding。
- `scripts/lumos` 經 macOS Python 3.9 語法解析：已看,無 finding。

最高 major，blocking 共 2 條。