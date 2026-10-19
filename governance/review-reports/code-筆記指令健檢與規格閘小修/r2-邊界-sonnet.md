severity: major

## Finding 1:帶空白的指令,只要後面沒有 `-` 旗標,refcheck 就把整串當路徑,誤報「已不存在」
severity: major
blocking: 是

- diff 段落:`_ref_cmdline_token` 改成「第一個詞之後有 `-` 開頭的詞」才截斷。
- 問題:「路徑加子命令、沒有旗標」的指令,例如 `scripts/lumos doctor`,以前只核對第一個詞,現在整串當路徑核對。
- 具體例:
  - 輸入:筆記正文寫 `` `scripts/lumos doctor` ``、`` `scripts/lumos search 詞 詞` ``、`` `scripts/lumos lint foo` ``。
  - 預期:核對第一個詞 `scripts/lumos`,存在,不報錯。
  - 實際:這三條整串都判成 missing。
- 重現:我在 b76b570e 的 clone 裡呼叫 `_refcheck_scan(text, root)`。
  - 修後:`[('scripts/lumos doctor','missing'), ('scripts/lumos search 詞 詞','missing'), ('scripts/lumos','ok'), ('scripts/lumos lint foo','missing')]`,`n_missing=3`。
  - 修前(55da596):只有 `('scripts/lumos','ok')`,`n_missing=0`。
  - 同一份文字裡,帶旗標的 `scripts/lumos --help` 仍是 ok。
- 影響:
  - `lumos refcheck` 在 `n_missing` 不為 0 時 rc=1。
  - 審查迴圈兩處 G1 閘會「✗」並失敗:`cmd_...settle` 與 `[gate] G1`,見 `file: scripts/lumos:13444` 和 `file: scripts/lumos:14281`。
  - doctor P 段會多出一堆「已不存在」。
  - 這個 repo 自己的 md 裡就有 `` `scripts/lumos doctor` `` 4 處、`` `scripts/lumos dispatch-lens --spec` `` 等類似寫法。規格文件寫「用 scripts/lumos doctor 檢查」非常普遍,實際會被擋。
- 為什麼不是設計取捨:計劃〈做法〉8 第 160 行只講「沒有旗標的帶空白路徑(`src/app v2/x.py`)照整串核對」,沒討論「路徑加子命令」。條款 S18「路徑加參數」也沒排除子命令。
- 測試缺口:若測試只用 `--flag` 例子,拿掉修補測試也綠。修法要在「缺檔判 missing」與「子命令當參數」之間分開,例如先判整串是不是以 `.` 副檔名結尾、或第二個詞是否像路徑或副檔名。
- 歸因:有證據的修復回歸。修前跑第一個詞,修後跑整串,兩版輸出如上。
- 引句:「if len(words) > 1 and any(w.startswith("-") for w in words[1:]) and not exists(s):」

## Finding 2:「時/前」子句記號改成明列標點後,半形與括類標點的子句不再被認出
severity: minor
blocking: 否

- diff 段落:`_ns_neg_clause_break` 把 Unicode 類別 P 改成明列的 `_NS_NEG_CLAUSE_PUNCT`。
- 具體例:`_ns_negation_hits(line)[1]` 的命中數。
  - `還沒回來時.顯示載入中`:修前 0,修後 1。
  - `還沒回來時"顯示"`、`還沒回來時[x]`、`還沒回來時】x`、`還沒回來時〈x〉`、`還沒回來時《x》`:修前 0,修後 1。
  - 這些寫法以前被當子句記號放行,現在變成否定現況句提醒。
- 意圖內的變動:`前/後端` 與 `等到期還沒做` 修前 0、修後 1。前者排除斜線並列詞,後者拿掉「等到」,這兩項是對的。
- 影響:`note_shape.negation` 預設是 warn,只多提醒,不擋。所以是 minor。
- 歸因:有證據的修復回歸(僅限 `.`、引號、括號類),兩版輸出如上。
- 引句:「_NS_NEG_CLAUSE_PUNCT = set(",,、。;;:：!?!?…—")」

## Finding 3:`--governance-log.jsonl` 之類常駐髒檔會讓「先提交」警告每次都印
severity: minor
blocking: 否

- diff 段落:`_spec_gate_low_not_red` 新增的 `git status --porcelain --untracked-files=no` 判斷。
- 具體例:本 repo 的 gitStatus 開場就是 `M docs/.governance-log.jsonl`。實作後重跑規格閘時,任何已追蹤檔有未提交改動都會印「⚠ 工作目錄現在有還沒提交的改動」。
- 判斷:這個警告沒有區分是不是實作檔,對只有帳檔髒的常見情形是噪音。因為只是提醒、不改 rc,所以是 minor。
- 歸因:新增行為,修前沒有這行,無回歸比較。
- 引句:「⚠ 工作目錄現在有還沒提交的改動:先做第 1 步,不然第 2、3 步會把實作覆寫掉、換不回來;」

## 已驗無問題的主張
- 下表各項都是用 b76b570e 的 clone 與 55da596 的 `lumos_before` 兩版對照跑的。

| 主張 | 輸入 | 結果 |
|---|---|---|
| `_git_ignored` 結尾斜線 | `build/`、`out dir/`、`中文 目錄/`、`-rf/`、`foo/build/` | 修後都判被忽略,修前全是空集合,中文與空白路徑可用 |
| `_git_ignored` 邊界輸入 | `/`、`//`、`a/../build/` | 都被剔除,不報錯 |
| `_git_ignored` 回傳 | 無斜線的 `build` | 回傳不含斜線,呼叫端 `rstrip("/")` 比對一致 |
| `_spec_gate_pick` ts 壞掉 | 缺時區或 `"bad"` 的 ts 配上正常 ts | 修前 TypeError,修後正常;缺時區排最前 |
| `_spec_gate_pick` 其他 | 同時間、同 token | 同時間取後列,同 token 先列的算數,符合說明 |
| `_spec_gate_status_at` | `""`、`HEAD`、`..HEAD`、`-x..HEAD`、`--output=/tmp/zz..HEAD`、全零 sha、不存在的 ref、前後有空白、`a..b..c`、`../../etc/passwd`、絕對路徑、目錄 | 全是 None(照嚴的判),無例外、無旗標注入 |
| `_spec_gate_status_at` 正常 | `HEAD~1..HEAD` | 回 `'doing'` |
| `summary-add` 的 `--nth` | 無 `--after` 的 `--nth 1` | 擋下並講原因 |
| `summary-add` 的 `--nth` | `0`、`-1`、`999` | 都擋下,訊息「要在 1 到 1 之間」 |
| `summary-add` 的 `--after` | 空 `--after`、找不到的片段 | 都擋下 |
| `note_shape.gate` | 同一條行號引用與缺格子的行,依序試預設、warn、off | 預設擋;warn 兩項都只提醒且預覽照出;off 兩道都不跑 |
| `_lint_excluded_lines` 先數冒號 | 逐項讀正則 | 先數冒號與 `_EXCLUDED_RE` 等價(該正則需要至少兩個冒號) |
| `_summary_line_rebuild` | 逐項讀 | 與原迴圈等價 |
| `_fmt_decision_value` | 逐項讀 | 與原判斷同式 |
| `_nodehome_changed_vs_disk` | 逐項讀 | 含已刪檔,沒有因換用它而漏刪除 |
| `cmd_cochange_check` | 逐項讀 | 預設 `--staged` 的改動語意清楚 |

## 未驗範圍與未判定
- 未跑全套與新增測試的拿掉實作翻紅檢查,只跑單點函式。
- `_spec_gate_push_one` 的 done 分支靠讀碼判斷,沒有建 fixture 端到端跑。
  - 讀碼結果:舊帳過期且「全靠人驗」時,現在會走小改動閘。但非過期的 done 計劃本來就走同一道,所以我判不算回歸。
- `A...B` 三點範圍的起點取的是 A 而不是 merge-base。推送前的範圍是兩點,故不報。

## 三問
1. 原問題的修復效果:
   - 有行為證據:`_git_ignored` 結尾斜線、`_spec_gate_pick` 的 ts 崩潰、`--nth` 無 `--after`、`note_shape.gate` 的 off 與 warn、`_spec_gate_status_at` 的 fail-safe。
   - 沒有證據、而且被證明走偏:`_ref_cmdline_token`,見 Finding 1。
2. 修補處的相鄰路徑:
   - 仍成立:`-` 開頭的檔名、中文路徑、空白路徑、`..` 路徑。
   - 退步:「路徑加子命令、無旗標」,見 Finding 1。
3. 新發現同一案例的修前與修後:
   - Finding 1:修前 ok,修後 missing。
   - Finding 2:修前 0 命中,修後 1 命中。

最嚴重 severity:major;blocking 共 1 條。
