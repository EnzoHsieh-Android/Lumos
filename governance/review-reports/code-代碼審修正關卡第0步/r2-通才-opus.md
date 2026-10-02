severity: minor

# 代碼審修正關卡第0步 r2 修正差異 — 通才-opus

審材:`r2-delta.patch`(900 行,全讀)。實驗都在自己的 clone(`fcc-r2-work-通才-opus/repo` = 3ddbffe0,含本輪修正;`fcc-r2-work-通才-opus/r1` = 同一提交反向套 r2-delta,還原成 r1 修完的樣子)裡跑,沒動 repo 根。

## F1 空字元檢查只擋了 NUL,同一族的「孤立代理字元」照樣當掉

severity: minor
blocking: 否
引句:「return None, "修正紀錄裡有空字元(\\u0000),路徑與版本都不能含它"」
佐證行:file: `scripts/lumos:11687`(`_fix_load_record` 的空字元檢查);當掉點 file: `scripts/lumos:11667`(`_fix_ls_tree` 把路徑交給 subprocess)與 file: `scripts/lumos:12129`(印失敗明細)

1. 上一輪 g1 的病根是「紀錄裡的字串被原樣交給 subprocess 或印出來,遇到編碼不了的字元就丟例外」;這輪只補了 NUL 這一個字元。JSON 合法的 `\ud800`(孤立代理字元)在 `json.loads` 後變成 Python 無法編成 UTF-8 的字串,走的是同一條路。
2. 重現(`fcc-r2-work-通才-opus/probe_nul.py`,用 `_fc_env/_fc_ledger/_fc_record/_fc_check` 夾具):
   ```
   /opt/homebrew/bin/python3 probe_nul.py
   == at 含孤立代理字元 \ud800 rc 1
     stderr tail: ... UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 4: surrogates not allowed
   == test 名含 \ud800 rc 1
     stdout tail: [fix-check] code-fx r1:✗ 沒過:tests-exist(0.7s)(修正前 cc94a8ac → 修正後 712be22d)
     stderr tail: ... line 12129, in cmd_loop_fix_check | print(f"  ✗ [{item}] {m}") | UnicodeEncodeError ...
   == base 含 \ud800 rc 1
     stderr tail: ... UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 40: surrogates not allowed
   ```
3. 後果跟上一輪 g1 一樣:輸入錯應回 2、不寫事件,實際回 1 帶 traceback;測試名那條更糟——已經寫了一筆 `warned` 事件才在印明細時當掉。觸發要手寫或 AI 寫出 `\ud800`,機率跟 NUL 同級,照上一輪對 g1 的定級給 minor。
4. 修法建議跟 F2 合一條規則:別在原始文字上找子字串,改在 `json.loads` 之後走過整份紀錄的每個字串,`"\x00" in s` 或 `s.encode("utf-8")` 失敗就回 2。這樣 NUL、孤立代理字元一次收掉,也不會誤擋 F2 那種合法輸入。

## F2 空字元檢查在原始文字裡找 `\u0000` 子字串,會把合法的「反斜線加 u0000」誤判成空字元

severity: minor
blocking: 否
引句:「if "\x00" in raw or "\\u0000" in raw:」
佐證行:file: `scripts/lumos:11687`

1. JSON 原文 `"\\u0000"` 解出來是六個普通字元(反斜線、u、0000),不是空字元;但它的原文裡含有 `\u0000` 這個子字串,這行一樣擋。
2. 會發生的場景:修正紀錄的 note 或 reason 要描述「紀錄含 \u0000 時回 2」這類修法(這一輪的 g1 本身就是),寫成 JSON 就是 `"\\u0000"`。
3. 重現(同一支 `probe_nul.py`):
   ```
   == note 含字面反斜線u0000(合法、不是空字元) rc 2
     raw has \u0000 substring: True
     stderr tail: 擋下:修正紀錄裡有空字元(\u0000),路徑與版本都不能含它
   ```
   一份完全合法的紀錄被擋成回 2,訊息還說它有空字元,使用者照訊息找不到東西可改。
4. 修法同 F1 第 4 點(解完再檢查解出來的字串)。

## F3 「真的連了才警告」的判法看的是主工作目錄有沒有依賴資料夾,不是樹裡有沒有真的建出連結

severity: minor
blocking: 否
引句:「linked = any((rr / rel / dep).is_dir() for rel in _dep_roots for dep in _LINT_DEP_DIRS)」
佐證行:file: `scripts/lumos:12024`;建連結的那支 file: `scripts/lumos:24309`(`_lint_link_deps`:樹裡那個名字已存在就跳過、`symlink_to` 丟 OSError 就靜默 pass)

1. 這輪宣稱「依賴資料夾警告只在真的連到東西時印」,但 `linked` 是重新算一次「主工作目錄有沒有 node_modules/.venv/venv」,跟 `_lint_link_deps` 實際有沒有建出連結脫鉤。兩種情況會講錯:
   - 依賴資料夾本身進了版控(例如提交了 `venv/`):樹裡已有同名資料夾,`_lint_link_deps` 跳過不連,但 `linked` 照樣是 True。
   - Windows 沒有建符號連結權限(一般帳號沒開開發人員模式時的預設):`symlink_to` 丟 OSError 被吞掉,什麼都沒連,`linked` 還是 True。
2. 重現(`fcc-r2-work-通才-opus/probe_link.py`:`_fc_env` 後提交一個 `venv/README`,再把 prod.py 改髒):
   ```
   rc 0
     · 這次驗的是提交裡的版本,工作目錄這幾支沒提交的改動不算:prod.py
     · 依賴資料夾連回主工作目錄,上面那幾支沒提交的改動可能被樹裡的測試載到
   ```
   樹裡的 `venv` 是提交裡的版本,沒有連回主工作目錄,這句話是錯的。
3. 只是一行說明講錯,不影響判定,所以給 minor。修法:讓 `_lint_link_deps` 回傳這次實際建了幾條連結(或事後檢查 `(tree / rel / dep).is_symlink()`),`linked` 用那個結果,不要另外重算。條款測試 ④d 只蓋到「主工作目錄完全沒有依賴資料夾」,蓋不到這兩種。

## 已核對、沒發現問題的部分

引句:「r = _lens_git(repo_root, "rev-parse", "--verify", "-q", "--end-of-options", f"{rev}^{{commit}}")   # 以 - 開頭的輸入不會被當旗標(修正關卡第0步)」
- `_lens_full_sha` 加 `--end-of-options` 對既有呼叫端(`scripts/lumos` 裡約 30 處,傳的是 `HEAD`、`{c}^`、`{tail}~1`、使用者給的 ref、pre-push 收到的 sha、空字串等):本機只有 Apple git 2.39.2(比 rev-parse 正式支援這個旗標的版本舊),實測 `rev-parse --verify -q --end-of-options 'HEAD^{commit}'` 與 `'HEAD~1^{commit}'` 都回 0 並給出正確 sha,`'-x^{commit}'` 回 1。舊版 git 在 `--verify` 模式下把不認得的旗標直接丟掉,新版明確支援,兩邊對正常輸入結果一樣;空字串的呼叫端(`pb.get("event_commit") or ""`)前後都是 None。沒找到會被影響的呼叫端。
- `_LENS_SHA_RE` 也收 64 碼,但 fix-check 後面用 40 碼檢查 HEAD,SHA-256 的 repo 會先停在「讀不到現在的 HEAD」回 2,不會拿錯的長度往下跑。

引句:「_qid, rmode, _tier_flag = _tpl_flags()   # record_cmd 與處置範本同一份旗標算法(代碼審 r1 架構席 F3)」
- `_tpl_flags` 三個值跟原本內聯的三行逐字同式。另用 `cmp_next.py` 在 r1 與 r2 兩份程式上跑 `loop next`(standard 第 1/2 輪、high 第 2 輪且編號含空白與分號、design 迴圈、light 新編號,各配文字/--json/--spec),去掉隨機的 canary_type 後 20 組輸出與 rc 全部相同;`record_cmd` 與 gate-pending 的 `disposal_cmd`(含 `'code-a b;x'` 的引號與 `--regression-set`)字面沒變。

引句:「with _isolated_worktree(proot, ghead, "lumos-kill-", keep=keep_worktree,」
- `_isolated_worktree` 改寫成內層 contextmanager 後,`yield` 在內層 try 外面,body 的例外不會被 `except BaseException` 吃到。用 `probe_iw.py` 在程序內實測:body 丟例外 → 例外照傳、暫存資料夾刪掉、worktree 登記清空;迴圈裡 `continue` 與 `return` → 都收乾淨;建樹失敗加 keep → ok=False、err 是 git 原文、on_keep 收到路徑、資料夾留著;git 不在 PATH → FileNotFoundError 照傳、沒留殘骸。拿 cbbdd46a 的 guard kill 原寫法逐行對照:keep 時不管成敗都印「現場保留」、不 keep 時先 remove 再 rmtree 再 prune,三步順序與條件一致。`.parent` 屬性拿掉了,repo 裡沒有其他地方用到。
- `_isolated_worktree_sweep` 只換成 `_ISOLATED_WT_STALE_SEC`(等於 `_LINT_NEW_STALE_SEC`),修正關卡的前綴 `lumos-fixcheck-` 跟 `lumos-kill-` 不互為前綴,不會清到 guard kill 的樹。

引句:「dirty_paths = [x for x in dirty_paths if x not in _BOOKKEEPING_FILES and not x.startswith(_BOOKKEEPING_DIRS)]」
- 簿記檔排除:porcelain 路徑是相對 repo 根,跟 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS` 的寫法對得上;修正紀錄本身在 `governance/review-reports/` 底下會被排除,但它本來就從主工作目錄讀、指紋也從主工作目錄算,不影響判定。
- `_fix_git_z`/`_fix_ls_tree` 改走 `_nodehome_git`:失敗回 None 的語意跟原本一樣,多了 20 秒逾時;`os.fsdecode` 在 macOS/Linux 等於原本的 utf-8 加 surrogateescape。
- `_fix_check_config` 讀不懂時的新警告:在 fix-check 裡實際走不到——樹裡設定檔讀不懂時,前面 `json.loads(tcfg…)`/`load_platforms` 已先回 2。沒有錯的行為,只是那條警告目前是死路,記一筆給作者參考。

條款測試:`-k fix_check` 96 條、`-k isolated_worktree` 9 條、`-k regression_set` 10 條全綠;`-k guard_kill` 257 條全綠。翻紅實測:在另一份 clone(`fcc-r2-work-通才-opus/mut`)拿掉簿記檔排除那行、把 `if dirty_paths and linked:` 改回 `if dirty_paths:`,清掉 __pycache__ 後跑 `-k fix_check_tree_setup` → 「✗ ④c 只有簿記檔(治理帳)沒提交」「✗ ④d 主工作目錄沒有任何依賴資料夾」,7 passed 2 failed,新加的兩條確實守得住。

固定席:這次派工詞尾端沒有附固定席筆記。審材裡唯一帶 ★INVARIANT★ 的節點是 guard-kill:rc 優先序那條不受影響(這輪沒改判定與 rc,只換建樹/收樹的寫法);--json 純度那條不受影響(「現場保留」照舊經 on_keep 在 --json 時印到 stderr,lambda 的預設參數在定義時就綁定了輸出目標)。

最高等級:minor,blocking 共 0 條
