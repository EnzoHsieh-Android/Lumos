severity: major

## F1 同一份審查帳(.canary-log.jsonl)的「哪些迴圈有審查紀錄」被獨立實作兩次
severity: major
blocking: yes
引句:「審查帳裡有審查紀錄的迴圈編號(NFC);規格閘留痕不算——風險低沒審的計劃也會有那種列。」
引句:「審查帳裡的審查紀錄,依迴圈編號(NFC)分組;規格閘留痕不算。」
`_review_loop_ids`(scripts/lumos:7533)與 `_escape_review_rows_by_loop`(scripts/lumos:9844)兩支函式各自
`.read_text` + `json.loads` + 過濾 `kind in _REVIEW_RECORD_KINDS` + `nfc(d["loop"])`,判斷邏輯逐字重複,只差
輸出容器(前者收集成 set,後者收集成 by_loop dict)。`_escape_stats` 兩支都呼叫、對同一檔案掃兩遍
(scripts/lumos:9893 起 `review_ids = _review_loop_ids(env)` 接著 `by_loop = _escape_review_rows_by_loop(env)`)。
這支 diff 在同一次改動裡才剛立下「共同檢查抽成一支共用函式」的慣例(見 `_escape_log_guard`,file: `scripts/lumos:7564`,
docstring 明講「手動記帳與撤回共用」),但這裡卻是同一份邏輯各寫一次——之後 `_REVIEW_RECORD_KINDS` 的定義若要調整
(例如再加一種 kind),兩處都要記得改,漏一處會讓「有沒有審查紀錄」判斷跟「審查紀錄內容」兩邊對不上而不自知。
建議:`_escape_review_rows_by_loop` 改成單一事實來源,`_review_loop_ids` 改用 `set(_escape_review_rows_by_loop(env))` 求值,
或反過來讓後者從前者的 key 集合驅動,只留一次檔案掃描與一次過濾邏輯。

## F2 `_escape_plan_scopes` 繞過 env.notes 直接重讀重解析檔案,跟既有取 tags 慣例不一致
severity: major
blocking: yes
引句:「fm, _ = split_frontmatter((env.vault / rel).read_text(encoding="utf-8"))」
file: `scripts/lumos:5798`(`note = env.notes.get(plan_rel)` 之後直接 `n.fields.get(...)` 取欄位,是本檔案裡
反覆出現的標準寫法,另見 `scripts/lumos:442`、`3083`、`3116`、`3178`)
新加的 `_escape_plan_scopes`(scripts/lumos:9828-9839)要拿一篇計劃節點的 `tags`,沒有走 `env.notes.get(rel).fields.get("tags")`
這條全檔一致的路,而是自己 `read_text` → `split_frontmatter` → `parse_frontmatter` 重新解析一次 frontmatter。
`env.notes` 是這支程式對「一篇筆記現在長怎樣」唯一的索引層,繞過它等於在讀取面另開一條路徑:如果 `env.notes` 之後改了
frontmatter 解析規則、快取或正規化(例如 NFC),這支函式不會跟著吃到,而是各表一枝獨立老化。函式本身也用 try/except
(OSError, ValueError) 吞掉解析失敗,跟 `env.notes` 構建時的錯誤處理策略不一定一致,增加了第二套「筆記讀不到怎麼辦」的行為。
建議:改成 `note = env.notes.get(rel)`,`tags = note.fields.get("tags") or []` 之後再取 `scope/` 前綴,與全檔用法對齊。

## F3(minor)`--by` 在本檔案裡已有兩種語意,新增的第三種語意沒有區隔說明
severity: minor
blocking: no
引句:le.add_argument("--by", dest="esc_by", help="--withdraw 用:誰撤的")
既有 `decision-supersede --by`(scripts/lumos:31508,「被誰取代(superseded_by 值)」)是自由文字的**取代目標**;
`rel-cascade --by`(scripts/lumos:31521,`choices=["ai","human"]`)是**誰判的**列舉值。這次新加的
`loop escape --withdraw --by` 又是第三種語意:**撤回操作者的自由文字姓名**。三個 `--by` 分別指「取代者」「判定者類別」
「操作者本人」,雖然各自 help 文字都寫清楚,但同一個旗標名在同一支 CLI 裡累積第三種不同語意,查文件時容易搞混
(尤其跟 `decision-supersede --by` 語意最近卻完全不同——一個是「這條決策被什麼取代」,一個是「這次撤回是誰做的」)。
判不準要不要為此另取名字(如 `--withdrawn-by`),標 ⚠,留給人裁。

## F4(minor)測試 fixture 命名跟本檔既有 `_mk_*` 慣例不一致
severity: minor
blocking: no
引句:def _esc_fx(review=(), converged=(), escapes=(), plans=None):
scripts/test_lumos.py 裡同類「造出一個帶假帳本的 vault/repo」的 fixture helper 全部叫 `_mk_<東西>`(例:
`_mk_gate_fixture`、`_mk_query_vault`、`_mk_spec_gate_repo`、`_mk_roster_fixture` 等,grep `^def _mk_` 有 25+ 個)。
這次新加的 `_esc_fx`(scripts/test_lumos.py:33018)是本檔第一個用 `_fx` 尾碼的 fixture 函式,功能上跟 `_mk_*` 系列
做的事完全一樣(建 vault、寫入合成的 .canary-log.jsonl/.governance-log.jsonl/.escape-log.jsonl、可選寫計劃筆記),
只是換了個命名風格。純風格層面,不影響行為,但下次有人要找「逃逸帳相關 fixture」會少一個可 grep 的入口。

已看,無:
- `_escape_log_guard`(scripts/lumos:7564)把符號連結擋下與安全建檔抽成手動記帳/撤回共用的一支函式,延續本檔既有
  「共同檢查抽成單一實作」的做法(對照 `_severity_check_row` 等)。
- `cmd_loop_escape` 對 `--withdraw` 的驗證(擋目標不存在/撤回紀錄不可再撤/理由與撤回者必填)全部收在
  `_escape_withdraw` 函式內、dispatch 只轉呼叫,符合本檔既有「dispatch 只路由,驗證不拆層」的明文慣例(r1 架構席 R-2,
  scripts/lumos:9739 附近註解)。
- main() 對 `loop escape` 呼叫加上 `try: ... except (ValueError, RuntimeError) as e: print("擋下:...")；return 2`,
  跟本檔 main() 裡另外十幾處相同寫法(如 `set`/`append`/`remove`、`new`、`self-audit` 等,scripts/lumos:32215/32232/32147)
  一致,是把既有分散的一致 idiom 補齊到之前漏掉的 `loop escape`,不是另立新規矩。
- `--withdraw`/`--withdrawn`/`--missing-defect-ref` 三個新旗標各自只做一件事、互斥檢查寫在函式開頭(混用即擋),
  跟 `--list` 不能跟記帳參數混用的既有擋法(scripts/lumos:9670 附近)手法一致。
- 撤回走「追加一列 kind=withdraw 紀錄、不改舊列」而不是像 `decision-supersede` 那樣就地改欄位——這是合理的,
  因為逃逸帳本身的既有合約就是 append-only(`cmd_loop_escape` docstring:「逃逸帳原語…整套審查系統的 ground truth
  側」,且既有讀者 `_escape_rows_for` 從一開始就只讀不改),套用 decisions[] 的原地翻案寫法反而會破壞 append-only
  合約,兩者屬不同層級的資料合約,不算「另起一套」。
- `escape-stats` 有 `--json` 而 `canary-stats` 沒有,是新指令補齊既有多處已有的 `--json` 輸出慣例
  (`list --json`、`rule-gap --json` 等),不是不一致。
