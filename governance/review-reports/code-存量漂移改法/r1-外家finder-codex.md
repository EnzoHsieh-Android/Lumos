severity: major

## F1 c4 可把 YAML 指示字元寫成另一種語意

severity: major

blocking: 是

引句:「if (t.startswith(("-", "#")) or ": " in new or t.endswith(":") or " #" in new or new.count('"') % 2」

file: `scripts/lumos:27857`

file: `scripts/lumos:27909`

1. 輸入 `valid_under:\n  - 未提交`，執行 c4 並給 `--old 未提交 --new '|'`。`_drift_c4_text_err` 放行，原始行變成 `  - |`；Lumos 的簡易 parser 把它讀成字串 `"|"`，標準 YAML 卻把它讀成空的 block scalar。後續項數檢查、形狀擋與寫後自驗全部使用 Lumos parser，因此會記帳成功，實際 YAML 語意已被改壞。

2. 純記憶體重現：

```text
$ PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -c 'import runpy,pathlib;m=runpy.run_path("scripts/lumos",run_name="review_probe");fm=["type: verification","status: pass","valid_under:","  - |"];print(m["_drift_c4_text_err"]("未提交","|"));print(m["parse_frontmatter"](fm)[0]["valid_under"],m["parse_frontmatter"](fm)[2]);print(m["_drift_fix_shape_err"](pathlib.Path.cwd(),[("|","other")]))' && ruby -e 'require "yaml"; p YAML.safe_load("---\ntype: verification\nstatus: pass\nvalid_under:\n  - |\n")'
None
['|'] []
None
{"type"=>"verification", "status"=>"pass", "valid_under"=>[""]}
```

3. `--new` 必須走既有 `_yaml_plain_ok`／安全引用規則，或對改後 frontmatter 做標準 YAML 等價驗證；只列舉部分結構字元不足以守住此邊界。

## F2 c2 keep 會繞過 dry-run 並真的寫表態帳

severity: major

blocking: 是

引句:「return cmd_drift_ack(env, rel, line, "c2", o["reason"])      # 照留:等同帶清單的 c2 表態」

file: `scripts/lumos:28063`

file: `scripts/lumos:27432`

1. 輸入 `drift fix Issues/I 3 --kind c2 --keep --reason 還沒解決 --dry-run`。`cmd_drift_fix` 在檢查 `dry_run` 之前直接呼叫 `cmd_drift_ack`；真實函式會追加 `governance/drift-acks.jsonl`，並使後續掃描把 c2 當成已表態。

2. 純記憶體 spy 重現：

```text
$ PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -c 'import runpy;m=runpy.run_path("scripts/lumos",run_name="review_probe");g=m["cmd_drift_fix"].__globals__;calls=[];g["_drift_fix_target"]=lambda e,n:("Issues/I.md",None);g["cmd_drift_ack"]=lambda *a:(calls.append(a),77)[1];o={"dry_run":True,"date":None,"close":False,"keep":True,"status":None,"reason":"還沒解決","by":None,"old":None,"new":None};rc=m["cmd_drift_fix"](object(),"Issues/I",3,"c2",o);print("rc=",rc,"ack_calls=",len(calls),"args=",calls[0][1:])'
rc= 77 ack_calls= 1 args= ('Issues/I.md', 3, 'c2', '還沒解決')
```

3. `--keep` 分派前必須先處理 `dry_run`，只預覽將寫入的表態，不得拿鎖或追加帳檔。

## F3 驗證與記帳不在同一鎖內，帳面指紋可與磁碟不同

severity: major

blocking: 是

引句:「ok = got == want and res["handled"](_drift_state_findings(Env(env.vault), only={cx["rel"]}), got.decode("utf-8"))」

file: `scripts/lumos:28028`

file: `scripts/lumos:28044`

1. `_drift_fix_verify` 在鎖外確認內容 B 後返回；另一個寫入者可在 `_drift_fix_record` 重新拿鎖前把同一篇改成 C。記帳函式不重讀目標，仍把由 `res["new"]` 算出的 B 指紋寫入帳中並回成功。

2. 純記憶體重現：

```text
$ PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -c 'import runpy,contextlib,hashlib,types;m=runpy.run_path("scripts/lumos",run_name="review_probe");g=m["_drift_fix_verify"].__globals__;state={"raw":b"B"};P=type("P",(),{"read_bytes":lambda s:state["raw"]});cx={"path":P(),"rel":"Issues/I.md","repo_rel":"docs/x/Issues/I.md","root":"/no-write","line":3,"kind":"c2","lines":["A"]};res={"new":["B"],"handled":lambda fs,txt:True,"extra":{}};g["Env"]=lambda v:object();g["_drift_state_findings"]=lambda *a,**k:[];env=types.SimpleNamespace(vault="v");print("verify=",m["_drift_fix_verify"](env,cx,res));state["raw"]=b"C";seen=[];g["_vault_write_lock"]=lambda v:contextlib.nullcontext();g["_drift_next_seq"]=lambda *a:1;g["_drift_ledger_append"]=lambda root,rel,rec:(seen.append(rec),0)[1];g["_gate_event_or_warn"]=lambda *a,**k:None;print("record_rc=",m["_drift_fix_record"](env,cx,res));print("disk_sha=",hashlib.sha256(state["raw"]).hexdigest());print("ledger_sha=",seen[0]["after_sha256"])'
verify= None
record_rc= 0
disk_sha= 6b23c0d5f35d1b11f9b683f0b0a617355deb11277d91ae091d399c655b87940d
ledger_sha= df7e70e5021544f4834bbee64a9e3789febc4be81470df629cad6ddb03320a5c
```

3. 追加修復帳前，必須在所持寫入鎖內再次比對目標位元組；否則修復帳不是寫入完成時的真實狀態。

## F4 壞掉的 seq 會被當成零號有效表態

severity: minor

blocking: 否

引句:「return v if isinstance(v, int) and not isinstance(v, bool) else 0」

file: `scripts/lumos:27390`

file: `scripts/lumos:27395`

1. 一筆 c2/c3 表態若 `related` 正常、但 `seq` 缺失或被改成字串，`_drift_ack_seq` 會回 0；若沒有其他同鍵紀錄，它仍成為最新一組並抑制目前發現。

2. 重現：

```text
$ PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -c 'import runpy;m=runpy.run_path("scripts/lumos",run_name="review_probe");f={"kind":"c2","path":"Issues/I.md","line":3,"text":"status: open","related":["Projects/P.md"]};a={"path":"docs/x-knowledge/Issues/I.md","text":"status: open","kind":"c2","related":["Projects/P.md"],"seq":"壞掉"};left,done=m["_drift_split_acked"]([f],[a],"docs/x-knowledge");print(len(left),len(done))'
0 1
```

3. 綁定表態應只採用正整數 `seq`；壞行可以略過或保守地重新列出，不能降成一個仍有效的序號。

## F5 產生的指令未跳脫含空白路徑

severity: minor

blocking: 否

引句:「base = f"lumos drift fix {node} {line} --kind {kind}"」

file: `scripts/lumos:27566`

file: `scripts/lumos:27848`

file: `scripts/lumos:28040`

file: `scripts/lumos:28094`

1. 節點為 `Issues/有 空白.md` 時，scan/check/doctor 印出的 fix 指令會把節點拆成兩個參數。寫後驗證失敗的 `git checkout -- ...` 與成功後的 `git add ...` 也未引用路徑；照貼可能失敗，甚至命中兩個意外存在的 pathspec。

2. 重現：

```text
hint: lumos drift fix Issues/有 空白 3 --kind c2 --close --status done --reason "<為什麼算解決,附提交或測試>"
argv: ['lumos', 'drift', 'fix', 'Issues/有', '空白', '3', '--kind', 'c2', '--close', '--status', 'done', '--reason', '<為什麼算解決,附提交或測試>']
```

3. 所有輸出的 shell 路徑都應用同一支 POSIX 跳脫函式處理。

## F6 NFC 索引路徑被直接當成實體路徑重開

severity: minor

blocking: 否

引句:「path = env.vault / rel」

file: `scripts/lumos:529`

file: `scripts/lumos:27662`

file: `scripts/lumos:27702`

1. `load_vault` 將實體檔名正規化成 NFC 後作為 `env.notes` 的鍵。若 Linux 工作樹實際追蹤的是 NFD 檔名，例如 `Issues/café.md`，`_drift_fix_target` 會回 NFC 的 `Issues/café.md`，接著 `_drift_fix_load` 用該 NFC 字串開檔而得到不存在。

2. 執行路徑在 `load_raw_for_edit` 就回「打不開」，尚未走到能由 `_guard_raw_git_path` 還原 Git 原始拼法的乾淨檢查。有效且可掃描的 Unicode 筆記因此無法修復。

3. 應保留正規化鍵到實體 `Path` 的對照，或像 Git 路徑處理一樣先解析實際拼法再讀寫。

## F7 一般正文只要以已結案開頭就被誤認成結案橫幅

severity: minor

blocking: 否

引句:「if j < len(body) and body[j].lstrip("> ").startswith("已結案"):」

file: `scripts/lumos:27747`

1. Issue 第一段若是「已結案通知功能仍會重複寄信」這類症狀，`_drift_close_banner` 會把它誤認為既有橫幅。c2 隨後把 status 改成結案值，卻沒有加入「以下是當時的排查紀錄,不是現況」標記。

2. 重現：

```text
$ PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -c 'import runpy;m=runpy.run_path("scripts/lumos",run_name="review_probe");body=["# I","","已結案通知功能仍會重複寄信","排查內容"];new,had=m["_drift_close_banner"](body,"> 已結案(2026-09-29,done):真正橫幅");print("had=",had);print("banner_added=",any("真正橫幅" in x for x in new));print(new)'
had= True
banner_added= False
['# I', '', '已結案通知功能仍會重複寄信', '排查內容']
```

3. 已有橫幅的判定應匹配工具產生的完整標記形狀，例如 `> 已結案(` 與歷史說明，而不是一般文字前綴。

## 圖譜鏡頭逐條判定

1. `Systems/guard-kill`：本 patch 未改 guard kill 的回碼優先序或 JSON stdout 路徑，兩條合約不受影響。
2. `Systems/lumos-cli-read`：search 的 superseded/stale 濾網未被修改，不受影響。
3. `Systems/lumos-cli-lifecycle`：re-inject sentinel 外內容保留邏輯未被修改，不受影響。
4. `Systems/bound-tests-gate`：code-loop check 的綁定測試執行與阻擋條件未被修改，不受影響。
5. `Systems/授權與歸屬`：vendored 白名單與 SPDX/MIT 檔頭未被修改，不受影響。
6. `Systems/測試假綠形態`：本審材只改 `scripts/lumos`；未改該合約綁定測試的現場前置斷言機制。
7. `Systems/design-loop`：設計審處置閘的計劃格式、條款綁定與日期判定未被修改，不受影響。
8. `Systems/pitfalls-code-loop`：新增修復帳到簿記白名單符合其用途；未見破壞該節點既有宣稱，但 F3 會使帳面內容失真，須先修正。

最高等級:major