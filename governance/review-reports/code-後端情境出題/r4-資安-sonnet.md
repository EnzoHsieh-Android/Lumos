severity: clean

這一輪我沒找到攻擊者能用的洞,也沒有撤出殘骸。檢查範圍是 `b187b5e9` 的程式與快照檔名清單。

**撤出殘骸:沒有。** 查了 `scripts/lumos`、`scripts/test_lumos.py`、技能說明和圖譜筆記:
- `scripts/lumos` 裡已沒有待決問題的解析函式、正規式或對它的呼叫。只剩 `PQ_STAGES`、`_REQUIREMENT_FACETS` 與 `_pitfalls_stage`,它們不再讀計劃正文那一節。
- 圖譜筆記與技能說明統一寫成「正文那一節只是給人看的清單,工具不讀,改存開頭欄位另案」。我看了 `SKILL.md`、`reference.md`、規格閘、情境出題和 pitfalls-code-loop 這幾篇的相關行,說法互相一致。
- 筆記綁的兩支測試 `t_backend_qo_question_section_not_parsed` 和 `t_backend_qo_stage_facets_only` 都存在。我跑了 `python3.14 scripts/test_lumos.py -k backend_qo`,結果 9 passed、0 failed。

**密鑰與個資:沒有外露。**
- 我掃了這支分支新增的目錄:`governance/eval/qo-ablation-2026-10`、`mcp-lab-2026-10-12`、`governance/replay/後端工程提問與證據擴充`、`scripts/scenario_probe.py` 和 Verification 筆記。
- 掃的內容是 `/Users/` `/home/` `/private/tmp` 絕對路徑、私鑰標頭、sk-、ghp_、AKIA、帶密碼的連線字串和電子郵件,全部 0 筆。
- 修補已把兩份 `codex-rater-raw.txt` 裡的本機暫存路徑換成 `<會談暫存目錄>`。
- `compose.yaml` 和 `init.sql.txt` 只有佔位字,沒有真密碼。連接埠都綁 `127.0.0.1`。
- 全 repo 掃出的 `/Users/enzo/...` 路徑都在舊檔(例如 `governance/eval/cd_fix.py`、`lens-utilization`),不是這支分支新增的,也不在本輪範圍。

**回溯風險:沒有。**
- 我拿 `kt-springdata` 和 `kt-springhttp` 兩組新觸發詞,餵 20 萬字元的空白、重複字樣和長英數串,每次都在 0.015 秒內。
- `qo_ablation.py` 的 `_LEAK` 沒有巢狀量詞,也是線性。

**執行邊界:沒有新風險。**
- `pitfalls <計劃> --stage` 只讀使用者自己指定的本機檔。
- 非 UTF-8 的檔案會回 2 並帶「擋下:」,不會吐追蹤。
- `--stage` 值有白名單,和 `--diff` 並用會被擋。
- `scenario_probe.py` 的 subprocess 呼叫都是參數陣列,沒用 `shell=True`。

總結:最嚴重 clean;blocking 共 0 條。
