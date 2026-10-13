severity: major

**回報**:沒有跑 git 寫入,也沒在 /tmp/lumos-seat-work 建任何東西。

### 1. quote-check 與 seat-check 讀設定沒有根目錄來源,台帳定位也引錯先例
severity: major
blocking: 是
引句:「手動 `lumos quote-check <報告> --spec <快照>`:預設用 `write_rule`,可加 `--rule legacy|full-span-v1`;人讀輸出第一行印「引句判準:<版本>」」
引句:「帳本照 `canary` 指令同一套方式找(專案根的 `docs/.canary-log.jsonl`)。」
file: `scripts/lumos:53141` quote-check 與 seat-check 都標「vault-free」,參數只有報告、`--spec`、`--json`,沒有 `--repo`。
file: `scripts/lumos:53160` 既有的 vault-free 指令(`severity-check`、`link-candidates`)用 `--repo`(預設 ".")決定根目錄。
file: `scripts/lumos:10475` `cmd_severity_check` 用 `root / "docs" / ".canary-log.jsonl"` 找帳本。
file: `scripts/lumos:49793` `_bound_tests_parallel(repo_root)` 必須有 repo_root 才讀得到設定。

1. 既有做法:`.lumos/config.json` 區塊讀取一律由呼叫端傳入根目錄。寫側走 `_vault_repo_root(env)`,處置閘走 `root` 參數。vault-free 指令的根目錄由 `--repo` 給,預設為 ".",不靠 env。
2. 稿的做法:要 `quote-check` 和 `seat-check`「預設用 `write_rule`」,也要 `--compare-rules` 掃專案根的帳本。但稿沒給這兩個指令 `--repo` 參數,也沒說根目錄從哪來(cwd、報告路徑往上找,還是找 .git)。
3. 差在哪:這是在 vault-free 層引入一種新的取根方式,等於第二種做法。
   - 在子目錄或別的 cwd 執行時,會讀到別專案的設定,或讀不到設定而退回預設。同一份報告的 `quote-check` 結果會跟處置閘不一致。
   - 「照 `canary` 指令同一套方式找」引錯了先例。canary 用 `env.vault.parent`(`scripts/lumos:11010`),要 vault。vault-free 的既有先例是 `severity-check` 的 `--repo` 加 `root/docs/.canary-log.jsonl`。
4. 驗收缺口:S5、S6 的測試(`t_quote_full_span_rule_stamped_on_ledger`、`t_quote_full_span_compare_and_event`)沒約束根目錄,實作選哪種都能綠。

### 2. 處置閘的 root 可以是 None,稿沒交代讀設定的退路
severity: minor
blocking: 否
引句:「讀法照 `_bound_tests_parallel`:區塊不是物件、值不在認得的集合,印一句提醒並當沒寫。」
file: `scripts/lumos:26195` `_loop_status_disposal(..., root=None, ...)`,函式裡有 `if root is not None` 的分支(26233)。
file: `scripts/lumos:6446` `_lumos_config_near_vault(env)` 是另一套「從 vault 往上找設定」的讀法。

1. 既有做法:`_bound_tests_parallel` 只接 repo_root。處置閘的 `root` 預設是 None。倉裡已有兩種讀設定的方式(repo_root 直讀、`_lumos_config_near_vault` 往上找)。
2. 稿沒寫新的 `quote_check` 讀取函式用哪一種,也沒寫 root 是 None 時怎麼辦。
3. 風險:實作若為了 root=None 再選一種根目錄解析,就是第三種讀法。
4. `_bound_tests_parallel` 的提醒靠模組層快取 `_BT_PARALLEL_WARNED` 去重。稿要求讀側隔離閥「印一行警告」。每次處置閘都印,還是去重,稿沒寫。

### 3. 互斥參數的做法沒寫,既有做法是手動檢查
severity: minor
blocking: 否
引句:「這時位置參數(報告)與 `--spec` 改成不必填,跟 `--compare-rules` 互斥;帶了 `--rule` 也拒絕。」
file: `scripts/lumos:53511` 註解「不用 argparse 的互斥群組:整支工具只有這裡用它,而且它的錯誤訊息是英文」,實際做法是手動檢查、印「擋下:…」、回 rc2。
file: `scripts/lumos:53147` `link-candidates` 用 `nargs="?"` 加手動檢查。

1. 既有做法:不用 `add_mutually_exclusive_group`,用手動檢查、中文「擋下:」訊息、rc2。
2. 稿只寫「互斥」,沒寫機制和 rc。實作者很可能用 argparse 的 group,那就會引入英文錯誤訊息這第二種做法。
3. 目前 `--spec` 是 `required=True`(53143),要改成手動必填檢查。稿也沒提這個改動。

### 4. 版本章是第二套「判準換版」機制,且舊的兩套沒有退場計畫
severity: minor
blocking: 否
引句:「「判準版本蓋在資料列上、讀的時候照那一列的版本選判準」在本 repo 是新機制」
file: `scripts/lumos:9966` `_SEV_WRITESIDE_CUTOFF`(日期字串比對)。
file: `scripts/lumos:8216` `_SECURITY_SEAT_SINCE`(帶時區,走 `_loop_ts_key`)。
file: `scripts/lumos:9969` `_REPLAY_ENGINE_REV`。

1. 既有做法:判準隨時間換版用常數加時間比對,共有兩個先例,加上回放的引擎版本。
2. 稿的做法:新增帳上 `quote_rule` 章。這是引入第二種做法。稿在 PRIOR-ART 明說是新機制,理由是兩個先例留下「合入當天舊碼寫帳」和時區兩個坑。我認可這個理由。
3. 差在哪:
   - 稿沒說舊的兩個常數日後是否改用章,倉裡就會同時存在兩種換版做法。
   - 稿自己又加了 `_QUOTE_RULE_STAMP_SINCE`(帶時區、走 `_loop_ts_key`)。它只用來警告,但仍是第三個時間常數。與 PRIOR-ART「不採用時間切換」的說法並存。
   - 這個常數的值是「第一階段合入日」。合入日在提交前未知,稿沒說怎麼填。
4. 定級:這是 r1 架構席已建議、並且有理由的刻意取捨,所以我標 minor,不阻擋。如果裁定「新機制須有退場計畫」,可升 major。

### 5. gov --stats 的分類寫法與新格有落差
severity: minor
blocking: 否
引句:「以 note 開頭 `quote-rule:` 計數,不再落進「缺 refuted-set」。」
file: `scripts/lumos:9532` 既有分類是 `"report-not-normalized" in _d(r)`(子字串),「缺 refuted-set」是剩餘值 `len(_rej) - _rn - _rf`。
file: `scripts/lumos:9736` 去重 token 是 `ts + note`,所以 note 需帶 `id=`。

1. 既有做法:用子字串比對,第三格靠相減得到。稿的 `quote-rule:` 開頭比對是第二種寫法。
2. 稿要求的新格如果沒有從剩餘值的相減式裡扣掉,「缺 refuted-set」就會雙算。S6 的測試必須同時斷言這一格的數字。
3. 稿的 note 形狀 `quote-rule:<…> kind=… cats=… loop=… auditor=… id=…` 符合既有 `name:detail loop= auditor= id=` 慣例,這點對齊。
4. 補充:`scripts/lumos:10975` 現行的載體引句擋下(`return 2`)並不記 `_gate_event_or_warn`。稿是在新增事件,不是改既有事件。

### 6. 讀章函式的位置沒指定
severity: minor
blocking: 否
引句:「讀章的規則(處置閘、回放、所有拿帳列判引句的地方共用一支小函式):」
file: `scripts/lumos:25773` `_quote_rows` 與 `_quote_norm` 同區。

1. 稿沒指定放在哪。依既有「單一實作放同區」的做法,應與 `_quote_rows` 同區,並且在〈範圍〉或 S5 寫明。
2. 「所有拿帳列判引句的地方」目前只有處置閘一處。回放是走 `_loop_status_disposal`(`scripts/lumos:1126`、`1140`、`1268`),不是另一處。稿以為有多處,實作者可能多加一個呼叫點。

### 已讀,沒有 finding 的項目
- `_quote_rows` 單一實作加必填 `rule`。四個呼叫點是 `scripts/lumos:10965`、`26373`、`26529`、`26787`,與稿所列相符,沒有遺漏的呼叫點。
- `seat-check` 跳過 `malformed` 列,沿用現行鍵(`scripts/lumos:26789`、`25802`),對齊。
- `_gate_event_or_warn(..., "canary", "blocked", note, hard=True)` 的簽名和 `id=` 慣例對齊(`scripts/lumos:1622`、`10933`)。
- 回放不推進 `_REPLAY_ENGINE_REV`,與 S7 一致,沒有第二種做法。

### 實務隱患(架構面)
- 跨層:見第 1 條,vault-free 指令碰到設定與帳本定位。
- 第二種做法:見第 4 條。其餘(金流、對外送出)稿已排除,同意。

總結:最高等級 major,blocking 共 1 條。
