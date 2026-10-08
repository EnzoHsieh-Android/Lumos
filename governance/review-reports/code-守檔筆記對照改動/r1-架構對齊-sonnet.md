severity: minor

## F1 reread-record 自己再寫一份「判定檔落盤」流程,沒有重用既有的 _note_audit_write_verdict
severity: minor
blocking: 否
引句:「+    d = Path(root) / _NOTE_REREAD_VERDICT_DIR」
佐證行:file: `scripts/lumos:26375`(既有 _note_audit_write_verdict:同一套 mkdir、UTC 時間戳、uuid4 hex、_write_lf 寫 JSON)
1. 既有的筆記內容審記判定檔走 `_note_audit_write_verdict(root, doc)`;新的 reread-record 在函式裡手寫同一套(mkdir、時間戳、uuid、`_write_lf(... json.dumps(..., indent=1))`),差別只有檔名前綴多一段對照指紋與目錄常數不同。
2. 這不算第二種做法(落盤手法、原子寫入、命名規則同款),只是少抽一個共用參數(目錄與檔名前綴);日後改落盤細節(例如換行、權限)要改兩處。
3. 最小處理:給 `_note_audit_write_verdict` 加 `dirname`、`prefix` 選配參數。不處理也不會做出錯的行為。

其餘逐問對照的結論(沒有問題,不列為 finding):
- 分層與依賴方向:reread 只用 `_nodehome_*`、`_ns_git`、`_note_audit_*` 既有函式,沒有反向依賴;`_notes_touched_in_range`、`_note_template_fill` 是從既有函式抽出共用,舊呼叫端行為照舊。
- 治理帳:閘名登記進 `_KNOWN_GATES`;事件一律經 `_gate_event_or_warn`;env 略過寫 `skipped-env`,與 note-audit、note-shape 同款。
- 設定讀取:`_note_reread_config` 與 `_note_audit_config`、`_note_shape_config`、`_drift_config` 並列,專案裡本來就是各道一支,沒有新增做法。
- 掛鉤段落:上線標記獨立一行 `# lumos note-audit reread-check`,與 `# lumos drift check` 同式,且不含 `note-audit check` 連續字串。
- 紀錄檔:目錄加進 `_BOOKKEEPING_DIRS`,與 note-verdicts 並列,列表型別沒動。
- CI 步驟:首次出現 `continue-on-error`,但註解寫明是刻意的(只提醒),不算引入第二種錯誤處理。

最高等級:minor
