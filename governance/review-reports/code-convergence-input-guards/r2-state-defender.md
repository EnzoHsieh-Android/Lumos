白話結論：兩條 raw major 都不是「R1 修補新生的 major 回歸」。真正需要在本輪修的是 `_nodehome_mark_note_content` 的實際複雜度增加；parser OSError 建議順手修正，但應降為 minor 診斷錯誤。

## 1. state-F1：live index 競態

raw severity: major；raw blocking: 是  
裁決：觀察成立；「本輪新回歸」反駁；major/blocking 降為非阻擋 hardening。

- 目前確實先從 index 算 `changes/changed_paths`，稍後再以 live index 重新列檔、讀內容：[scripts/lumos](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:27677) 的 27681–27687、28492、28517–28520。兩次讀取沒有共同快照。
- 現存 counter 證明手動在 `_nodehome_route_tests` 前恢復 test index entry 時，最終 cached diff 已無 test，但 current 仍 rc0；main `cc032633` 為 rc1。[/tmp/lumos-batch-index-race-counter.json](/tmp/lumos-batch-index-race-counter.json:5)
- 同型注入在 R1 `4f0c979a` 已經 rc0，所以它不是 R1 修補造成的新回歸，而是第一版 optional-test routing 已有的缺口。[/tmp/lumos-batch-index-race-original-counter.json](/tmp/lumos-batch-index-race-original-counter.json:4)
- 但對完整 branch 相對 main 而言，這仍是新能力帶入的窄缺口，不能用「R1 已存在」說成完全不存在。
- 沒找到明文合約排除「檢查期間 index 被改」。既有合約只釘「讀 index、不信未 staged 工作樹」，沒有承諾 index 交易式不變：[scripts/test_lumos.py](/tmp/lumos-review-snapshot-encoding-preflight/scripts/test_lumos.py:47724)。

正常 Git 情境要分開：

- `git commit -a`、`--include`、pathspec partial commit 會讓 hook 使用鎖住或獨立的暫存 index；Git 同時透過 `GIT_INDEX_FILE` 告知 hook 應讀哪一份。一般外部 writer 很難重現 counter 的中途替換。[Git commit index preparation](https://github.com/git/git/blob/master/builtin/commit.c), [run_commit_hook](https://github.com/git/git/blob/master/commit.c#L1867-L1888)
- plain `git commit` 的 as-is 路徑則把真實 index 交給 hook。從 Git 原始碼可推論，另一程序仍可能在 hook 期間更新它；Git 甚至會在 pre-commit 後重讀 index。因此不能宣稱「正常 commit 絕對不可觸發」，只能說提供的 counter 沒有證明自然並行可達。[Git pre-commit](https://git-scm.com/docs/githooks#_pre_commit)

判準：這是所有 live-index 檢查共有的 TOCTOU 背景，現有契約沒有要求完整交易一致性。故不維持 major blocker；若產品要特別 harden optional-test routing，最小修法是在計算 route evidence 前後取得 index tree 身分，若不同就清空 `staged_route_tests`、沿既有路由拒收，不必重寫整個 home 機制。

翻紅判準：保留前置斷言「最終 cached diff 不含 test」，修前 rc0；修後 rc1，且訊息點名 `Systems/TestHome`「不是任何一支改動檔的家」。

本席未重新跑兩個 counter：唯讀 sandbox 在建立 wrapper 時即 `PermissionError`，尚未進 fixture。上述 rc 來自既有 JSON 與程式控制流核對；first-counter 的 wrapper 問題未當產品紅。

## 2. 兩條新增 C901

### `_nodehome_mark_note_content`

裁決：成立，是真惡化，不應 waive。

本席用相同 Ruff 規則重算：

- main `cc032633`：7
- R1 `4f0c979a`：13
- current `f678`：14

目前新增快取、候選與版本迴圈都留在 [scripts/lumos](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:27954) 內，確實增加控制流。

最小修法：把 27984–28004 的「單一 group 算 route tests＋兩版快取」抽成一支 ≤10 的 helper；原函式只保留一次呼叫。翻綠判準是 Ruff 不再對 `_nodehome_mark_note_content` 報 C901，且新 helper 也不超過 10。

### `_nodehome_evaluate`

裁決：false positive，可走精確 `lint-waive`，不要改全域指紋算法。

機械數字：

- main：52
- R1：53
- current：52

目前相對 main 沒增加。新告警只是 def 行多了 `staged_route_tests`，而 `_lint_new_key` 明確以「規則＋檔案＋命中程式片段」當身分：[scripts/lumos](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:26236)。

本席重算指紋：

- main：`5db1e104244ca032`
- current：`36c23613f0cfca05`

舊指紋已有 waiver，理由也是既有複雜度：[lint-waivers.json](/tmp/lumos-review-snapshot-encoding-preflight/.lumos/lint-waivers.json:2004)。新指紋必須另做精確 waiver；理由應寫 `52→52、只改簽名`。另需在計劃綁機械 REVISIT，因 `lint-waive` 紀錄本身沒有期限或回訪欄位。

## 3. alignment-F1：quote parser 的 OSError

raw severity: major；raw blocking: 是  
裁決：診斷錯誤成立；新安全回歸反駁；建議降為 minor、非阻擋，但最小修法值得折入。

current 把 `_quote_rows` 放在捕捉 `OSError` 的 try 內：[scripts/lumos](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:9576)。本席用合法既有 report/snapshot、只替換 parser：

- current：rc2，訊息為「`--snapshot 指的檔案讀不到: parser-side`」。
- main：用寫入 stub 防止落帳後實跑為 rc0。舊版其實吞掉 parser OSError 後繼續成功，不是 controlled 拒收。
- `cmd_quote_check` 的 parser 在 read/decode try 外，`OSError("parser-side")` 會正常逸出：[scripts/lumos](/tmp/lumos-review-snapshot-encoding-preflight/scripts/lumos:23276)。

所以 current 相對 main 是 fail-open → fail-closed 的安全改善，但把內部 parser 故障誤報成使用者檔案讀不到。現有反控制只注入 `RuntimeError`，[test_lumos.py](/tmp/lumos-review-snapshot-encoding-preflight/scripts/test_lumos.py:26027)；它證明 unknown Runtime 不被吞，沒有覆蓋 OSError 邊界。

最小修法：try 內只做 `read_bytes()` 與 UTF-8 decode；離開 try 後才呼叫 `_quote_rows`。不要擴大其他入口。

翻紅判準：新增 OSError parser shim；修前 rc2 且含「snapshot 檔案讀不到」，修後應 rc1／traceback 含 `OSError: parser-side`，成功帳逐位元不變。既有 RuntimeError 反控制繼續保留。

全程未修改 source、graph 或 Git 帳；工作樹狀態與進場時相同。