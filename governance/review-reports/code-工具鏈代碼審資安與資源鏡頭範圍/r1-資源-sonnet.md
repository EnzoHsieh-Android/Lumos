severity: clean

我讀了 patch 裡 `scripts/lumos` 的 `cmd_loop_next` 改動、新常數,以及 `scripts/test_lumos.py` 的 8 支新測試和幾個輔助函式,沒有找到資源類 finding。文件類的 diff(計劃、Issues、Systems、skills)只有文字,不碰這三類問題。

**①子程序與執行緒的收尾**
- `cmd_loop_next` 的新增段落沒有開子程序、執行緒或檔案控制代碼。
- 新測試只用 `run(...)` 同步子程序。`_lens_next` 每次兩個,S1 共 4 個、S2 共 6 個,都同步等完。
- `t_loop_next_lens_scope_fail_open` 在行程內把 `m._vault_repo_root` 換成會丟例外的版本,並放進 `try/finally` 還原。測試中途失敗也不會把替換留給後面的測試。
- 已讀,無 finding。

**②時間預算**
- 新增的判別只做一次 `_vault_repo_root` 向上找 `.git`(層數有限),加一次 `is_file`。沒有迴圈和等待。
- 例外時退回 default,所以不會因為判別失敗擋掉 `loop next`,退出碼也不變。
- 已讀,無 finding。

**③記憶體與二次方工作**
- `_tpl_dispatch_fences` 逐行掃描 `templates.md`。每個圍欄只用 `next(...)` 找一次收尾線,整體是線性的,輸入只有 `templates.md` 一份,沒有帳本或巢狀輸入。
- `_rm_literal_missing` 只對最多 8 份圍欄做子字串比對。
- 變異測試每個都複製一份整檔字串(約數百 KB)再替換,規模很小。
- S4、S5、S6、S10 的 `split` 和 `partition` 都是單次線性切段。
- 已讀,無 finding。

**測試暫存**
- `_mk_lens_dirs` 用 `mkdtemp(prefix="gctl-lens-")` 建目錄,測試結束後沒有刪。
- 這跟既有的 `mkvault()` 慣例一樣,`mkvault()` 的 `gctl-test-` 目錄也沒刪,所以不算本次新增的缺陷。
- 兩支新測試各留一個很小的目錄,不影響全套的耗時。

**測試夾具的環境依賴(非資源類)**
- S3 的「消費專案基準」假設 `vault.parent` 往上找不到 `.git`。如果 `TMPDIR` 落在某個 git 工作樹裡,`_vault_repo_root` 會往上解析到那個 repo,基準就可能變成 toolchain,測試可能出現假紅。這只在特殊環境才會發生,我沒有在這台機器上跑過測試。

最高等級 clean,blocking 0 條。
