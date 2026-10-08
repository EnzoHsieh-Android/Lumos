severity: major

**1. 分層與依賴方向**

新碼都留在 `scripts/lumos` 單檔內,呼叫方向沒變。`_codeloop_record_valid` 呼叫 `_codeloop_record_valid_ex`,後者呼叫 `_codeloop_bookkeeping_code`,算背書的 `_contract_backing_one` 也呼叫 `_codeloop_record_valid_ex`(`scripts/lumos:38748`)。沒有跨層直呼。`_backing_kill_rows` 改呼叫 `_drift_jsonl_rows`(`scripts/lumos:38811`),上一輪的第二套讀法已刪掉。
`cmd_gov` 內的 `load` 改成自己 `read_bytes` 再呼叫 `_drift_jsonl_parse`,見 R3A2。

**2. 命名與錯誤處理**

- 新增的 `_shallow`、`_code`、`_raw` 都是區域底線前綴,跟鄰居一致。
- `_codeloop_bookkeeping_code` 加了 `timeout=None` 參數,同檔 `_codeloop_record_valid_ex` 也用這個寫法(`scripts/lumos:38108`)。
- 判不了的做法(傳 `unknown=None`,讓函式回 `None`,呼叫端再轉成 `unsure=True`)是新的三態慣例。該函式原本只回布林,repo 裡同樣的三態回傳先例只有 `_codeloop_record_valid_ex` 的三元組,而那個上一輪已放行。我把它視為同一套判不了語意的延伸,不列條。
- `except OSError: return` 對照 `_drift_jsonl_rows` 的 `except OSError`(`scripts/lumos:28955`),處理方式一致。

**3. 第二種做法**

**R3A1**
severity: major
blocking: 是(repo 已有判淺 clone 的共用函式,新碼在 `_codeloop_record_valid_ex` 內另寫一套,屬於引入第二種做法)
引句:「+            _shallow = _sp.run(["git", "rev-parse", "--is-shallow-repository"], capture_output=True, text=True,」
對照:repo 已有 `_git_is_shallow(repo_root)`,內容就是 `git rev-parse --is-shallow-repository`,並有 `OSError` 容錯。呼叫端有 `check-j` 的 Tier B 驗證跳過、`scripts/lumos:12293`、`scripts/lumos:29418`。另外 `_lens_git(root, "rev-parse", "--is-shallow-repository")` 也有兩處(`scripts/lumos:25790`、`scripts/lumos:26280`)。
佐證:file: `scripts/lumos:4907`。
差別:新碼多了 `timeout=_to`,這是 `_git_is_shallow` 沒有的。判準是同功能該共用:要嘛給 `_git_is_shallow` 加 `timeout` 參數後共用,要嘛直接呼叫它,不要在函式內另寫一套。

**R3A2**
severity: minor
blocking: 否(結構對,只是繞過了帳檔讀取的入口函式,重複了讀檔與錯誤處理)
引句:「+            _raw = p.read_bytes()」
對照:`_drift_jsonl_rows(fp)` 就是「`read_bytes` 加 `OSError` 容錯再交給 `_drift_jsonl_parse`」的入口,上面 `if not p.exists(): return` 已經守住了檔案存在。`cmd_gov` 的 `load` 自己展開這段,結果跟 `_backing_kill_rows` 那邊不一致,一處用 rows、一處用 parse。
差別:`_drift_jsonl_rows` 不跟符號連結,`load` 版本會跟,行為有細微不同。若這是刻意的,應註明;否則直接呼叫 `_drift_jsonl_rows(p)`。
佐證:file: `scripts/lumos:28952`。

不對齊共 2 條,其中 major 1 條
