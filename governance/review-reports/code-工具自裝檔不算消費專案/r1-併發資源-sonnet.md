severity: blocker

### F1 about_code 唯一寫入口把既有多路徑清單靜默塌成一筆,寫成功卻是資料損毀
severity: blocker
blocking: 是 — 對本 repo 現存至少 30 篇多路徑 about_code 節點,首次用這個新指令就會永久丟資料且不報錯。
引句:「fm[a:b + 1] = [f"about_code: {v}"]     # 清單形(含範本的空 [])或壞掉的純量,一律換成一行乾淨路徑」
1. `_set_about_code` 對「已存在的 about_code」一律用單一新值整段覆寫(`struct["about_code"]` 的 a..b 整區間被換成一行),不分原本是空清單、單一項、還是多項清單。
2. 診斷文件自陳「這個欄位在實務上都是一條純量路徑」與現況不符:`grep -rln "^about_code:$" docs/lumos-toolchain-knowledge/` 後逐篇數清單項,`Systems/codex-harness.md` 等至少 30 篇節點目前是真的多路徑清單(例如 `codex-harness.md` 記著 6 個真實檔案)。
3. 最小重現(把該節點複製進 /tmp 暫存 vault,不動本 repo):`cp docs/lumos-toolchain-knowledge/Systems/codex-harness.md /tmp/aboutcode-repro/kg/Systems/` 後跑 `python3 scripts/lumos --vault /tmp/aboutcode-repro/kg set codex-harness about_code scripts/lumos`——預期應該拒絕或至少警告「已有多筆路徑」,實際輸出 `✓ set Systems/codex-harness.md: about_code 已改成 scripts/lumos`(rc=0),檔案裡原本 6 項路徑(`scripts/hooks/claude/check-graph-sync.py` 等)只剩 1 項,其餘 5 項永久消失、沒有任何提示。
4. 新增測試 `t_set_about_code_is_writable_and_checked`(file: `scripts/test_lumos.py:1375`)只鋪了空清單 `about_code:` 一種起始狀態,完全沒蓋到多項清單這個實際存在的情境,所以這個洞沒被自己的測試釘住。

### F2 消費專案裡把風險代碼放進 scripts/hooks/、scripts/templates/ 或五個固定檔名,能讓推送前代碼審完全不觸發
severity: blocker
blocking: 是 — 端到端重現到 `code-loop check`(pre-push/CI 實際呼叫的判定式)直接放行帶後門的分支。
引句:「return r in _VENDORED_TOOLKIT or any(r == d or r.startswith(d + "/") for d in _VENDORED_DIRS)」
1. `_is_vendored_path` 純用路徑字串比對(`_VENDORED_TOOLKIT` 5 個固定檔名 + `scripts/hooks`/`scripts/templates` 兩個目錄前綴),不驗內容、不比對 hash;在非工具鏈 repo(`_is_toolchain_repo` 回 False)時,任何落在這些路徑下的檔案一律被 `_stack_changed_ok(cur_file, skip_vendored=True)` 排除出 pitfalls 掃描。
2. 最小重現:在 /tmp 建一個乾淨 git repo(非工具鏈 repo,無 `skills/lumos-project-notes/SKILL.md`),在 `scripts/hooks/claude/evil.py` 放 `subprocess.run(cmd, shell=True)` + 沒有 `with` 的 `open(...)`,commit 後跑 `python3 scripts/lumos code-loop check --diff HEAD~1..HEAD --at-sha <sha> --branch demo --repo /tmp/pf-repro`——預期含這種寫法的分支該被判 tier=high、要求審查留痕,實際輸出 `✅ code-loop check: OK——可以推(分支 main,版本 d522e059,tier=standard):tier=standard(非 high)`,rc=0,`pitfalls --diff` 回 `{"claims": [], "tier": "standard", ...}`。
3. `scripts/hooks`、`scripts/templates` 是很泛用的目錄名稱,不需要惡意動機——任何消費專案本來就可能拿這兩個名字放自己的真業務程式(hook 腳本、樣板引擎),一樣會被整批跳過,不只是刻意藏後門的情境。
4. file: `scripts/lumos:22673` — `code-loop check` 的 blocked 判定完全依賴這個可被路徑繞過的 tier 值(`if tier != "high": return {"blocked": False, ...}`),沒有第二道獨立於路徑名單的偵測層兜底。

### F3 判別鍵檔案(skills/lumos-project-notes/SKILL.md)若出現在消費專案裡,方向是關掉跳過而非開後門
severity: minor
blocking: 否 — 唯一可觀察後果是重新掃描 vendored 檔(退回本 PR 想修的①②③舊行為),不會讓風險代碼隱形。
引句:「return (Path(root) / "skills" / "lumos-project-notes" / "SKILL.md").is_file()」
1. `_is_toolchain_repo` 為 True 時 `_skip_vendored = not _is_toolchain_repo(...)` 變成 False,亦即該判別鍵一旦在消費專案裡出現,效果是**恢復**掃描 vendored 路徑,不是跳過——方向與 F2 相反,fail-closed(較嚴)不是 fail-open。
2. 重現:同一個 /tmp repo 加上 `skills/lumos-project-notes/SKILL.md` 標記檔後,同一支 `scripts/hooks/claude/evil.py` 再跑 `pitfalls --diff` 回 `{"claims": [{"file": "scripts/hooks/claude/evil.py", ...}], "tier": "high", ...}`——確認不是可被用來逃審的方向。
3. 此判別鍵是沿用既有 `_self_repo_origin`(file: `scripts/lumos:14162`)的既有慣例,非本次新增設計,風險屬性一致、非本 PR 引入的新洞。

### F4 os.walk 剪枝新增的 _rel() 對同一 dirpath 重複算 relpath,非零但有界的額外成本
severity: minor
blocking: 否 — 只是每個未被剪掉的子目錄/命中副檔名檔案各多一次 `os.path.relpath` 呼叫,不是隨 repo 大小失控增長。
引句:「rd = _os.path.relpath(dirpath, _base)」
1. `_rel(dirpath, name)` 在 `dirnames[:]` 的 list comprehension 裡對同一個 `dirpath` 下每個候選子目錄各呼叫一次,沒有把 `relpath(dirpath, _base)` 提到迴圈外算一次快取起來,filenames 迴圈同理(命中副檔名才觸發)。
2. 由於 `_stack_scan_skip(d)` 的短路求值仍在 `and` 前段,`node_modules` 等大目錄第一時間就被剪掉、不會走到 `_rel`,原本 r1 修的「大型專案線性變慢」問題本質沒有回歸,只是新增的判斷本身重算了本可只算一次的字串運算。

風險掃描清單那 1 條(scripts/lumos:17562,open( 命中):誤報——命中的是 docstring 裡描述性文字「命中 open(...)」的引號片段,不是真正的檔案控制代碼,無資源洩漏風險。

總結:最高 severity blocker,blocking 共 2 條
