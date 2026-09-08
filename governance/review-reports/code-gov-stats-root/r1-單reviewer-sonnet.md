severity: clean

# 審查對象

`governance/review-reports/code-gov-stats-root/r1-snapshot.patch`(`scripts/lumos` + `scripts/test_lumos.py`,2 個 hunk 群)。
已核對:此 patch 已原封落在 HEAD(`63be882 fix(gov): --stats hook 段從 vault 反推 repo 根…`),工作樹與 patch 內容逐位元組一致,可直接對真檔跑測試/mutant,不需另外 `git apply`。

# 逐段讀

## 段①:刪 `_gov_repo_root_for_hooks` + `_render_gov_stats` 簽名加 `repo_root=None`

已讀,無 finding。舊函式用 `subprocess.run(["git","rev-parse","--show-toplevel"])`(讀 cwd 的 git 根,不吃任何參數)——這正是假紅的根因,刪除方向正確。新簽名 `repo_root=None` 保留「找不到就跳過」的原設計語意(見下段)。

## 段②:`_hp` 解析改用 `repo_root` 參數

已讀,無 finding。`_hp = (Path(repo_root) / "governance" / "runtime" / "hook-events.jsonl") if repo_root else None`——`repo_root` 目前恆為呼叫端傳進的 `Path`(見段③),Path 物件除 `None` 外一律 truthy,`if repo_root` 等價 `is not None`,無誤判空字串/ 相對路徑的風險。

## 段③:呼叫端改傳 `repo_root=_vault_repo_root(env)`

已讀,無 finding。`grep -n "_render_gov_stats("` 確認全庫僅此一處呼叫(`cmd_gov` 內,`scripts/lumos:4549`),不存在漏傳 `repo_root` 的第二呼叫端。`gov` 子指令的 argparse 定義(`scripts/lumos:21028-21036`)本來就沒有 `--repo` 覆寫選項,`_vault_repo_root(env)` 是唯一根來源,不存在「寫讀兩側用不同根」的分裂風險。

## 段④:新測試 `t_gov_stats_hook_section_reads_vault_repo_not_cwd`

已讀,無 finding。詳細驗證見下方「特別要驗」1-5。

# 特別要驗(逐項回答)

**1. `_vault_repo_root` 在非 git vault 退 `vault.parent=docs/` 時,`docs/governance/runtime/...` 永遠不存在,等於「非 git vault 永遠不印 hook 段」——是否可接受?**
可接受,已用程式碼查證,不是臆測。寫入端與讀取端對「有沒有 git」的依賴是**對稱**的:`scripts/hooks/claude/_hookevent.py` 的 `_root_from_cwd()`(第 95-105 行)本身就是 `git rev-parse --show-toplevel`,失敗就回 `None`,而 `guard()`(第 138 行起)在 `root` 為 `None` 時整段跳過、**根本不呼叫 `record()`**——也就是說非 git 專案永遠不會產生 `governance/runtime/hook-events.jsonl` 這個檔案,讀端「非 git 就不印」只是如實反映「非 git 就沒有資料」,不是新的資料遺失。另外 `lumos init`(`scripts/lumos:13089-13100`)在非 git 目錄下確實可跑(`git rev-parse` 失敗就退 `Path.cwd()`),所以非 git vault 是合法佈局,但因為上述對稱性,這條分支本來就沒有 hook 段可看,新舊實作在此無行為差異。⚠ 唯一值得留意但不到「finding」等級的觀察:這個對稱性目前沒有機械守衛綁著,若日後 `_hookevent.py` 單方面加了非 git fallback 而讀端沒跟進,才會產生真的遺漏——但那是假設中的未來變更,不是這份 patch 引入的缺陷。
引句:「★不准用 cwd 的 git 根★」

**2. mutant 實驗:拿掉 `git init` 那行 / 退回「cwd 版」實作,新測試是否真的翻紅?**
兩個 mutant 都翻紅,已用暫存副本實際跑過(未動工作樹):
- 拿掉 `_sp.run(["git","-C",str(root),"init","-q"], ...)` 那一行(複製 test_lumos.py 到 `scripts/` 下另建檔名跑,跑完即刪):第二、三個斷言雙雙翻紅——`_vault_repo_root` 找不到 `.git` 退到 `vault.parent`,`docs/governance/runtime/...` 不存在,hook 段整段不出現。證明 `git init` 是承重的,不是裝飾。
- 退回「cwd 版」(把 `_hp` 解析復原成 `subprocess.run(["git","rev-parse","--show-toplevel"])` 讀 cwd):把 mutant `lumos` 與未改的 `test_lumos.py` 放進本 repo 內一個未追蹤子目錄(`.tmp-mutant-review/scripts/`,跑完即刪)、從那裡執行,cwd 落在真 repo 內、`git rev-parse` 真的解到 `/Users/enzo/harness/lumos-toolchain`——第二、三個斷言翻紅,且印出的是**真 repo 的實際 hook 事件**(`pretooluse-dispatch-lens-hook: 成功 127 / 逾時 0 / 失敗 0` 等),不是假 vault 那份,精確重現作者自述的原始 bug(假 vault 讀到真 repo 的檔)。兩個 mutant 都證明這支測試咬中目標層,不是空殼。
引句:「讓 _vault_repo_root 走到 root」

**3. `repo_root=None` 的路徑:還有沒有別的呼叫端沒傳?**
`grep -n "_render_gov_stats("` 結果只有定義行(`4164`)與唯一呼叫行(`4549`),呼叫行恆傳 `repo_root=_vault_repo_root(env)`。無漏傳呼叫端。
引句:「_hp = (Path(repo_root) / "governance" / "runtime" / "hook-events.jsonl") if repo_root else None」

**4. 刪掉的 helper 有沒有別處引用?**
`grep -rln "_gov_repo_root_for_hooks" .`(排除 `.git/`)只命中 `governance/review-reports/code-gov-stats-root/` 與 `code-enforcement-obs/` 兩份審查報告的 patch/逐字稿存檔(審查歷史紀錄,非活碼、非 skill 文件、非圖譜筆記)。`scripts/hooks/*`、`docs/lumos-toolchain-knowledge/` 皆無引用。無懸空引用。
引句:「gov --stats 讀 hook 事件檔時用的 repo 根(唯讀,找不到就讓呼叫端跳過那一段)。」

**5. 時區:`datetime.now().astimezone().isoformat(timespec="seconds")` 產生的字串,py3.9(本專案下限)的 `fromisoformat` 能不能解?**
能。Python <3.11 的 `fromisoformat()` 只接受 `isoformat()` 自己吐出的格式子集,但那個子集本來就包含帶冒號的時區偏移(如 `+08:00`)——3.9 不能解的是 `time.strftime("%z")` 吐出的**無冒號**格式(`+0800`),`_hookevent.py` 第 60-68 行的行內註解已明文記錄這條界線並說明選用 `isoformat()` 正是為了繞開它。新測試與正式寫入端(`_hookevent.record`)用的是同一支 `datetime.now().astimezone().isoformat(timespec="seconds")` 呼叫,兩邊格式逐字一致,不存在測試造出讀側解不了的字串這種情況。
引句:「now = _dt.datetime.now().astimezone().isoformat(timespec="seconds")」

# 圖譜鏡頭(impact --diff 固定席,逐條必答)

以下 8 篇為派工時貼了 KEY 內容的固定席,逐條答「這批改動會不會破壞該節點宣稱的行為或合約」;其餘列名節點超出上限,不必答。

1. **slim-install-安裝器.md**(CLAUDE.md 注入/manifest/Windows 直譯器等 INVARIANT)——不影響。這批只動 `gov --stats` 的 hook 統計段讀取路徑,未觸及 CLAUDE.md 注入、vendor、manifest 任何一行。
2. **lumos-cli-read.md**(`search` 排除 superseded/保留 stale)——不影響。未動 `search`/濾網邏輯。
3. **slim-uninstall-一行卸載.md**(卸載四步互不阻擋、manifest/skill 備份)——不影響。未動卸載路徑。
4. **lumos-cli-lifecycle.md**(re-inject 只覆蓋 sentinel 內)——不影響。未動 re-inject。
5. **bound-tests-gate.md**(code-loop 對固定席合約綁測試逐支真跑)——不影響此節點自身邏輯;本審查即是該閘的一次實例(把新測試真跑過,見上「特別要驗 2」),閘本身程式碼未被這批改動。
6. **canary-audit.md**(canary record/second 落盤與 rc 隔離)——不影響。未動 `cmd_canary`/canary 讀寫路徑。
7. **guard-kill.md**(guard kill rc 優先序、`--json` 純淨)——不影響。未動 guard kill。
8. **slim-get-一行安裝.md**(`.ps1` ASCII/無 BOM、`$Args` 保留名)——不影響。未動任何 `.ps1`。

# 總結

severity: clean;findings 0 條;blocking 0 條。
