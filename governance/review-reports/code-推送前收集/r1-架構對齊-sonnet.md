severity: major

我的評語在「做法」,不在功能。掛鉤收集寫法、`push-summary` 子命令、`_cl_say_*` 拆分、`_fin` 收尾和 `LUMOS-BLOCKS:` 機讀行都跟既有做法一致。只有版本探測一處是第二種做法。我只讀了兩份 patch 和 `prepush-collect` 工作樹的 `scripts/hooks/pre-push`、`scripts/hooks/pre-commit`、`scripts/lumos`,沒有實際執行任何程式。

**對齊的幾項,逐一說明**
- 掛鉤收集寫法:`pp_record_block` 加判斷點統一 `exit 1`,承襲 pre-commit Gate L 的「記旗標、跑完再擋」。它多了暫存檔與筆數,是延伸,不是第二套做法。
- `LUMOS-BLOCKS:` 機讀行:`scripts/lumos` 已有 `LUMOS-SPEC:` 標記讓掛鉤讀,同一種慣例,不另算。
- `push-summary`:跟 `push-range` 一樣是扁平、掛鉤專用的頂層子命令,記帳走 `_gate_event_or_warn`(`hard=True`),也加進 `_KNOWN_GATES`。`loop escape --auto` 是 `loop` 底下需要知識庫的子命令,兩者定位不同,不衝突。
- 掛鉤被叫的方式:`loop escape --auto` 是 `|| true`,`push-summary` 是回非零就改印簡版再 `exit 1`,都是「記帳失敗不能改變擋不擋」。
- `_cl_say_*` 拆出的函式:內容是搬動,沿用原有的 `_codeloop_guard_verdict.last_*` 函式屬性傳遞方式。
- `_fin` 收尾:所有 return 都經過它,不帶 `--keep-going` 時原樣交回。

severity: major
blocking: 是 — 同一支掛鉤裡「判斷 runner 認不認得某旗標」出現第二種寫法,而且跟掛鉤自己白紙黑字寫下的教訓相反,修法只要一行,沒理由留。
引句:「探測一次 code-loop check 認不認得 --keep-going,不認得就不帶」
對照:file: `scripts/hooks/pre-push:758-761`(探 `--shard`、`--suite`、`--graph` 都是 `grep -q -- '"--xxx"' "$REPO_ROOT/scripts/test_lumos.py"`)
判定理由:既有三處探測一律讀檔找旗標字樣,不執行對方,註解明寫「探測不能用跑 --help 看輸出」。新增這處卻反過來執行 `code-loop check --help` 再比對輸出。argparse 版的 `lumos` 對 `--help` 不會跑全套,所以危害比註解說的小。但這是同一件事的兩種做法:多一次啟動 Python 的成本,還要多一個 `code-loop-help` 中斷條目和 `clh_rc` 變數。建議改成 `grep -q -- '"--keep-going"' "$GRAPHCTL"`,再刪掉那條中斷條目。

severity: minor
blocking: 否 — 只影響邊角行為,功能不受影響。
引句:「root = Path(repo) if repo else Path.cwd()」
對照:file: `scripts/lumos:35636`(`_note_audit_root`,`cmd_push_range` 用它找 git 根,不是 git 專案回 rc2)
判定理由:同為「掛鉤叫的扁平子命令」,`push-range` 用 `_note_audit_root` 解析 repo 根,`push-summary` 自己用 `Path(repo)`。掛鉤永遠傳 `--repo "$REPO_ROOT"`,所以實際沒差,只有手動叫(help 寫「手動不用叫」)時兩者表現不同。

severity: minor
blocking: 否 — 擋下理由與提示字串各存兩份,現在內容相同,是日後可能漂移的風險。
引句:「# 代碼審判定 rc1 時,LUMOS-BLOCKS: 行裡每個種類各記一筆的原因(對照表寫死;查不到用通用句)」
對照:file: `scripts/lumos` 的 `_codeloop_guard_verdict` 內各道 `reason` 字串,以及 `_PUSH_SUMMARY_ANCHOR_NOTE`
判定理由:`pp_cl_reason` 在 bash 裡重寫了一份種類對原因的對照,Python 端每筆擋下本來就帶 `reason`。`pp_plain_summary` 又把 `push-summary` 的彙總版面和「裁判檔沒簽名」那句話在 bash 重寫一份。後者是為舊版 lumos 留的退路,可以接受。但這兩份字串沒有守衛測試綁在一起,建議至少加一條漂移守衛,或在掛鉤註解標明「與 Python 端同步」。

不對齊共 3 條,其中 major 1 條。
