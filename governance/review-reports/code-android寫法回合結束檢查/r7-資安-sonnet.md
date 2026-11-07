severity: clean

我核對了第六輪資安席的兩條發現,也看了這輪新增的程式,沒有找到新的可利用洞。

**F1(三支 shell 掛鉤 PATH 空項)已修好。**
- 我把新的 path-clean 段單獨在 bash 跑了八組 PATH:`:/usr/bin`、`/usr/bin::/bin`、`/usr/bin:`、`.`、`~/x:/usr/bin`、空字串、`/usr/bin:./`、`/usr/bin: :/bin`。
- 每組都只剩絕對項,`command -v git` 都落在 `/usr/bin/git`。
- 我另外在臨時 repo 的根放了會寫記號的假 `git` 和假 `python3.14`。
- 把這輪的三支掛鉤複製進去、用 `PATH=":/usr/bin:/bin"` 以 `/bin/bash` 跑,記號檔都沒出現,假檔沒被執行。
- 對照組(用 HEAD 的舊 pre-commit 重現原本的攻擊)沒跑成:舊 pre-commit 在我的最小 repo 裡沒走到找 python 那步。所以「修前確實會中」這件事我沒有親眼重現。
- `_lumos_any_python` 取到相對路徑就回失敗,且不再往後試其他候選,是失敗即封閉。

**F2(旗標檔天花板)**
- assume-unchanged 與 skip-worktree 的檔不比對工作樹,現在已寫進計劃天花板第 4 條。
- 要讓檔帶這兩個旗標,得有人在本機對索引下 `git update-index`,clone 下來的 repo 帶不進來,所以不是陌生專案能打的洞。

**新函式與逐字複本沒有新增讀工作樹內容的 git 指令。**
- `_rel_in_project` 只用字串運算,加上對專案根與 repo 根兩個目錄做 `resolve()`。
- `_git_status_entries` 只多了一道濾掉專案外條目的步驟。
- 這道濾網只會讓點名變少,不會多執行任何東西。
- 路徑不可能是絕對路徑或 `..`,因為 `_rel_in_project` 會拒掉 `/` 與 `..` 開頭的,git 本身也產不出。
- `hash-object`、`ls-files --debug` 與 `--worktree-nofilter` 的程式這輪沒動。

**測試檔(`test_lumos.py`)**
- 新測試只在 `tempfile.mkdtemp` 的臨時目錄裡跑。
- 它們放假 `git`/`python3.14` 的對象是自己複製出來的 repo,沒有真憑證,也沒有外部輸入拼進命令。

**逐類**
- ①提示注入:已看,無。
- ②讀寫與執行越界:已看,無。
- ③非刻意繞過:已看,無。

**範圍外,不報。** 第一行 `#!/usr/bin/env bash` 在 PATH 洗淨前就被解析,已記在計劃天花板第 9 條,依你裁定的環境層範圍不報。

臨時目錄 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/資安-sonnet/t` 已用字面絕對路徑刪除,我沒有改 repo。

總結:最嚴重的是沒有發現,會擋 0 條。
