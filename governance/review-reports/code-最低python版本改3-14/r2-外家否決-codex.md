severity: major

## F1 共用 launcher 把任意可執行檔當 Python，會假成功並漏寫帳

severity: major  
blocking: 是 — 無效或相對的 `LUMOS_PYTHON` 會在驗證前被執行，安裝器可回 0 卻沒安裝，post-commit 也可回 0 卻沒留下跳過帳。  
引句:「if [ -n "${LUMOS_PYTHON:-}" ] && [ -x "$LUMOS_PYTHON" ]; then _LUMOS_ANY_EXE="$LUMOS_PYTHON"; return 0; fi」  
file: `install.sh:12`  
file: `install.sh:37`  
file: `scripts/hooks/post-commit:102`  
file: `scripts/hooks/post-commit:133`

1. 這裡只檢查 `-x`，沒有落實 S1 的「必須是絕對路徑且確實是 Python」。例如 `/usr/bin/true` 會被七份 launcher 接受；`install.sh` 隨後 `exec true ...`，整支安裝器回 0 但什麼都沒安裝。

2. `post-commit` 不會再呼叫 lumos 驗證版本，而是直接把 Python 程式經 stdin 交給該檔。若選到 `/usr/bin/true`，程式完全沒執行，hook 卻繼續印「記下了」，使 `--no-verify` 帳靜默缺失。

3. 最小重現：

```sh
sed -n '/# ── python-launcher begin/,/# ── python-launcher end ──/p' install.sh |
env LUMOS_PYTHON=/usr/bin/true bash -c 'source /dev/stdin; _lumos_any_python; "$_LUMOS_ANY_EXE" - <<"PYEOF"
print("PYTHON_RAN")
PYEOF
rc=$?; printf "selected=%s rc=%s\n" "$_LUMOS_ANY_EXE" "$rc"'
```

輸出沒有 `PYTHON_RAN`，但仍成功：

```text
selected=/usr/bin/true rc=0
```

4. 相對路徑也被直接接受；實測 `LUMOS_PYTHON=install.sh` 得到 `selected=install.sh kind=RELATIVE`。因此全域設成相對名稱時，陌生 repo 裡的同名可執行檔會在絕對路徑檢查前先被執行。

## F2 自家掛鉤只比檔名，別家的同名掛鉤仍會被誤認

severity: minor  
blocking: 否 — 只造成 doctor 與 enforcement 的錯誤診斷，不會擋提交。  
引句:「if (len(parts) >= 2 and parts[1].replace("\\", "/").rsplit("/", 1)[-1] in ours」  
file: `scripts/lumos:19936`

1. 判斷只比較第二個參數的 basename，沒有確認它位於 `~/.claude/hooks` 或 Codex hooks 目錄。別的工具只要也叫 `lumos-entry-hook.py`，便被當成 Lumos 自家掛鉤。

2. 輸入命令 `/usr/bin/python3 /opt/other/lumos-entry-hook.py` 時，實際 `_hook_python_problems` 回傳：

```text
([('claude', '/usr/bin/python3', '版本 3.9.6,低於 3.14')], ['claude 的掛鉤註冊的是 /usr/bin/python3:版本 3.9.6,低於 3.14'])
```

3. doctor 因此要求重跑 `lumos install`，但安裝不會改動 `/opt/other` 的外部掛鉤，上一輪要求的「只看 Lumos 自家掛鉤」仍未修到根上。

## F3 uv 逾時或執行失敗被謊報成找不到 3.14

severity: minor  
blocking: 否 — 擋下結果正確，但候選診斷不符合 S2，會把執行故障誤導成版本不存在。  
引句:「tried.append((desc, "uv 找不到 3.14"))」  
file: `scripts/lumos:176`  
file: `scripts/lumos:200`

1. `_py_uv_find` 對 `TimeoutExpired`、`OSError`、總時限耗盡及正常的「無匹配版本」全部回傳同一個 `None`。

2. 新分支將所有 `None` 固定記成「uv 找不到 3.14」。輸入一支存在但卡住五秒、沒有執行權限或啟動失敗的 `uv`，輸出仍宣稱它正常執行但沒有找到版本，沒有列出該候選的真實結果。

## 已看，無 finding

1. README 中英文與升級／Codex 重新信任說明已看，無 finding。

2. pre-push「只推刪除也擋」註解、CI setup-python 提示、doctor 問題數比對已看，無 finding。

3. `_py_which` 的目前目錄排除、Windows launcher 絕對路徑執行、3.9 前置 import 清單已看，無其他 finding。

4. 七份 launcher 清單漂移測試、舊文法與 doctor 測試修正已看，無其他 finding。實跑確認九支檔案可由 Python 3.9 編譯，七支 shell 腳本均通過 `bash -n`。

總結:最高 major，blocking 共 1 條。