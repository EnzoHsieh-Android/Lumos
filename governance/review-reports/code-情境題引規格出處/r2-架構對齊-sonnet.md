severity: major

## 1. 分層與依賴方向

對齊。
- 新碼都在人裁指令那一塊(`scripts/lumos:75430` 起),也就是補丁修改的 `_situation_rule_*` 那一帶。它們向下呼叫共用層,沒有反向依賴,也沒有跨層直呼。
- 讀 HEAD 版改走 `_kt_sit_read_many`(`scripts/lumos:39912`),取代原來自己 `subprocess` 跑 `git show`。這跟切段共用同一個讀法,方向正確。
- 寫計劃改走 `_write_refusal_reason`(`scripts/lumos:30492`)加 `_write_bytes_atomic`(`scripts/lumos:30559`),取代自寫的原子寫。這是把上一輪自寫的一套收回共用,對照 `_write_lf`(`scripts/lumos:30549`)也是呼叫 `_write_bytes_atomic`。
- 共用函式被改的方式一致:
  - `_confirm_tty_open` 是從 `_confirm_tty_dev` 抽出來的,`_confirm_tty_dev` 的行為沒變(`scripts/lumos:35727` 一帶)。
  - `_clause_sha` 放在 `_clause_body_of` 旁邊(`scripts/lumos:13913`)。
  - `_expected_gov` 沿用 `ctx["exp_gov"]` 一次讀帳的做法,`_gov_vc_gate_events` 收 tuple 的閘名也有先例(`scripts/lumos:28255`)。
  - 保留標記常數放在 `_ISOLATED_WT_STALE_SEC` 旁邊。
- `_kill_plat_top({"tops": {}}, …)` 臨時自組 ctx 的形狀符合該函式(`scripts/lumos:26379`)的要求。

## 2. 命名與錯誤處理

大致對齊。
- 命名:`_situation_rule_*`、`_confirm_tty_*`、`_expected_gov` 都用 `_` 前綴,跟鄰居一樣。
- rc 與輸出:
  - 拒絕一律走 `_situation_rule_say`,印 stderr 回 2。
  - 帳沒記到回 1。這跟 `cmd_situation_rule` 原本的 docstring 一致。
- `_situation_rule_write` 把 `WriteBlocked` 接住轉成回傳原因字串,不往上漏。鄰居(`scripts/lumos:30483` 的註解)是「各分派照原本寫法接」,這裡的做法在人裁指令內部自洽。
- 唯一的小差異見 a2:CRLF 讀檔的判定。

## 3. 第二種做法

不對齊兩處。

**訊號處理(a1)**
- 專案現有的 SIGTERM 處理只有 `_lint_wt_begin`/`_lint_wt_end`/`_lint_wt_on_term`(`scripts/lumos:41454`、`41481`、`41518`)。
- 它的寫法:
  - 全域登記表;
  - 處理器自己收程序群組並刪暫存;
  - `os._exit(3)`;
  - 離開時一律還原成 `SIG_DFL`。
- 新的 `_situation_rule_signals`(`scripts/lumos:75700` 起)是另一套:
  - 處理器改成丟 `KeyboardInterrupt`;
  - 多接 SIGHUP;
  - 用巢狀 `contextmanager` 存下並還原進來前的處理器,進來前是忽略就保留忽略;
  - 不在主執行緒就不裝。
- docstring 寫「寫法照 `_lint_wt_begin/_lint_wt_end`」,但實際是不同機制。
- 同一個訊號現在有兩種安裝與還原語意,而且 `_lint_wt_begin` 的註解說這是「新慣例」。
- 我標 ⚠:若編排者認為「轉成 `KeyboardInterrupt` 走既有 Ctrl-C 收尾」算同一慣例的延伸,可降為 minor。

**讀計劃拒 CRLF(a2)**
- 新增 `_situation_rule_read`(`scripts/lumos:75484`)自己判 `b"\r\n" in raw`,並把 `load_raw_for_edit`(`scripts/lumos:30525`)的拒絕訊息整段抄過來。
- `load_raw_for_edit` 同時拒 BOM,這裡不拒。
- 專案裡已有幾處行內 CRLF 判斷(`scripts/lumos:33064`、`34753`),所以不算全新的做法。但這是同一個判定的第二份拷貝,行為還有出入,所以只列 minor。

## a1 殺傷力期間的訊號處理另起一套寫法(不同於 _lint_wt_begin)
severity: major
blocking: 是
引句:「signal.signal(s, _on)」
file: `scripts/lumos:75700`(對照 `scripts/lumos:41454`、`scripts/lumos:41518`)

## a2 讀計劃拒 CRLF 另寫一份,訊息照抄且少了 BOM 判定
severity: minor
blocking: 否
引句:「計劃的換行是 Windows 式(CRLF),工具只寫 Unix 式(LF)、不偷偷幫你改行尾」
file: `scripts/lumos:75484`(對照 `scripts/lumos:30516`)

不對齊共 2 條,其中 major 1 條
