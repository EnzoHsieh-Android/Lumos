severity: minor

審查範圍:架構對齊鏡頭。我逐節讀完 spec,並對照 repo 的設定讀取、版本欄位、時間切換、事件記帳、指令參數、互斥檢查、測試寫法。沒有發現跨層直呼,也沒有 major 級的第二種做法。有一處是否算第二種做法判不準,標 ⚠ 交編排者。

已讀,無 finding 的部分:

- **互斥檢查**:spec 寫「不用 argparse 互斥群組,同檔既有做法」。我 grep 過,`scripts/lumos` 全檔沒有 `add_mutually_exclusive_group`,屬實。
- **指令參數**:`--repo` 預設「.」,與 `severity-check` 及 `link-candidates` 一致,而且該 parser 同檔已有大量 `--repo`。`--since N` 與 gov 的 `--since` 同為「近 N 天」。
- **事件記帳**:`_gate_event_or_warn(_vault_repo_root(env), "canary", "blocked", note, hard=True)` 與既有寫側四處同形(10564、10724、10933、10943)。note 前綴加 `id=` 隨機碼也是既有做法。
- **記帳寫側取根**:用 `_vault_repo_root(env)` 與既有一致。
- **抽取函式**:`_quote_rows` 是唯一抽取實作,呼叫點共 4 處(10965、26373、26529、26787),與 spec 說的四個對得上。
- **測試風格**:`t_quote_full_span_*` 沿用 `_load_lumos_inproc`、`check()` 與 `_stats_fixture`,與既有 `t_quote_check_*` 同風格。
- **補充**:`_loop_ts_key` 對非字串 `ts` 會丟 `AttributeError`,spec 已寫「不是字串算略過」,沒問題。

## 1. 〈判準版本蓋在帳上〉:是否算第二種版本做法 ⚠
severity: minor
blocking: 否
引句:「「判準版本蓋在資料列上、讀的時候照那一列的版本選判準」在本 repo 是新機制」
file: `scripts/lumos:9964`、`scripts/lumos:9969`、`docs/lumos-toolchain-knowledge/Projects/改制回測_計劃.md:34`

1. repo 已有一個版本欄位 `_REPLAY_ENGINE_REV`。它的註解寫「d5 判定語意改版就 bump」,`改制回測_計劃` 第 34 行寫「制度演進≠漂移(engine_rev 分流)」。換句話說,判定語意改版的既有做法是推進回放版本。
2. spec 為「引句判準換版」另開一套「帳上的章」,同時明說不推進 `_REPLAY_ENGINE_REV`。spec 已自己標出這個取捨,並用 `decision-add` 記成決策。
3. 因此 repo 會有兩套並存的判定版本機制。這算不算第二種做法,我判不準,⚠ 交編排者裁。spec 的理由(推進版本會讓 305 個黃金抽查跳過重算)我查過,與 `scripts/lumos:1224` 的 `_engine_stale` 行為相符。
4. 這個決策的事實依據是 `_engine_stale` 為真時只跳過重算、不報紅,不是 spec 自己的臆測。

## 2. PRIOR-ART 說「新機制」,但 repo 已有帳列蓋規則版本的先例
severity: minor
blocking: 否
引句:「既有的版本欄位(回放凍結閉包的 `engine_rev`)語意是「版本對不上就視為過期、跳過重算」」
file: `scripts/lumos:7908`、`scripts/lumos:8135`

1. spec 說既有版本欄位只有 `engine_rev`。實際上 `_DOOR_RULE_VERSION` 已經蓋在 spec-gate 帳列上(`door_rule`、`small_change_rule` 兩個欄位,帳上各 295 筆)。
2. 它只記錄不分派判準,所以「讀的時候照那一列選判準」仍是新的。但「判準版本蓋在帳列」本身不是新機制。
3. 命名上 `quote_rule` 與 `door_rule` 同尾碼,可以。值型別不同(整數對字串),不構成問題。
4. 建議 PRIOR-ART 補列這個先例,並說明差在「只記錄」與「分派」。

## 3. 設定讀取:PRIOR-ART 與實作、行為描述互相矛盾
severity: minor
blocking: 否
引句:「設定區塊沿用 `.lumos/config.json` 的 `bound_tests` 讀法(`_bound_tests_parallel`:寫錯出聲、退回預設)。」
file: `scripts/lumos:49793`、`scripts/lumos:13780`

1. PRIOR-ART 說壞值「退回預設」。但〈判準版本蓋在帳上〉第 63 行寫壞值一律退回 `legacy`。第二階段預設改成 `full-span-v1` 之後,「預設」與 `legacy` 就是兩個值,PRIOR-ART 的描述會變錯。
2. 回傳形狀也不同。`_bound_tests_parallel` 直接印 stderr 並用 `_BT_PARALLEL_WARNED` 去重;`_fix_check_config` 回 dict 帶 `warnings` 清單。spec 的 `(write_rule, 警告或 None)` 是第三種形狀。三種各有人用,不構成 major,但 PRIOR-ART 該改寫成「參考 `_fix_check_config`」或明說差異。
3. 第 64 行說「處置閘與回放用它們既有的 `root`」取設定。但處置閘只讀帳上的章,全 spec 沒有處置閘讀設定的動作。這句是多餘的,而且容易被實作者誤解成要讓處置閘讀設定。

## 4. 同步清單漏掉一支會被 `rule=` 關鍵字打壞的既有測試
severity: minor
blocking: 否
引句:「同步把那個測試的替身改成收 `rule=`)。」
file: `scripts/test_lumos.py:27411`、`scripts/test_lumos.py:37152`

1. spec 只列了 `cmd_seat_check` 的注入測試(37152 的 `lambda *_: []`)。
2. 另有一處也替換 `_quote_rows`,spec 沒提。`test_lumos.py:27411` 的 `def quote_rows(*args)` 會被注入 `cmd_canary` 的 `__globals__`。
3. 寫側改成 `_quote_rows(..., rule=...)` 之後,這個替身會丟 `TypeError`,而不是預期的 `RuntimeError`、`OSError`。它斷言 stderr 含 `RuntimeError: snapshot-quote-parser-fault`,必紅。
4. spec 也沒規定 `rule` 是位置參數還是關鍵字參數。新測試 `_qfs_record_with_broken_other_rule` 靠 `k.get('rule')`,等於要求用關鍵字傳。這點該寫進 spec。

## 5. S8 測試釘住的是第一階段的預設,第二階段會翻紅,但 spec 只說改一支測試
severity: minor
blocking: 否
引句:「有一支測試釘「沒有設定時寫側用舊判準、新帳蓋 legacy」。」
file: `scripts/test_lumos.py:27138`

1. 第 79 行與第 80 行說釘預設值的是「一支測試」。
2. 實際上至少兩支:`t_quote_full_span_rule_stamped_on_ledger` 的「沒有設定檔蓋 legacy」,以及 `t_quote_full_span_manual_commands_repo` 的 `--repo bare`(沒設定的根走舊判準、不越界)。
3. 第二階段把預設改成 `full-span-v1`,S8 那個 bare 根的斷言會翻紅。第二階段的待辦清單要把它列進去。

## 6. 〈同步改的地方〉對〈驗收條款〉的對應:已讀,無 finding
- S1 到 S8 的 `[test:]` 名稱與實際函式一一對得上。
- 檔案內部的交叉引用目標(`_loop_ts_key`、`_vault_repo_root`、`cmd_severity_check`、`decision-add --decided/--context/--why`)都存在。

實務隱患逐類,只列與本鏡頭有關的:
- **自我治理**:spec 已有對策,不在架構鏡頭範圍。
- **跨層直呼**:無。四個呼叫點都經 `_quote_rows`,設定讀取放在 `_quote_check_config`,處置閘只讀帳。
- **第二種做法**:只有第 1 條 ⚠。

我沒有建立任何實驗目錄,沒有東西需要刪。

總結:最高等級 minor,blocking 共 0 條(另有第 1 條 ⚠ 交編排者裁)
