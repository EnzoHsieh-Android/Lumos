severity: minor

以下對照用的行號,都來自 `git show 47434676:scripts/lumos`(被審版本)。

## 問 1. 分層與依賴方向

整體層次跟鄰居一致。新的 `_secev_tq_source_problems` 和 `_secev_tq_relevance` 放在 `_secev_judge_tq` 旁邊,由它呼叫。檔案讀取走 `ctx.tree.read_many`,算雜湊走 `_sha256_bytes`,`ctx.home_about` 是 `_SecevCtx` 上既有的掛載點。都在 `_secev_*` 這層內,沒有跨層直呼。

兩處值得記:
- `_secev_judge_tq` 新增 `ctrl` 參數,對齊 `_secev_judge_guard_kill(it, ctx, ctrl)`,同形。
- `_secev_tq_relevance` 在判單一項時,又呼叫 `_secev_items_for(ctx.env, ctrl, ctx._facts)`(8940 行),等於逐項判定回頭去重解析同一條護欄的兄弟項。`ctx._facts` 的用法跟 10481 行一致,但「單項判定依賴兄弟項」是這次新增的依賴方向。結構上沒跨層,只標注。⚠(判不準這算不算新做法,不列為不對齊條數。)

## 問 2. 命名與錯誤處理

判定代碼與例外類別的命名大致一致:
- `receipt_source_changed` 放在 `stale` 組,對應 `binding_changed`、`revision_changed`。
- `receipt_source_unmapped` 和 `fault_unrelated` 放在 `invalid` 組。
- `mainline_unknown` 沿用既有的整道代碼。
- `_SecevDataError(ValueError)` 對照 `_SecaprTooLong`(9452 行)、`_SecinvDupKey`(7152 行),同為 ValueError 子類、同一命名樣式。
- 「擋下:」字首、`_secev_*` 前綴也都沿用。

不一致處:

**輸出出口的寫法在同一函式內混用。**
新增了 `_secinv_say`,但舊寫法沒有收乾淨。
- `cmd_codeloop_security_approval_add`(11666 行)裡,「找不到 git 專案根目錄」和 `_secapr_add_read` 的錯誤仍是裸 `print(f"擋下:...", file=sys.stderr)`。
- 同一函式的「✓ 核可鏈第…筆已追加」和「提醒:」仍是 `print`。
- 前面的「擋下:{e}」已改成 `_secinv_say`。
- `cmd_security_approvals` 的 `print(f"擋下:{_secinv_show(str(e))}", file=sys.stderr)` 也是舊寫法。
- `_cl_say_sec_block` 自己寫 `print(_secinv_show(ln, None), file=sys.stderr)`,跟 `_secinv_say(ln, err=True)` 重複。

所以同一件事(印一行並跳脫)現在有三種寫法。結構對,屬 minor。

**同一個符號連結訊息有三份文字。**
`cmd_codeloop_security_approval_add` 前置檢查寫「是符號連結或跑出 repo,不讀也不寫」,`_secev_append_target.why` 寫「是符號連結(可能指到 repo 外),不寫」,`_note_audit_safe_dir.why`(44555 行起)寫「不寫也不清」。前置檢查還自己內嵌 `bad[1].relative_to(Path(root)).as_posix()`,沒走 `why`。

**`_SecevDataError` 沒有任何 raise 點。**
在 47434676 版全檔 grep,它只有定義(8506 行)和 `_secev_judge_item` 的 `except`(10290 行)。所以單項壞資料的兜底現在接不到任何東西。這不是命名問題,是行為落差,可能歸別的審查員管。⚠ 列出供他們查,不計入條數。

## 問 3. 第二種做法

**1. 寫入前擋符號連結:重做了既有的「安全資料夾」守衛。**
`_secev_append_target` 底層有走共用的 `_repo_path_unsafe`(44534 行),這點對。但它自己又寫了一份 `why()` 訊息、`mkdir` 加建前建後各查一次的包裝。這跟 `_note_audit_safe_dir`(44555 行)同形:同樣回 `(路徑, None)` 或 `(None, 原因)`,同樣建前建後各查、同樣有 `why`。那個函式的 docstring 明講「逐層與解析後的檢查用共用的 `_repo_path_unsafe`」,也就是已把這層收成單一來源。另外 22137 行附近有「r3 架構對齊席:不另寫一套」的註解先例。這次又多一份。若檔案本身要查,可以用 `_note_audit_safe_dir` 處理父資料夾,再對檔案呼叫 `_repo_path_unsafe`。
- 這條歸因為:有證據的修復回歸(新加的函式)。

**2. git 呼叫吃剩餘預算:沒有重做,但手寫樣式增生。**
沿用既有的 `_git_timeout`(57583 行)和 `_nodehome_git(..., timeout=)`(39497 行),擴充既有參數,沒有新工具。不過「`t = _git_timeout(deadline); if t <= 0: raise _SecevTimeout()`」這個四行樣式,在新碼又複製進 `_SecevTree.__init__`、`_secev_snap_clash`、`_secev_is_shallow`、`bookkeeping_only`、`_secev_mainline_override`。
另外新增 `_secev_deadline_check`(9706 行),而同層已有 `_SecevCtx.tick`(10048 行)和 `_SecevRun.tick`(10821 行)兩份「`monotonic() > deadline` 就丟 `_SecevTimeout`」。這是第三份,屬 minor。快照函式沒有 ctx 可呼叫,但樣式仍是重複。

**3. 輸出出口統一跳脫:沒有重做跳脫本身。**
`_secinv_lines_text` 和 `_secinv_say` 都建在 `_secinv_show` 之上,JSON 路徑改用既有的 `_json_text_escaped`,對。問題只是上面問 2 說的,新舊寫法並存。
`_jsonl_append_line_verified` 從文字模式 `"a"` 改成 `"ab"`,這是改共用函式,不是第二種做法。不過 canary、審查帳等其他呼叫者的行為也跟著變,請確認這是有意的。

## findings

### 寫入前擋符號連結的包裝,重做了既有的安全資料夾守衛
severity: minor
blocking: 否
引句:「建資料夾之前、之後各查一次(建的途中被換成連結)。」
file: `scripts/lumos:44555`(`_note_audit_safe_dir`,同形的 `why`、`mkdir`、前後各查)
file: `scripts/lumos:11644`(被審版的 `_secev_append_target`)
歸因:有證據的修復回歸。

### 資安族輸出出口新舊寫法在同一函式內混用
severity: minor
blocking: 否
引句:「print(f"擋下:{_secinv_show(str(e))}", file=sys.stderr)」
file: `scripts/lumos:11666`(approval_add 內 `print` 與 `_secinv_say` 並存)
file: `scripts/lumos:63397`(`_cl_say_sec_block` 自寫 `print(_secinv_show(ln, None), ...)`)
歸因:有證據的修復回歸。

### 符號連結擋下訊息出現三份不同文字,approval_add 的前置檢查另內嵌路徑組字
severity: minor
blocking: 否
引句:「是符號連結或跑出 repo,不讀也不寫——刪掉那個連結再跑」
file: `scripts/lumos:44555`(`_note_audit_safe_dir` 的 `why`)
歸因:有證據的修復回歸。

### 截止時間檢查再多一份自由函式,git 剩餘預算的四行樣式在新碼複製多處
severity: minor
blocking: 否
引句:「沒有截止時間不查;過了就丟 _SecevTimeout(整道 evaluation_timeout)。」
file: `scripts/lumos:10048`(`_SecevCtx.tick`)
file: `scripts/lumos:10821`(`_SecevRun.tick`)
歸因:有證據的修復回歸。

不對齊共 4 條,其中 major 0 條

severity: minor
(blocking 條數:0)

重判說明:第一條降為 minor。它底層檢查確實走共用的 `_repo_path_unsafe`,單一來源沒有分岔。重複的只是外層訊息與建資料夾的薄包裝,結構與依賴方向都對,所以不算引入第二種做法。檔首與末行已隨之改為 minor。
