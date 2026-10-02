severity: minor

# 第 2 輪 架構對齊(架構對齊-sonnet)

核對方式:逐 hunk 讀完 r2-delta.patch(901 行),再到 repo 根查同層對照。第 1 輪的六條,五條確實改成照既有做法;剩一條只改了一半(見 F1,minor)。沒有新的第二種做法。

## 問一:分層與依賴方向
- 重造既有功能那條已收乾淨。`_fix_rev` 整支刪掉,改呼叫 `_lens_full_sha`;`_fix_git_z` 改成 `_nodehome_git` 加 `_nodehome_split_z`;hashlib 兩處改呼叫 `_sha256_file`。
  引句:「raw = _nodehome_git(repo_root, *args)」
  file: `scripts/lumos:25494`(`_nodehome_git`)、`scripts/lumos:25507`(`_nodehome_split_z`)、`scripts/lumos:8432`(`_sha256_file`)。
  依賴方向:修正關卡這批 `_fix_*` 往下呼叫通用的 `_lens_git` 家族,沒有反過來,沒有跨層直呼。
- `_lens_full_sha` 加 `--end-of-options` 是改共用函式,不是另寫一支。其他呼叫端行為只會更嚴,不會變寬。
  引句:「"--end-of-options", f"{rev}^{{commit}}")」
- 簿記檔過濾用的是既有的單一來源。
  引句:「dirty_paths = [x for x in dirty_paths if x not in _BOOKKEEPING_FILES and not x.startswith(_BOOKKEEPING_DIRS)]」
  file: `scripts/lumos:34531`、`scripts/lumos:29269`、`scripts/lumos:34444`。這幾處都是同一句 `f in _BOOKKEEPING_FILES or f.startswith(_BOOKKEEPING_DIRS)`,寫法一致,沒有自開第二份名單。
- 殘骸時限不另訂一個數字,而是別名指向既有常數。
  引句:「_ISOLATED_WT_STALE_SEC = _LINT_NEW_STALE_SEC」
  file: `scripts/lumos:24043`。一個數字、兩個名字,單一來源,沒有第二個真值。
- 處置範本與 record_cmd 的旗標已合成一份 `_tpl_flags`。
  引句:「_q, _rm, _tf = _tpl_flags()」
  file: `scripts/lumos:12231`(定義)、`scripts/lumos:12240`、`scripts/lumos:12265`(兩處消費)。檔內 `round r{n_next}` 只剩 12235 這一處,沒有漏網的第三份算法。

## 問二:命名與錯誤處理
- `_isolated_worktree` 改成函式加內層 `contextlib.contextmanager`,`return _cm()`,跟 `_vault_write_lock` 同形。這個檔裡的 `contextmanager` 只有這兩處,現在 `_IsolatedWorktree` 那個「檔內第一個類別式 with」已經沒了。
  引句:「@contextlib.contextmanager
+    def _cm():」
  file: `scripts/lumos:16900`、`scripts/lumos:16924`(`_vault_write_lock` 的同形寫法)。
  小差別:這裡用 `types.SimpleNamespace` 當 yield 出去的把手,`_vault_write_lock` yield 的是 None。`scripts/lumos` 裡 `SimpleNamespace` 只有這一處(`scripts/lumos:14622`)。因為呼叫端必須讀 `iw.ok`/`iw.err`/`iw.path`,這算結構上需要,不是第二種做法,所以不列為不對齊。
- `_fix_check_config` 現在在設定讀不懂時會加警告。
  引句:「cfg["warnings"].append(f"設定檔讀不懂({type(e).__name__}),fix_check 照預設")」
  file: `scripts/lumos:24186`(`_lint_new_config`)。結構相同:預設值、警告清單、讀失敗回預設,檔案不存在時兩邊都靜默回預設。只有訊息字面有出入,見 F1。

## 問三:第二種做法
- 未發現。上面五個對照點都已回到既有做法。
- 附帶觀察,不判不對齊:`_isolated_worktree_sweep` 與 `_lint_new_clean_stale` 各自掃一個地方(系統暫存區與 `.lumos/lintbase-*`),規則(超時就刪)相同。目錄與型態不同,不是同一件事做了兩遍。

## F1 修正關卡設定讀不懂的警告沒寫出檔名,跟 lint_new 同類警告不一樣
severity: minor
blocking: 否
引句:「cfg["warnings"].append(f"設定檔讀不懂({type(e).__name__}),fix_check 照預設")」
file: `scripts/lumos:24186`(`_lint_new_config`,訊息含 `.lumos/config.json 讀不了(...)`)
1. 鄰居 `_lint_new_config` 的警告字面是「.lumos/config.json 讀不了(…),新增告警閘用預設值」,指名是哪個檔。這裡只寫「設定檔讀不懂」。
2. 使用者看到時不知道是哪份設定,尤其這份讀的是樹裡的那份(`_fix_check_config(tree)`),跟主工作目錄那份可能不同。這是命名與錯誤處理上的小出入,結構是對的,所以只判 minor。

不對齊共 1 條,其中 major 0 條

最高等級:minor,blocking 共 0 條
