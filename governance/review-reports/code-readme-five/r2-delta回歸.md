# code-readme-five r2 delta 回歸審查

範圍:`governance/review-reports/code-readme-five/r2-snapshot.patch`(r1 findings 修法 delta)。逐 hunk 讀完,並在 `/private/tmp/.../scratchpad` 下建臨時 git repo,直接跑 repo 內真正的 `scripts/hooks/pre-commit` / `scripts/hooks/post-commit` 二進位重現,不是憑讀碼推論。

## 1. `git show ":$path"` 對含引號/控制字元的檔名會查不到內容,靜默放行(major)

`is_shebang_code()` 用 `git show ":$path"`(pre-commit)/`git show "HEAD:$path"`(post-commit)去讀 staged/commit 內容首行。但 `$path` 來自 `git -c core.quotePath=off diff --cached --name-only` 的**顯示用**輸出——`core.quotePath=off` 只關掉「非 ASCII 位元組」的引號化,雙引號、反斜線、控制字元(換行等)不論設定為何**一律**被 git 轉成 `"...\"..."` 這種帶跳脫的顯示形式(git 官方文件明載)。把這個顯示形式原樣塞回 `git show ":<顯示形式>"` 對不到真正的索引路徑,`first` 讀成空字串,`[[ "" == "#!"* ]]` 為假,函式回 false——一個真的無副檔名 shebang 腳本,只因檔名裡有個雙引號,就被判定「不是程式碼」。

已用 repo 內真正的 `scripts/hooks/pre-commit` 重現:staged 檔 `bin/weird"tool`(內容 `#!/bin/dash\necho hi\n`)在源 repo 模式下 `bash scripts/hooks/pre-commit` 回 rc=0(放行);把同一內容存成不含引號的 `bin/weirdtool` 則正確回 rc=1(擋下,印出「擋下:這次 commit 改了程式碼…」)。兩者唯一差異是檔名有無雙引號,證明是這個查找路徑本身的問題,不是我讀錯。

此洞不是 r2 這次改到的行(`git show ":$path" …` 這一行在 diff 裡是未動的 context,r1 就已存在),但 r2 的兩處 fix 都圍著這行改、且指名要我探這條路徑,所以在此提出。更值得注意的是:`post-commit` 的 `is_shebang_code()` 用同一套邏輯(`git show "HEAD:$path"`)去判斷要不要記 bypass 事件——同一個查找失敗,代表這類檔名連 post-commit 的「至少留痕」補償機制都會一起失效,不只是 pre-commit 沒擋,是**擋跟記都沒有**,完全無痕。

severity: major
blocking: 否
引句:「local first; first="$(git show ":$path" 2>/dev/null | head -c 200 | head -n 1)" || return 1」
file: `scripts/hooks/pre-commit:125`

## 2. 雙前導點檔名(`..foo` 型)只脫一層點,被誤判成「有副檔名」而跳過 shebang 檢查(minor)

`${base#.}` 只移除**一個**前導 `.`。逐一驗證(bash 實測,見下表):

| 輸入 `path` | `base` | `${base#.}` | 結果 |
|---|---|---|---|
| `..` | `..` | `.` | 判「有副檔名」(`.` 能配上 `*.*`,因兩個 `*` 都可配空字串) |
| `.` | `.` | (空) | 繼續看 shebang |
| `.tar.gz` | `.tar.gz` | `tar.gz` | 判「有副檔名」——正確 |
| `.env.local` | `.env.local` | `env.local` | 判「有副檔名」——正確 |
| `.env` | `.env` | `env` | 繼續看 shebang——正確 |
| `a.b/tool` | `tool` | `tool` | 繼續看 shebang——正確(目錄的點不干擾) |
| `dir/`(結尾斜線) | (空) | (空) | 繼續看 shebang,但這種路徑 `git show` 本來就查不到,無實際影響 |
| `..foo` | `..foo` | `.foo` | **判「有副檔名」**——`.foo` 因為還帶一個點,被 `*.*` 吃到 |

`..`/`.`/`dir/` 這幾種本來就不是 git 會列出的合法 blob 路徑名,不可利用。但 `..foo` 是雙前導點的合法檔名(雖罕見,例如某些備份/隱藏檔命名習慣),若它是無副檔名的 shebang 腳本,會被誤判成「有副檔名」而完全跳過 shebang 檢查——即放行(pre-commit)/不計 bypass(post-commit)。範圍窄、且不是本輪新引入的 fix 直接造成(是既有單層 `#` 剝法沒考慮多重前導點),列為 minor。

severity: minor
blocking: 否
引句:「local path="$1" base; base="${path##*/}"; [[ "${base#.}" == *.* ]] && return 1」
file: `scripts/hooks/pre-commit:124`

## 3. `impact-hook.py` 刪常數後留下 4 個連續空行(cosmetic)

`check-graph-sync.py` 刪 `_SHEBANG_INTERPS` 常數時連前後多餘空行一起清乾淨(現況剛好 2 空行,PEP8 正常);`impact-hook.py` 刪 `_SHEBANG_HINTS` 只刪了常數那一行,兩側各自留下的 2 空行沒收斂,現在 `_is_excluded_path` 結尾到 `_shebang_is_code` 定義之間變成 4 個連續空行(現檔 114–117 行)。純風格,不影響行為,repo 沒有跑 flake8 之類的 blank-line 檢查,不會壞任何測試。

severity: minor
blocking: 否
引句:「_SHEBANG_HINTS = (b"python", b"bash", b"/sh", b"env sh", b"zsh")」
file: `scripts/hooks/claude/impact-hook.py:116`

## 4.「任何 #! 都算程式碼」誤判面——找不到具體反例

在整個 repo 掃過所有無副檔名檔案(`find . -type f ! -name "*.*"`),首行是 `#!` 的只有 `scripts/lumos`、`scripts/hooks/{pre-commit,post-commit,pre-push}` 及 `dist/`、`slim/` 底下的鏡像——全部本來就是真程式碼。沒有找到「無副檔名、首行剛好是 `#!` 卻不該算程式碼」的實例(例如文件裡貼一段以 `#!/bin/bash` 開頭的範例、無副檔名存檔這種情境,repo 裡沒有)。這是已知、有註解承認的取捨(寧可誤判成程式碼、不要漏判),沒有現存反例可證偽,列 clean。

severity: clean
blocking: 否

## 5. 其餘探針——逐項確認,均無新洞

- `${LUMOS_AUTOLOOP_OFF:-1}` 在 `set -u` 下實測 unset/`""`/`"1"` → 暫停;`"0"`/`"false"`/`"off"` → 跑。看似「false/off 卻會跑」反直覺,但與同 repo既有的 `LUMOS_STOP_BLOCK_OFF`(`check-graph-sync.py:532`)、`LUMOS_ENTRY_HOOK_OFF`(`lumos-entry-hook.py:89`)完全同一種「只有等於 `"1"` 才算關」慣例一致,是既有慣例延伸,非本輪新增風險。`mkdir -p "$DIR/logs"` 在檔頭第 16 行執行,早於任何寫 log 的分支,順序沒問題。
- 全 repo(`scripts/`、`skills/`)搜不到 `codex_stop_decision` 殘留引用,只剩 `docs/`、`governance/review-reports/` 底下的歷史紀錄文字(預期內,舊帳)。別名刪除乾淨。
- `_load_hook_mod` 是 Codex S1 既有 helper(非本輪新增),`impact-hook.py`/`check-graph-sync.py` 都有 `if __name__ == "__main__": sys.exit(main())` 守門,`exec_module` 載入不會誤跑 main()。
- `_shebang_script`/`_shebang_is_code` 用 `head.startswith(b"#!")`,`bytes.startswith()` 保證回傳真正的 Python `bool`(`True`/`False` 是 CPython 單例),測試裡 `is want` 比對不會誤判——七種案例(dash/env -S/fish/prose/make/bin/empty)實跑 `python3 scripts/test_lumos.py -k code_exts` 全部 25 個 check 過、`-k shebang` 20 個 check 過。

severity: clean
blocking: 否

max severity: major
