severity: major

**1. 分層與依賴方向**:對齊。寫側 `_cmd_codeloop_dispositions` 呼叫 `_contract_backing_apply`,同鄰居 `_dispositions_validate`、`_codeloop_dispositions_gov_log`;讀側 `_backing_warn` 與 `_lens_backing_note` 只讀記錄;`_codeloop_record_valid` 是重用(`scripts/lumos:37276`)。⚠ `_backing_kill_rows` 用 Path(repo_root)/"docs" 硬拼(`scripts/lumos:37907`),寫側用 env.vault.parent(`scripts/lumos:13321`);硬拼 docs 另有先例(`scripts/lumos:22991`、`scripts/lumos:37254`),不算跨層。

**2. 命名與錯誤處理**:命名、stderr「提醒:」格式(`scripts/lumos:1011`)、只提醒吞例外的做法皆對齊。

**AA1**
severity: minor
blocking: 否
引句:「ok, why, _unsure = _codeloop_record_valid(repo_root, rec_sha, marker_sha, detail=True)」
detail 旗標決定回二元組或三元組;鄰居慣例是固定回傳形狀 (ok, 一句為什麼)(`scripts/lumos:37427`、`scripts/lumos:37764`)。file: `scripts/lumos:37276`

**AA2**
severity: minor
blocking: 否
引句:「marks.append([len(results), "", False, False])」
位置式四格 list 加事後 enumerate 回填;鄰居是在 results.append({...}) 當下把欄位寫進 dict。file: `scripts/lumos:13181`

**AA3**
severity: minor
blocking: 否
引句:「gka.add_argument("--note", default=None, help="業務上壞了什麼(人話)")」
--note 預設改 None 以區分沒帶與空字串;--test/--platform 本來就是 None 預設,不違反慣例;但 same_rest 逐欄 is None 比對是 kill-add 原本沒有的部分更新語意。file: `scripts/lumos:12921`

**3. 第二種做法**

**AA4**
severity: major
blocking: 是
引句:「def _jsonl_tolerant_rows(path):」
第二種讀 jsonl 的方式(read_bytes + split + 逐行 decode);既有標準是 read_text(errors="replace").splitlines() 或 open(errors="replace") 逐行讀再 json.loads except ValueError(`scripts/lumos:8610` 註解「半截多位元組行不炸」、`scripts/lumos:8572`、`scripts/lumos:10234`、`scripts/lumos:7179`);還套進 gov 的 load 讓六本帳全改走新路(`scripts/lumos:7266`),擴大範圍。

**AA5**
severity: major
blocking: 是
引句:「def _append_repair_partial_line(path):」
第二種補殘行做法且只補 kill-log;既有 append 寫者(`scripts/lumos:8559` `_jsonl_append_verified` 與 `_gate_event_or_warn`)都直接 open("a") 寫一行、沒有前置補換行;只掛在 cmd_guard_kill 一處(`scripts/lumos:13320`),其他帳的殘行風險沒對齊。

觀察(不計):gov 的 bk-* 欄與 cand 同表,結構對;`_backing_git_repo` 另建三提交 fixture 而非重用 `_disp_repo`,判不準是否因需要簿記檔提交,⚠。

不對齊共 5 條,其中 major 2 條
