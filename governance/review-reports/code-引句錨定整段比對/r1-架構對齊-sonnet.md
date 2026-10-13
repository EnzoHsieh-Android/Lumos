severity: clean

我沒找到引入第二種做法或跨層直呼的地方,所以沒有 finding。下面每個檢查點都附既有的對照位置。我只讀了 patch 和 repo,沒建任何實驗檔。

- **判準函式的位置與命名**:新增的 `_quote_rows`(依 rule 分派)、`_quote_rows_legacy`、`_quote_rows_full_span_v1`、`_quote_rule_of`、`_quote_block_note`、`_quote_anchor_row`,都放在 `scripts/lumos` 既有的 `_quote_norm` 和 `_QUOTE_MIN_NORM_LEN` 一帶,命名沿用 `_quote_*` 前綴。`seat-check` 的呼叫點 `scripts/lumos:27020` 一帶只加了 `rule=_QUOTE_WRITE_RULE`,沒另開一條路徑。
- **讀帳**:`_quote_compare_rules` 用 `_ledger_lines(text)` 切行,跟 `scripts/lumos:13284` 的定義和 `26680`、`49461` 等讀者一致。帳本路徑用 `root / "docs" / ".canary-log.jsonl"`,跟同樣不靠 vault、帶 `--repo` 的讀者 `scripts/lumos:10478`、`2370` 一樣。壞行和不是 dict 的列都計入 `bad`,沒有另一套讀法。
- **事件記帳**:寫側擋下走 `_gate_event_or_warn(_vault_repo_root(env), "canary", "blocked", note, hard=True)`,跟 `scripts/lumos:10936`、`10946`、`10727` 同形,note 也帶 `id=uuid` 防去重折疊。`gov --stats` 的四格互斥用 `startswith("quote-rule:")` 先分流,其餘照舊用包含判斷。這跟舊格的包含寫法不同,但 patch 內有註解說明原因,不算第二種做法。
- **互斥檢查與 argparse**:`--compare-rules` 跟報告、`--spec`、`--rule` 的互斥是在 `cmd_quote_check` 函式內手動檢查,回 rc2。repo 沒有 `add_mutually_exclusive_group`(grep 為空),`link-candidates` 的 `code_file` 與 `goldset` 互斥也是函式內手動檢查,所以這是既有慣例。`--rule` 用 `choices=_QUOTE_RULES`,`--repo` 預設 `.`,跟其他子指令的 `*_repo` 一致。
- **測試寫法**:`_qfs_lumos` 在子程序裡用 `-c` 字串載入 `scripts/lumos`、改常數、包裝 `_quote_rows` 丟例外。這跟 `scripts/test_lumos.py:696` 一帶(`run_sync` 在子程序裡改 `m._RETIRED_STUB_CLAUDE_HOOKS`)和 `:780` 同一種做法,所以不算第二種做法。另一種是行程內用 `_load_lumos_module` 加 `patch.object`(`:45231`)或直接指派(`:6392`)。新測試需要走完整 CLI 和落帳,選子程序可以接受。

兩個低度觀察,不列為 finding:
- ⚠ `_QUOTE_LABEL_RE` 在 `_quote_rows_full_span_v1` 之外,跟 `_quote_rows_legacy` 內部的 `_Q_LABEL` 是同一條規則的兩份。舊分支依規格要一字不改,這份重複是被迫的,patch 內有註解說明,所以只當觀察。
- `_qfs_lumos` 的載入模板是測試檔裡第 N 份載入樣板(`:230`、`:682`、`:703`、`:781` 已有),屬風格問題,不列。

總結:最高等級 clean,blocking 共 0 條
