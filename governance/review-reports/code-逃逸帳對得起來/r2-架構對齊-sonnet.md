severity: clean

已看,無:第 1 輪架構席四點都照做,而且 r2 新增的修正也都沿用既有寫法,沒有另開第二種做法或跨層直呼。

- 第一點(掃帳只寫一份):`_review_loop_ids` 改成直接回傳 `_escape_review_rows_by_loop(env)` 的 key 集合,不再自己重讀一次 `.canary-log.jsonl`,和 `_escape_stats` 共用同一支掃帳函式。file: `scripts/lumos:9535`(`return set(_escape_review_rows_by_loop(env))`)、`scripts/lumos:9897`(`by_loop = _escape_review_rows_by_loop(env)`)。
- 第二點(計劃欄位走 env.notes):`_escape_plan_scopes` 從自己 `split_frontmatter`/`parse_frontmatter` 讀檔改成 `env.notes.get(rel)` 取 `n.fields.get("tags")`,跟全檔其他讀計劃欄位的寫法一致。file: `scripts/lumos:9833`(`n = env.notes.get(rel) if rel else None`),對照既有慣例 `scripts/lumos:3083`、`scripts/lumos:5798`、`scripts/lumos:10655` 也都是 `env.notes.get(...)`。
- 第三點(`--by` 改名):argparse dest 保留 `esc_by`(內部變數不動、只換旗標字面與提示文字),`--withdrawn-by` 在 `scripts/lumos`、`skills/lumos-code-loop/SKILL.md`、`skills/lumos-code-loop/reference.md`、`skills/lumos-design-loop/SKILL.md`、`skills/lumos-design-loop/reference.md`、`skills/lumos-project-notes/commands/06-代碼審與推送.md`、計劃筆記與 Systems 筆記同步改完,沒有漏改的地方留 `--by`。file: `scripts/lumos:9689`(`le.add_argument("--withdrawn-by", dest="esc_by", ...)`)。
- 第四點(測試夾具命名):`_esc_fx` 全檔改名 `_mk_escape_fixture`,`scripts/test_lumos.py` 裡逐處呼叫點都同步改了,沒有殘留舊名或兩個名字並存。file: `scripts/test_lumos.py:33013`(`def _mk_escape_fixture(...)`)。

r2 新增的其餘修正(token 重複擋撤回、`--missing-defect-ref` 與 `--sha`/`--defect-ref` 互斥、`_escape_evidence_keys` 拆成 sha/defect_ref 各自比對、`_plan_for_loop` 擋路徑字元)都沿用檔案裡既有的錯誤處理慣例(`擋下:` + `return 2`、`_esc_clean` 清洗輸出),沒看到另立門派或直接跨層呼叫底層 I/O 的寫法:

引句:「if any(ch in lid for ch in ("/", "\\", "..")) or not lid.strip():」

這一行的寫法跟同檔案 `scripts/lumos:619` 既有的 `if any(ch in str(loop_id) for ch in ("/", "\\", "..")):`(golden 目錄防路徑逃逸)是同一個慣用寫法,不是新發明的做法。file: `scripts/lumos:619`、`scripts/lumos:9467`。

`loop_kind` 欄位的寫入端(`scripts/lumos:9788` `rec["loop_kind"] = _escape_loop_kind(...)`)與讀取端(`scripts/lumos:9937` `r.get("loop_kind")`)欄位名與寫法一致,不是各寫各的。
