severity: blocker

### F1 消費專案自己放在 scripts/hooks/ 或撞名 scripts/lumos 的真代碼,風險掃描直接失明
severity: blocker
blocking: 是 — pitfalls --diff 的 tier 判準被路徑字串繞過,消費專案自己寫的真風險代碼不會再觸發 high、也不會要求代碼審。
引句:「return r in _VENDORED_TOOLKIT or any(r == d or r.startswith(d + "/") for d in _VENDORED_DIRS)」
- `_is_vendored_path` 只比對路徑字串(精確等於 `_VENDORED_TOOLKIT` 五檔之一,或落在 `scripts/hooks/`、`scripts/templates/` 前綴下),完全不驗證內容或安裝來源。
- 重現(在 /tmp 開的乾淨 git repo,非工具鏈本體):`mkdir -p scripts/hooks && printf "def deploy():\n    fh = open('/etc/secrets/deploy_key')\n    return fh.read()\n" > scripts/hooks/my_own_deploy_hook.py && git add -A && git commit -m x && python3 scripts/lumos pitfalls --diff HEAD~1..HEAD --repo . --json`。
- 預期:這是消費專案自己寫的代碼,應該被掃到、tier 應該是 high;實測輸出 `{"claims": [], "tier": "standard", ...}`——risk 完全消失。同一套字串比對用同一支 `scripts/lumos` 檔名撞名也重現(consumer 自己取名叫 `scripts/lumos` 的檔,同樣被吃掉),我已用兩種輸入各自實跑驗證過(未寫進檔案,只在 /tmp 跑)。

### F2 about_code 的存在性檢查用 pathlib `/` 拼路徑,絕對路徑與 `../` 逃逸都能繞過「限定在這個 repo 裡」的宣告
severity: major
blocking: 是 — 印出的擋下訊息與實際行為互相矛盾(內部不一致,依紀律一律要報),about_code 可被寫成 repo 外的任意存在路徑。
引句:「print(f"擋下:about_code 要填這個 repo 裡真的存在的路徑,「{v}」找不到(從 {root} 算起)。」
- `if not v or not (root / v).exists():` 用 `root / v` 判存在;pathlib 的 `/` 運算子遇到右邊是絕對路徑時會**整個丟掉 `root`**,所以任何在機器上存在的絕對路徑一律通過,與訊息宣稱的「這個 repo 裡」矛盾。
- 重現:`lumos set <node> about_code /etc/hosts` → rc=0,印「✓ set …about_code 已改成 /etc/hosts」,frontmatter 真的寫成 `about_code: /etc/hosts`(我在 /tmp 假 vault 上實跑過,未動 repo 任何檔案)。
- 同一個檢查對 `../` 逃逸(`about_code: ../outside/leak.txt`,指到 repo 外但存在的檔)與純目錄(`about_code: src`,不是檔案)一樣放行,兩者我都各自實跑重現過,`.exists()` 不分檔案/目錄、也不做 `resolve()` 後的 repo 邊界比對。

### F3 `lumos set <node> about_code <路徑>` 會把既有的多筆 about_code 靜默壓成一筆,且事後 append 永久回不去
severity: major
blocking: 是 — 這篇筆記文件自己寫「about_code 0~3 支」是合法用法,新寫入口卻會無警告丟資料,而且丟了之後沒有任何指令救得回來。
引句:「fm[a:b + 1] = [f"about_code: {v}"]     # 清單形(含範本的空 [])或壞掉的純量,一律換成一行乾淨路徑」
- `_set_about_code` 對「已存在」的 about_code(不論是空清單、壞掉的純量、或**正常的多筆清單**)一律用 `struct["about_code"]` 的 `(a,b)` 整段換成單行 `about_code: {v}`。
- 重現:先 `lumos append S about_code src/a.ts`、`lumos append S about_code src/b.ts`(合法建出兩項清單,frontmatter 變成 `about_code:\n  - src/a.ts\n  - src/b.ts`),再 `lumos set S about_code src/c.ts` → rc=0 印「✓ set」,結果變成 `about_code: src/c.ts`,a.ts/b.ts 整個消失、不留痕跡(我在 /tmp 假 vault 上實跑過)。
- 更糟的是事後想救:`lumos append S about_code src/b.ts` 直接被擋(「about_code 是scalar型欄位,append 只能加進清單型欄位」,rc=2)——這正是本次修的④想解決的死局,`set` 自己重新製造了一次。

風險掃描清單那 1 條:誤報——命中的是 `_stack_changed_ok` docstring 裡描述「以前踩過『命中 open(...)』字面誤觸發」的說明文字本身,不是真的未關檔資源;因為這段 docstring 在本次 diff 裡被拆成兩段(原本結尾 `"""` 搬到後面),整行以 `+` 重新出現,regex 對純文字比對不分是不是註解正文。

總結:最高 severity blocker,blocking 共 3 條
