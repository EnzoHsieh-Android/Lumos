severity: clean

我沒有找到任何跟既有做法不一致的地方。

**問 1:分層與依賴方向**

`_turn_key` 放在 `scripts/hooks/claude/stop-lint-hook.py` 這支鉤子裡,位置沒問題。

- 專案裡沒有現成的處理兩家回合欄位的共用函式。我搜了 `scripts/hooks/` 全部,只有這支鉤子讀 `prompt_id` 或 `turn_id`。
- `scripts/hooks/claude/_hookshared.py` 只放標記目錄、`_mark_name`、`_claim_mark`、`_safe_path`、git 防護這幾段(`_hookshared.py:27,105,137,145,163,195`)。
- `scripts/hooks/claude/check-graph-sync.py` 另一支收工鉤子,完全不讀回合編號。它處理兩家差異的方式是 `--harness` 旗標加逐字稿讀取(`check-graph-sync.py:11,154-231,1012`),跟回合編號是兩回事。
- `_hookevent.py` 也沒有這類函式(`_hookevent.py:40-143`)。
- 這支鉤子只有一個呼叫端會用 `_turn_key`,所以不需要搬進共用模組。
- 它也沒有跨層直呼:`_on_prompt` 和 `_on_stop` 都在同一個檔案裡呼叫它。
- 引句:「+def _turn_key(payload):」

**問 2:命名與寫法**

- 函式名:`_turn_key` 跟同檔的 `_turn_start` 同一組命名。
- docstring:出處照鄰居的寫法放在括號裡,有日期,而且講明沒有實測。
- 測試命名:`t_stop_lint_hook_codex_turn_id` 跟 `t_stop_lint_hook_timeout`、`t_stop_lint_hook_registration` 同一個後綴形式(`scripts/test_lumos.py:133594,133672`)。
- 測試 docstring:有「翻紅釘」,專案裡共 781 處用到。四個檢查點的編號寫法跟 `t_stop_lint_turn_start`(`scripts/test_lumos.py:133325`)一樣。
- 筆記 PITFALL:補了 `[修法:]` 和 `[test:]`,拿掉 `[repro:]`。規範是三選一,而且鄰居也是這樣配(`docs/lumos-toolchain-knowledge/Systems/回合結束寫法檢查.md:145,149`)。
- `[closed:日期 理由]` 的寫法跟 `docs/lumos-toolchain-knowledge/Projects/Codex行為精修_計劃.md:107` 一樣。
- 新 REVISIT 是 `REVISIT:2027-02-08 …` 的日期式,符合 SKILL 的規定。
- 引句:「+def t_stop_lint_hook_codex_turn_id():」
- 引句:「+REVISIT:2027-02-08 有能跑的 Codex 模型時,在實驗專案用 codex exec 實跑一次」

**問 3:第二種做法**

沒有引入新做法。別的鉤子取 Codex 資訊的方式,是用 `--harness` 旗標(`check-graph-sync.py:1012`)或看 tool 名稱和 cwd(`dispatch-lens-hook.py:474-527`、`impact-hook.py:62`),沒有人用過別的方式取回合編號。

- 引句:「+    for k in ("prompt_id", "turn_id"):」

不對齊共 0 條,其中 major 0 條。

我只想提一點給編排者參考,不算 finding:
- 紀錄檔的鍵名仍叫 `prompt_id`,值在 Codex 下是 `turn_id`。程式註解有說明。
- 鉤子檔頭第 13 行的「防無限擋」還寫 `prompt_id`。
- 兩處都不影響行為,也沒有鄰居的做法可對照,所以不列。
