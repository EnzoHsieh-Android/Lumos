severity: minor

## 一、分層與依賴方向

沒有發現這一輪的修補破壞分層。

- 判定函式沒有直接寫帳。修補只動純文字函式:`_tg_stmt_at`(`scripts/lumos:48889`)、`_tg_path_join`(`:48449`)、`_tg_class_at`(`:48423`)、`_tg_class_has_body`(`:48459`)、`_tg_catch_no_fail`(`:48800`)。
  - 比對區段(`:48366`~`:49270` 左右)裡沒有 `_gate_event_or_warn`。
  - 這個函式在 `:49325` 以後才出現,屬於 `cmd_note_shape`,不是比對工具。
- 沒有繞過共用的 git 讀取函式。
  - 修補移除了 `_tg_retry_ok`。它在讀檔路徑上原本是 `_lens_git_dl(... "grep" ...)` 加逐支 `show`,沒有總量上限,現在整段不在了。
  - 剩下的 git 讀取仍走 `_lens_git_dl`(改動清單,`:48986` 一帶)和 `_nodehome_cat_blobs_capped(... max_total_bytes=_TG_MAX_TOTAL)`(內容)。修補沒有新增第二條讀檔路。
- 工具層沒有反向依賴印訊息層。
  - `_tg_stmt_at` 的括號配對改用共用的 `_rg_bracket_map`(`:47657`),由 `_tg_test_hits` 傳入。
  - `_tg_cand` 呼叫 `_out_clean`(`:19408`)是這一輪前就有的。`_out_clean` 的文件已寫明是底層共用,方向沒變。

## 二、命名與錯誤處理

新增與改寫的部分,命名、錯誤處理、印訊息都跟鄰居一致。

- **常數**
  - `_TG_MAX_STMT_CHARS`、`_TG_MAX_GENERIC_CHARS`、`_TG_MAX_PATH_CHARS` 沿用 `_TG_MAX_BYTES`、`_TG_MAX_LINES`、`_TG_MAX_TOTAL`、`_TG_MAX_STMTS`、`_TG_MAX_LINE_CHARS` 的 `_TG_MAX_*` 命名,也放在檔頭同一組(`:48376`~`:48378`)。
  - 舊的 `_TG_GENERIC_MAX`、`_TG_STMT_MAX` 已刪,grep 無殘留。
  - `_TG_CLASS_STOP`、`_TG_SUPERTYPE` 只是移到使用它們的函式前面。
  - `_TG_STMT_STOP`、`_TG_STMT_GOES_ON` 緊貼 `_tg_stmt_at`,`_TG_CHECK_CALL`、`_TG_NONSPACE` 跟同函式用的 try、catch 正則放在一起。
  - 以上跟「限制放檔頭、正則貼著函式」的現有做法一致。
- **`_tg_path_join` 的摘要**
  - 用 `hashlib.sha256(...).hexdigest()[:16]`,跟 `_tg_cand`(`:48980`)和圖片候選(`:49145`)同一寫法,上一輪點名的 sha1 前 12 碼已經沒了。
  - 函式內 `import hashlib` 是這個檔的慣例(同樣寫法有 41 處)。
- **`_tg_class_at`**
  - 改存路徑字串後,`_tg_functions` 取值用 `cls.get(s, "")`,空值是 `""`,不再是 `None`,兩端一致。
  - `_tg_class_has_body` 新增的行尾逗號與冒號判斷,沿用既有的 `continue` 加 `for _step in range(8)` 結構,行尾那段的長度沒有另立常數。同一區段裡 `end + 60`、`k + 200`、`k + 400` 也都是行內數字,所以沒有不對齊。
- **`_tg_kind`**
  - 建置檔與 CI 回 `None`,跟「不是這個工具管的檔」的既有回法一致。
  - `_tg_sort_changes` 對 `None` 直接 `continue`,沒有另開錯誤路。
  - 文件字串提到「代碼審 r4」,這個檔裡早有同樣的過程註記寫法(`:118`、`:192` 等)。
- **`_tg_stmt_at`**
  - 新簽名 `(kept, blank, bmap, i)` 的參數順序、用 `blank` 找位置再回 `kept` 取原文,跟 `_tg_strip` 的「位置一一對應」用法一致。
  - 括號配不到(`bmap.get` 回 `None`)就跳到 `end`,沒有丟例外,跟 `_rg_bracket_map` 使用者的處理一樣。

## 三、有沒有第二種做法

上一輪被點名的幾處都處理了,這一輪沒有引入新的第二種做法。

- **敘述擷取自己數括號**:已處理。`_tg_stmt_at` 現在用共用的 `_rg_bracket_map`(`:48889` 起,`:47657`),不再自己數深度。它另外靠 `_TG_STMT_STOP` 找邊界,這是「assume 敘述到分號或換行為止」的專用切法。`_tg_statements`(`:48581`)是從斷言字切到右括號再接鏈,用途不同,不算重複。
- **摘要用 sha1 前 12 碼**:已改 sha256 前 16 碼(見第二節)。
- **上限常數命名與位置**:已處理(見第二節)。
- **重試設定另走沒有上限的讀檔路**:已處理。`_tg_retry_ok`、`_tg_build_cands` 和整組建置檔與 CI 的函式、常數都拿掉了。
- **自動放行原因的第二寫入點**:這一輪修補沒有碰它。`:38905` 的 `out["autopass_reason"] = out["autopass_reason"] or ...` 與 `_lint_new_autopass`(`:39065`)並存的狀況維持上一輪的結論,已附理由放行,不再當成新問題。
- **拿掉建置檔與 CI 後有沒有留下沒人用的東西**:對固定版本逐項 grep,`_TG_SET`、`_TG_CI_*`、`_TG_BUILD_RES`、`_tg_head_id`、`_tg_block_heads`、`_tg_ci_*`、`_tg_build_*`、`_tg_names_test_task`、`tq/build-config`、`tq/ci-config` 全部是 0 處。
  - 仍保留的 `_TG_SNAP_WORDS`、`_TG_TIMEOUT`、`_TG_NUM`、`_tg_norm`、`_tg_diff_locs`、`_tg_timeout_raised` 都有呼叫者(`:48870`、`:48942`、`:49237` 一帶、`:49137`)。
  - 只剩下面一條殘留。

### A1 拿掉建置檔與 CI 後留下單一項目的分派表與過期說明
severity: minor
blocking: 否 — 結構是對的、行為沒錯,只是跟其餘「沒有只有一個鍵的分派表」的鄰居不一致,而且說明文字已經過期
引句:「per_kind = {"main": _tg_main_cands}」
file: `scripts/lumos:49066`(使用處 `:49084` 的 `cands += per_kind[kind](path, b, h)`;過期說明在 `_tg_has_long_line` 文件字串 `:49089` 起,寫「正式程式、建置檔、CI 是逐行線性的判讀」)

`_tg_analyze` 的 `per_kind` 原本分派 build、ci、main 三類。現在 `_tg_sort_changes` 只會送出 `test` 與 `main` 兩類,`test` 已在前面的 `elif` 處理,`else` 裡永遠只剩 `main`。單一項目的字典加動態取函式,是上一版三類分派留下的空殼,直接呼叫 `_tg_main_cands(path, b, h)` 即可。

另外 `_tg_has_long_line` 文件字串仍然提到建置檔與 CI,這兩類已不在這個工具的範圍內。這類文件字串有測試釘住文字的機制,建議跟著改。

不對齊共 1 條,其中 major 0 條
