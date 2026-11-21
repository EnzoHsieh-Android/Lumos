severity: minor

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/5af35610….json.warming` 不存在,沒有要處理的鎖,直接審。

以下 file 行號指現行工作樹的 `scripts/lumos`、`scripts/test_lumos.py`(已含這份 diff 的改動)。

## 1. 分層與依賴方向:對齊
- 新增的 `_finding_seat_parse`、`_finding_seat_required_block`、`_finding_seat_write_block` 放在 `cmd_canary` 正上方。鄰居 `_none_reserved_lines` 也放在這裡(file: `scripts/lumos:19456`)。
- 呼叫方向跟鄰居一樣:`cmd_canary` 先在 `finding_kinds` 旁驗形式與涵蓋(file: `scripts/lumos:19891`),再到 `--finding-source` 讀帳那一段之後才呼叫需要讀帳的檢查(file: `scripts/lumos:20195`)。那一段同樣用 `_lrows`、`_lerr`,載體最後記的順序也相同。
- 型別檢查沒有另寫一支,直接擴充既有的 `_finding_sources_typed`(file: `scripts/lumos:37209`),寫側、處置閘、`_gov_event_types_ok` 共用,符合「同形狀共用一支」的鄰居做法。
- gov 讀帳加 `finding_seats` 欄位(file: `scripts/lumos:18513` 附近)、`_GOV_FIELD_TYPES` 加型別,都是照 `finding_sources` 的位置擴充。
- 統計段在 `_render_gov_stats` 的「發現在修什麼」之後、「辯方明確表態」之前插入 `_render_seat_noise`,沒有跨層直呼。
- 測試的造帳工具照用既有的 `_mr_project`、`_mr_seat`、`_mr_carrier`、`_mr_append`、`_mr_gate`(file: `scripts/test_lumos.py:9092`、`:9117`、`:9123`、`:9149`、`:9164`)。

## 2. 命名與錯誤處理:大致對齊,三條 minor
- 旗標名、擋下訊息(「擋下:」開頭)、rc2、blocked 事件的 `<原因> loop=… auditor=… id=<隨機碼>` 寫法,都跟 `refuted-set-missing` 一致(file: `scripts/lumos:19820`)。
- 缺漏必填時留 blocked 事件,跟 `--refuted-set` 缺漏同一做法。

**minor 1:生效日的覆寫寫法跟鄰居不同。**
- 鄰居的環境變數覆寫都是純日期,用 `_DAY_RE` 驗證,不合格退回常數(`_choice_since` 見 `scripts/lumos:77912`,`_expected_since` 見 `:14519`)。測試總檔預設值也是 `9999-12-31`。
- 新碼的環境變數收的是帶時區的 ISO 時間,預設值是 `9999-12-31T00:00:00+08:00`,解析改走 `_loop_ts_key`(file: `scripts/lumos:19555`)。這是兩種既有寫法的混合。
- 註解寫「寫法同 `_SECURITY_SEAT_SINCE`」,但 `_SECURITY_SEAT_SINCE` 沒有環境變數覆寫(file: `scripts/lumos:15770`)。
- 結構(迴圈首筆帳對生效日、時間讀不動就擋)確實跟資安席那步一致(file: `scripts/lumos:37084`)。
severity: minor
- blocking: 否
- 引句:「_FINDING_SEAT_SINCE = "2026-11-22T00:00:00+08:00"」

**minor 2:`finding-seat-unknown` 的 blocked 事件,鄰居沒有同類做法。**
- 席名對不上同輪帳,這是「內容核對不過」。同類的 `--finding-source` 核對失敗(file: `scripts/lumos:20170` 起)只印訊息、rc2,不留 blocked 事件。
- 反過來,`finding-seat-missing` 留事件與 `refuted-set-missing` 相符。
- 同一支新碼裡,「時間讀不動」那條擋下(file: `scripts/lumos:19579` 附近)又沒留事件,內部也不一致。
- 這是「哪些擋下要入治理帳」的口徑不統一,不是結構問題。
severity: minor
- blocking: 否
- 引句:「_gate_event_or_warn(root, "canary", "blocked", f"finding-seat-unknown loop={loop} auditor={auditor or ''} id={uuid.uuid4().hex[:8]}", hard=True)」

## 3. 第二種做法:兩條 minor,沒有 major
- 生效日判法沒有另起第三套,還是 `_loop_ts_key` 加首筆帳比較,與資安席同法。
- 測試覆寫小工具 `_fs_since` 是 class + `__enter__/__exit__`,跟 `_ksp_since` 同形(file: `scripts/test_lumos.py:133451`),也加了 `setdefault` 預設,同 `LUMOS_KT_SIT_SPEC_SINCE` 那排。
- 沒有重寫 `_finding_sources_typed`、`_mr_*`,也沒另造一套解析 `=` 的工具。

**minor 3:gov 統計段自己帶一個固定窗口。**
- `_render_seat_noise` 用 `now()` 往前 56 天,再跟 gov 的 `--since` 起算日取較晚的(file: `scripts/lumos:18071`)。
- 鄰居的統計段(`fk`、`rv` 等)只吃 gov 已依 `since_days` 過濾好的 `rows`,沒有各自的時間窗。
- 這是統計段裡第一個自帶窗口與 `now()` 的做法,算輕度的「第二種窗口判法」。
- 計劃有明講 56 天,我判不是 major。若編排者認定這就是「另一套窗口判法」,可升 major,標 ⚠ 請裁。
severity: minor
- blocking: 否
- 引句:「floor = _dtm.datetime.now().astimezone().timestamp() - _SEAT_NOISE_DAYS * 86400」

**minor 4(測試):數 blocked 事件的小工具沒沿用鄰居寫法。**
- 鄰居測試直接讀 `docs/.governance-log.jsonl` 這一個檔再 grep(file: `scripts/test_lumos.py:51824`、`:51781`)。
- 新的 `_fs_blocked_n` 用 `rglob` 掃臨時專案底下所有同名檔,另起一套數法。
severity: minor
- blocking: 否
- 引句:「n += sum(1 for ln in p.read_text(encoding="utf-8").splitlines() if why in ln and '"blocked"' in ln)」

不對齊共 4 條,其中 major 0 條。
