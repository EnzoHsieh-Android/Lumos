severity: major

line 號:`scripts/lumos:行號` 是基底版 d42840cf 的行號;被審版本 b99f52c8 裡這些行因 diff 插入而位移。diff 內的位置寫成「patch 行 N」。這次沒有跑測試,也沒有改 repo 任何檔。

## 三問

**1. 分層與依賴方向:對齊**
- 新碼都放在 `scripts/lumos` 單檔內,用 `_secev_*`、`_secapr_*`、`_seccell_*` 前綴,跟既有的 `_secinv_*` 家族同層、同命名法。
- 讀提交樹走 `_nodehome_list` 和 `_nodehome_cat_blobs_capped`(`scripts/lumos:35543`、`:35974`),跟鄰居一樣不讀工作目錄。
- 嚴格 JSON 沿用 `_secinv_json_loads`(`scripts/lumos:7035`),只多加深度檢查。
- JUnit 與收證核對沿用 `test_quality.junit`、`load_receipt_data`、`fault_check`,沒有另寫第二份解析。
- 接進 code-loop 的方式是 `_codeloop_security_step`,結果用 `_codeloop_guard_verdict.last_security` 帶出。這跟既有的 `last_bound`、`last_lint_new`(`scripts/lumos:59001`、`:59056`)同一做法。
- argparse 註冊也一樣:`security` 底下新增 `evidence` 和 `approvals`,`code-loop` 底下新增旗標。
- pre-push 掛鉤用「讀檔找旗標字樣」探測舊版 lumos,沿用 `--keep-going` 的探法,沒有跨層直呼。

**2. 命名與錯誤處理:大體對齊,有三處偏離**
- 對齊的部分:
  - 擋下訊息用 `擋下:` 開頭加 stderr,rc 1 是擋、2 是參數錯,跟 `_jsonl_append_verified`(`scripts/lumos:13965`)一致。
  - 治理帳寫入走 `_gate_event_or_warn`(`scripts/lumos:1910`)。
  - 擋下訊息用三段式。
- 偏離一:`_secev_log_exception_use` 讀治理帳的方式不同(見 F4)。
- 偏離二:非分支 ref 的 pre-push 把任何非 0 都當擋下(見 F5)。
- 偏離三:寫檔不處理 `OSError`(見 F3)。

**3. 第二種做法:有三條 major**
- 重複的雜湊函式(F1)。
- 手寫的 git 呼叫包裝,另有一套逾時處理(F2)。
- 手寫的 JSONL 追加(F3)。

## findings

### F1 雜湊函式 `_secev_sha` 重造 `_sha256_bytes`,另有一處行內雜湊
severity: major
blocking: 是
引句:「r["_sha256"] = _h.sha256(ln).hexdigest()」
- 對照:`scripts/lumos:13190` 的 `_sha256_bytes(raw)` 是專案共用的「位元組 sha256」。它的 docstring 寫明是共用入口,`:30173` 的呼叫端也直接用它。
- 這份 diff 新增 `_secev_sha`(patch 行 2006),本體同樣是 `hashlib.sha256(b).hexdigest()`。`_secev_backing_rows`(patch 行 1921)又在行內再算一次。
- 兩處的功能都跟 `_sha256_bytes` 一樣,卻沒有呼叫它。`_secev_sha` 被用在核可鏈與規範化 JSON 約 20 處。
- 建議:改呼叫 `_sha256_bytes`,刪掉 `_secev_sha`。`_secapr_fingerprint` 要的是 base64 的原始摘要,不同形狀,可以留。

### F2 `_secev_git` 手寫 git 包裝,忽略截止時間,另開一套逾時機制
severity: major
blocking: 是
引句:「return _lens_git(repo_root, "-c", "log.showSignature=false", *args, timeout=timeout)」
- 對照:`scripts/lumos:53558` 的 `_lens_git_dl(repo_root, *args, deadline=None)` 已經把截止時間經 `_git_timeout`(`:53550`)夾進單次 git 逾時。`_push_rev`、`_nodehome_cat_blobs_capped`、`_push_mainlines` 都走這條路。
- `_secev_git`(patch 行 2367)寫死 `timeout=20`,沒有 `deadline` 參數。
- 這份 diff 同時有整道 60 秒預算(`_SecevCtx.tick`、`_SecevRun.tick`,在 `_SecevTimeout` 上)。但 `ctx.ancestor`、`ctx.depth`、`log -1`、`grep -l` 等呼叫(patch 行 2584、2592、3274、3390、3551、3591)明明有 `ctx.deadline` 可用,卻各自吃固定的 20 秒,不受剩餘預算約束。同一道判定因此有兩套逾時語意:一套 deadline,一套固定秒數。
- `_secapr_verify_sig` 呼叫 `ssh-keygen` 也是固定 `timeout=20`(patch 行 2044),同樣不看 deadline。
- `showSignature=false` 這個需求鄰居已處理過(`scripts/lumos:40000` 附近有註解),可以走既有路徑。
- 建議:`_secev_git` 改成 `_lens_git_dl` 加那個 `-c`,所有呼叫傳 `deadline`。

### F3 JSONL 追加手寫,沒走 `_jsonl_append_verified`
severity: major
blocking: 是 ⚠(是否能直接套用,交編排者判斷)
引句:「with open(wt, "ab") as fh:」
- 對照:`scripts/lumos:13965` 的 `_jsonl_append_verified` 負責:
  - 補尾端缺的換行,用 `_ledger_tail_needs_newline`(`:1847`)。
  - 捕捉 `OSError`,回 rc2 並印 `擋下:寫不進記錄檔`。
  - 寫完另開檔讀回自驗。
- 這份 diff 有兩處手寫追加(patch 行 3948 的 `cmd_codeloop_security_approval_add`,patch 行 4005 的 `cmd_codeloop_security_backing`)。
- 兩處自己處理「尾端沒換行」,沒有 `try/except OSError`,也沒有讀回自驗。寫入失敗會直接噴 traceback,而不是 `擋下:`。
- ⚠ 保留原因:核可鏈要求規範化位元組(`separators=(",", ":")`、`sort_keys`),`_jsonl_append_verified` 內部是 `json.dumps(rec, ensure_ascii=False)`,不能原樣套用。可行做法是抽出「已序列化行的追加加自驗」這一層,讓兩邊共用,而不是各寫一套。

### F4 治理帳去重用字串搜尋,沒走 `_ledger_lines` 加 `json.loads`
severity: minor
blocking: 否 ⚠
引句:「if f'"sec_exc_key": "{key}"'.encode() in text:」
- 對照:讀 `docs/.governance-log.jsonl` 的鄰居都走 `_ledger_lines(...)` 再逐行 `json.loads`,例如 `scripts/lumos:1349`、`:13041`、`:15356`。
- `_secev_log_exception_use`(patch 行 4493)用 `read_bytes()` 加子字串比對。這依賴 `json.dumps` 預設的 `": "` 分隔,也依賴鍵名順序與跳脫方式,是第二種讀帳法。
- 結構是對的(寫入仍走 `_gate_event_or_warn`),只是讀法不一致。我不確定治理帳的寫入端是否保證這個序列化格式,所以標 ⚠,保守標 minor。

### F5 非分支 ref 的 pre-push 對 rc 的解讀跟分支路徑相反
severity: minor
blocking: 否
引句:「if [[ "$sec_rc" -ne 0 ]]; then」
- 對照:同檔分支路徑(diff 內相鄰的 context 註解)是「rc=1 擋、其餘 rc≠0/1 異常 fail-open 放行」。
- 新的 tag 路徑(patch 行 87 到 100)把任何非 0 都當擋下。diff 的註解有寫這是刻意的,`cmd_codeloop_security_only` 也特別規定判不清回 1。
- 這是有理由的偏離,但同一支掛鉤裡 rc 語意因 ref 種類而相反,後來的人容易誤判。
- 建議:至少在對照表或註解裡指回分支路徑,說明為何不同。

### F6 `_JUnitStream` 重複 DTD 拒收邏輯,`NoDtdTreeBuilder` 變成死碼
severity: minor
blocking: 否
引句:「raise ValueError("DTD/entity declarations not accepted")」
- 對照:`scripts/test_quality.py` 的 `NoDtdTreeBuilder.doctype`(`:133` 附近)原本是唯一的拒 DTD 點。
- 新的 `_JUnitStream.doctype`(patch 行 4989 附近)複製了同一句。現在全 repo 只剩 `test_quality.py:133` 的定義和 `:160` 的 docstring 提到 `NoDtdTreeBuilder`,實際不再有人使用。
- 建議:讓 `_JUnitStream` 以 `NoDtdTreeBuilder` 的 `doctype` 為本體(委派或繼承),或刪掉 `NoDtdTreeBuilder`。

### F7 小工具函式重複
severity: minor
blocking: 否
引句:「return root if root is not None and (Path(root) / ".git").exists() else None」
- 對照:`scripts/lumos:6932` 的 `_secinv_repo_root` 已經只回帶 `.git` 的上層。
- `_secev_repo_root`(patch 行 3705)在它外面再檢查一次 `.git`,是多餘的薄包裝。
- 另外 `_dt_now_iso`(patch 行 4013)是新工具函式,而同區 `cmd_security_list` 的做法是行內寫 `_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")`(patch 行 1048、1162)。
- 兩者都無害,只是一致性問題,各自能合併。

## 結論

不對齊共 7 條,其中 major 3 條(F1、F2、F3)。F3 的可行修法需要編排者判斷,已標 ⚠。

被審 patch 位置:`/Users/enzo/orca/workspaces/lumos-toolchain/security-gate/governance/review-reports/code-安全證據閘與資安格子/r1-lumos.patch`。
基底版 `scripts/lumos` 我抽出放在 `/tmp/lumos-seat-work/code-安全證據閘與資安格子/架構對齊-sonnet/base_lumos.py`,共用 helper 的行號都取自這份檔。
