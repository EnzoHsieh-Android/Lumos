severity: minor

我站在攻擊者角度逐類看過,沒找到能讓測試少跑而不被發現的洞,也沒有注入面。只有一條需要本機配合的低風險疑慮(標推論)。

## 逐類結論

**1. 不可信輸入流到危險操作(耗時表與 run 檔):已看,無可利用的洞。**
- 耗時表鍵只用在 `table.get(nm, med)` 查詢和 `sorted()`。它不拼路徑、不進 shell、不被 `eval`,也不印出來。`json.loads` 是純資料解析。
- 一個 PR 改耗時表,最多讓分片不平均。
  - 表格式不對:`_load_durations_table` 丟 `ValueError`,每一份都 rc2,屬於失敗關閉,不會假綠。
  - 權重是 `inf` 或 NaN:被 `isfinite` 擋掉。
  - 權重極大:只會讓某一份變慢,屬於 DoS,不報。
- 測試清單來自 `globals()` 的 `t_` 函式名,分片只對這份名單切。`_shard_by_duration` 把名單裡每一支都丟進恰好一個桶,表裡多餘的鍵被忽略。所以表的內容不可能讓某支測試落到所有分片之外。
- 同名函式只會重複跑,不會漏跑。
- 分片失敗時退回名字輪流分的路徑已被移除:表壞了每一份都擋,不會混用兩種分法。
- 表中位數與權重下限的算法在極端值下仍是確定的。

**2. CI(`concurrency` 與每份耗時那行 shell):已看,無。**
- 群組鍵是 `ci-${{ github.event_name }}-${{ github.event.pull_request.number || github.sha }}`。
  - PR 編號由平台指派,fork 作者無法挑別人的編號,所以取消不到別人的 CI。
  - 群組鍵含事件名,PR 的群組碰不到 push 的群組。
  - main 以提交編號各自一組且不取消,攻擊者無法用新提交取代主線 CI。
  - fork 的 `pull_request` 事件只作用在 PR 自己的群組。
- 每份耗時那行 shell 的變數有 `$i`、`$SHARD_TOTAL`、`$s`、`$rc`。
  - `$i` 來自 `MY_SHARDS`,是 workflow 矩陣的靜態值,PR 作者不可控。
  - 沒有 `github.head_ref`、PR 標題或分支名插值進 `run:`。
  - 算術展開只用 `date +%s`,無注入面。
- `exit $rc` 保留了 python 的退出碼,耗時行不會把紅吞成綠。

**3. 執行邊界:**
- refresh 刪檔:glob 範圍是 `Path(root)/".lumos"` 底下的 `test-durations-run*.json`,不會刪到別處。
  - `unlink` 對符號連結只刪連結本身,不跟隨。
  - `.lumos/` 被 git 忽略,PR 帶不進內容。
- 寫耗時表:
  - 寫到 `.lumos-tmp` 再 `os.replace`,是原子寫法。
  - 最終檔若是符號連結,`replace` 會取代連結,不會寫穿。
- 耗時表列進簿記檔清單:
  - 比對是完整路徑字串相等,夾帶不了別的檔。
  - 表是純資料(JSON),不會被執行。
  - 它只影響分片,所以「只改它的提交不讓審查留痕失效」不會讓程式改動繞過審查。
- 只改耗時表的推送判成 docs 子集:
  - 程式沒變,不需要全套。
  - 任何混了程式改動的提交仍走全套。

**4. 繞過面:已看,無。**
- 表壞、缺檔、空片都是 rc1 或 rc2 的失敗關閉。
- 沒表時走舊的輪流分。
- 跳過的測試不寫進耗時,不影響分片聯集。
- 耗時表只改「誰跑哪一片」,不改「跑哪些」。

## Findings

下面這條是推論。它需要有人在不可信的分支上本機跑 `refresh`,且前提條件是攻擊者能把符號連結提交進分支。

引句:「tmp = table_path.with_suffix(table_path.suffix + ".lumos-tmp")」
severity: minor
blocking: 否
- 誰:能提交分支或 PR 的人。他讓受害維護者在 checkout 該分支後跑 `lumos test-durations refresh`。
- 從哪:`cmd_test_durations_refresh` 的寫入段。
- 送什麼:提交一個符號連結 `governance/test-durations.json.lumos-tmp`,指向維護者機器上的某個檔,例如 shell 設定檔。
- 拿到什麼:`tmp.write_text(...)` 會跟隨連結,把目標檔覆寫成 JSON 內容。
- 成立條件:`.lumos-tmp` 暫存名可預測,沒有用 `O_NOFOLLOW`。
- 同族:file: `scripts/test_lumos.py` 裡既有的失敗快取寫法(`_cache.with_suffix(... ".lumos-tmp")`)是同一形狀,這次又複製了一處。
- ⚠ 它只有在受害者主動跑 refresh,且該分支帶了惡意連結時才成立。覆寫內容也不受攻擊者控制(只是耗時表 JSON)。
- 應該是:寫之前先 `tmp.unlink(missing_ok=True)`,或用 `tempfile.mkstemp` 在同目錄建暫存檔。

## 固定席節點逐條判

- 測試假綠形態(★INVARIANT★ 還原翻紅釘要配前置斷言):不影響。新測試 `t_runner_shard_by_duration` 與 `t_test_durations_refresh` 都有 `★前置★` 斷言。這條不涉及利用面。
- lumos-cli-lifecycle(re-inject 的 sentinel 外內容):不影響。本次沒碰 re-inject。
- lumos-cli-read(search 預設排除 superseded):不影響。本次沒碰 search。
- guard-kill 兩條(rc 優先序、`--json` 純淨):不影響。`test-durations refresh` 沒有 `--json`,也沒碰 guard kill。
- design-loop(處置閘第五步):不影響。
- pitfalls-code-loop、loop-convergence-recording、reversibility-governance-ledger(RISK 節點):
  - 簿記清單多一項耗時表。
  - 這份清單同時是 pitfalls 掃描排除和代碼審留痕失效豁免兩處的單一來源。
  - 只有完整路徑相等的檔受影響,資料檔不含可執行內容,所以不影響。
- 超出上限只列名的節點(bound-tests-gate 等):
  - bound-tests-gate 與「推送判成 docs 子集」相關,上面第 3 點已看過,無洞。
  - 其餘與資安面無關。

總結:最嚴重等級 minor,blocking 共 0 條。
