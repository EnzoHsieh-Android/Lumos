# r1 對抗審計 — S4 視角:既有消費端整合與回歸面

審查對象:`/tmp/檢核收緊五件-r1.md`(135 行)。視角:pre-commit/pre-push/CI 呼叫鏈、`slim-gen.py` KEEP 閉包、`SCALAR_KEYS`/`_KNOWN_GATES` 既有漂移釘、`gov --stats` 既有測試、`_append_governance_log` dedup key、`doctor --ci` 的消費端契約。

---

## Finding 1(major)— `ratchet_ack` 是單一純量欄,同節點命中 ≥2 個閘會互相踩掉

引句:「節點 frontmatter `ratchet_ack: <gate>@<date>`(走 `lumos set`,白名單加一鍵)」

**驗證**:`ratchet_ack` 要加進 `SCALAR_KEYS`(`scripts/lumos:7039`),而 `cmd_set`(`scripts/lumos:7298-7322`)對純量鍵的語意是「整行覆寫」——`edit_fm_scalar` 找到既有 `key:` 行就整行取代(`scripts/lumos:7098-7101`),沒有既有行就插入一行(單一鍵、單一值)。frontmatter 不可能同時存在兩行 `ratchet_ack:`。

但 S2 的棘輪判準是 **(gate, node)** 一對一(「同一 (gate, node) 在 ≥20 個不同 commit 出現」),同一個節點完全可能同時被兩個不同的軟閘念(例:同一節點同時被 `check-s`「無 self_audit」與 `check-k` 命中),兩者各自獨立跑到 ≥20 commit 門檔。若使用者對 `check-s` 先 `lumos set N ratchet_ack check-s@2026-08-21`,之後 `check-k` 也升級,再 `lumos set N ratchet_ack check-k@2026-08-25`——第二次 `set` 會整行覆寫第一次的值,`check-s` 的 ack 靜默消失。下次 `doctor --ci` 會在使用者以為「已經 ack 過」的狀態下重新對 `check-s` 判定升級並硬擋,且完全沒有錯誤訊息或警告——這正是文件本身在 self-governance 段落強調「逃生口全部寫治理帳,繞過有痕」要防的那種靜默失效,只是這次不是逃生口被濫用,是逃生口本身把自己蓋掉。

**該有的規則**:`ratchet_ack` 若要支援多閘,必須是 list(如 `LIST_KEYS`/`append`)而非 `SCALAR_KEYS`/`set`;或者判準文件必須明講「同節點同時只認一個 ack,第二個閘升級時原 ack 會被覆蓋且不留痕」並讓 `cmd_set` 對此鍵在覆寫時印出警告。目前文件的「白名單加一鍵」暗示走既有純量鍵慣例,而既有 `set` 從未考慮過一個鍵要代表多組獨立 (gate,date) 配對。

---

## Finding 2(major)— 棘輪升級事件本身是否落治理帳、落哪個 `gate` 值,文件完全未定義;兩種自然實作都會出錯

引句:「②`--ci` 時每項計 1 issue(**硬**);純 doctor 列出不計。」

**驗證**:`run_doctor` 現有的落帳慣例(`scripts/lumos:1305-1327`,check-j/check-r 等)是「issues 計數」與「`gov_events.append(...)` 落 `.governance-log.jsonl`」兩件事分開做,`_append_governance_log` 的寫入者「僅 doctor --ci」(`scripts/lumos:422`)。文件對 S1(Check A)明講「`--ci` 時寫 `gate: check-a`」,對 ack 逃生門明講「ack 寫治理帳 `gate: ratchet-ack`」,但對「棘輪升級這件事本身」——也就是本節真正要硬擋的那個判定——完全沒講它要不要落帳、落哪個 `gate` 字面值。兩條路都有問題:

- **若落帳且重用原閘名**(例如原本 `check-s` 被升級,寫 `{"gate": g, "kind": "escalated", "hard": True, ...}`,`g` 是從治理帳讀出的變數而非字串字面值)——這會在原始碼裡新增第二處「`"gate":` 後面不是字串字面值」的寫法。`t_gov_stats_gate_drift`(`scripts/test_lumos.py:3047-3060`)已有專門釘死這件事的斷言:`dyn = _re.findall(r'"gate": [^"]', src); check(... len(dyn) == 1 ...)`,目前全檔案唯一一處動態 `"gate":` 寫法是 `cmd_gov` 的讀側 passthrough(`scripts/lumos:2993`,測試註解明講「讀側 passthrough,合法」)。S2 若走這條路,`len(dyn)` 會變成 2,這條既有回歸測試會直接翻紅——而文件的測試策略第 15 條(`t_known_gates_updated`)只提到要把 `check-a`/`ratchet-ack`/`external-absent` 三個字面值加進 `_KNOWN_GATES`,完全沒提到這第四種動態寫法會撞上既有的「動態閘名恰一處」釘子。
- **若不落帳**(只印 stdout、只計本地 `issues` 變數)——那麼本案動機文件裡反覆強調的稽核可追溯性(「check-s 軟提醒響 18,283 次/46 天零人處理,靠做別的事順手 grep 才發現」)在棘輪升級當下這個最關鍵的事件上反而沒有留痕,`gov --stats` 統計不到任何一次棘輪真正 fire 的紀錄,S2 自己的退場條件「90 天內零升級事件 → 棘輪退場候選」也將無帳可查(唯一資料來源變成人工盯 `doctor` 輸出的 stdout)。

**該有的規則**:S2 必須明講升級事件的 `gate` 字面值(例如新增一個固定字面值 `"gate": "ratchet"` 並在 `_KNOWN_GATES` 裡加入,`nodes` 另外攜帶原閘名),並把這第四個字面值補進測試策略第 15 條與 `_KNOWN_GATES` 異動清單——而不是靠隱含假設借用原閘名。

---

## Finding 3(blocker)— S3 的 fail-closed 掛在 `loop status --panel --gate`,但真正擋 `git push` 的是完全獨立的 `code-loop pass/skip` 留痕檔,兩者無耦合;`--panel --gate` 可以整段被繞過

引句:「這是把 `_TIER_ROSTER` 裡 `required-fail-closed` 從「轉述」變「執行」」

**驗證**:
1. `pre-commit`/`pre-push`/`.github/workflows/ci.yml` 三處自動化入口,沒有任何一處呼叫 `lumos loop status`(`grep -rn "loop status" scripts/hooks .github` 全無命中)。`pre-push` 唯一會擋 tier=high 分支 push 的機制,是第 108-123 行的 `code-loop check --diff ... --branch` 呼叫(`scripts/hooks/pre-push:110-123`)。
2. `cmd_code_loop`(`scripts/lumos:14138-14195`)的 `pass`/`skip` 子命令**完全不呼叫 `loop status`、不讀 `_TIER_ROSTER`、不檢查外家席**——它只是 `_codeloop_write(...)` 把 `{head_sha, status:"passed"/"skipped", note, ts}` 寫進 `governance/code-loop/<branch>.json`,綁定 HEAD sha。`check` 子命令(pre-push 會呼叫的那個)只驗證「tier=high 且無有效 pass/skip 留痕 → blocked」(`_codeloop_guard_verdict`),同樣不讀 `loop status` 的輸出或 `_TIER_ROSTER`。
3. 因此:任何人(或編排 Claude)只要直接執行 `lumos code-loop pass --note "..."`,完全不必先跑 `loop status --panel --gate`,pre-push 就會放行——S3 新增的「外家席缺席 → 合取 FAIL」判準只活在 `loop status` 這一個命令的輸出裡,而這個命令從未被任何自動化入口強制執行過。

這正好是本案動機清單裡列的第二個真事故的翻版:「skill 明寫 tier=high fail-closed、**code 未實作**」——S3 把「code 未實作」改成「code 實作了,但沒接線到任何會真的擋 push 的位置」,對「代碼作為唯一有效防線」的最終效果沒有改變:S3 上線前後,只要編排者(agent 或人)選擇跳過 `loop status --panel --gate` 直接記 `pass`,`git push` 都一樣會過。文件第 63 行自己也承認這是把「轉述」變「執行」,但只驗證了 `_TIER_ROSTER` 的資料語意被讀對,沒有驗證「執行」這個詞在推送路徑上真正成立——`loop status` 的 rc 從未進入任何會影響 `git push`/CI exit code 的鏈路。

**該有的規則**:若要讓 S3 真正 fail-closed,`code-loop check`(pre-push 唯一會呼叫、真正決定 rc 的函式)必須在 tier=code/high 且外家席缺席條件成立時本身回傳 blocked——即把 S3 判準內嵌進 `_codeloop_guard_verdict`/`cmd_code_loop check`,或者讓 `code-loop pass` 寫入前先跑一次等同 `loop status --panel --gate` 的外家席檢查並在不通過時拒寫留痕檔。現行設計把判準放在一個從不被自動呼叫的命令裡,等於只把警告文字換了個更長的位置。

---

## Finding 4(minor)— `external-absent` 的 `nodes` 語意是 loop id 而非圖譜節點,文件未比照既有 `_STATS_NODE_SEMANTICS` 慣例登記,`gov --stats` 的「不同 nodes 值數」欄會被污染

引句:「並寫治理帳 `gate: external-absent`。」

**驗證**:S3 的 streak 判準是「跨 loop 累計」(design/high、standard、indeterminate kind 三類 loop 的外家席缺席連續輪次),量測單位是 **loop id**(如 `code-abc123`),不是圖譜節點路徑。而 `gov --stats` 現有的 per-gate 統計表(`_render_gov_stats`,`scripts/lumos:2909-2954`)有一欄「不同 nodes 值數」,其計數依據是 `cmd_gov` 讀 `.governance-log.jsonl` 時把每筆事件的 `nodes` 欄位當成圖譜節點集合處理(`load(".governance-log.jsonl", ...)`,`scripts/lumos:2989-2992`)。這條路徑上唯一已知的「`nodes` 欄語意不是圖譜節點」例外是 `anchor-approve`(記檔案路徑),為此程式碼特地建了 `_STATS_NODE_SEMANTICS = {"anchor-approve": "此來源記的是檔案路徑"}`(`scripts/lumos:2902-2906`)並在表格輸出時附註(`scripts/lumos:2943-2944`),註解明講原因:「與其他 gate 的圖譜節點名不同質,同欄並列會被誤讀成可互相比較」。

`external-absent` 的 `nodes` 若如實填 loop id(文件全篇沒說要填什麼,但「跨 loop 累計」是這個 gate 的唯一自然鍵),就會落入與 `anchor-approve`完全相同的處境——但 S3 的設計文字、測試策略(第 12 條 `t_external_streak_print`)都沒有提到要把 `external-absent` 也登記進 `_STATS_NODE_SEMANTICS`。結果是 `gov --stats` 表格會把「缺席了幾個不同 loop」和「缺席了幾個不同圖譜節點」用同一欄呈現,且不像 `anchor-approve` 有附註提醒讀者這欄語意不同——重蹈這個常數就是為了防止的那種誤讀。

**該有的規則**:S3 應在測試策略裡明講 `external-absent` 事件的 `nodes` 欄填什麼(loop id 或乾脆留空),若填 loop id 則同步把 `"external-absent": "此來源記的是 loop id"` 加進 `_STATS_NODE_SEMANTICS`,並在退場條件量測(S3 退場條件依賴「連續 N 個 high loop」計數)時說明這個數字要從哪一欄讀。

---

## 嚴重度統計

blocker: 1, major: 2, minor: 1
