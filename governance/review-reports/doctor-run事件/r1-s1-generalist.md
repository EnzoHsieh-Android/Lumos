# doctor-run事件 r1 — s1 generalist 對抗審計

審對象:`/tmp/doctor-run事件-r1.md`
審法:讀真代碼(`scripts/lumos` run_doctor/`_append_governance_log`/`cmd_gov`/`_render_gov_stats`/`_KNOWN_GATES`)、`scripts/test_lumos.py` 既有測試、`.github/workflows/ci.yml`、`scripts/hooks/pre-push`、`_BOOKKEEPING_FILES`/code-loop 簿記豁免邏輯,逐條核對 spec 的宣稱是否與現況機制相容。

## Blocker

### B1 — 「非 --full 隱藏 doctor-run」不成立:唯一現有摺疊機制的判準是 `kind == "warned"`,新事件的 `kind` 卻是 `"ran"`

引句:「`gov` 不印 `doctor-run`;`gov --full` 印」

現況機制(`scripts/lumos:3040`)裡,`gov` 預設(非 `--full`)畫面唯一會把某一列「藏起來/摺起來」的路徑是 `_is_advisory`:

```python
def _is_advisory(r):
    return (not r["hard"]) and r["kind"] == "warned" and not r.get("token") and not r["detail"]
```

只有命中的列才會被摺進 `agg` 群組(仍會印一行摘要,不是真的「不印」);沒命中的列一律落到 `else` 分支最後的 `print(...)`(`scripts/lumos:3082` 附近),逐列印出。spec 給的事件字面值是 `"kind": "ran"`(見設計節「加 `{"gate": "doctor-run", "kind": "ran", ...}`」),`"ran" != "warned"`,`_is_advisory` 恆回 False——doctor-run 列**不會**被摺,更不會被藏,會在預設 `gov` 畫面逐列印出。

而 pre-push hook(`scripts/hooks/pre-push:148`)每次 push 都跑 `doctor --ci`,dedup 鍵含 commit(`scripts/lumos` 約 3013 行 `k = (r["commit"], frozenset(r["nodes"]), r["gate"], r["kind"], r.get("token", ""))`)——正常開發流程裡每次 push 幾乎都是新 commit,所以「同 commit 折一筆」在跨 push 場景幾乎不生效,doctor-run 會**逐 push 累積、逐列印在預設 `gov` 畫面**,正好是設計節自己想避免的「否則 500+ 筆灌版面」。

「設計」節列出的四個改動(①`run_doctor` 加事件 ②`gov` 隱藏 ③`_KNOWN_GATES` 加值 ④dedup 鍵含 commit)裡,沒有一項真的改到 `cmd_gov` 的呈現邏輯本身——②只是宣稱結果,沒給機制;唯一可能借用的既有機制(`_is_advisory`)因 `kind` 選字不符而用不上。按 spec 字面實作,測試 3(`t_gov_hides_run_marker_unless_full`)會直接翻紅,且是設計明文要求的收斂判準之一。這是自我矛盾/不可實作的宣稱,不是次要枝節。

## Major

### M1 — 事件字典用鍵 `"detail"`,但 `cmd_gov` 讀 `.governance-log.jsonl` 的欄位是 `d.get("note", "")`,不是 `"detail"`——照字面實作,note 文字會靜默消失

引句:「`"detail": "issues=<n> gates=<本次有事件的 check-* gate 數>"`」

`_append_governance_log`(`scripts/lumos:421`)是把 gov_events 的 dict 原樣 `**e` 展開寫進 jsonl,不做欄位改名;`cmd_gov` 讀這個檔案的 mapper 在 `scripts/lumos:2995`:

```python
"nodes": [stem(x) for x in d.get("nodes", [])], "detail": d.get("note", "")})
```

即讀側只認 `"note"` 這個鍵映成呈現用的 `detail`。現存唯一一個真的帶人讀文字的 `_append_governance_log` 呼叫點(`anchor approve`,`scripts/lumos:10152`)寫的正是 `"note": note`,不是 `"detail"`。spec 設計節給的事件字面值卻寫 `"detail": "issues=..."` —— 若照字面實作,寫進帳本的 JSON 會有 `"detail"` 鍵而沒有 `"note"` 鍵,`cmd_gov` 讀出來 `d.get("note", "")` 一律拿到空字串,`gov --full` 畫面會印出空白 detail,spec 想保留給棘輪讀的 `issues=<n> gates=<n>` 數字會整個消失於 `gov` 呈現層(帳本原始行本身雖然還留著 `"detail"` 鍵,但 `cmd_gov` 讀不到,等於「有記但顯示不出來」)。這條屬於「照字面走,實作行為出錯」,對應 major 判準。

## 其餘核對過、沒發現問題的點(供交叉確認,非新發現)

- `_KNOWN_GATES` 漂移測試 `t_gov_stats_gate_drift`(`scripts/test_lumos.py:3047`)只掃字面值 `"gate": "..."`;spec 的寫法是字面值,不會被「動態閘名恰一處」的釘子擋下,加進 `_KNOWN_GATES` 即可過。
- `run_doctor` 只有一個呼叫點(`scripts/lumos:14806`,CLI 入口),不會有第二處內部復用意外觸發。
- `issues` 變數在 `_append_governance_log` 呼叫點(`scripts/lumos:1328` 附近)之前已累積完成,`issues=<n>` 取值沒有 scope 問題。
- 既有測試「gov-log: 純 doctor 不寫」(`scripts/test_lumos.py:2933`)與「gov-log: --ci 寫入 governance-log」(`scripts/test_lumos.py:2929`)在只新增一筆固定事件、不動 `if ci:` 分支結構的前提下不會被破壞。
- CI workflow(`.github/workflows/ci.yml`)裡 `doctor --ci` 之後沒有任何 git-dirty-tree 檢查步驟,新事件寫進 CI runner 的 checkout 但從不 commit/push 回去,不會讓 CI 步驟因此變紅。
- `.governance-log.jsonl` 已在 `_BOOKKEEPING_FILES` 白名單(`scripts/lumos:10299`)內,code-loop pass 的簿記豁免邏輯(`scripts/lumos:14115` 一帶)本來就把它算進「純簿記」,新增一種恆寫的事件不改變這條豁免的判準(仍是「diff 出的檔案是否都在白名單」),沒有新的交互風險。
- `gov --stats` 的「未出現清單」邏輯(`absent = [g for g in _KNOWN_GATES if g not in agg]`,`scripts/lumos:2947`)不會被污染——doctor-run 幾乎每次都會出現在 `agg`,只是多一個有列的 gate,不影響其它 gate 的未出現判定。

## 嚴重度計數

blocker: 1, major: 1, minor: 0
