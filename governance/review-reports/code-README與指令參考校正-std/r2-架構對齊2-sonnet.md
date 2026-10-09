severity: major

核對範圍:`r2-repair.patch` 全部 hunk 我都逐段讀過。我另在 `/tmp/lumos-seat-work/code-README與指令參考校正-std/架構對齊2-sonnet/repo`(`git clone --shared`,停在 b53500e2)做了這些核對:
- 執行 `generate.py --check`。
- 跑 `spec-gate --help`,並用不同的 `COLUMNS` 值各跑一次。
- 對照 `test_lumos.py` 鄰近的寫法。
- 對照指令參考現有表格和區塊。
- 對照 README 現有連結。

沒核對的範圍:
- 沒跑新測試以外的任何測試。
- 沒讀 r1 材料。
- 沒看 SVG 的視覺排版,只確認重產結果可重現。

## A1 新測試用子行程剖 `--help` 排版字串,不走檔內唯一的「直接問 parser / HELP_WHEN」做法
severity: major
blocking: 是

`t_spec_gate_help_says_low_risk_blocks` 起兩個子行程跑 `run(kg, "spec-gate", "--help")` 與 `run(kg, "--help")`,再用子字串比對 stdout。這是檔內已明文放棄的做法,而且比對結果會受終端寬度影響。

引句:「    r = run(kg, "spec-gate", "--help")」
引句:「    check("① 子命令說明講到風險低時紅綠是放行條件", "風險低時紅綠是放行條件" in r.stdout, r.stdout[-600:])」

既有對照寫法:
- `scripts/test_lumos.py:8201`
  引句:「而且剖的是給人看的排版——排版一改,守衛跟著壞。這裡直接拿 parser 物件,」
  `_lumos_parser_tree()` 的說明(8193 起)明說這是「唯一」的真值來源。
- `scripts/test_lumos.py:8204` 起接著說:
  引句:「    第一版只有新守衛用這條路,舊的兩支測試還在跑子行程剖字串——同一個檔案裡」
  上一次有人加「又一種」做法,就被架構席判為必須折回。
- 檢查 help 文字的鄰近測試走 `m.HELP_WHEN["drift fix"]`,見 `scripts/test_lumos.py:68184`;`t_every_subcommand_has_when` 走 `tree[...].format_help()`,見 `scripts/test_lumos.py:8780` 一帶。

實測這個脆弱點是真的:
- `COLUMNS=40 python3.14 scripts/lumos spec-gate --help` 會把「風險」與「低時紅綠是放行條件」切成兩行,斷言 ① 變 False。
- `COLUMNS=60` 和 `COLUMNS=100` 則是 True。

測試因此依賴環境變數。
- 斷言 ③ 只確認舊句不在、`spec-gate` 字樣在,沒有驗證新句進了總表那一行。
- 同一支測試也沒有檢查 `HELP_WHEN["spec-gate"]` 這個單一來源。

歸因:有證據的修復回歸。
- 查證:`git show 0221bd2e:scripts/test_lumos.py` 沒有這支函式。
- `git show b53500e2:scripts/test_lumos.py` 在 56631 行新增它。

## A2 規格閘家筆記的改動紀錄寫成正文裸條目,不是同篇既有的摘要前綴行
severity: minor
blocking: 否

這次新增的是一行正文裸條目,結尾掛 `[test:…]`,內容是「哪天做了什麼」。同一篇之前所有帶日期的改動紀錄,都是摘要裡的前綴行(`KEY:[日期…]`、`WHY:[…]`、`PITFALL:[…]`)。

這篇正文在這之前沒有任何 `- 2026-…` 條目。摘要第 19 行仍寫著「半套只印不擋紅綠」,這次沒有跟著更新。

引句:「- 2026-10-10:`spec-gate` 的說明文字(子命令 help 與總表那句)原寫「綁的測試真跑一次印紅綠(不擋)」」

既有對照寫法:
- `docs/lumos-toolchain-knowledge/Systems/規格閘.md:19`
  引句:「  KEY:[2026-09-17]半套只印不擋紅綠、不寫審查帳;每次跑寫治理帳一行 kind=spec-gate-run」
- `docs/lumos-toolchain-knowledge/Systems/規格閘.md:22`(`WHY:[2026-10-01 …]` 的前綴寫法)

另一篇 `Systems/README圖產生器.md` 的做法沒有偏離。它本來就用正文 `- 2026-…:` 條目,這次改動照同篇的互相指向寫法,對得上 10-01 那條的前例。

歸因:有證據的修復回歸。
- `git show 0221bd2e:docs/lumos-toolchain-knowledge/Systems/規格閘.md` 沒有這條。
- b53500e2 的版本在 74 行新增它。

## A3 「只列出、不擋」改成指令區塊後,混進一條非 `lumos` 指令,且 `lumos doctor` 重複列出
severity: minor
blocking: 否

改成「指令加註解」的方向符合既有規矩。偏離的是內容:其他所有 bash 區塊每行都以 `lumos` 開頭(我用 awk 掃過),只有這一行是 `git commit`。`lumos doctor` 在 84 行已有一列註解不同的條目,這裡又列一次。

引句:「git commit                            # commit-time reminders: split a line binding several tests; tag count sentences; don't point to list items as "item N"」

中文同位置:`docs/指令參考.md:106`。

既有對照寫法:`docs/command-reference.md:84`
引句:「lumos doctor [--ci]              # health check across every note (--ci blocks)」

歸因:有證據的修復回歸。
- `git show 0221bd2e:docs/command-reference.md` 這段是條列散文。
- b53500e2 的版本改成區塊。

## A4 專案開關表新增一列合併四個開關,鍵名不完整
severity: minor
blocking: 否

表裡其他每列都是「一列一個完整鍵名」(如 `drift_check.old_sentence`、`note_shape.test_refs`),可以直接複製進 `config.json`。新列把四個開關併成一格,後三個省略 `note_shape.` 前綴,讀者無法直接照抄。實際鍵名見 `scripts/lumos` 的 `note_shape.tag_hints` 等。

引句:「| `note_shape.negation`, `tag_hints`, `close_summary`, `wording` | commit-time wording reminders」

中文同位置:`docs/指令參考.md:165`。

既有對照寫法:`docs/command-reference.md:157`
引句:「| `drift_check.retire` | the part that catches a RULE whose retire condition has come true」

歸因:有證據的修復回歸。
- `git show 0221bd2e:docs/command-reference.md` 沒有這一列。
- b53500e2 的版本在 165 行新增它。

## A5 README 英文版新增的連結,標示方式與同檔既有連結不一致
severity: minor
blocking: 否

中文版是 `[10/7–10/10 更新清點](…)`,跟中文 179 行的連結標籤是同一種形式,中英對應沒有問題。英文版 154 行的標籤寫成數字日期 `10/7–10/10`,也沒有標註內容是中文。英文版 179 行對同一份文件的連結用 `October 7–10`,並標了 `(Chinese)`。

引句:「(details in the [10/7–10/10 update audit](docs/updates/2026-10-10-readme-audit.md))」

既有對照寫法:`README.en.md:179`
引句:「The [October 1–7](docs/updates/2026-10-07-readme-audit.md) and [October 7–10](docs/updates/2026-10-10-readme-audit.md) update audits (Chinese)」

歸因:有證據的修復回歸。
- `git show 0221bd2e:README.en.md` 沒有這個連結,是在 082a5d7d 加入。
- b53500e2 的版本在 154 行。

## 圖譜鏡頭(固定席逐條判)
- **`design-loop`、`lumos-cli-read`、`測試假綠形態`、`bound-tests-gate`、`guard-kill`、`lumos-cli-lifecycle`、`授權與歸屬` 的 ★INVARIANT★:不影響。**
  - 改動只動 `scripts/lumos` 的 `HELP_WHEN["spec-gate"]` 與 `spec-gate` 子命令的 `help=` 字串,另加 `scripts/test_lumos.py` 一支測試,沒有碰任何合約綁的函式或行為。
  - 授權檔、`_VENDORED_TOOLKIT` 白名單、SPDX 檔頭、`search`、`guard kill`、`re-inject` 都沒被改。
  - 新測試不在任何合約的 `[test:]` 綁定裡。
- **`README圖產生器`(無 ★INVARIANT★):不破壞。** `generate.py` 只改兩個 `desc` 字串。重產的 SVG 與目前提交一致,`generate.py --check` 通過(22 張 SVG 驗證、可重現)。沒有手改 SVG。
- 其餘「超出上限只列名」的節點:這份 diff 沒有動到它們宣稱的行為。

最高等級:major
