severity: minor

三問答案先講:①兩項原問題都修好了。②沒有帶進新的錯。③同形狀沒有漏改的,但測試有一個缺口(見 F1)。

**① 原問題修好了**
- 在 `/Users/enzo/orca/workspaces/lumos-toolchain/android-write-check` 跑 `python3.14 scripts/test_lumos.py -k lint_new_cli`,29 條全過。
- 其中 ③ 造了 25 條新增告警:預設印 20 條、其餘印條數,提示改成 `lumos lint-new --diff … --all`,不再出現 `code-loop check`。
- 加 `--all` 後 25 條全印,rc 仍是 1,治理帳筆數前後相同。
- `--all` 只被 `cmd_lint_new` 和 `_lint_new_cli_items` 讀,不經過任何會寫帳的路徑,所以照樣唯讀。
- 我沒有另外在臨時 repo 手動重跑一次,靠的是上面這個測試加讀程式。

**② 沒有新的錯**
- `--all` 沒給 `--diff`:先被「沒給範圍」的檢查擋下,回 rc 2,不受影響。
- `--all` 配 `--repo`:兩個旗標各自獨立,沒有互相干擾。
- `skipped` 的讀側,我搜了 `bt["status"]`、`last_bound`、`"skipped"`:
  - `scripts/lumos:71658`、`71681` 只比對 `red` 和 `unfilterable`。
  - `scripts/lumos:72008` 的 `startswith("skipped")` 在 `_codeloop_marker_skipped` 裡。這支函式只在 `_codeloop_guard_verdict` 的非 `mech_only` 路徑被呼叫(`scripts/lumos:71972`)。
  - 那條路徑一開頭先把 `last_bound` 清掉(`scripts/lumos:71589`)。`mech_only` 在 `scripts/lumos:71745` 就提早返回,走不到那裡。
  - 所以 `LUMOS_SKIP_CODE_LOOP` 的疊用拒絕判斷不會被 `mech_only` 殘留的 `skipped` 影響,判定沒變。
  - `code-loop pass` 的通過路徑只用 `v.get("blocked")` 和 `blocks`,不讀 `bound_tests`。

**③ 同形狀**
- `scripts/lumos` 裡其他寫著「全部看」的截斷提示,指的都是唯讀指令,例如 `scripts/lumos:72459` 的 `android-e2e check`。
- 仍指向 `code-loop check` 的,只剩 `scripts/lumos:72511` 這一處,它本來就在 `code-loop` 自己的擋下訊息裡,不算同形狀。

**F1 `skipped` 這項修補沒有測試守著**

severity: minor
blocking: 否

引句:「bt = ({"status": "skipped", "reason": "只跑新增告警與表態兩道,合約測試沒跑"} if mech_only else」

- 在 `scripts/test_lumos.py` 搜 `last_bound`、`not-run`、`合約測試沒跑`,沒有任何斷言檢查只跑兩道時的合約測試狀態。
- 合理的改壞:把 `"skipped"` 改回 `"not-run"`,或改成 `"green"`。目前可見的行為都不變,上面那 29 條測試照綠。
- 真正會咬人的只有一種情境:日後有人讓 `mech_only` 路徑的後續碼讀 `last_bound`,把 `"not-run"` 當成「不以 skipped 開頭」。這是潛在風險,目前沒有具體失敗場景,所以只標 minor。
- 建議補一條小測試:`mech_only=True` 後斷言 `_codeloop_guard_verdict.last_bound["status"] == "skipped"`。

**F2 `--all` 在 warn 路徑沒有測試**

severity: minor
blocking: 否

引句:「_lint_new_cli_items(lv, sys.stdout, show_all)」

- 把 warn 路徑改成不傳 `show_all`,測試仍全綠。③ 只用 blocked 路徑驗證了 `--all`。
- 實際影響很小:`gate=warn` 且超過 20 條時,提示會叫人加 `--all`,而 `--all` 其實不生效。這個場景能具體重現,所以保留為 minor。

總結:最嚴重是 minor,會擋 0 條。
