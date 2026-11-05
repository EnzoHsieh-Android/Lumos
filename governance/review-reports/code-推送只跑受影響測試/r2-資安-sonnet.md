severity: minor

**1. 主線名集合查詢失敗或逾時時只剩 main 和 master，非 main/master 命名的主線會被當成功能分支**
severity: minor
blocking: 否
標題：⚠ 推論，沒有重現
引句:「分支短名在 _note_reread_mainline_names 的集合裡(永遠含 main、master,再加主線候選指到的分支名,不看遠端名)→ true;其他 → false。」
file: `scripts/lumos:54087`（`_note_reread_mainline_names` 在 `err`、`not mls` 或逾時時回傳固定集合）、`scripts/lumos:65632`（`_push_mainlines` 的候選只含遠端 HEAD、main、master）
- 攻擊路徑四件：
  - 誰：使用者本人，照常 `git push origin HEAD:<主線名>`。
  - 從哪：一個主線不叫 main 或 master（例如 trunk、develop）的 clone，而且 `refs/remotes/<遠端>/HEAD` 沒設（例如 `git init` 加 `remote add` 建的），或 10 秒查詢逾時。
  - 送什麼：推送行的遠端 ref 為 `refs/heads/trunk`。
  - 拿到什麼：`pushed_mainline` 為 false，加上 `suite_computed` 為 true，掛鉤把全套降成 light；這個分支又沒有 CI（`ci.yml` 的 push 事件只限 main 與 tag），全套沒人跑。
- 本 repo 主線就是 main，`main` 與 `master` 寫死在集合裡，所以對本 repo 不成立。
- 這個失敗方向（查不到就當功能分支）是 `_note_reread_mainline_names` 原本的設計，這次改動是把它搬到「決定少跑全套」這個新用途上。
- 歸因：未判定。我沒有建出這個環境，沒有修前與修後的指令輸出。

**已看、無洞的項目：**
- **降級條件（①）**：掛鉤只在 `"pushed_mainline": *false` 與 `"suite_computed": *true` 兩個都 grep 到時才降。`pf_json` 為空（pitfalls 出錯或舊版不認 `--pushed-ref`）、推 main 或 master、推標籤、遠端 ref 為空，一律維持全套。檔名等外來字串在 JSON 裡被跳脫成 `\"`，湊不出 `"pushed_mainline"` 這個字樣。
- **主線判定（③）**：`_pitfalls_pushed_mainline` 對非 `refs/heads/` 與 `refs/heads/` 空名回 true，也就是保守倒向全套。刪除遠端 ref 的推送行在迴圈開頭就跳過。
- **混推（③）**：只要有一個 ref 是 full，整次推送就照全套。`_SUITE_BRANCH_DOWN` 只在 `_suite_mode` 為 light 時才印提示。
- **降級後的子集（③）**：降級後仍跑文件子集，關鍵字子集沿用原本 light 的取法。
- **修補合併（③）**：`_down` 合併成一段後，兩條降級路徑的行為沒變。`computed` 每條回傳都帶；git 失敗時是 `computed=False`，掛鉤改走全套。
- **讀寫與執行越界（②）**：新增的 `_rref` 只作為 argv 單一參數傳給 `pitfalls`，沒有 shell 插值、沒有路徑寫入。`_pf_extra` 用陣列展開，也沒有注入面。
- **提示文字（①③）**：改寫後的提示句只教人等 PR 頭提交的 `lumos ci-wait` 判定為綠再合併，沒有教人繞過檢查。拿掉「嫌久可 --no-verify」反而收斂了繞過入口。
- **密鑰與下載來源（②）**：改動裡沒有新增密鑰或信箱，沒有下載來源的變動。

**看過的檔：**
- `scripts/hooks/pre-push`、`scripts/lumos`（`_test_suite_for_range`、`_pitfalls_pushed_mainline`、`_pitfall_diff_collect`、`_pitfall_diff_mode`、`cmd_pitfalls`、argparse 與 dispatch；另讀 `_note_reread_mainline_names`、`_push_mainlines`、`_diff_range_ends`）。
- `.github/workflows/ci.yml` 的 `on:` 段。
- 完整快照中的其他檔只確認了檔名，沒有逐行審：`.lumos/lint-waivers.json`、`CLAUDE.md`、`README.md`、`README.en.md`、`docs/.canary-log.jsonl`、`docs/.escape-log.jsonl`、`docs/.kill-log.jsonl`、三篇 Projects 計劃筆記、`Systems/bound-tests-gate.md`、`Systems/pitfalls-code-loop.md`、`governance/anchor-baseline.json`、`scripts/test_lumos.py`、`skills/lumos-project-notes/commands/08-自動跑的.md`。
- 共用規則檔 `r2-common-push.md`。
