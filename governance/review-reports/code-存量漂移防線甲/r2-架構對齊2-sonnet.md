severity: minor

# 問1:分層與依賴方向(有沒有跨層直呼)

已看,無 finding。確認方向:
- `_drift_guard_findings`、`_guard_formal_line` 的呼叫端都是 drift 這一層呼叫 guard-kill 家族(`_guard_planned_prose`、`_guard_formal_line`),沒有反向依賴——guard 家族的 `_guard_settle_home`(scripts/lumos:11985 附近)沒有呼叫任何 `_drift_*` 函式。
- `_notes_status_flipped` / `_note_status_seq` 放在 note-audit 那一段(scripts/lumos:24471 起),drift 側的 `_drift_range_events` 只是呼叫端,沒有把自己的邏輯塞進 note-audit 那層,方向正確,也符合筆記本身講的「共用、不另寫一套」。
- `cmd_drift_check` 只讀不寫,寫入(ack/settle)仍各自留在自己的指令函式裡,check 不繞過 `cmd_drift_ack`/guard settle 直接改檔。

# 問2:命名與錯誤處理

## F1 doctor 開頭讀 .lumos/config.json 少了鄰居兩支都有的目錄捷徑防護
severity: minor
blocking: 否 — doctor 這段只影響提醒文字的呈現(不是任何會擋推送的判定),沒有具體會翻紅的行為差異可指
引句:「txt = cp.read_bytes() if cp.is_file() and not cp.is_symlink() else None」
1. 新函式 `_drift_gate_doctor_lines`(scripts/lumos:25704)讀 `.lumos/config.json` 只判斷檔案本身是不是 symlink(`scripts/lumos:25711`)。
2. 同一支檔裡緊鄰的兩支「鄰居」——`_note_shape_doctor_lines`(scripts/lumos:24230)與 `_note_audit_doctor_lines`(scripts/lumos:26103)——做的是同一件事(doctor 開頭讀專案的 `.lumos/config.json` 判 gate 模式),但兩支都多一段 `cp.resolve() == root.resolve() / ".lumos" / "config.json"`(scripts/lumos:24241、scripts/lumos:26111),連 `.lumos` 資料夾本身是不是捷徑都會跟過去判掉,註解明講這是「代碼審 r1 架構對齊席」補回來的洞(scripts/lumos:24240)。
3. `_drift_gate_doctor_lines` 的 docstring 自己就寫「照筆記形狀擋與筆記內容審那兩支的位置與呈現」(scripts/lumos:25705),等於宣稱要仿同一個形狀,但只仿了呈現位置,沒仿到這段防護——三支函式裡有兩支有、一支沒有,是同一檔內部的不一致,不是純風格差異。
4. 重現:在 repo 根目錄把 `.lumos` 整個資料夾換成連到別處的符號連結,指向一個帶 `drift_check.gate: block` 的假 config,對 `_note_shape_doctor_lines`/`_note_audit_doctor_lines` 會因為 `cp.resolve() != root/.lumos/config.json` 而判 `txt=None`(照預設),但 `_drift_gate_doctor_lines` 會直接讀進那個假 config 並印出來——沒有寫成單元測試,標 ⚠(判不出這在目前 doctor 全走 advisory 提醒的路徑下是否有人會刻意這樣繞)。

## F2 env.undecodable 用類別外動態賦值補,沒有照 Env 既有欄位宣告的慣例
severity: minor
blocking: 否 — 讀取端一律用 `getattr(..., [])` 防禦,拿不到欄位時退化成空清單,不會炸
引句:「env.undecodable = bad」
1. `Env` 類別的 transient/私有欄位(`_edges`、`_texts`)一律在 `__init__`(scripts/lumos:413-414)與 `from_texts`(scripts/lumos:428)裡宣告成 `None`,再由各自的存取端(如 `env_text`)用 `getattr(env, "_texts", None)`(scripts/lumos:463)防禦性讀。
2. 這次新增的 `env.undecodable`(scripts/lumos:25369,在 `_drift_tree_env` 裡)沒有走同一條路——它是在 `Env.from_texts` 回傳之後,從 `_drift_tree_env` 外部直接對已建好的物件賦值,`Env` 類別本身完全不知道有這個欄位。
3. 讀取端 `_drift_check_core` 用 `getattr(tenv, "undecodable", [])`(scripts/lumos:25434)防禦,所以不會壞,但這代表「Env 可能帶 undecodable」這件事只存在於 `_drift_tree_env` 的 docstring 裡,跟既有「_texts/_edges 兩處都要看」的宣告慣例不一致——之後有人照 `Env.__init__`/`from_texts` 去找「這個物件有哪些欄位」會找不到這個。

# 問3:第二種做法(有沒有又自己刻一套已有的工具)

已看,無 finding(這輪多處是把上一輪的「自己刻一套」修回既有工具,不是新增第二種做法)。核對過的既有工具與這次的呼叫端:
- 連結解析:`_drift_c3_hit`、`_drift_plan_followups` 這次改用 `build_typed_index(env)` 的 `fwd`/`rev`/`ambiguous`(scripts/lumos:25214、25323),用法跟既有呼叫端(scripts/lumos:13387 的 `idx["rev"].get(rel, []) if et == "verified_by"`、scripts/lumos:15843 的 `for (asrc, lit, aetype, cands) in idx["ambiguous"]`)同一種取值方式,沒有另外自己猜同名候選。
- 鎖:`cmd_drift_ack` 新增的 `with _vault_write_lock(env.vault):`(scripts/lumos:25537)包住 `_jsonl_append_verified`,跟既有的手動記帳寫入(scripts/lumos:9873-9877「手動記帳也上鎖(跟自動記、撤回同一把)」)是同一把鎖、同一種包法,`key_field="id"` 對應 `rec["id"]`,跟其他呼叫端 `key_field` 對應 `rec[key_field]` 的慣例一致。
- frontmatter/欄位邊界解析:`_drift_field_line` 新增的 `pred` 掃描仍然靠共用的 `TOP_KEY_RE`(scripts/lumos:179)畫欄位邊界,沒有另外刻一套 frontmatter 掃描;`_drift_set_status_text` 沿用 `edit_fm_scalar`/`edit_fm_sync_status_tag`,不是自己改字串。
- doctor 提醒呈現:`_drift_gate_doctor_lines` 的輸出走跟兩支鄰居一樣的 `print(f"  {C['Y']}⚠{C['X']} {_ln}")` 外層迴圈(scripts/lumos:1037/1042/1047 三段結構一致);Z 段的 `_drift_doctor_lines` 走既有的 `section()` + `warn_soft()`(scripts/lumos:2042-2044),不是另外刻一套排版。
- 逐提交讀狀態:`_note_status_seq` 是從已放行的 `_notes_status_flipped` 拆出來的既有邏輯搬家,不是重寫一套 git log 解析;`_nodehome_cat_blobs` 批次讀取仍是唯一的批次讀路徑,只加了 `timeout` 參數,預設值(60)維持原行為,寫法跟 `_lint_new_verdict` 的 `budget_end`/`timeout=max(1, int(...))` 預算模式一致(scripts/lumos:21866-21886)。

## F3(⚠判不準)doctor 呼叫端少了鄰居都有的 vault / ci 參數
severity: minor
blocking: 否 — 有文件明講「發現」搬到 Z 段的 `_drift_doctor_lines(env)` 另外處理,不是漏做
引句:「for _ln in _drift_gate_doctor_lines(_vault_repo_root(env)):」
1. `run_doctor` 呼叫兩支鄰居時都是 `_note_shape_doctor_lines(_vault_repo_root(env), env.vault, ci=ci)`(scripts/lumos:1037)、`_note_audit_doctor_lines(_vault_repo_root(env), env.vault, ci=ci)`(scripts/lumos:1042),簽名一致(`repo_root, vault, ci=False`)。
2. 新的 `_drift_gate_doctor_lines(_vault_repo_root(env))`(scripts/lumos:1047)只帶一個參數,定義也只收 `repo_root`(scripts/lumos:25704)——跟兩支鄰居的簽名形狀不同。
3. ⚠ 這是有意的設計拆分:「筆記內容的發現」(對應鄰居的事後掃描/vault 相依部分)搬進另一支 `_drift_doctor_lines(env)`,在 Z 段獨立呼叫(scripts/lumos:2038),`_drift_gate_doctor_lines` 只剩「開關模式 + CI 有沒有接線」這兩件不需要 vault 的事,筆記裡也寫明這個拆法(Systems/存量漂移守衛.md 的「跟設計稿不一樣的兩處」段)。判不準的地方在於:這樣拆之後,「doctor 開頭這一組函式」不再是同一個呼叫形狀家族(兩支四參數、一支一參數),往後第四支要照哪個抄不明顯,但目前功能上沒有缺口。

---
最高等級 minor,blocking 0 條。
