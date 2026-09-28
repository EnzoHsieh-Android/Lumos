severity: minor

## 三問逐答

### 1. 分層與依賴方向

新碼放在 `scripts/lumos` 既有的「筆記形狀擋」區塊正下方(第二層緊接第一層),層次對:第二層的計劃節點在 `Systems/筆記內容審`,共用抽行函式的家在 `Systems/筆記內容閘`,跟 [[Systems/筆記內容閘]] 的 `responsibility` 改寫吻合(file: `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:5`)。

依賴方向查證:
- 共用抽行函式 `_notelines_new` / `_notelines_range_added` / `_notelines_regions` / `_notelines_headings` / `_notelines_structural_lines` / `_notelines_content_id` 被 `_note_shape_eval`(第一層)與 `_note_audit_items`(第二層)兩邊呼叫,第一層改成呼叫共用函式而不是自己重複邏輯,方向正確(file: `scripts/lumos:23931`、`scripts/lumos:24240`)。
- 第二層沒有繞過既有共用函式自己刻一套 git 存取:全程只用 `_lens_git` / `_ns_git` / `_nodehome_git` / `_nodehome_cat_blobs` / `_nodehome_name_status` / `_nodehome_split_z` 這些既有 wrapper,整個 `_note_audit_*`/`cmd_note_audit_*` 區塊(scripts/lumos:24166–24990)裡沒有任何一處直接呼叫 `subprocess`(已用 grep 核對),跟 `_note_shape_eval`、`cmd_home_check` 的做法一致。
- 範圍起點判法呼叫既有 `_lens_push_base` + `_nodehome_clamp_base`,跟 `cmd_home_check`(scripts/lumos:23393)、`cmd_note_shape`(scripts/lumos:24115)共用同一支,不是另刻一套(file: `scripts/lumos:24405`)。
- `_note_audit_resolve` 把「解出 base/tip/vault_rel」抽成獨立函式供 prepare/record/check/skip 四個子指令共用,這點跟第一層(`cmd_note_shape` 單一命令、邏輯內嵌)形狀不同,但屬合理演化——第二層本來就有四個子指令都要同一段解析,抽出來是避免四份重複,不算「跨層直呼」或「第二種做法」。
- `decision-amend`(`cmd_decision_amend`,file: `scripts/lumos:24839`)沿用 `cmd_decision_supersede`(file: `scripts/lumos:14821`)的手術式編輯手法:`load_raw_for_edit` → `decisions_items` → 逐行找欄位 → `atomic_write_verify(path, new_lines, "decisions", _check)`,跟鄰居一模一樣的分層(不重新序列化整份 frontmatter),依賴方向正確。

判斷:第 1 問沒有找到「跨層直呼」或「繞過共用函式自刻一套」的具體案例。

### 2. 命名與錯誤處理

- 前綴命名一致:`_NOTE_AUDIT_*` 常數、`_note_audit_*` 私有函式、`cmd_note_audit_*` 四個子指令,跟鄰居 `_NOTE_SHAPE_*` / `_note_shape_*` / `cmd_note_shape` 同一套命名法。
- rc 語意一致:0=放行、1=擋下(block 模式)、2=參數或環境錯誤,跟 `cmd_note_shape`、`cmd_home_check` 相同;`cmd_note_audit_check` 的 fail-open 訊息「跳過(fail-open)」、`擋下:`/`提醒(...,不擋)` 的頭字、`_gate_event_or_warn(..., hard=True, nodes=...[:50])` 的呼叫形狀都逐字比對過跟 `cmd_note_shape`(scripts/lumos:24148–24163)相同。
- `_note_audit_config` 的讀法(bytes/None → (gate, warnings))跟 `_note_shape_config` 一致,錯誤訊息風格(「…讀不成 JSON,照預設 block」)也同一套白話中文。
- 治理帳事件命名(`prepare`/`recorded`/`skipped`/`blocked`/`warned`/`skipped-env`)跟既有閘的事件詞彙同一組,`_KNOWN_GATES` 也照既有格式在尾端加一筆並附日期註解(file: `scripts/lumos:6605-6610` 附近,對照патch)。
- 有一處組織上的不一致(見 F1):`decision-amend` 是「decision-*」指令家族的新成員,但它的 argparse 子解析器與 `HELP_WHEN` 條目都沒有跟 `decision-supersede` / `decision-add` / `decision-reindex` 放在一起,而是插進「筆記內容審」那個區塊裡。

### 3. 第二種做法

逐一核對計劃裡點名要防的「第二種做法」風險:
- 設定讀法:沒有另一套,`_note_audit_config` 完全照抄 `_note_shape_config` 的形狀。
- git 解析:沒有另一套,見第 1 問。`_note_audit_closed_plans` 用 `git log -z --format=%H --name-only` 這個組合是新出現的解析需求(找「收尾」的提交序列),репo 裡沒有既有的共用函式處理同一種「sha+檔名交錯」格式,所以這裡手刻解析並不是重複既有機制的「第二種做法」,是填補一個原本沒人做過的需求;而且它明確記了 PITFALL(file: `docs/lumos-toolchain-knowledge/Systems/筆記內容審.md` 的 PITFALL 行)承認踩過格式坑,不是悄悄引入。
- 寫檔:`_note_audit_write_verdict`/`_note_audit_work_dir` 都呼叫既有 `_write_lf`,不是另刻原子寫入。
- 範圍解析:同一支 `_lens_push_base`。
- 自創工具函式頂替既有同功能:`_note_audit_prompt` 找範本檔用 `Path(__file__).resolve().parent.parent` 這個既有到處在用的 idiom(第 89、16147、17235、17286、18065 行都這樣寫),不是自創。
- 判定者報告的「獨立宣告行」解析(`seat:`/`provider:`/`model:`/`prepared:`,`re.search(rf"^{k}:\s*(\S.*?)\s*$", text, re.M)`)跟審查報告既有的「嚴重度獨立宣告行」慣例(scripts/lumos:7196、7225)同一套設計哲學,不是新發明的報告格式。
- 判定列的 pipe-table 格式(`id | class | evidence | reason`)在庫裡沒有逐字相同的既有機制被繞過,屬於填補新需求,不算「第二種做法」。

沒有找到符合「major=引入第二種做法或跨層直呼」錨的案例。

## F1 decision-amend 沒有跟 decision-* 家族放在一起註冊

severity: minor
blocking: 否 — 純組織/可發現性問題,不影響行為,command 本身功能正確(dispatcher 裡 `decision-amend` 分支就緊接在 `decision-supersede`/`decision-add`/`decision-reindex` 那組之前,執行路徑沒有被打散)
引句:「dam = sub.add_parser("decision-amend", help="改一條還沒推上去的決策的某個文字欄;spec=Projects/筆記內容審_計劃")」
file: `scripts/lumos:33487`(新增的 decision-amend 子解析器)
file: `scripts/lumos:33197`、`scripts/lumos:33203`、`scripts/lumos:33216`(既有 decision-supersede / decision-reindex / decision-add 三支子解析器彼此緊鄰註冊的既有慣例)
file: `scripts/lumos:32630-32633`(HELP_WHEN 裡 decision-supersede/decision-reindex/decision-add 三條緊鄰)
file: `scripts/lumos:32678`(新增的 `"decision-amend"` HELP_WHEN 條目,插在 note-audit 那組裡,離上面三條有一段距離)

具體場景:下次有人要盤點「decision-* 家族還有哪些指令」、或要在 argparse 註冊區/HELP_WHEN 表加一個新的 decision-* 指令(例如 decision-remove),照既有慣例會去 `decision-supersede`/`decision-reindex`/`decision-add` 那三行緊鄰的地方找同類指令抄樣式,會漏看已經存在的 `decision-amend`——它被歸類進「筆記內容審」那個功能區塊,而不是跟它真正所屬的「decision-*」語法家族放在一起。這是本次診斷唯一具體、可用 file:line 驗證的「跟既有做法不一樣」之處,但因為不影響 rc/行為、只影響下次找碼的人力成本,判 minor 不判 blocking。

---

不對齊共 1 條,其中 major 0 條
最高 severity:minor(decision-amend 的 argparse/HELP_WHEN 登記位置離它所屬的 decision-* 家族較遠,其餘分層、依賴方向、命名、錯誤處理、git 呼叫、原子寫入、治理帳事件都跟既有做法一致,沒有發現引入第二種做法或跨層直呼)。
