severity: major

# code-enforcement r1 代碼審

## Finding 1 — settings.json 只查「有沒有登記」,不查對應 hook 檔還在不在:懸空註冊會被判 active(major)

`scripts/lumos:12094-12113`(`enforcement_status` ①②③)只在 `~/.claude/settings.json` 的 command 字串裡 substring 比對 needle,從沒去確認 `~/.claude/hooks/<needle>` 這個真檔還存不存在。

引句:「hit = any(needle in cmd for cmd in reg)」

但 `scripts/merge-claude-settings.py:99-121` 的 `_prune_dangling` 存在的唯一理由,就是「settings 裡的註冊」和「hooks 真檔」會脫鉤——它自己的 docstring 寫死了真實事故:

引句:「起因 2026-07-07 現場事故:code-loop-guard.py 被工具鏈更新刪除、settings 註冊沒清」

`_prune_dangling` 只在 `lumos install`/init 同步時才跑一次,不是每次 session 都清。也就是說在「hook 檔被刪掉」到「下次 install/init」這段真實存在的窗口裡,`lumos enforcement` 會把一支「每次觸發必報錯、實際上完全不生效」的 hook 報成 `active`——正好是這個新指令號稱要抓的那類問題,卻是它自己的偵測邏輯的盲點。

更嚴重的是:這個測資本身就默默證實了這件事。`scripts/test_lumos.py:22303-22319`(`_enforcement_fixture`)在 `all_active=True` 分支裡,把 settings.json 的 command 指向 `chd / "hooks" / "lumos-entry-hook.py"` 等路徑,但從頭到尾沒有 `mkdir`/`write_text` 建出 `chd/"hooks"` 這個目錄或任何 .py 檔:

引句:「"command": "python3 " + str(chd / "hooks" / "lumos-entry-hook.py")」

`t_enforcement_all_active` 照樣斷言這三支是 `active`——用一個「檔案不存在」的樣本去驗證「active」,等於親手示範了假陽性。

## Finding 2 — `_GLOBAL_CLAUDE_HOOKS` 有 4 支現役全域 hook,enforcement_status 只查 3 支,`ci-status-hook.py` 整層漏掉(major)

`scripts/lumos:11017`:

引句:「_GLOBAL_CLAUDE_HOOKS = ("check-graph-sync.py", "impact-hook.py", "ci-status-hook.py", "lumos-entry-hook.py")」

這 4 支都是 `_sync_global_claude`/`lumos install` 會實際 copy 進 `~/.claude/hooks/` 並在 `merge-claude-settings.py` 註冊進 `SessionStart` 的現役 hook(`scripts/merge-claude-settings.py:44-53`,CI 紅燈後備網)。但 `enforcement_status` 的 ①②③ 只列了 `lumos-entry-hook.py` / `impact-hook.py` / `check-graph-sync.py` 三支(`scripts/lumos:12106-12108`),`ci-status-hook.py` 完全沒有對應的 row——不是標 unknown,是根本不出現。這支 hook 若被誤刪或註冊被剪掉,`lumos enforcement` 不會有任何一列反映出來,九層防護的「九」本身就少算了一層真實存在的機制。

## Finding 3 — `_version_nudge` 回 None 有四種語意,enforcement_status 全部併成 active(major)

`scripts/lumos:12133-12138`:

引句:「add("vendored-cli", "degraded" if lag else "active", lag or "最新或來源不可達")」

但 `_version_nudge`(`scripts/lumos:10759-10797`)docstring 自己列的 None 情境不是只有「已是最新」:

引句:「來源 clone 不存在/不可達 → None(靜默 skip;CI 無來源 clone 不誤報)」

回 None 的路徑其實有四種:①`root/CLAUDE.md` 根本不存在(這個 repo 從沒裝過 lumos 紀律區塊)②有 CLAUDE.md 但抓不到 sentinel 版本欄位 ③來源 clone 不可達 ④版本相等或本地較新。只有④是真的「已驗證是最新」,①②③都是「量不出來」,語意上該跟第 ⑩ 層(遠端檢查)一樣誠實標 `unknown`,不該跟④共用 `active`。detail 字串自己都寫「最新或來源不可達」承認這個模糊,但 status 欄位還是硬選了 `active`——對一個從沒裝過 lumos 的專案(CLAUDE.md 都不存在),`vendored-cli` 這層照樣顯示綠燈,誤導性跟 finding 1 是同一類問題。

## Finding 4 — python 層沒包 try(minor)

`scripts/lumos:12131`:

引句:「add("python", "active", sys.version.split()[0])」

docstring 承諾「每層各自 try 包住」,這行是唯一一個裸露在外的。`sys.version.split()[0]` 實務上幾乎不會炸,风险低,但跟聲明的設計不變量不一致,若之後改成更複雜的偵測邏輯容易忘記補 try。

## Finding 5 — `--repo`/`root` 沒有存在性驗證,typo 會安靜印出一片 inactive(minor)

`scripts/lumos:12079-12080`:

引句:「if root:\n        root = Path(root)」

跟同檔 `_anchor_repo_root`(`scripts/lumos:11414-11426`)對照,後者對顯式傳入且非目錄的 `--repo` 會擋下並印錯誤;`enforcement_status` 完全不驗證,--repo 打錯字時所有 git/檔案層都會安靜退化成 inactive/unknown,使用者看到一片紅字容易誤判「這台機器沒裝防護」,而不是「路徑打錯」。

## Finding 6 — 分母排除 unknown 的斷言是恆真式,測不到真正的行為(minor)

`scripts/test_lumos.py:22427`:

引句:「n_total + n_unknown == len(rows)」

`enforcement_summary`(`scripts/lumos:12172-12177`)本身就是用 `total = len(rows) - unknown` 算出來的,所以 `n_total + n_unknown == len(rows)` 對任何輸入必然成立,跟「unknown 有沒有正確被排除在分母外」這件事完全無關——就算日後把 unknown 判準改錯(例如把 degraded 也算進 unknown),這條斷言照樣過。同一個測試裡另外兩條(`n_unknown >= 1`、`0 <= n_active <= n_total`)才有一點實質意義,但也沒有針對具體 row 組合去核對 total/active 的真實數字。

## Finding 7 — 「缺目錄不炸」只驗 `>= 8`,不是精確的 10 列(minor)

`scripts/test_lumos.py:22437`:

引句:「isinstance(rows, list) and len(rows) >= 8」

九層 + 1 列遠端應該固定是 10 列(3 hooks + git-pre-commit + git-pre-push + python + vendored-cli + ci-workflow + anchor-baseline + required-status-check)。用 `>= 8` 留了兩列的容錯空間——如果哪個 layer 的 try/except 之後被改壞、提早 return 漏了兩列,這條「回清單、不炸」的測試照樣綠燈,測不出「清單被砍不完整」這種退化。

## Finding 8 — anchor-baseline / vendored-cli 的 active/degraded 分支完全沒被測到(minor,觀察)

`_enforcement_fixture`(`scripts/test_lumos.py:22303-22319`)無論 `all_active` 真假都沒建立 `governance/anchor-baseline.json`,也沒建 `CLAUDE.md`。結果是:即使叫 `all_active=True`,anchor-baseline 這層實際上永遠是 `inactive`(沒有測試斷言去核對這件事),vendored-cli 這層的 `active` 是靠 finding 3 講的「None 因 CLAUDE.md 不存在」這條漏洞路徑撐出來的,不是真的驗證到「版本比對通過」。四個測試函式沒有任何一條真正走過 anchor-baseline 的 `active`/`degraded` 分支,也沒走過 vendored-cli 的 `degraded` 分支或「真的比對出 active」的分支。

## 核過無誤的部分

- anchor-baseline 的 sha256 比對邏輯(`scripts/lumos:12142-12157`)跟既有 `cmd_anchor_verify`(`scripts/lumos:12199-12233`)演算法一致:缺檔或 hash 不符都算 bad,bad==0 才 active。
- summary/cmd 印出時不會除零:`enforcement_summary` 只做整數相減與比較,`cmd_enforcement` 只把 `active`/`total` 兜進字串,從沒真的做除法運算,`total==0` 時也只是印出 `0/0`,不會拋 ZeroDivisionError。
- git-pre-commit/git-pre-push/CI-workflow/anchor-baseline 四層各自都有獨立 try/except 包住(檔案操作、subprocess、JSON 解析全在 try 內),缺目錄/壞 JSON/沒權限確實會被各自吞掉、不拖垮 `enforcement_status` 整體(finding 4 的 python 層例外)。
- `cmd_enforcement` 恆 rc0(唯讀查詢不判成敗)符合 docstring 承諾,`--json`/純文字兩種輸出路徑都測過分支存在(雖然 CLI 層本身沒有專屬測試,見下)。
- CLI 接線(argparse subparser、`args.cmd == "enforcement"` dispatch、HELP_WHEN 條目)三處都對得上,沒有打錯 dest 名稱或漏接的情況。
