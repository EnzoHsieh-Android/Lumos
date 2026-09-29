severity: major

## F1 c4 會放行標準 YAML 禁止的控制字元

severity: major  
blocking: 是  
引句:「+    if _yaml_plain_ok(item):」  
file: `scripts/lumos:27994`

1. `--new` 含 U+001B 時，單行檢查與 YAML 白名單都回成功；後續極簡 parser 也不會拒絕，因此會把無效 frontmatter 寫入磁碟並通過自驗。

2. 唯讀重現：

```sh
/opt/homebrew/bin/python3 -c 'import runpy,yaml; m=runpy.run_path("scripts/lumos",run_name="lumos_audit"); new="已提交"+chr(27)+"abc"; print("text_err=",m["_drift_c4_text_err"]("本工作樹(未提交)",new)); print("yaml_err=",m["_drift_c4_yaml_err"]("  - "+new)); yaml.safe_load("valid_under:\n  - "+new+"\n")'
```

輸出：

```text
text_err= None
yaml_err= None
ReaderError: unacceptable character #x001b: special characters are not allowed
```

3. 執行路徑是 `_drift_c4_text_err` → `_drift_c4_yaml_err` → `parse_frontmatter` → `_drift_fix_write`。`--new $'已提交\eabc'` 可由 shell 傳入，結果會把 Obsidian／標準 YAML 無法讀取的內容真正寫進筆記。

## F2 可貼用的 git 路徑被截斷，失敗後無法按提示還原

severity: major  
blocking: 是  
引句:「+    return _esc_clean(_drift_sh(_guard_raw_git_path(cx["root"], cx["repo_rel"]) or cx["repo_rel"]), 300)」  
file: `scripts/lumos:28149`  
file: `docs/lumos-toolchain-knowledge/Projects/存量漂移改法_計劃.md:132`

1. `_drift_git_arg` 對實際 git 路徑套用 300 字截斷。合法的多層長路徑會被改成另一條路徑；若路徑需要 shell 引號，截斷還可能移除結尾引號。

2. 唯讀重現使用兩個各 145 字、未超過檔案系統單一元件上限的目錄：

```sh
/opt/homebrew/bin/python3 -c 'import runpy,shlex; m=runpy.run_path("scripts/lumos",run_name="lumos_audit"); raw="docs/"+("a"*145)+"/"+("b"*145)+" x.md"; m["_drift_git_arg"].__globals__["_guard_raw_git_path"]=lambda root,rel: raw; got=m["_drift_git_arg"]({"root":"/no-read","repo_rel":"ignored"}); print(len(raw),len(got),repr(got[-12:])); print(shlex.split(got)[0]==raw)'
```

輸出：

```text
301 301 'bbbbbbbb x.…'
ValueError: No closing quotation
```

3. 驗證失敗與修復帳失敗都發生在筆記已經寫入之後，卻以此結果產生 `git checkout -- …`；成功路徑的 `git add` 也使用同一結果。這破壞了 [S9]「失敗時指到可用的 git 還原」合約。

## 其餘指定重點查核

`_nfc_child`、`_phys_path`、`_plan_file_exists`、`_drift_sh`／`./` 節點往返、兩個正則、placeholder 判定與 `_issue_close_revisits` 均已追過呼叫路徑；除上述兩項外，未發現符合本席門檻的項目。

## 圖譜鏡頭逐條判定

- `Systems/guard-kill`：未改動 kill 的回傳碼優先序，也未碰成功時 JSON stdout 純度。
- `Systems/lumos-cli-read`：未改動 search 的 superseded／stale 篩選。
- `Systems/lumos-cli-lifecycle`：未改動 re-inject sentinel 外內容保留。
- `Systems/bound-tests-gate`：未改動綁定測試的執行與阻擋判定。
- `Systems/授權與歸屬`：未改動 vendored 白名單、deinit 刪除集合或程式檔授權標頭。
- `Systems/測試假綠形態`：新增測試對既有修正有前置輸入，但沒有覆蓋 F1 的控制字元與 F2 的長路徑。
- `Systems/design-loop`：未改動設計審材料、條款綁定或處置閘。
- `Systems/pitfalls-code-loop`：本次仍屬守衛面改動；上述兩條會使寫入安全與人工回復路徑失真。

最高等級:major