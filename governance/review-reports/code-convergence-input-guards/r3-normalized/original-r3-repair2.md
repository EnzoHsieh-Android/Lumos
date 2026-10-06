severity: major

固定 HEAD 已確認為 `95735eff7f3e17c930d43eecde5dd9d7c4fe9eff`。本席找到 1 個 major、1 個 minor；未修改 repo、git 或帳務。

## Findings

repair2-F1
severity: major
blocking: 是

引句:「取這個編號最新一筆人裁紀錄 D(治理帳檔內順序),再取 D 之後最新一筆 recorded 或 skipped 事件 E:」

- 觀察：`_cap_retro_status` 找到最新人裁後，只要其後最後一筆事件的 `kind` 是 `skipped` 就直接放行，沒有確認該事件綁的是同一筆人裁。另一方面，`cmd_loop_retro` 是先讀最新人裁、稍後才追加 skipped；兩個程序交錯時，舊人裁啟動的 skip 可以落在新人裁之後。
- 佐證：`scripts/lumos:13553` 直接接受 skipped；讀人裁與寫 skip 分別在 `scripts/lumos:13867`、`scripts/lumos:13946`，中間沒有精確人裁識別或原子檢查。
- 判準：程式自己的提示宣告「之後再記人裁要重新回顧或跳過」，因此 recorded/skipped 必須綁定確切的人裁事件，而不只是帳中位置或 rounds。只比 rounds 也不足，因為重記決策可能沿用相同 rounds。
- 具體輸入路徑：`D1(rounds=[r1]) → D2(rounds=[r1,r2]) → skipped(rounds=[r1])`；預期 D2 未被跳過，實際回傳 `state=skipped`。處置閘及新輪記錄呼叫者會把這個狀態當成通過。
- 最小實驗，cwd=`/tmp/lumos-future-repair-regression-research`，實際載入 HEAD 的 `scripts/lumos`，未落盤：

```sh
python3.14 -c 'import runpy; from pathlib import Path; m=runpy.run_path("scripts/lumos",run_name="repair2_review"); es=[{"gate":"loop-retro","kind":"cap-decision","loop":"code-x","decision":"extra-round","rounds":["r1"],"tier":"standard","cap":1},{"gate":"loop-retro","kind":"cap-decision","loop":"code-x","decision":"extra-round","rounds":["r1","r2"],"tier":"standard","cap":2},{"gate":"loop-retro","kind":"skipped","loop":"code-x","rounds":["r1"]}]; o=m["_cap_retro_status"](None,"code-x",Path("/nonexistent-review-root"),events=es,rows=[],rows_err=None,dir_exists=True); print({"decision_rounds":o["decision"]["rounds"],"state":o["state"],"applies":o["applies"]}); assert o["state"] != "skipped", "舊 rounds 的 skipped 不得替最新人裁放行"'
```

原輸出，rc=1：

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
AssertionError: 舊 rounds 的 skipped 不得替最新人裁放行
{'decision_rounds': ['r1', 'r2'], 'state': 'skipped', 'applies': True}
```

- 修正方向：讓 cap-decision 產生不可混淆的識別，recorded/skipped 攜帶並核對該識別；寫入前須在同一鎖或同一原子流程內重新確認決策未變。不能只補 rounds 相等檢查。

repair2-F2
severity: minor
blocking: 否

引句:「要繼續記新一輪的出口:」

- 觀察：審查帳損壞時，處置閘一律把 `loop retro --skip` 印成「繼續記新一輪的出口」；但最新人裁若是 `accept-risk`，`_cap_retro_record_block` 明確判定 skip 解不了阻擋，必須改記 `extra-round`。
- 佐證：錯誤提示位於 `scripts/lumos:13748`；同一片段的記錄擋點會拒絕 accept-risk，兩個使用者指引互相矛盾。
- 判準：復原指令必須在所描述狀態下可達到承諾結果；若 accept-risk 不能藉 skip 開新輪，就不得稱其為出口。
- 具體輸入路徑：`rows_err=審查帳壞`、最新決策 `accept-risk`、回顧狀態 `skipped`。
- 最小實驗以同一份 HEAD 原始碼注入上述狀態，未落盤。原輸出：

```text
disposal {'return': True, 'stdout': '[disposal] 跑滿回顧: ✗ — 審查帳壞;這個迴圈有人裁紀錄,帳壞了判不了,先不放行\n    對照 git 上一版找出壞列:git diff HEAD -- docs/.canary-log.jsonl(要繼續記新一輪的出口:lumos loop retro code-x --skip --note "<理由>")\n⛔ DISPOSAL GATE FAIL (code-x: 跑滿回顧)\n'}
record-block ('cap-ledger-bad', ['擋下:code-x 有人裁紀錄,但審查帳壞——判不了這一列是不是人裁之後的新一輪,所以先不記。', '  帳壞在哪:上面那句;對照 git 上一版找出壞列(git diff HEAD -- docs/.canary-log.jsonl)。', '  出口:修好審查帳再記;或人裁改記破例再開一輪(lumos loop cap-decision code-x --decision extra-round --note "<理由>")再決定寫回顧或跳過——最新人裁是接受風險時,跳過回顧解不了這個擋下'])
```

- 修正方向：提示依最新 decision 分流；accept-risk 應沿用記錄擋點的「改記 extra-round」出口，只有 extra-round 才建議 skip。

## 三問

1. 修復了嗎：未能給正向修復結論。所選修補候選是「回顧事件只對最新人裁有效」；函式層最小實驗已翻紅，呼叫者又會把錯誤的 skipped 當成通過，因此判為未修復。修前版本沒有這組新增函式，不能拼成兩版修復證據。
2. 保留了嗎：一項保留候選成立。既有 `_kill_add_warn` 在配方判定為 `ok` 時仍保持 `return=None`、stdout/stderr 皆空；呼叫者 `scripts/lumos:16488` 仍執行既有提醒，新增綁定提醒是下一個獨立呼叫。相同輸入、Python 3.14、相同 cwd，實際載入修前 `f678762...` 與修後 HEAD，原輸出：

```text
before {'return': None, 'stdout': '', 'stderr': ''}
after {'return': None, 'stdout': '', 'stderr': ''}
```

其餘保留路徑未跑，不外推為全輪無回歸。

3. 新發現：repair2-F1 是可實跑重現的治理閘誤放行；repair2-F2 是可實跑重現的無效復原指引。

## 固定合約逐條

- design-loop `.md` 計劃與第五步綁定：不影響；指定 hunk 新增第八步及提示，未改第五步的迴圈分類或 `.md` 判準。未實跑合約測試。
- search 排除 superseded、不排 stale：不影響；指定 hunk 未觸及 search 分流。
- bound-tests gate：不影響；未改 impact 固定席、run_cmd 或 blocked 判定。
- guard-kill rc 優先序：不影響；新增內容位於 kill-add/doctor 提醒，沒有改 guard-kill 執行結果聚合。
- guard-kill JSON 純度：不影響；新增提醒寫 stderr 且屬 kill-add，不在 guard-kill `--json` 成功路徑。
- LICENSE/COPYING/NOTICE 不得進 vendored whitelist：不影響；沒有白名單或 deinit 刪除變更。
- vendored 檔 SPDX：不影響；沒有新增被複製檔案或修改檔頭集合。
- 假綠測試需前置斷言：指定直接片段沒有測試 hunk，故未見新增破壞；是否由其他席覆蓋及是否具殺傷力未判定。

`r3-pitfalls.json` 是注意力 manifest；落在本席指定新增行的 claim 為 0。未據此宣稱 lint 無警告，也未跑父席負責的 lint-new。圖譜鏡頭按手動固定附檔使用，不宣稱 hook 成功。

## 已讀材料與界線

- `repair-2.patch`：1132 行
- `r3-scope-binding.txt`：15 行
- `r3-graph-lens.txt`：57 個邏輯行，末行無換行
- `r3-pitfalls.json`：198 行
- `r3-test-layers.txt`：0 行，空檔
- `/Users/enzo/.agents/skills/python-idioms/SKILL.md`：233 行
- 指定必讀合計：1635 行
- repo 規則：`AGENTS.md` 97 行；依其指路完整讀 `CLAUDE.md` 101 行
- 額外定點程式上下文：`scripts/lumos:9038` 起 23 行、`:16482` 起 11 行、`:24763` 起 10 行；合計 44 行
- 未讀：其他席、前輪報告、完整巨型 CLI、其他來源與測試檔
- 未跑：全套、合約測試、lint-new；唯讀限制下未建立 temp fixture
- 最高級：major
- blocking 數：1
- 三問未判定範圍：除上述一條兩版保留案例外，其他修復與保留路徑均未取得同案例兩版實跑證據；空白 test-layers、圖譜末行所述外部碼表補選中止，以及其他席負責的完整來源/控制覆蓋均不納入本席結論。