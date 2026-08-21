# S2 軟提醒棘輪 v2 — 對抗審計(ratchet: 20-run 連續判準)

審對象:`/tmp/檢核收緊五件-r2.md` S2 節(行 58-66)+ 相關退場條件(行 90)、測試(行 98)、未決(行 109)。
對照真碼:`scripts/lumos`(`_append_governance_log` 421-441、`run_doctor` 449 起各 gate 寫帳點、`_KNOWN_GATES`/`_STATS_NODE_SEMANTICS` 2890-2906、`_codeloop_gov_log` 14020-14038)+ 真倉庫實帳 `docs/.governance-log.jsonl`(20540 行、526 個 distinct commit,現況 gate 分布 check-s 18583 / check-e1 1732 / anchor-approve 146 / code-loop 79)。

---

## Finding 1 — blocker:鍵定義「節點相對路徑,非 stem」在現有帳本結構下不可實作(碰撞問題被搬回原點)

引句：「鍵=(gate, **節點相對路徑**,非 stem;r1 s2-F2)。」

**錯在哪**:文件宣稱 r1 s2-F2 已把鍵從 stem 改成「節點相對路徑」以避免同 stem 碰撞。但實際檢查 doctor 對七道棘輪輸入閘(check-e1/e2/e3/j/k/r/s)的**每一個**寫帳點,全部寫的是 `.stem`,沒有任何一處寫 `rel`(相對路徑):

- check-r:`scripts/lumos:785,789,792`(`"nodes": [nnote.stem]`)
- check-s:`scripts/lumos:819,825`(`"nodes": [n.stem]`)
- check-e1:`scripts/lumos:866`
- check-e2:`scripts/lumos:948`(`notes[arel].stem`)
- check-e3:`scripts/lumos:989`
- check-k:`scripts/lumos:1030`
- check-j:`scripts/lumos:1307-1308`(`n_.stem`)、`scripts/lumos:2477`(`note.stem`,`check_regen_provenance` 內)

即帳本(`docs/.governance-log.jsonl`)物理上**從未含相對路徑**,只含 stem(小寫化再經 `cmd_gov` 的 `stem()` mapper 二次正規化,`scripts/lumos:2965-2967,2988`)。ratchet 要「用路徑當鍵」,唯一路徑是讀帳後用 `by_stem` 反查回 rel——但 `by_stem`(`scripts/lumos:236-239`)本身是 `defaultdict(list)`,多值代表**同 stem、不同資料夾的碰撞是系統已知會真實發生的情形**(碰撞偵測見 `collisions = {s: rs for s, rs in by_stem.items() if len(rs) > 1}`,`scripts/lumos:478`)。一旦真的撞到,反查得到 ≥2 個候選 rel,無法把某一筆歷史帳目唯一歸還給哪個節點——r1 s2-F2 想解決的「同 stem 不同資料夾互撞」問題,在寫入端早就已經把資訊丟了,讀出端換鍵定義救不回來。

**正確規則**:要嘛承認鍵只能是 stem(碰撞風險留在文件裡明講、不宣稱已解),要嘛在**寫入端**(doctor 各 gate 的 `gov_events.append`)把 `nodes` 一併改成 rel——這是七個既有 gate 寫帳點都要動的變更,不是 ratchet 讀帳邏輯能片面決定的,文件完全沒提到要動這批既有寫帳呼叫。

---

## Finding 2 — blocker:「同 commit 視為一次 run」未排除非 doctor 來源事件,literal 定義下棘輪永久失能;文件自身的上線基線主張在此定義下不成立(重算=0 組,非文件所稱 5 組)

引句：「**執行單位=「一次 --ci run」**:同 commit 的所有事件視為一次 run;run 依首筆 ts 排序。」

**錯在哪**:`.governance-log.jsonl` 不是只有 doctor --ci 一種寫者。`_append_governance_log` 自己的 docstring 講明「寫者=doctor --ci + anchor approve」(`scripts/lumos:422`),另外 `code-loop pass/skip` 走獨立的 `_codeloop_gov_log`(`scripts/lumos:14020-14038`)也寫進同一份帳、也帶 `commit` 欄(`"commit": commit_short`,`head_sha[:7]`)。這些事件(`anchor-approve` kind=`approved`、`code-loop` kind=`passed`/`skipped`)雖然被 `hard=false ∧ kind=warned` 過濾掉、不會**產生**鍵,但它們的 `commit` 值一樣會被「同 commit 視為一次 run」規則拿去**分組出一個 run**——這個 run 對所有鍵而言天生「不出現」。

實測驗證(對真倉庫 `docs/.governance-log.jsonl`,526 個 distinct commit):

```
phantom (無任何 doctor 閘事件的 commit) 數: 98 / 526 (≈18.6%)
```

用文件字面規則(commit 全部算 run,不篩 gate)重算「check-e1 是否連續出現在最近 20 次 run」:

```
=== check-e1, 版本 A(字面:所有 commit 都算 run)===
keys present in ALL of last 20 runs: []          ← 一個都沒有
```

用隱含「run 需含至少一筆 doctor 閘事件」的合理定義重算:

```
=== check-e1, 版本 B(限定:僅含 doctor 閘事件的 commit 才算 run)===
keys present in ALL of last 20 runs:
  ['guard-kill', 'slim-get-一行安裝', 'slim-install-安裝器',
   'slim-uninstall-一行卸載', '測試假綠形態']
```

版本 B 的「5 組」數字才對得上文件行 66 的宣稱,但即使如此該行文字「guard-kill + 4 個 slim 節點的死背書」本身也算錯——實際是 3 個 `slim-` 節點(`slim-get-一行安裝`/`slim-install-安裝器`/`slim-uninstall-一行卸載`)加 1 個非 slim 節點(`測試假綠形態`),不是「4 個 slim 節點」。

**正確規則**:「一次 run」的定義必須明講「只計入含至少一筆本棘輪關心之 gate(check-e1/e2/e3/j/k/r/s)事件的 commit」,否則字面規則下只要 push 節奏裡持續穿插 `anchor approve` 或 `code-loop pass/skip`(這在正常工作流裡是常態——code-loop pass 本身就綁在每次 tier=high push 前),20-run 窗口就會永遠混進 phantom run,任何鍵都無法連續出現滿 20 次——棘輪等於永久不會升級任何東西,與 S2 的立案目的(把被無視 ≥20 次的軟提醒硬化)直接矛盾。這不是邊角案例:phantom run 占真實歷史 commit 的近兩成。

---

## Finding 3 — minor:ack `<gate>@<YYYY-MM-DD>` 的 30 天到期沒有指定用哪個時鐘/日期基準,延續既有已知的 tz 混用類問題而未處理

引句：「元素 `<gate>@<YYYY-MM-DD>`;自該日 30 天內該鍵不升級,過期恢復;append 時寫 `gate: ratchet-ack, kind: acked`。」

**錯在哪**:帳本裡的 `ts` 欄本身帶各機器自己當下的 UTC offset(如 `"2026-08-21T13:02:18+08:00"`——本機 Taipei 執行;CI runner 若是 UTC 環境則寫 `+00:00`),而既有的「N 天窗口」計算慣例(如 `cmd_gov` 的 `--since` cutoff,`scripts/lumos:2957-2963` 一帶,用 `datetime.date.today()` 純本地日期字串比較)已知會在日界附近跟不同 offset 來源的 ts 混用出現 ±1 天誤差——這正是 E2 檢查曾經被實測抓到、需要專門修法的同一類問題(`scripts/lumos:934` 附近的 `[tz 跨日修 2026-07-20]` 註解:「ledger ts=UTC、ended=本地日期…混用兩時間源」)。S2 對 ack 的 30 天到期計算完全沒提要用哪個時鐘(本機執行 doctor --ci 的本地日期?ack append 當下的日期?UTC?)、要不要比照 E2 的修法做時區正規化,是把同一類已知會出錯的模式原樣複製到新機制而未特別處理的遺漏。**正確規則**:應明講「30 天到期用哪個時間源計算(建議:比照 E2 修法,統一轉本地日期或統一 UTC 再比較)」,並補一條邊界測試(ack 日期與判定日期跨時區/跨日界時的行為)。

---

一共 3 項發現(blocker 2 / minor 1)。
