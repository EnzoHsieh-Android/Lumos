severity: major

我是三個月後的接手人,逐項對了計劃與兩篇 Systems 節點的句子、掛鉤與註冊程式的實際行為、各處平行名單,以及條款 [S1]–[S5] 綁的測試。有 1 條 major、3 條 minor。

**平行名單與命名(逐項對過,沒有問題)**
- 事件名 `pretooluse-bypass-ask-hook` 與 `enforcement_status` 的列名一致。
- 預篩字樣、長度上限 2 萬字、`_inner_budget` 的複本都與計劃相符。`HOOK_BUDGET` 的 5 與 `_codex_entries` 跳過 Bash 的寫法,和計劃、S5 也相符。
- `scripts/lumos` 裡凡是列舉掛鉤檔名的地方都改到了:
  - 安裝名單 `_GLOBAL_CLAUDE_HOOKS`、工具自裝檔名單 `_VENDORED_TREE_FILES`、錨點名單 `ANCHOR_FILES`、`enforcement_status` 的列。
  - `_own_hook_scripts` 由安裝名單推出,不必另改。
  - 安裝與拆除流程用的 `_GLOBAL_HOOKS` 與 `_GLOBAL_CLAUDE_HOOKS` 是同一份,所以拆除會清掉這支。
- `governance/anchor-baseline.json` 的 sha256 與現檔相符。
- 三篇筆記的 `lumos lint` 都是 0 問題;摘要行的必有鍵(WHY 的出處與因、PITFALL 的出處、根因與 test)都齊,`[test:]` 指的測試名都存在。
- 我跑了 `-k bypass_ask`、`vendored`、`budget`、`anchor`、`enforcement`、`codex_r1`、`hook_python`,全綠。
- 文件裡沒有別的地方列舉掛鉤檔名,不必跟著改。

**1.** 計劃〈回退〉說拿掉註冊就能退,實際做不到
severity: major
blocking: 是
引句:「拿掉 `merge-claude-settings.py` 那條 Bash matcher 並重跑安裝,掛鉤就不再被呼叫;掛鉤檔留著不影響任何事。」
- 輸入:照這句做,從 `HOOK_ENTRIES` 刪掉 `matcher: "Bash"` 那條,重跑 `merge-claude-settings.py`。
- 走到哪:合併器只會新增、遷移、去重,並剪掉指向不存在檔案的註冊,不會移除已經寫進 `settings.json` 的條目。見 `scripts/merge-claude-settings.py:381-394`。
- 結果:`bypass-ask-hook.py` 仍在 `_GLOBAL_CLAUDE_HOOKS`,檔案照舊被複製,所以註冊不算懸空,也不會被剪。
- 重現:我在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/合約圖譜-sonnet/rb.py` 用假 HOME 先裝再用拿掉該條的版本重跑,重跑後 PreToolUse 仍是 `('Bash', ['ude/hooks/bypass-ask-hook.py" --budget 5'])`。
- 應該是:〈回退〉要寫成同時把檔名移出安裝名單並加進 `_RETIRED_CLAUDE_HOOKS`(讓檔被刪、註冊變懸空後被剪),或改寫成只能靠分類函式收窄。目前的句子會讓接手人以為拿掉就退了,實際上每次命中仍會跳確認框。

**2.** `LUMOS_SKIP_*` 接 lumos 指令的判法,與計劃寫的規則和 S1 的前綴說法不一致
severity: minor
blocking: 否
引句:「的詞當程式,或 `python*` 的第一個參數檔名是 `lumos`」
引句:「if self._skip_before(seg, min(len(seg), i + 4)) and _is_lumos_cmd(seg, i):」
- 輸入與輸出(`bypass_reasons(指令, "/Users/someone/work/repo")`):
  - `LUMOS_SKIP_FIX_CHECK=1 timeout 60 lumos code-loop check` 回 `[]`。
  - `LUMOS_SKIP_X=1 sudo lumos code-loop check` 回 `[]`。
  - `lumos search LUMOS_SKIP_X=1 foo` 回 `['lumos-skip']`,這是誤問。
- 原因:`_is_lumos_cmd` 只看「略過賦值與關鍵字之後的第一個詞(含 `env` 之後)」是不是 lumos。計劃寫的是「段裡有檔名為 lumos 的詞」,git 那邊也確實是掃整段,只有 lumos 這條不一致。
- 前綴不一致:S1 說前綴 `env/timeout/time/command/then/!/括號` 都認得,但 `timeout` 與 `sudo` 這類沒列在 `_KEYWORDS` 的包裝詞會漏。
- 誤問:`i + 4` 的視窗計劃沒寫,視窗內的參數若長得像 `LUMOS_SKIP_X=1` 會被當成賦值。
- 應該是:程式改成與計劃一致,或計劃改寫成實際行為。S1 的測試也沒有這個形狀的案例。

**3.** S4 的三種最壞形狀與預篩例外,測試沒有真正驗到
severity: minor
blocking: 否
引句:「10 萬字單詞、數萬個分段、大量未閉合 `<<EOF` 三種形狀 應 各在 0.5 秒內判完」
引句:「("大量未閉合 heredoc", "cat <<EOF " * 3000 + "\n git push --no-verify")):」
引句:「預篩階段丟例外、輸入不是 UTF-8、`command` 不是字串時 應 放行、不印 traceback」
- 未閉合 `<<EOF` 那筆長 30022 字,超過 `MAX_LEN`,直接走 `_literal`,從沒跑到 `strip_heredocs`。10 萬字單詞同樣只走字面判。
- 我另外量了真正走結構分類的形狀,都在 0.5 秒內:
  - 未閉合 heredoc 1900 次,19022 字,0.02 秒。
  - 1900 個含換行的 heredoc,0.25 秒。
  - 4900 個指令替換,0.31 秒。
  - 實測沒有效能問題,但 S4 綁的測試沒有驗到條款說的最壞情形。
- 「數萬個分段」測的是 9000 個,不到數萬。
- 條款列了「預篩階段丟例外」,測試沒有這一項。非 UTF-8 的案例走的是替換解碼,不會丟例外。計劃的審計紀錄承認這層「刻意不釘」,但條款文字仍把它列為應驗項,兩邊不一致。
- 應該是:條款拿掉這一項,或測試補上。

**4.** S3 說暫存根以 `_temp_roots()` 為準,但測試把它整個換掉
severity: minor
blocking: 否
引句:「暫存根以 `_temp_roots()` 為準,相對 `cd` 依序疊加解析」
引句:「m._temp_roots = lambda: [str(tmp_root)]」
- 整份新測試沒有任何一處驗預設根(`/tmp`、`/private/var/folders` 等六個、`TMPDIR` 有設才加、空字串不加)。
- 把 `_temp_roots` 裡的 `"/tmp"` 拿掉,S1 到 S5 照樣全綠。
- 設計審量到的主要情境(審查席在 `/tmp/lumos-seat-work/` 做實驗)因此沒有守衛。
- 應該是:補一條不換掉 `_temp_roots` 的案例,例如 `cd /tmp/新目錄 && … --no-verify` 放行。

**一個附帶觀察(不算 finding)**
- `_GLOBAL_HOOKS` 與 `_GLOBAL_CLAUDE_HOOKS` 同名單,安裝時 Codex 的 `~/.codex/hooks` 也會多收到一份未註冊的 `bypass-ask-hook.py`。
- 這不會被執行,也沒有測試因此翻紅。計劃〈做法〉只寫了 `~/.claude/hooks/`。

**固定席節點逐條判**
- `Issues/code-loop守衛main-direct盲區`:不影響。它管 pre-push 的 tier 判定,diff 沒動 `scripts/hooks/pre-push`。
- `Systems/lumos-cli-lifecycle`(★INVARIANT★ re-inject):不影響。新增的是一行 WHY 與安裝名單、錨點、列舉各一處,沒碰注入範本或 sentinel 邏輯,`t_reinject_preserves_outside` 不在改動路徑上。
- `lumos-cli-read`、`測試假綠形態`、`design-loop`:不影響。只加了新測試與一個 hook 檔,沒改 search 排除、還原翻紅釘或處置閘。
- `guard-kill`:不影響。沒動 guard kill 的 rc 優先序或 `--json` 輸出。
- `pitfalls-code-loop`、`reversibility-governance-ledger`(★RISK★):不影響。diff 沒碰 pitfalls 規則與逃逸帳的流程;新掛鉤也不寫帳,只寫存活事件。
- 其餘「超出上限、只列名」的節點:diff 沒有觸及它們登記的檔案行為,不逐條展開。

總結:最嚴重 severity 為 major,blocking 共 1 條(第 1 條)。

相關路徑:
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/scripts/merge-claude-settings.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/scripts/hooks/claude/bypass-ask-hook.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/docs/lumos-toolchain-knowledge/Projects/代理繞閘字樣問人_計劃.md`
- `/tmp/lumos-seat-work/code-代理繞閘字樣問人/合約圖譜-sonnet/rb.py`(第 1 條的重現)
- `/tmp/lumos-seat-work/code-代理繞閘字樣問人/合約圖譜-sonnet/p.py`(第 2 條的重現)

臨時目錄 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/合約圖譜-sonnet/` 是我建的,留給編排者在收齊後刪除。
