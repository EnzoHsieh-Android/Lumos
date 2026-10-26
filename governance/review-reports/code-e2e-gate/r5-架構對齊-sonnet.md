severity: major

調查結果:鎖檔 `.warming` 不存在,沒有需要處理的鎖,照派工詞審查。以下都對照現行 `/Users/enzo/orca/workspaces/lumos-toolchain/e2e-gate/scripts/lumos`。

## 問 1 分層與依賴方向

新碼的分層大多和鄰居一致:
- `_e2e_parent`、`_e2e_clean`、`_e2e_say_block` 都放在 e2e 區,由 e2e 閘內部呼叫。
- 掛鉤複本(`lumos-entry-hook.py`)與主程式的 `_e2e_ai_pending_all` 同步修改,維持原有的「複本要一致」做法。

不一致的是 `_macrobench_mode`:

1. `_macrobench_mode` 呼叫 e2e 專屬的 `_e2e_say_block`(跨層直呼)。
   - `_macrobench_mode` 在 macrobench 區,e2e 區在它之後,依賴方向是 e2e 用 macrobench。這裡反過來,macrobench 往上呼叫 e2e。
   - `err`、`terr`、`serr` 是一般 `lumos macrobench` 也會碰到的設定錯誤,不只端到端驗收才有。結果是一般 macrobench 的擋下訊息也被套上 e2e 專屬的「拆 pre-push 字樣」處理。
   - macrobench 區其他的「擋下:」都是裸 `print`。
   - 若要共用,清理函式該放在兩區都能用的底層(比照 `_esc_clean`),不該由 macrobench 呼叫 `_e2e_` 前綴的函式。

引句:「_e2e_say_block(err or terr or serr or eerr)」
severity: major
blocking: 是
file: `scripts/lumos:40273`、`scripts/lumos:40301`、`scripts/lumos:41393`(對照 `scripts/lumos:40263` 上下裸 print 的寫法)

## 問 2 命名與錯誤處理

命名都跟鄰居一致:`E2E_*` 常數、`_e2e_*` 函式、`E2E_RECORD_FILE_MAX` 這類上限,以及「擋下:」開頭的訊息。治理帳事件沒有新增。

不一致有兩處,都是 minor:

2. `_e2e_say_block` 自稱「單一出口」,但 e2e 區仍有裸 `print(f"擋下:…")`。
   - 它們沒改成走 `_e2e_say_block`:`scripts/lumos:41333`、`41349`、`42092`、`42167`、`42182`。
   - 其中 `_e2e_full_blocked`(`42167`)和 `--precheck`(`42182`)印的原因,可能帶設定或指紋計算的外來文字。
   - 隔壁安全證據閘的做法是整族只走 `_secinv_say`(`scripts/lumos:8267`),`_cl_say_sec_block` 也是一行一行過它(`scripts/lumos:66466`)。
   - 結構是對的,只是出口沒收乾淨。

引句:「訊息常帶紀錄或設定裡的外來文字,印之前一律清(單一出口)。」
severity: minor
blocking: 否
file: `scripts/lumos:41393`

3. 兩處小地方跟既有寫法不一致。
   - `64 層` 是寫死在函式裡的數字,而同批的上限都是具名常數(`E2E_DIR_LIST_MAX`、`E2E_RECORD_FILE_MAX`、`MACROBENCH_MAX_CYCLES`)。
   - `_e2e_relpath_err` 裡又寫了一次 `import unicodedata`,但檔案開頭已 import(`scripts/lumos:63`)。
   - `E2E_DIR_LIST_MAX` 的名字帶 DIR,卻也管 `shared_paths`(檔案路徑),這點只是命名上的小疙瘩。

引句:「if p.count("/") >= 64:   # 64 層以上:歸屬查表逐層組前綴是層數平方」
severity: minor
blocking: 否
file: `scripts/lumos:40335`(對照 `scripts/lumos:40365`、`scripts/lumos:41873`)

4. ⚠ 交編排者判斷:`_E2E_PREPUSH_MARKERS` 是新增的機制,專案裡沒有對應做法。
   - 隔壁安全證據閘回顯外來文字時,只做跳脫,不拆 pre-push 認的字串。
   - 所以這是 e2e 比鄰居多防一層,不算做法衝突。
   - 但這兩串字是從原因文字(`scripts/lumos:64978`、`66308`)和 `scripts/hooks/pre-push:590`、`595` 抄來的字面值,沒有共用常數,也沒看到綁定測試。原因文字改字時兩邊會悄悄脫鉤。
   - 我判 minor,是否要綁測試請編排者裁。

引句:「_E2E_PREPUSH_MARKERS = ("受波及合約的測試沒過", "tier=high 且")」
severity: minor
blocking: 否
file: `scripts/lumos:41380`

## 問 3 第二種做法

先回答被點名的五項:
- `_e2e_clean` 拆逃逸帳字樣:是在 `_esc_clean` 外面疊一層,不是另起一套,見上面第 4 條。
- `E2E_DIR_LIST_MAX`:是比照既有的具名上限常數,算比照。
- `_e2e_relpath_err` 的控制字元判斷、`_E2eGitErr`、`_e2e_parent`:這三項各引入一種專案裡已有現成做法的第二種寫法,見第 5 到 7 條。

5. `_e2e_relpath_err` 自己寫了一份控制字元類別判斷,沒用專案共用的那一套。
   - 專案的共用底座是 `_PATH_SPECIAL_CATS`(`scripts/lumos:5392`)。
   - 現成的判斷函式是 `_path_special_chars(s, surrogate=False)`(`scripts/lumos:47974`)。新碼的 `("Cc","Cf","Zl","Zp")` 正好是它的 `surrogate=False` 結果,等於把同一組類別手抄一份。
   - 文件上也有指引:`_esc_clean` 的 docstring(`scripts/lumos:19352`)寫明,要「拒收或看得見」的用 `_PATH_SPECIAL_CATS` 那組。
   - 同族的 `_NOTE_REREAD_CTRL_CATS`(`47985`)是用 `_PATH_SPECIAL_CATS - {"Cs"}` 組出來的,沒有再手抄。
   - 以後共用組若新增類別,這裡會漏跟。

引句:「if any(unicodedata.category(ch) in ("Cc", "Cf", "Zl", "Zp") for ch in p):」
severity: major
blocking: 是
file: `scripts/lumos:40332`(對照 `scripts/lumos:47974`、`scripts/lumos:5392`)

6. `_E2eGitErr(str)` 是專案裡唯一一個用 `str` 子類別當錯誤型別旗標的做法。
   - 專案對「暫時失敗」與「內容有問題」的分法,是回傳多一格代碼或布林。例如 `_secev_mainline` 回傳 `(sha, 說明, 代碼)`(`scripts/lumos:10044`),`_push_rev` 回傳 `(sha, 失敗了嗎)`(`scripts/lumos:60636`)。另一種是專用例外,例如 `_SecevTimeout`(`scripts/lumos:8541`)。
   - `str` 子類別一旦被 `f"…{rerr}"` 串接、切片或 `.format`,型別就掉了,`isinstance` 判不出來。這比前一版看訊息文字的寫法穩,但屬於新做法。
   - `_e2e_tree_blob` 和 `_e2e_tree_json` 的 `(值, 錯誤)` 二元組若要加旗標,應改成既有的三元組(多一格代碼),或用專用例外。

引句:「class _E2eGitErr(str):」
severity: major
blocking: 是
file: `scripts/lumos:41429`(消費處 `scripts/lumos:41650` 附近的 `bad_record=not isinstance(rerr, _E2eGitErr)`;對照 `scripts/lumos:10044`、`scripts/lumos:60636`)

7. `_e2e_parent` 重寫了「取上一版提交,且分得出 git 失敗與沒有上一版」,專案已有現成的。
   - `_push_rev(repo, f"{sha}^1")` 就回 `(sha 或 None, 失敗了嗎)`:git 失敗是 `(None, True)`,根提交是 `(None, False)`,語意完全一樣。
   - 同一條 e2e 路徑的 `_e2e_gate_resolve` 已經在用 `_push_rev`(`scripts/lumos:41622`),`_push_start`(約 `scripts/lumos:61001`)也用 `_push_rev(f"{tip}^1")` 取第一個上一版。
   - 另有 `_merge_side_parents`(`scripts/lumos:65440`)用 `rev-list --parents -n 1` 取母提交,所以 `rev-list --parents` 這個指令本身有先例,問題是又多了第三個取上一版的函式。

引句:「raw = _nodehome_git(root, "rev-list", "--parents", "-n", "1", sha, timeout=_secev_git_left(deadline))」
severity: major
blocking: 是
file: `scripts/lumos:41634`(對照 `scripts/lumos:60636`、`scripts/lumos:41622`、`scripts/lumos:65440`)

不對齊共 7 條,其中擋實作的 4 條
