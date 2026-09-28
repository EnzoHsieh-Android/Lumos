severity: major

## F1 半套恢復會把其他 frontmatter 區塊誤認成正式合約

severity: major  
blocking: 是 — 守衛可在家筆記仍只有預告合約時被標成 pass，之後 c1、c5 都不會揭露這個假綠。  
引句:「+    for i in range(1, e):」

1. `_guard_formal_line` 宣稱只找摘要，實際掃完整個 frontmatter。只要 `valid_under` 等區塊出現相同 `KEY:★INVARIANT★` 與測試標記，就會回 `True`。
2. `_guard_settle_home` 因此跳過真正的摘要預告行；第二步仍把守衛紀錄改成 pass 並改寫其預告句。家筆記的 `★INVARIANT-PLANNED★` 留著，但 c5 只查 pending、c1 只查守衛紀錄內的預告句，整體呈現假綠。
3. 最小重現：

```text
python3 -c 'import importlib.machinery; m=importlib.machinery.SourceFileLoader("lumos","scripts/lumos").load_module(); lines=["---","type: system","status: doing","summary: |-","  KEY:★INVARIANT-PLANNED★ 大額退費要人工核可 [watch:Verification/G] [due:2099-12-31]","valid_under: |-","  KEY:★INVARIANT★ 大額退費要人工核可 [test:t_refund]","---"]; print(m._guard_formal_line(lines,7,"大額退費要人工核可","t_refund"))'
輸出: True
```

file: `scripts/lumos:11802`  
file: `scripts/lumos:11837`

## F2 合約正文含方括號標記時，做到一半的 settle 無法補完

severity: major  
blocking: 是 — 第一步已拿掉預告行、第二步失敗後，合法合約會永久停在 pending，重跑同一指令也救不回來。  
引句:「+        if _GUARD_MARKS_RE.sub("", m.group(1)).strip() == claim:」

1. `_GUARD_MARKS_RE.sub` 會刪除合約文字內所有 `[鍵:值]`，不只刪行尾由工具附加的 `[test:]`、`[audit:]`。
2. 輸入合約為 `錯誤帶 [status:manual] 時要人工核可` 時，正式行被正則化成 `錯誤帶 時要人工核可`，與守衛紀錄保存的原始合約不相等。
3. 若前次 settle 已完成家筆記改寫、但守衛紀錄寫入失敗，重跑會先判「不是正式行」，接著又因預告行已不存在而擋下。
4. 最小重現：

```text
python3 -c 'import importlib.machinery; m=importlib.machinery.SourceFileLoader("lumos","scripts/lumos").load_module(); lines=["---","summary: |-","  KEY:★INVARIANT★ 錯誤帶 [status:manual] 時要人工核可 [test:t_manual] [audit:opus/2026-09-20]","---"]; print(m._guard_formal_line(lines,3,"錯誤帶 [status:manual] 時要人工核可","t_manual"))'
輸出: False
```

file: `scripts/lumos:11796`  
file: `scripts/lumos:11810`

## F3 非 UTF-8 守衛紀錄會被當成不存在並乾淨放行

severity: major  
blocking: 是 — 無法解碼本應屬「判不了、要處理」，目前卻同時退出狀態翻轉與 c1 檢查。  
引句:「+        except UnicodeDecodeError:」

1. 守衛紀錄只要任一處含無效 UTF-8 位元組，`_note_audit_status_of` 就回 `(None, None)`，所以 pending→pass 事件不會進 `passed`。
2. `_drift_tree_env` 又直接略過同一篇筆記，終點環境沒有 c1 finding。
3. `_drift_check_core` 最終回傳 `([], [], [])`，不是 unknown；block 模式照樣回 0。
4. 不落盤最小重現：

```text
python3 -c 'import importlib.machinery,pathlib; m=importlib.machinery.SourceFileLoader("lumos","scripts/lumos").load_module(); bad=b"---\ntype: verification\nstatus: pass\n---\nTEST:\xff\n"; print("tip_status=",m._note_audit_status_of(bad)); a,b=m._drift_range_events,m._drift_tree_env; m._drift_range_events=lambda *x,**k:{"touched":{"Verification/G.md"},"passed":set(),"closed":set()}; m._drift_tree_env=lambda *x,**k:m.Env.from_texts(pathlib.Path("docs/kg-knowledge"),{}); print("check=",m._drift_check_core(pathlib.Path("."),"A","B","docs/kg-knowledge")); m._drift_range_events,m._drift_tree_env=a,b'
輸出:
tip_status= (None, None)
check= ([], [], [])
```

file: `scripts/lumos:24423`  
file: `scripts/lumos:25298`

## F4 scan --at 與 history 在圖譜根目錄改名後會掃空樹

severity: major  
blocking: 是 — 任一提交樹的檢查與歷史重放會靜默漏掉改名前的全部筆記，直接污染考試門檻。  
引句:「+        tenv = _drift_tree_env(root, sha, vault_rel)」

1. `cmd_drift_scan` 先從目前工作目錄的 `env.vault` 算 `vault_rel`，指定 `--at` 後仍沿用該路徑，沒有用 `_drift_vault_rel(root, sha)` 查那棵樹。
2. `exam --history` 同樣只在 HEAD 算一次圖譜路徑，再拿它重放所有舊提交。
3. 本 repo 的實際歷史已能重現：舊提交的圖譜是 `docs/kg-knowledge`，用目前路徑讀到 0 篇，用該提交自己的路徑可讀到 2 篇。

```text
python3 -c 'import importlib.machinery,pathlib; m=importlib.machinery.SourceFileLoader("lumos","scripts/lumos").load_module(); root=pathlib.Path(".").resolve(); old="67b75fd670764582b8bd61bc1cf1be61c33c9145^"; print("tree_vault=",m._drift_vault_rel(root,old)); print("scan_current_vault_notes=",len(m._drift_tree_env(root,old,"docs/lumos-toolchain-knowledge").notes)); print("scan_tree_vault_notes=",len(m._drift_tree_env(root,old,"docs/kg-knowledge").notes))'
輸出:
tree_vault= docs/kg-knowledge
scan_current_vault_notes= 0
scan_tree_vault_notes= 2
```

file: `scripts/lumos:25555`  
file: `scripts/lumos:25564`  
file: `scripts/lumos:25688`

## F5 c3 把已有空 guards 欄的紀錄誤判成沒有 guards 欄

severity: minor  
blocking: 否 — c3 只列出不擋，但會製造規格明確排除的誤報。  
引句:「+    if n.fields.get(GUARD_MARK_FIELD):」

1. 規格定義是「沒有 `guards` 欄」才算 c3；實作檢查欄位值的 truthiness。
2. `guards: []` 或空字串代表欄位存在，程式仍繼續做 c3 判定。
3. 最小重現輸出為 `[('c3', 'Verification/V.md')]`：

```text
python3 -c 'import importlib.machinery,pathlib; m=importlib.machinery.SourceFileLoader("lumos","scripts/lumos").load_module(); T={"Projects/P.md":"---\ntype: project\nstatus: done\n---\n# P\n","Verification/V.md":"---\ntype: verification\nstatus: pending\nguards: []\nplan_refs:\n  - [[Projects/P]]\n---\n# V\n"}; e=m.Env.from_texts(pathlib.Path("docs/kg-knowledge"),T); print([(f["kind"],f["path"]) for f in m._drift_state_findings(e)])'
```

file: `scripts/lumos:25151`

## F6 欄位型 finding 使用合成文字，ack 成功後仍不生效

severity: minor  
blocking: 否 — 受影響的是只列出的 c2、c3、c5，但使用者會收到成功訊息卻無法消除 finding。  
引句:「+                            "text": f"status: {st}", "related": [p for p, _d in plans],」

1. c2 的 finding 固定保存 `status: open`；`drift ack` 保存磁碟上的逐字原文。
2. 合法寫法 `status: "open"` 因兩段文字不同，表態檔永遠無法匹配。c3、c5 的合成 `status: pending` 有相同問題。
3. 最小重現：

```text
python3 -c 'import importlib.machinery,pathlib; m=importlib.machinery.SourceFileLoader("lumos","scripts/lumos").load_module(); T={"Projects/P.md":"---\ntype: project\nstatus: done\n---\n# P\n","Issues/I.md":"---\ntype: issue\nstatus: \"open\"\n---\n# I\n[[Projects/P]]\n"}; e=m.Env.from_texts(pathlib.Path("docs/kg-knowledge"),T); f=m._drift_state_findings(e)[0]; a={"path":"docs/kg-knowledge/Issues/I.md","text":"status: \"open\"","kind":"c2"}; print("finding_text=",repr(f["text"])); print("unacked=",len(m._drift_split_acked([f],[a],"docs/kg-knowledge")[0]))'
輸出:
finding_text= 'status: open'
unacked= 1
```

file: `scripts/lumos:25197`  
file: `scripts/lumos:25441`

## F7 doctor 把已表態的存量漂移完全藏掉

severity: minor  
blocking: 否 — doctor 是提醒面，但會把仍存在且刻意保留的漂移顯示成零。  
引句:「+    left, _done = _drift_split_acked(_drift_state_findings(env), _drift_load_acks(root), vault_rel)」

1. 規格要求 scan 與 doctor 對已表態行照列並標示「已表態」。
2. doctor 直接丟棄 `_done`，後續只統計 `left`；當全部 finding 都已表態且沒有其他提醒時，整段 Z 消失。
3. 文字模式 scan 也只逐筆列 `left`，已表態項目只剩總數，無法知道是哪幾行。

file: `scripts/lumos:25570`  
file: `scripts/lumos:25596`  
file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:57`

## F8 doctor 只在已接線時提示非 block 模式，與規格相反

severity: minor  
blocking: 否 — 不直接改變閘判定，但隱藏了專案把守衛設為 warn 或 off 的狀態。  
引句:「+    if wired:」

1. 設計與 S14 都要求 gate 不是 block 時 doctor 印一行，沒有「接線後才印」的條件。
2. 實作把設定檔讀取與模式提醒整段放進 `if wired`；尚未有掛鉤標記的專案即使明寫 `drift_check.gate=off`，doctor 仍不提示。
3. 新增的 Systems 筆記明載這是「跟設計稿不一樣」的決定，但計劃仍是本次交付規格，兩份權威目前互相矛盾。

file: `scripts/lumos:25605`  
file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:60`  
file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:144`

## F9 exam 把同篇其他 finding 全部排除，誤報分數被低估

severity: minor  
blocking: 否 — 影響考試與預設模式決策，不直接改變單次 check 的擋放。  
引句:「+    others_m = [f for f in must if f["path"] != note]」

1. 設計將「不是題目那一行的 finding」計為誤報；實作改成只要跟題目同一路徑就全部排除。
2. 具體輸入是 commit 題目命中守衛紀錄的 TEST 行，同篇另有無關的 c4 finding；後者不是題目行，依規格應算誤報，實作因路徑相同而不計。
3. Systems 筆記再次明載這是偏離設計的決定，會讓「零假擋、噪音不超過 5」的上線數字偏低。

file: `scripts/lumos:25656`  
file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:105`

已看：`load_vault` 抽成 `_note_from_text`、`Env.from_texts` 與 `env_text`，除 F3 外無 finding。

已看：`_notes_status_flipped` 與 `_note_audit_resolve` 參數化後的筆記內容審既有語意，無 finding。

已看：guard plan、settle、abandon 的寫入鎖範圍，未找到兩個指令交錯後互相覆蓋的路徑。

已看：CLI parser/dispatch、簿記白名單、其餘測試與圖譜筆記，無 finding。

最嚴重等級 major，blocking 共 4 條。