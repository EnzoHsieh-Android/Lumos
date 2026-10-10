severity: minor

# 架構對齊第 3 輪(最後一輪)審查

核對範圍是 `r3-repair.patch` 全部 hunk 加 `r3-repair-binding.json`。我沒讀 r1、r2 檔,也沒讀舊卷證目錄。我在 `--shared` clone 裡跑了 `python3.14 scripts/test_lumos.py -k t_spec_gate_help_says_low_risk_blocks`,3 passed、0 failed,沒跑全套。

整體上,上一輪的主要偏差已經收掉:
- 測試不再起子行程剖 `--help` 排版,改走 `HELP_WHEN` 和 `_lumos_parser_tree()` 這條路。
- 開關表改成一列一個完整鍵名。
- `Systems/規格閘.md` 的正文過程紀錄改成合格的 PITFALL 行。

剩下三條都是輕微不一致,沒有 major。

## A1 總表那行的取法多用了一個 argparse 私有屬性 `_choices_actions`
severity: minor
blocking: 否

`t_spec_gate_help_says_low_risk_blocks` 的 ③ 先用 `_lumos_parser_tree()` 拿頂層 parser,再讀 `a._choices_actions` 取總表那一行的 `.help`。

- 路徑沒有另起第二條。`tree[()]._actions` 加 `isinstance(a, _ap._SubParsersAction)` 的走法,跟 `_lumos_parser_tree` 內的 `_walk` 一樣,所以不算 major。
- 但 `_choices_actions` 是這個檔唯一一處用到的私有屬性(grep 全檔只有這一處)。
- 檔內既有的「讀說明文字」做法是 `tree[...].format_help()`(`t_every_subcommand_has_when`),不碰私有屬性。①② 讀 `m.HELP_WHEN[...]` 有既有先例,沒問題。

引句:「line = next((ca.help for a in tree[()]._actions if isinstance(a, _ap._SubParsersAction)」

既有對照:
- `scripts/test_lumos.py:8791`:`return tree[tuple(prefix)].format_help()`
- `scripts/test_lumos.py:8239`:`if isinstance(act, _ap._SubParsersAction):`
- `scripts/test_lumos.py:68189`:`h = m.HELP_WHEN["drift fix"]`

歸因:有證據的修復回歸。
- 修前版本(2494971e)是 `run(kg, "--help")` 剖排版,沒有 `_choices_actions`;這個私有屬性是 cbb854a0 才引進的。
- 修後版本:`_choices_actions` 出現在 `scripts/test_lumos.py:56642`,是它在全檔唯一的位置。
- 改善方向:改讀 `tree[()].format_help()`,或在 `_lumos_parser_tree` 旁加共用小工具,不要在單支測試裡直取私有屬性。

## A2 開關表四列的括號語氣,中英對得不齊,而且用了跨列的「同上」
severity: minor
blocking: 否

中英都是四列,鍵名也一一對應。細節不齊有兩處:
- 中文 `close_summary`、`wording` 兩列寫「（同上，受總開關管）」,英文只寫 `(same)`,少了 `governed by the master switch`。`tag_hints` 那列中英是對齊的。
- 表內既有寫法是每列自足,例如 `note_shape.slots` 寫「也受 `note_shape.gate` 管」,`drift_check.old_sentence` 寫「照 `drift_check.gate`」。「同上」要讀者往上一列找,是新寫法。

引句:「| `note_shape.close_summary` | 提交時提醒結案後摘要還寫待定（同上，受總開關管） | warn / off | warn |」

英文對應列:「| `note_shape.close_summary` | commit-time reminder when a closed note's summary still says pending (same) | warn / off | warn |」

既有對照:
- `docs/指令參考.md:147`(`note_shape.slots` 列,自足寫法)
- `docs/command-reference.md:147`

歸因:有證據的修復回歸。修前版本是單一合併列 `note_shape.negation`、`tag_hints`、`close_summary`、`wording`;「同上」是 cbb854a0 拆列時新增的。

## A3 英文 README 對中文文件的標示法,跟檔內既有「(Chinese)」括號寫法不同
severity: minor
blocking: 否

`README.en.md` 這一句寫成 `…audit.md), in Chinese)`,是逗號加 `in Chinese`。同檔既有的寫法,都是連結後面接獨立的 `(Chinese)`。

引句:「details in the [October 7–10 update audit](docs/updates/2026-10-10-readme-audit.md), in Chinese).」

既有對照:
- `README.en.md:179`:「update audits (Chinese) list each audit's commits」
- `README.en.md:88`:「[test quality onboarding standard](skills/lumos-project-notes/commands/test-quality-standard.md) (Chinese)」
- `README.en.md:181`:「[onboarding guide](ONBOARDING.md) (Chinese)」

歸因:有證據的修復回歸。修前版本沒有任何語言標示,「in Chinese」是 cbb854a0 才加的。連結文字改成 `October 7–10`,跟 `README.en.md:179` 一致,沒問題。

## 核對過、判無不一致的項目
- **指令參考「只列出、不擋」區塊**:`lumos doctor` 從指令區塊搬成粗體前綴散文段。同一節已有散文先例,見 `docs/指令參考.md:110`「**派審查員時**：…」和 `:112`「**治理事件帳**：…」。粗體加全形冒號(中文)、粗體加半形冒號(英文)的寫法也一致。中英段落一一對應。
- **`lumos note-shape --staged` 那行**:區塊內「指令加 `#` 註解」格式沒變,中英語意對應。
- **前言改寫**:中英逐句對應,對照 `docs/指令參考.md:107` 和 `docs/command-reference.md:107` 的前言。
- **README 中英「補凍結」那句**:中文是「回放與補凍結執行出錯」,英文是 `the replay or catch-up freeze run hits an error`,對應。
- **`Systems/規格閘.md`**:
  - PITFALL 行有 `[出處:]`、`[根因:]` 和 `[test:t_spec_gate_help_says_low_risk_blocks]`,格式合格,該測試在檔內存在且實跑綠。
  - 刪掉正文的日期過程紀錄,符合「過程紀錄不寫進筆記」。
  - KEY 行的日期括號寫法 `[2026-09-17;2026-10-10 校正]` 沿用檔內 `[日期 代碼審 r1 折入]` 這類既有形式。

## 圖譜鏡頭(固定席筆記)
本次改動只動 `scripts/test_lumos.py` 裡的一支測試,加文件和 `Systems/規格閘.md` 的筆記行。沒有改 `scripts/lumos` 的行為,也沒有動 `HELP_WHEN` 或 parser 內容。

- **`design-loop`、`測試假綠形態`、`lumos-cli-read`、`bound-tests-gate`、`guard-kill`、`lumos-cli-lifecycle`、`授權與歸屬`、`README圖產生器`**:不影響。它們的合約(處置閘第五步、還原翻紅釘需前置斷言、search 濾網、bound-tests 的 rc 規則、guard kill 的 rc 與 JSON 純淨、re-inject 保留 sentinel 外內容、授權檔不進白名單、SPDX 與 MIT 檔頭、README 圖產生)所綁的測試與被測碼都沒被碰到。
- **`測試假綠形態` 的「還原翻紅釘需前置斷言」**:新版 ①②③ 直接讀字串,沒有「現場走不到被測分支」的風險。①③ 都是正向包含檢查,②③ 的反向 `not in` 檢查也各有正向檢查擋著,不會變成空殼綠。
- **「超出上限,只列名」的節點**:不是合約,不逐條答。

最高等級:minor
