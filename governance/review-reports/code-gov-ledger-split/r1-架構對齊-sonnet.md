severity: major

## 問1 分層與依賴方向
部分不對齊。寫入側對齊:`_gate_event` 與 `_append_governance_log` 都只是改路徑,分流判定集中在 `_gov_routes_local`,兩支寫入器共用;cmd_gov 用同一個 `load(...)` 加一行條件載入,與 `.ci-log` 的載入方式同形(`scripts/lumos:8247` load 定義)。`_BOOKKEEPING_FILES`、`_COCHANGE_DEFAULT_EXCLUDE` 也各補了兩本新帳,對齊。
不對齊在讀側:新函式 `_gov_ledger_rows_by_time` 沒走既有共用工具 `_drift_jsonl_iter` / `_gov_tail_bytes`,自己讀檔、切行、解析 JSON、解析時間(見 F1)。鄰居:`scripts/lumos:33718`(_drift_jsonl_iter)、`scripts/lumos:3801`(_gov_tail_bytes)、`scripts/lumos:3928`(_gov_metric_events 的時間解析)、`scripts/lumos:8260`(cmd_gov 用 _drift_jsonl_parse)。
另一處:`_doctor_metric_lines` 對本機帳有正確重用 `_gov_metric_events`(`scripts/lumos:3928`),與 F1 形成對比。

## 問2 命名與錯誤處理
大致對齊。`_append_governance_log` 保持 `except OSError: pass`(原樣);`_gate_event` 保持回 False、不新增 print;`_usage_log` 保持 `except Exception: pass`;doctor 新段用 `except Exception as _e: ok(f"…跳過(fail-open:{_e})")`,與上一段治理帳成長觀測(`scripts/lumos:2397` 一帶)同形。常數命名 `GOV_LOCAL_LOG_NAME` / `USAGE_LOCAL_LOG_NAME` 與 `CI_LOG_NAME`(`scripts/lumos:38595`)同形。唯一偏差見 F3。

## 問3 第二種做法
有。F1(第二支 JSONL 解析加第二套時間解析);F2(對既有 .gitignore 原地追加,是專案裡第一個)。測試檔新增輔助:`_gov_events_all` 是薄包 lumos 函式,不重複;`_gov_split_repo` 與同檔既有 `_run_marker_repo`(`scripts/test_lumos.py:5974` 附近)、`_nh_repo` 類建 repo 輔助各有不同佈局,不算重複;`_gov_since` 無既有同功能。`_m1_events` 把 dict 轉回字串再 loads 是繞路,見 F4。

## F1 另寫一支 JSONL 逐行解析與時間解析,繞過 _drift_jsonl_iter 與 _gov_metric_events
severity: major
blocking: 是
引句:「text = p.read_text(encoding="utf-8", errors="replace")」
file: `scripts/lumos:33718`
佐證行:引句:「for ln in text.splitlines():」
file: `scripts/lumos:33711`
說明:鄰居 `_drift_jsonl_parse` 的 docstring 明講「只在 \n 切行」,因為 `str.splitlines()` 會在 U+2028、U+0085 切開 `json.dumps(ensure_ascii=False)` 寫出的一筆,且 cmd_gov(`scripts/lumos:8253-8260`)特地為此選了它。新函式用的正是被點名的壞做法;結果是 gov 讀得到、spec-gate 摘要與測試輔助 `_gov_events_all` 讀不到同一筆。同函式的時間排序鍵(`_dt.datetime.fromisoformat(ts)`、`t.astimezone()`、except 三種例外)是 `_gov_metric_events`(`scripts/lumos:3928-3944`)那段時間解析的第二份,例外集也不同(那邊 `(ValueError, OverflowError)`,這邊多了 OSError)。且沒用 `_gov_tail_bytes`(`scripts/lumos:3801`)的 24MB 檔尾上限,而 doctor 其他讀治理帳的段落都走它。正確對齊:讀檔用 `_drift_jsonl_iter` 或 `_drift_jsonl_parse`,時間解析抽共用或直接重用 `_gov_metric_events` 的邏輯。

## F2 對既有 .gitignore 原地追加,是專案第一種寫法
severity: minor
blocking: 否
引句:「with open(gi, "ab") as f:」
file: `scripts/lumos:21018`
說明:鄰居 `_init_additive_setup` 的 governance/.gitignore 是「不存在才用 `_write_lf` 寫整份,存在就整個跳過」,scaffold 的 docs/.gitignore 也是 `_write_lf` 整檔寫(`scripts/lumos:20996`);`_write_lf`(`scripts/lumos:17722`)是 docstring 自稱的「vault 唯一寫入原語」且有 tmp→os.replace 原子替換。新函式在檔案已存在時改用裸 `open(...,"ab")` 追加,繞過原子寫入。專案裡原本沒有「補行進既有 .gitignore」的先例,屬於 ⚠ 鄰居沒有既有做法:追加本身有理由(保留 CRLF、不覆寫使用者內容),但可用 `_write_lf` 搭配讀入再整檔寫,或維持追加;交編排者裁。因專案無先例,降為 minor。

## F3 _docs_local_log_path 的名稱與簽章跟鄰居 _ci_log_path 不一致,且被拿去指版控帳
severity: minor
blocking: 否
引句:「p = _docs_local_log_path(docs_dir, name)」
file: `scripts/lumos:38688`
說明:鄰居 `_ci_log_path(env)` 一個參數、回固定帳路徑;新函式收 (docs_dir, name),且在 `_gov_ledger_rows_by_time` 與 `_append_governance_log` 裡被拿去組 `.governance-log.jsonl`(版控帳),名字叫「local」卻指版控帳。docstring 寫「比照 _ci_log_path」但簽章不比照。

## F4 測試輔助 _m1_events 經 dumps 再 loads 繞一圈
severity: minor
blocking: 否
引句:「for ln in (_j.dumps(d, ensure_ascii=False) for d in _gov_events_all(root / "docs")):」
file: `scripts/test_lumos.py:1`
說明:`_gov_events_all` 已回 dict 清單,後面卻轉回字串再 `_j.loads`,與同檔其他改過的輔助(`_gate_rows`、`_ns_gov` 直接回清單)寫法不一致;行為無誤。行號欄無法對到單一既有行,對照 `_gate_rows`、`_ns_gov` 兩支同次改動後的寫法。

不對齊共 4 條,其中重大 1 條
