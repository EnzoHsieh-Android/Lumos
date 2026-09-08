severity: clean

# r1 架構對齊審查——`gov --stats` hook 段 repo_root 傳遞方式

LUMOS-IMPACT: Lumos/main..HEAD

## 問 1:分層與依賴方向——`repo_root` 由 `cmd_gov` 算好傳進純渲染函式,跟鄰居一樣嗎?有沒有跨層直呼?

對齊。

引句:「_render_gov_stats(_raw, ded, loaded, since_days, cutoff, node, repo_root=_vault_repo_root(env))」

改動前,`_render_gov_stats`(純渲染函式,自己的 docstring 就寫「純數字報表…恆不影響 rc、不改既有輸出」)內部直接呼叫 `_gov_repo_root_for_hooks()`,而該函式又直接 `subprocess.run(["git","rev-parse","--show-toplevel"])`——沒有 `cwd=` 參數,吃的是進程當下的 cwd。這是一個渲染層自己動手做 IO/子行程解析根目錄的跨層直呼,而且解析邏輯(cwd 找 git 根)跟 repo 裡任何一支既有的「找根」helper 都不同款,是第四種寫法(見問 3)。

改動後,`_render_gov_stats(rows, ded, loaded, since_days, cutoff, node, repo_root=None)` 只接收呼叫端算好的 `repo_root`,自己不再解析根目錄,函式內只剩 `Path(repo_root) / "governance" / "runtime" / "hook-events.jsonl"` 這種純組路徑動作。呼叫端 `cmd_gov` 在 `scripts/lumos:4549` 做:

```
_render_gov_stats(_raw, ded, loaded, since_days, cutoff, node, repo_root=_vault_repo_root(env))
```

即「有 env 的那一層算根,傳給沒有 env 的純渲染函式」。這跟同檔 `_render_gov_nags(ded, min_days)`(`scripts/lumos:4312`,純資料進、無 IO)是同一種「渲染函式只吃資料/已算好的值」形狀,也跟同檔另一支已存在的「repo_root 當參數,呼叫端自己解析」helper 一致,例如:
- `_intake_dir_status(repo_root, loop_id)`(`scripts/lumos:4617`),呼叫端在 `scripts/lumos:1403` 用 `_repo_root = _vault_repo_root(env)` 算好才傳進去(呼叫點在 `scripts/lumos:1427`)。
- `_codeloop_read(repo_root, branch)` / `_codeloop_write(repo_root, branch, ...)`(`scripts/lumos:19685`、`scripts/lumos:19733`),同樣只吃 `repo_root` 參數,不自己解析。
- freshness 判斷函式(`scripts/lumos:11789` 那段,`f = Path(repo_root) / "governance" / "runtime" / "hook-events.jsonl"`)也是同一形狀。

這批 diff 是把一個原本跨層直呼的寫法,改成跟這幾支既有 helper 同款的「呼叫端傳根」,方向是往既有慣例對齊,不是引入新的跨層直呼。

## 問 2:命名與錯誤處理——`repo_root=None` 時靜默跳過 hook 段,跟鄰居「找不到就跳過那一段」的慣例一不一致?

對齊。

引句:「_hp = (Path(repo_root) / "governance" / "runtime" / "hook-events.jsonl") if repo_root else None」

`_render_gov_stats` 函式本體對「這段有沒有資料」的處理慣例本來就是「沒有就整段不印,不噴錯、不擋」,同函式內到處都是這個形狀(`scripts/lumos:4164-4302` 區間):`if tot:` 才印流程自產工作量段、`if rvt:` 才印辯方表態段、`if dl:` 才印設計迴圈結案段、`if hard or skipped or fo:` 才印閘動作段。新的 hook 段沿用同一慣例:

```
_hp = (Path(repo_root) / "governance" / "runtime" / "hook-events.jsonl") if repo_root else None
if _hp is not None and _hp.exists():
    ...
```

`repo_root` 為 `None`(或檔案不存在)就整段不印,不丟例外、不印警告——跟改動前的 `try/except Exception: _hp = None` 效果一致(都是「拿不到就跳過這段,不影響其餘畫面與 rc」),只是換了個更直接的表達方式(改動前是把 git 子行程失敗吞掉,改動後是把「呼叫端沒給根」這個狀態用預設值 `None` 表達)。

需要指出但不影響判定:實際唯一呼叫端 `cmd_gov` 傳的是 `_vault_repo_root(env)`,而 `_vault_repo_root` 自己的 docstring 明寫「找不到退 vault.parent」(`scripts/lumos:4732-4739`)——它從不回傳 `None`。所以 `repo_root=None` 這個分支在目前唯一呼叫路徑下不會被觸發,是防禦性預設值,不是「合約上會發生的靜默跳過」。這與 `_intake_dir_status`、`_codeloop_read` 等鄰居的簽名慣例(參數無預設值,呼叫端必給)有一點點形狀差異,但因為 `_render_gov_stats` 本來就是「其餘參數都無預設、只有這個新參數給了 `None` 預設」,屬於命名/簽名細節,不到「跟鄰居結構不一致」的程度。⚠標記給編排者:這點是否要收斂成 minor 見仁見智,我判為不列(風格層級),因為它不影響任何一條「找不到就跳過」的行為對齊。

## 問 3:第二種做法——這批用的是哪一種既有找根方式?跟 `gov` 指令其他部分一致嗎?

對齊,而且是消除既有的第二種做法(第四種寫法被拿掉),收斂到已有的一種。

引句:「return _s.run(["git", "rev-parse", "--show-toplevel"],」

專案裡目前找 repo 根有三支具名 helper,各自用途分明,靠 `grep -n "_vault_repo_root(\|_repo_root_from_env(\|_anchor_repo_root("` 可全部列出:
1. **`_vault_repo_root(env)`**(`scripts/lumos:4732`):從 `env.vault` 往上找 `.git`,找不到退 `env.vault.parent`。docstring 明講是「disposal 留痕路徑的落帳/解析根,寫讀兩側必須同用這一份」。既有消費端包括 `cmd_doctor` 內兩處直呼(`scripts/lumos:1403`、`scripts/lumos:1485`,這兩處函式簽名本身沒有 `repo` 參數,直接用 `env` 算)、`_lint_load_and_validate` 前置(`scripts/lumos:2240`)、`cmd_about_code_migrate_stamp` 等多處以 `Path(repo).resolve() if repo else _vault_repo_root(env)` 形式出現(`scripts/lumos:559`、`6558`、`6938`、`7465`、`7562`、`13513`、`13531`、`13542`)。
2. **`_repo_root_from_env(env)`**(`scripts/lumos:7606`):docs 佈局感知(找 `docs/` 上層),用於 `_platform_test_index` 等平台判定路徑(`scripts/lumos:7664`、`7782`、`8143`)。
3. **`_anchor_repo_root(repo)`**(`scripts/lumos:13213`):`--repo` 顯式優先,否則從 **cwd** 往上找 `.git`,找不到印錯到 stderr、回 `None`——docstring 自己寫「同 refcheck 慣例」,用於 anchor-approve 一類真的有 `--repo` 旗標、cwd 可信賴的指令。

`gov` 子指令本身**沒有 `--repo` 旗標**(`scripts/lumos:21028-21035` 的 `add_parser("gov", ...)` 只有 `node/--since/--full/--stats/--nags`),六本帳的載入路徑是 `docs = env.vault.parent`(`scripts/lumos:4363`)——也就是 `gov` 從頭到尾都是「vault-based,不吃 cwd、不吃 --repo」的唯讀工具。這批 diff 選 `_vault_repo_root(env)`,是三支裡跟 `gov` 既有設計(無 `--repo`、以 vault 為錨)語意最貼近的一支;也正是 `cmd_doctor`(同樣無 `repo` 參數的指令)已經在用的那一支(`scripts/lumos:1403`、`1485`)。

改動前的 `_gov_repo_root_for_hooks()` 用 `subprocess.run(["git","rev-parse","--show-toplevel"])`(無 `cwd=`,吃進程 cwd)——這是上述三支之外的**第四種**寫法,而且正是這次要修的 bug 根因(測試裡假 vault 用 cwd 撞到真 repo 的 `hook-events.jsonl`,平行推送閘期間被追加造成假紅,見新測試 `scripts/test_lumos.py:4440`、`t_gov_stats_hook_section_reads_vault_repo_not_cwd` 的 docstring)。diff 把這第四種寫法整支刪掉,改用 `_vault_repo_root(env)`——是「消滅一個既有的第二種做法」,不是「新增一個」。

測試面:新測試 `t_gov_stats_hook_section_reads_vault_repo_not_cwd`(`scripts/test_lumos.py:4440-4463`)沿用 `_stats_fixture` 建假 vault,並在假 root 上 `git -C str(root) init -q`(`scripts/test_lumos.py:4455`)讓 `_vault_repo_root` 能在假 root 找到 `.git`、不誤爬到真 repo。這與既有測試對「假 root 需要 git 根才能讓某支 `_xxx_repo_root` 生效」的處理慣例完全一致,例如 `_enforcement_fixture`(`scripts/test_lumos.py:25378`)裡 `subprocess.run(["git","-C",str(root),"init"], capture_output=True, text=True)`,以及 `scripts/test_lumos.py:2569`、`5077`、`5095`、`5114` 等多處同款 `git -C <root> init -q` + `capture_output=True`。不是新發明的測試手法。

## 結論

不對齊共 0 條,其中 major 0 條。

這批 diff 的效果是把渲染層裡一個跨層直呼、且解析邏輯與全庫任何既有 helper 都不同款的子行程呼叫,改成跟 `_intake_dir_status`/`_codeloop_read`/`cmd_doctor` 同款的「呼叫端用 `_vault_repo_root(env)` 算好、以參數傳進純函式」寫法;錯誤處理(拿不到就整段跳過、不擋 rc)沿用該渲染函式自己一路的慣例;測試用 `_stats_fixture` + `git init` 假 root,也是全檔重複出現的既有手法。三問都對齊,沒有 major、沒有 minor 需要折。
