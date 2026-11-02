severity: major

## 一、分層與依賴方向

三個子問題的結論:

- **判定函式寫帳**:沒有。`_lint_new_autopass` 只改 `out`,不寫帳。帳仍由 `_codeloop_lint_new_step` 用 `_gate_event_or_warn` 寫(`scripts/lumos:69470` 前後),和上一輪一致。
- **工具層反向依賴印訊息層**:沒有。`_tg_*` 沒有新增對 `_say_*` 或 `print` 的呼叫。
- **`_lint_waive_show` 加的 `_out_clean`**:呼叫方向和同族的 `_lint_waive_origin`(`scripts/lumos:37873`)一樣,只有顯示函式往下用清洗函式。

只有一處讀 git 的做法和鄰居不同:

### A1 `_tg_retry_ok` 另走一條沒有大小上限的讀檔路
severity: minor
blocking: 否 — 照樣經過共用的 `_lens_git_dl`,沒有跨層;只是同一個比對功能裡,讀建置檔內容多了一條沒有單檔上限的路。
引句:「got = _lens_git_dl(root, "show", ref, deadline=deadline)」
file: `scripts/lumos:49214`(`_tg_read`:同一模組讀建置檔內容走 `_nodehome_cat_sizes` 加 `_nodehome_cat_blobs_capped`,受 `_TG_MAX_BYTES`、`_TG_MAX_TOTAL` 限制)
說明:

- 上一版用 `git grep -h`,輸出只有命中的行,量自然有界。這一版改成 `git grep -l` 再逐支 `git show` 整檔,單檔大小沒有檢查。
- 建置檔其他讀取一律經 `_tg_read`,超過上限會列 `tq/too-large`。這裡的 `[:50]` 是寫死的魔術數字,不是 `_TG_*` 常數。
- 結構上沒有越層,所以只列 minor。要對齊的話,可以把 `ref` 切成提交和路徑,交給 `_tg_read` 的批次讀取。

## 二、命名與錯誤處理

這一輪新增或改寫的函式,命名都落在 `_tg_` 加動詞或名詞的同一組。錯誤處理也跟鄰居一致:

- `_tg_read` 失敗回 `None`,呼叫端轉成 `(None, 訊息)`,和 `_tg_changes` 的 `None` 慣例相同。
- `_lint_waive_show` 外來字串逐欄清洗,和同族的 `_lint_waive_origin` 同做法。檔案裡另有「整行過一次 `_out_clean`」的寫法(`scripts/lumos:42038`、`43300`),但這裡 `_ai` 後綴必須留在清洗之外,所以我不列。
- `skip_env` 改成 `== "1"`,對齊 `LUMOS_SKIP_ROOM_GUARD`(`scripts/lumos:48273`)和 `LUMOS_SKIP_NOTE_SHAPE`(`scripts/lumos:49576`)。

命名上有一處不一致:

### A2 新常數的命名樣式與位置和既有的上限常數不同
severity: minor
blocking: 否 — 命名與位置不一致,結構對。
引句:「_TG_STMT_MAX = 2000」
file: `scripts/lumos:48372`(`_TG_MAX_BYTES`、`_TG_MAX_LINES`、`_TG_MAX_TOTAL`、`_TG_MAX_STMTS`、`_TG_MAX_LINE_CHARS` 集中在檔頭,樣式是 `_TG_MAX_<物>`)
說明:

- 新增的 `_TG_STMT_MAX`(字元數,`scripts/lumos:48945`)和 `_TG_GENERIC_MAX`(`scripts/lumos:48515`)用的是 `<物>_MAX`,而且散在函式之間,不在檔頭那組。
- `_TG_STMT_MAX = 2000` 和 `_TG_MAX_STMTS = 2000` 數字一樣、意思不同(字元數對敘述個數),讀的人很容易看錯。
- `_TG_SUPERTYPE`、`_TG_CLASS_STOP`、`_TG_GENERIC_MAX` 定義在使用它們的 `_tg_supertype_next_line` 之後。鄰居是正規式先於使用它的函式,例如 `_TG_NAME_RE` 在 `_tg_class_at` 前(`scripts/lumos:48417`)。
- 上一輪點的「單行上限放在不同層」,這次用 docstring 講清楚理由(測試檔才套,所以放 `_tg_analyze`),我認為算處理了。

## 三、第二種做法

### A3 `_tg_stmt_at` 是第二套「敘述擷取加括號配平」
severity: major
blocking: 是 — 同一個模組裡,「一個敘述」現在有兩套邊界定義和兩套括號深度計算。
引句:「depth, k, end = 0, i, min(len(t), i + _TG_STMT_MAX)」
file: `scripts/lumos:48584`(`_tg_statements`:用 `_rg_bracket_map(sb)` 一趟算好配對,從斷言字取到右括號,再接 `_TG_CHAIN` 的鏈)、`scripts/lumos:47657`(`_rg_bracket_map`)
說明:

- 既有做法是「斷言字、配對括號、鏈」,括號配對全部交給 `_rg_bracket_map`。`_tg_class_at`、`_tg_functions`、`_tg_catch_no_fail` 也都這樣用。
- 這一輪的 `_tg_stmt_at` 自己逐字元數 `([{` 與 `)]}` 的深度,另外定義「敘述到哪結束」:分號、多出的右括號,或換行且上一段不像沒寫完。
- `_rg_bracket_map` 的 docstring 寫明:配對規則由 `t_rg_methods_expression_body_and_backtick` 綁住,要改就兩支一起改。這第三份手寫計數沒有被綁住。
- `_tg_test_hits` 裡的 `kept` 沒有先算 bracket map,但可以算一次,遇到左括號就跳到 `bmap[k] + 1`。換行與分號的判斷是新增的語意,可以留,括號計數不該另寫。
- 測試名稱等身分現在有兩種「敘述」口徑:`assert` 類取到鏈尾,`assume` 與 `snapshot` 類取到分號或換行。

### A4 `_tg_head_id` 用了另一種摘要
severity: minor
blocking: 否 — 同樣是截短的十六進位摘要,只有演算法和長度跟鄰居不同。
引句:「return norm[:120] + "…#" + hashlib.sha1(norm.encode("utf-8", "replace")).hexdigest()[:12]」
file: `scripts/lumos:49180`(`_tg_cand` 的 `hashlib.sha256(...).hexdigest()[:16]`)、`scripts/lumos:49403`(`_tg_image_cands` 的 `sha256(...)[:16]` 加 `d + ":" + sig`)
說明:

- 同一個模組裡有兩處,摘要都是 sha256 取前 16 碼。檔案裡其他指紋也幾乎全是這個形狀,例如 `scripts/lumos:14031`、`26191`、`45584`。
- 這一處改用 sha1 前 12 碼,連接字串也不同(`…#`,鄰居用 `:`)。
- 建議對齊 sha256 前 16 碼。如果編排者認定「另一種雜湊身分」一律算 major,可以升級這條。

### A5 自動放行的寫入點只收了一半
severity: minor
blocking: 否 — 主要的四個早退點已經統一成一個函式,剩下的是語意不同的一處。
引句:「out.update(status="env-unavailable", autopass=True, reason=reason, autopass_reason=reason)」
file: `scripts/lumos:38904`(`_lint_new_classify` 另外直接寫 `out["autopass"] = True`、`out["autopass_reason"]`,下面再單獨設 `status` 與 `reason`)
說明:

- 這次 `_lint_new_autopass` 收掉了 `_lint_new_verdict`、`_lint_new_tools` 的四處早退,也拿掉事後補欄位的 `if out["autopass"] and not out["autopass_reason"]`。上一輪的主訴處理了。
- `_lint_new_classify` 仍是第二個寫入點:`autopass_reason` 用 `or` 保留先寫的值,`reason` 另寫「有命令跑不動(已自動放行並記帳)」。
- 現在寫 `autopass_reason` 有兩種做法(helper 和直接寫欄位)。讀端已經統一只看 `autopass_reason`,所以不會出錯,只是日後改欄位語意要兩處一起改。

上一輪點名的幾處,逐項結果:

- **重試設定自己用 split 剝註解**:已改用 `_tg_strip(..., keep_strings=True)`,處理了。
- **改寫後沒人用的常數**:我對 `_TG_*` 與 `_tg_*` 逐一數了引用,沒有剩下無人用的。`_TG_TASK_REF`、`_TG_QUOTED`、`_TG_SKIP_RE`、`_TG_CI_TEST_TASK` 都已刪掉。
- **正規式寫在函式裡**:`_tg_ci_test_tasks` 新增的 `re.findall(r"[^\s()<>{}`]+", …)` 和 `_tg_retry_ok` 裡的 `re.compile`,還是在函式內。但這個區段原本就有大量函式內正規式(例如 `scripts/lumos:48642`、`48663`、`49071`),所以不算違反鄰居做法,我不列。
- **單行上限放在不同層**:已加文字說明理由,算處理。
- **分岔點的第三種組合**:已附理由放行,我沒再審。

不對齊共 5 條,其中 major 1 條
