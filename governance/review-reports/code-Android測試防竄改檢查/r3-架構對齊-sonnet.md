severity: major

白話總結:這一輪修補多半真的收斂了,沒有跨層直呼。但 `_tg_retry_ok` 又自己手寫了一套註解剝法,而且我實跑過,它和專案既有的 `_tg_strip` 結果不一樣。

## 一、分層與依賴方向

這一輪沒有判定函式直接寫帳、繞過共用 git 讀取函式、或讓工具層反過來依賴印訊息層。

- 判定函式只回傳 events,不寫帳。
  - `_lint_new_off` 新增的錯誤事件只是 `out["events"].append((kind, …))`,跟既有的 `("skipped"…)` 同一個出口。
  - 對照:`_lint_new_verdict` 的 docstring「★這裡不寫帳★」,以及 `scripts/lumos:69327` 的 `_gate_failopen` 才是寫帳點。
- git 讀取都走共用函式。
  - `_tg_retry_ok` 用 `_lens_git_dl`(`scripts/lumos:63872`)。
  - `_tg_start` 用 `_lens_default_base`(`scripts/lumos:64296`),兩次呼叫都傳了 deadline。
- `_tg_cand`、`_lint_waive_origin` 改用 `_out_clean`(`scripts/lumos:19408`)。它的 docstring 寫明「底層共用」,不是印訊息層專屬,所以方向沒有倒。
- `_lint_waivers_add` 的時間改呼叫 `_e2e_now`(`scripts/lumos:41566`)。這是 lint 閘借用 e2e 區的小工具。`scripts/lumos:37927` 的 `_e2e_who`、`_e2e_now` 已有同樣的借法,我不列為不對齊。

### A1 `_tg_start` 的主線查法是第三種組合
severity: minor
blocking: 否 — 只是共用函式參數的組合,不是新算法,命名與結構沒歪
引句:「fork = _lens_default_base(root, tip=head, include_local=False, deadline=deadline) \」
file: `scripts/lumos:51040`(回頭重讀只用 `include_local=False`)、`scripts/lumos:47855`(手動檢查只用 `include_local=True`)
說明:兩個鄰居各選一種模式。`_tg_start` 變成「遠端優先、找不到再退本機」的串接(`scripts/lumos:49122-49123`),語意跟兩邊都不同。算法仍是同一支共用函式,所以只算 minor。

## 二、命名與錯誤處理

命名大致跟鄰居一致:`_tg_has_long_line` 對得上 `_tg_has_assertion`,`_ASSUME_RE`、`_SKIP_ANN_RE` 帶 `_RE` 尾碼也對得上。`_TG_QUOTED`、`_TG_NOT_TEST_PLUGIN` 沒尾碼,但同檔既有的 `_TG_TRY`、`_TG_CONST` 也沒有,所以不算不一致。

錯誤處理方面,`_lint_new_off` 現在會為比對出錯記一筆帳,格式跟既有事件一致。

### B1 改寫後留下兩個沒人用的舊常數
severity: minor
blocking: 否 — 只是清理沒做完,行為不受影響
引句:「_TG_SKIP_RE = re.compile(_TG_SKIP_ANN_RE.pattern + "|" + _TG_ASSUME_RE.pattern)」
file: `scripts/lumos:48777`(`_TG_SKIP_RE`)、`scripts/lumos:48886`(`_TG_CI_TEST_TASK`)
說明:
- `_TG_SKIP_RE` 在 `_tg_test_hits` 改成分開用 `_TG_SKIP_ANN_RE` 與 `_TG_ASSUME_RE` 之後,全檔只剩定義;`test_lumos.py:120605` 只在 docstring 裡提到它。
- `_TG_CI_TEST_TASK` 也只剩定義。「什麼算測試任務名」的判法現在寫在 `_tg_ci_test_tasks` 裡的 `re.fullmatch(r"\w*(?:[Tt]est\w*|check)", name)`,所以同一個定義有兩份,其中一份是死的。

### B2 `_tg_catch_no_fail` 把正規式寫在函式裡,有一個還重複 `_TG_TRY_OK`
severity: minor
blocking: 否 — 結構仍對,只是跟同檔常數做法不一致
引句:「("assert", _TG_ASSERT_RE), ("ok", _TG_TRY_OK), ("fail", re.compile(r"(?<![\w])(?:Assert\.)?fail\s*\(")),」
file: `scripts/lumos:48735`(`_TG_TRY_OK`、`_TG_RUNCATCH` 都是模組常數)
說明:同一區塊的 try/catch 相關正規式都放在模組層,這裡的 `fail` 與 `throw` 卻在每次呼叫時才 `re.compile`。`_tg_statements` 與這支函式也各自區域 `import bisect`,雖然 `scripts/lumos:57` 已在頂部匯入;不過 `scripts/lumos:48081` 也這樣寫,這點不算不一致。

## 三、第二種做法

### C1 `_tg_retry_ok` 自己手寫一套註解剝法
severity: major
blocking: 是 — 判準是「引入第二種做法」,同一組建置檔已有現成的剝註解函式
引句:「return any(pat.search(ln.split("//", 1)[0]) for ln in r.stdout.splitlines())」
file: `scripts/lumos:48859`(`_tg_build_hits` 用 `_tg_strip(text, keep_strings=True)`)、`scripts/lumos:48409`(`_tg_strip` 定義)
說明:
- 同一個函式族讀建置檔的註解,一律走 `_tg_strip`。這裡改用 `split("//")` 硬切。
- 我把 frozen 版本載入後實測了。
  - `'val u = "http://x"; failOnPassedAfterRetry = true'`:`_tg_strip(ln, True)` 保留整行,手切的結果是 `'val u = "http:'`,把後面的 `= true` 切掉了。
  - `'failOnPassedAfterRetry = true /* c */'`:`_tg_strip` 認得區塊註解,手切不認得。
- `_tg_strip` 對單行文字可直接用,改成 `_tg_strip(ln, True)` 就是現成的做法。
- 這個問題是「判斷一致性」,不是找 bug。

### C2 單行長度上限放在 `_tg_analyze`,不在放其他上限的 `_tg_read`
severity: minor
blocking: 否 — 同一條規則 `tq/too-large`、同一批常數群,只是檢查位置分散;判不準 ⚠ 交編排者,若認為「另一套上限檢查」可升 major
引句:「elif _tg_has_long_line(b) or _tg_has_long_line(h):」
file: `scripts/lumos:49079`(`_tg_read` 的 docstring 寫「單檔上限、總量上限都在這一層」,`scripts/lumos:49098`、`scripts/lumos:49102` 是位元組與行數兩個上限)
說明:
- 位元組、行數、總量三種上限都在 `_tg_read`,以 `"TOOLARGE"` 哨兵值回傳。
- 新的單行上限改在 `_tg_analyze` 另開一個分支,指紋也改成 `:line` 後綴並多帶 `extra`。
- 結果是 `tq/too-large` 有兩個產生點,`_tg_read` 的 docstring 也不再完整。

### C3 上一輪被點名的幾處處理狀況

| 項目 | 處理了嗎 | 備註 |
|---|---|---|
| CI 區塊開頭兩種算法 | 是 | `_tg_ci_head` 刪了,改由 `_tg_ci_blocks` 的堆疊一趟回傳 `parent`,算法只剩一種。 |
| 外來字串清法 | 是 | `_tg_cand` 與 `_lint_waive_origin` 都統一成 `_out_clean`。 |
| 時間格式 | 是 | `_lint_waivers_add` 的 `ts` 改用 `_e2e_now()`,跟 `scripts/lumos:37927` 和 e2e 端同格式。 |
| 沒宣告檢查工具的判斷 | 是 | 抽成 `_lint_new_declared`,兩處(`_lint_new_verdict`、`_lint_new_tools`)共用。 |
| 放行檔路徑常數 | 是 | `_cl_say_lint_next` 改用 `_LINT_NEW_WAIVERS_REL`,全檔不再有寫死的字面路徑。 |
| 重試查詢的正規式方言 | 部分 | git grep 改成 `-F` 粗篩,判定改用 Python 的 `_TG_SET`,方言統一了。但新引入 C1 的手切註解。 |
| 括號配對兩份並存 | 折衷 | 見 C4。 |
| 自動放行原因兩個寫入點 | 沒處理完 | 見 C5。 |

### C4 括號配對兩份並存,只搬位置與寫文件,沒合併
severity: minor
blocking: 否 — 兩份規則已註明並有隨機字串測試綁住等價,不再各自漂移;判不準 ⚠ 交編排者
引句:「★跟 _rg_balanced 是同一條配對規則的兩種查法★」
file: `scripts/lumos:47639`(`_rg_balanced`)、`scripts/lumos:47654`(`_rg_bracket_map`)、`scripts/test_lumos.py:121346`(`t_rg_methods_expression_body_and_backtick`,內有 300 組隨機字串比對)
說明:`_rg_bracket_map` 已搬到 `_rg_balanced` 旁邊,docstring 寫明「改其中一支的規則要兩支一起改」,並由測試綁住。兩份實作仍然存在。

### C5 自動放行原因仍有兩個寫入點加兩個讀取端的退路
severity: minor
blocking: 否 — 兩處已改成同一語意「沒填才填」,但來源仍分散
引句:「out["autopass_reason"] = out["autopass_reason"] or "%d 條命令跑不出可解析的結果(工具沒裝/逾時/拉不到規則)" % len(env_undone)」
file: `scripts/lumos:38983-38984`(`_lint_new_verdict` 的 `if out["autopass"] and not out["autopass_reason"]`)、`scripts/lumos:69327`、`scripts/lumos:70394`(讀取端仍寫 `autopass_reason or reason`)
說明:
- 寫入點有兩處:`_lint_new_classify` 和 `_lint_new_verdict`。
- `_lint_new_verdict` 開頭兩條早退路徑(例如 `status="env-unavailable", autopass=True, reason=…` 後直接 `return out`)沒有填 `autopass_reason`,只靠兩個讀取端的 `or reason` 補。
- 這樣「帳要寫哪個原因」有三種來源:寫入端複製 reason、classify 自己填、讀取端退路。

不對齊共 8 條,其中 major 1 條
