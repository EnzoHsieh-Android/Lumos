severity: major

審查範圍:`/tmp/code3-r1.patch`。對照用的行號取自 repo 在 2f9cb94f 的狀態,該提交含這份 patch。

## ① 分層與依賴方向

整體結構對齊,有兩處例外。

- 對齊的部分:
  - drift 側是沿用 `_drift_probe_check` 已有的 `extract=` / `kind=` 參數,在 `_drift_probe_scan` 裡照做,沒有另開 scan 路徑。`cmd_drift_scan` 把 retire 接在 probe 之後,也共用同一棵樹。`_gov_tail_bytes` 是把 doctor 帳增速段原本的檔尾讀法抽出來共用。
  - `_drift_retire_guarded` 拆成判定、報告、印出三支,方向跟 `_drift_m1_guarded` → `_drift_m1_report` 一致。
- 不對齊 1:doctor 層的 `_metric_gate_off` 手寫了「閘名到各閘設定函式」的對照表,依賴 note-shape、note-audit、note-reread、drift、nodehome、lint-new 六個閘的設定層。它還混了兩種讀法:前五個吃已讀好的文字,`lint-new` 卻自己再讀一次磁碟(見 A1)。
- 不對齊 2:退回分給報告段的職責不同。m1 的表態扣除在 report 裡(`_drift_m1_report`),retire 這次把扣除搬到 guarded 判定裡,report 只收 `acks`。分法跟 m1 不一樣(見 A5)。

## ② 命名與錯誤處理

**A1**
severity: major
blocking: 是 — 設定讀法出現第三種,而且少了既有兩處 doctor 設定讀取都有的捷徑檔防護,等於把前幾輪審查補上的洞又開了一個。
引句:「cfg_text = cp.read_bytes() if cp.is_file() else None」
`_doctor_metric_lines` 自己讀 `.lumos/config.json`,沒有 `is_symlink()` 和 `resolve()` 比對。既有的 doctor 設定讀取(`_drift_gate_doctor_lines`、`_note_audit_doctor_lines`)都有這兩道檢查,且註解寫明是代碼審 r2 要求的。
`_metric_gate_off` 還把磁碟檔案餵給 `_nodehome_config(..., from_snapshot=True)`。該函式的磁碟模式本來有捷徑防護,快照模式是給 git 版本內容用的,這樣用等於繞過防護。
同一個函式裡 `lint-new` 又走 `_lint_new_config(root)` 直讀磁碟,與其他五個閘不一致。`except Exception: return False` 也是第二種壞值處理:各閘既有函式都是「退回預設並附警告」。
佐證 file: `scripts/lumos:3613`
佐證 file: `scripts/lumos:3564`
佐證 file: `scripts/lumos:34066`
佐證 file: `scripts/lumos:33538`

**A2**
severity: major
blocking: 是 — 「節點#dN」決策引用多出第二套解析,語意跟既有的 `_dref_parse` / `_dref_norm` 略有出入。
引句:「m = re.fullmatch(r"(\S+?)#(d\d+)", v)」
`_slot_replacement_dead` 自己寫了一條正規式,又自己做 `env.resolve(x) or env.resolve(x + ".md")`。既有的 `_dref_parse`(`(.+?)#(d\d+)`)和 `_dref_norm` 就是為這個格式寫的。
決策翻案的判斷 `str(d.get("valid","true")).lower() == "false"` 倒是沿用了慣例,只有引用的解析是另一套。
佐證 file: `scripts/lumos:3521`
佐證 file: `scripts/lumos:18101`
佐證 file: `scripts/lumos:18107`

**A3**
severity: minor
blocking: 否 — 新的摘要抽取方式跟 drift 側的 `_retire_lines` 一致,對照的是舊的 S16;但同一個 doctor 裡相鄰兩段對同一批 RULE 看到的內容會不同。
引句:「for no, line in _ns_summary_logical(text).items():」
S16 的 `_doctor_stale_rules` 讀 `n.fields["summary"]` 後逐行判,不接回續行。S17/S18/S19 改用 `_ns_summary_logical`(接回續行)加 `slot_parse`。
欄位寫在續行時,S16 會判成「沒寫 [confirmed:]」,S18 卻讀得到。
`_slot_superseded(sp)` 與既有的 `_ns_superseded(line)` 判的是同一件事,多一份實作。
`_slot_summary_entries` 還用 `env_text` 重讀每篇全文,沒用 `env.notes` 已解析的內容。
⚠ 我沒查 S16 是否刻意不接續行。
佐證 file: `scripts/lumos:3485`
佐證 file: `scripts/lumos:3434`
佐證 file: `scripts/lumos:27850`
佐證 file: `scripts/lumos:30561`

**A4**
severity: minor
blocking: 否 — 軟段呈現多了第二套截斷。
引句:「_shown19 = _fact19[:_FACT_RECHECK_SHOW] + (」
`warn_soft` 本身已經有每段上限 `_SOFT_CAP`,`--verbose` 可以全列。S19 先自己截到 20 條,再附一行「…還有 N 條」。
結果是 `--verbose` 也看不到全部,而且那行「…還有」被 `_soft["lines"]` 當成一條提醒計數。
佐證 file: `scripts/lumos:2543`
佐證 file: `scripts/lumos:1354`

**A5**
severity: minor
blocking: 否 — 三段都不寫治理帳、也沒有保護殼,跟鄰居 S16 及幾段讀本機帳的段落作法不同。不寫帳在註解裡有交代,保護殼則沒交代。
引句:「_met18 = _doctor_metric_lines(env, _vault_repo_root(env))」
S16 對每篇過期的筆記記一筆 `check-s16` 事件。S17/S18/S19 刻意不記,patch 註解寫了理由(重複噪音),屬於有意的差異。
更值得一提的是 S18 要讀帳檔和設定檔,卻沒有包 try。doctor 其他讀本機帳的段落(帳增速、規格閘)都包了 `except Exception` 並用 `warn_soft` 說「這一段算不出來」。
`_gov_tail_bytes` 的 `stat` / `open` 一旦拋 `OSError`,整個 doctor 會中斷。
⚠ 我沒實測這條會不會真的中斷整個 doctor。
佐證 file: `scripts/lumos:2505`
佐證 file: `scripts/lumos:2531`
佐證 file: `scripts/lumos:2678`

**A6**
severity: minor
blocking: 否 — 治理帳的逐行解析有第三種寫法。
引句:「for d in _drift_jsonl_parse(raw):」
`_drift_jsonl_parse` 的註解寫明是「表態檔與修復帳共用」,現在借給治理帳用。它只在 `\n` 切行。doctor 帳增速段自己用 `decode("utf-8","replace").splitlines()` 加逐行 `json.loads`。
兩個讀者切行規則不同。`_gov_tail_bytes` 共用得很好,只有解析這步分岔。
佐證 file: `scripts/lumos:3577`
佐證 file: `scripts/lumos:31226`
佐證 file: `scripts/lumos:2045`

**A7**
severity: minor
blocking: 否 — retire 這組的兜底和 m1 的做法分岔,結構上沒壞。
引句:「acks = _drift_load_acks(root, tip) if must else []」
m1 的表態扣除在 report 裡做,印出不另包 try。retire 把扣除搬進 guarded,印出另包一層 `try/except` 並說「判定照舊」。
這個意圖合理,但跟 m1 的做法不同:m1 若在印出時拋例外,仍是整體兜底。
佐證 file: `scripts/lumos:32379`
佐證 file: `scripts/lumos:33382`
佐證 file: `scripts/lumos:32398`

## ③ 第二種做法

- 另一套摘要行抽取:有,見 A3,與 S16 並存。
- 另一套欄位解析:有,見 A2,節點#dN 引用的解析。欄位本身用 `slot_parse`,是對的。
- 另一套決策讀法:決策本身用 `_node_decisions`,對齊。只有 A2 的引用解析是另一套。
- 另一套設定讀法:有,見 A1,這是最重的一條。
- 另一套帳檔讀法:檔尾讀取共用了,解析分岔,見 A6。
- 測試檔:`mkvault` / `write` / `run` / `_dr_repo` / `_dr_scan` / `_rt_*` 都有沿用,沒有新增第二套小工具。

不對齊共 7 條,其中 major 2 條
