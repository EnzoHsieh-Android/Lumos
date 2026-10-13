severity: major

已讀整份修訂稿,逐項對照 `scripts/lumos` 與 `scripts/test_lumos.py`(行號為 `Word-wild-search-quote` 內的現況)。多數地方有照既有做法走:
- `_quote_rows` 維持單一實作。呼叫點確為四處:`scripts/lumos:10965`、`26373`、`26529`、`26787`。
- 在寫側 `rec["quote_rule"]=…` 加欄位,跟 `10941`、`10782` 等同一寫法。讀側對未知欄位本來就容忍(`6572`)。
- 擋下事件走 `_gate_event_or_warn(…,"canary","blocked",…,hard=True)`,跟 `10933`、`10943` 同一形狀。

不對齊處如下。

### 1. S6 測試讀錯治理帳位置,實作做對了也不會綠
severity: major
blocking: 是
引句:「gov = v.parent / ".governance-log.jsonl"」
file: `scripts/lumos:1496`(`_gate_event` 內 `docs = root / "docs"`,不是目錄就回 None,不落帳)
file: `scripts/test_lumos.py:37940`(既有的 canary blocked 事件測試先 `git init` 再讀 `root/docs/.governance-log.jsonl`)

1. `t_quote_full_span_compare_and_event` 用 `mkvault()`,其 `v.parent` 是私有暫存根,底下沒有 `docs/`,也沒有 `.git`。
2. 寫側呼叫 `_gate_event_or_warn(_vault_repo_root(env), …)`。`_vault_repo_root` 找不到 `.git`,退回 `vault.parent`,再往下找 `docs/` 找不到,`_gate_event` 回 None,什麼都不寫。
3. 就算有落帳,事件也在 `root/docs/.governance-log.jsonl`,不在 `v.parent/.governance-log.jsonl`。
4. 結果:`hit` 恆為空,`len(hit) >= 1` 永遠紅。這是只有改測試才能解的假紅,不是實作做對就會綠。
5. 既有做法是 `git init` 加 `docs/` 目錄,並讀 `d/.governance-log.jsonl`(`37940-37953`)。修訂稿 S6 的測試沒照這個做。

### 2. 擋下事件的 note 沒照既有慣例,也只記新判準那一種擋下
severity: minor
blocking: 否
引句:「note 帶 `quote-rule=full-span-v1` 與不合的類別,REVISIT 到期有資料可數。」
file: `scripts/lumos:10933`(note 寫成 `<標籤>:<數> loop= auditor= id=<隨機碼>`,註解寫明 id 是為了讓同一秒連撞兩次在 `gov` 去重時不被折成一次)
file: `scripts/lumos:10968-10979`(現有載體引句錨不到的擋下,不落任何事件)

1. 既有 canary 擋下事件一律帶 `loop=`、`auditor=`、`id=`。稿裡只寫 `quote-rule=…` 與類別,沒提 `id=`。照稿實作,連撞兩次會被去重折成一筆,REVISIT 數到的是低估。
2. 稿裡只規定「因新判準擋下」才記。同一個 `if _qmiss` 區塊現在對舊判準的擋下也不留痕。同一道檢查兩種判準,一種有帳、一種沒有,`gov` 看到的是殘缺的分母。沒有任何既有做法是同一道擋下只對某個分支記事件。

### 3. 判準版本欄位的先例說得比實際更像
severity: minor
blocking: 否
引句:「照搬資料格式版本欄位的做法(序列化格式的 schema version、本 repo 回放凍結閉包的 `engine_rev`、`grader` 欄位)」
file: `scripts/lumos:1173`(`engine_rev` 蓋在凍結 verdict 上)
file: `scripts/lumos:1224`(`_engine_stale = g.get("engine_rev") != _REPLAY_ENGINE_REV`,不同就跳過重算)
file: `scripts/scenario_probe.py:1255`(`grader` 只出現在探針腳本的結果紀錄,不在 `scripts/lumos`,也不在 canary 帳)

1. 兩個先例的語意是「版本對不上就視為過期、跳過」。沒有任何先例是「讀的時候依逐列欄位值,在兩套活著的判準之間分派」。
2. 稿裡的 `quote_rule` 是這種分派,還要同時保留 `legacy` 與 `full-span-v1` 兩條分支。這是專案原本沒有的第二種機制,跟 `_REPLAY_ENGINE_REV` 並存,各管一段回放的決定性。
3. 稿裡明說要記決策並推翻 Issue 的前提,所以我不列 major。但「照搬」這個說法不實,PRIOR-ART 該改成「新機制,與 engine_rev 並存的理由」。

### 4. `quote-check --compare-rules` 的參數形狀跟現有子命令不相容,`--since` 語意也撞名
severity: minor
blocking: 否
引句:「`lumos quote-check --compare-rules [--since YYYY-MM-DD] [--repo 根]`:照〈量測〉的口徑掃帳」
file: `scripts/lumos:53141`(`quote-check` 的 `qc_report` 是必填位置參數,`--spec` 是 `required=True`)
file: `scripts/lumos:53147`(`link-candidates` 的做法:`nargs="?"` 加 `--all-goldset` 切模式,`--repo` 預設 ".")
file: `scripts/lumos:52457`(`gov --since` 是整數天數)

1. 測試 `quote-check --compare-rules --repo …` 不帶報告也不帶 `--spec`,現行 argparse 會直接報錯。稿裡沒寫要改成 `nargs="?"` 加互斥,實作者得自己發明。
2. 既有的唯讀統計模式是在同一指令上用旗標切(`gov --stats`、`link-candidates --all-goldset`),稿的方向一致。
3. `--since` 在 `gov` 是「近 N 天」整數,在這裡是日期字串,同一個旗標名在兩個指令語意不同。

### 5. 「格式不合」沒指名既有的 `malformed` 旗標
severity: minor
blocking: 否
引句:「`seat-check` 用 `_QUOTE_RULE_WRITE`(它只拿抽出的引句文字比材料範圍,格式不合的列照舊跳過)。」
file: `scripts/lumos:25802`(格式壞的列現在是 `{"ok": False, "malformed": True}`)
file: `scripts/lumos:26789`(`seat-check` 靠 `q.get("malformed")` 跳過這種列)
file: `scripts/lumos:26388`(處置閘把 `ok` 為 False 的一律印成「錨不到快照」)

1. 稿沒寫新判準的格式不合列要沿用 `malformed: True` 這個鍵。若實作者另立鍵,`seat-check` 會把格式壞的片段當一般引句拿去比材料,誤報 `out_of_scope`。這等於 `_quote_rows` 回傳形狀出現第二種慣例。
2. 新判準的格式不合列在處置閘會被印成「N 條錨不到快照」,但其實是格式問題。稿沒說是否區分措辭。

### 逐節狀態
- 前言、〈量測〉、〈範圍〉:已讀,無架構面 finding。
- 〈抽取規則〉:已讀,無架構面 finding。稿把新舊兩版放在 `_quote_rows` 用參數選,符合單一實作約定;第 6 點拿掉「標籤數減抽取數」補差額,但沒指名要保留 `malformed` 鍵,併入第 5 條。
- 〈判準版本蓋在帳上〉:見第 3、5 條。
- 〈量測與留痕〉:見第 1、2、4 條。
- 〈同步改的地方〉、〈驗收條款〉、〈回退〉:已讀,除第 1 條的測試位置問題外無 finding。
- 〈實務隱患〉:此功能碰的風險類逐類如下。
  - 自我治理:有對策,屬正確性席範圍。
  - 帳本不可逆:稿已寫明。
  - 金流、對外送出:稿已排除,屬實。
  - 並行寫帳:無新增,因為沿用 `rec[...]` 同一條 append 路徑。

總結:最高等級 major,blocking 共 1 條
