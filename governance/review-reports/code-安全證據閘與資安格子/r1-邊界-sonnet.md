severity: major

我只審 r1-lumos-b.patch(新檔約 8243 到 11190 行)。固定席筆記沒附,圖譜鏡頭沒有可逐條判的項目。manifest 兩條都落在這一包,是 `security approvals` 的追加寫入(11110 行)和 guard kill 背書的追加寫入(11167 行)的 `open(...,"ab")`,兩處都在 `with` 裡,判無問題。

以下三條都用 `python3.14` 載入被審版本 b99f52c8 的 `scripts/lumos` 實跑過(第 3 條除外)。

1. 壓測與動態掃描的目標主機解析,遇到 `#` 或 `?` 會取錯主機,把外部主機當成回環
severity: major
blocking: 是

引句:「h = re.sub(r"^[a-z][a-z0-9+.-]*://", "", t).split("/", 1)[0]」

- 輸入:`environment` 寫成 `target=http://evil.com#@localhost`,或 `target=http://evil.com?x=@127.0.0.1/`。
- 走到哪:`_secev_target_host` 只用 `/` 切授權段,接著 `h.rsplit("@", 1)[-1]` 取最後一個 `@` 之後的字串。`#`、`?` 沒有先切掉,所以真正的主機 evil.com 被誤判成 `localhost` 或 `127.0.0.1`。`_secev_item_tool` 再用 `_secev_loopback(h)` 判斷,就不會產生 `target_not_authorized`。
- 重現(實跑輸出):
  ```
  _secev_target_host("target=http://evil.com#@localhost")        -> localhost
  _secev_target_host("target=http://evil.com?x=@127.0.0.1/")     -> 127.0.0.1
  ```
- 這道檢查就是擋「壓測打到未核可的外部目標」,這兩種輸入會讓它漏判。
- 附帶:大寫 scheme(`HTTP://localhost`)不會被剝掉,主機變 `http`,結果是誤擋。這個方向安全,只是錯誤代碼沒講出原因。

2. 欄位型別錯會丟 AttributeError 或 TypeError,整道變成 `evaluation_error`,訊息指不出哪一列哪一欄
severity: major
blocking: 是

根因是同一個:把 JSON 讀進來的值直接當 dict 或 hashable 用,沒先檢查型別。三個實例如下。

- 1a. k6 摘要的 `values` 不是物件。
  引句:「vals = {m["name"]: m.get("values") or {} for m in metrics if isinstance(m, dict) and isinstance(m.get("name"), str)}」
  - 輸入:指標的 `"values": [1]` 或 `"values": "abc"`。
  - `_secev_k6_parse` 的 `or {}` 會留下非空的 list 或 str,後面 `(vals.get("iterations") or {}).get("count")` 就丟 AttributeError。`_secev_k6_parse` 只接 `(KeyError, TypeError)`,接不到這個。
  - 重現:`_secev_judge_k6(...)` 對 `[1]` 與 `"abc"` 都丟 `AttributeError: 'list' object has no attribute 'get'`。
  - 同一條壞報告應該只讓這一項變 `report_unparseable`。現在是整個推送被擋,訊息只有類別名,沒有項目與指標名。
  - `{"count":"x"}` 這種值則有被正確處理。

- 1b. guard kill 背書的 `verdict` 或 `recipe_id` 不是字串。
  引句:「probs.append(_SECEV_KILL_CODES.get(last.get("verdict"), "kill_weak_only"))」
  - 輸入:背書列的 `{"verdicts":[{"verdict":[]}]}`。
  - 重現:`_secev_gk_group` 丟 `TypeError: cannot use 'list' as a dict key (unhashable type: 'list')`。
  - `recipe_id` 是 list 時,`by = {g.get("recipe_id"): g ...}` 建字典同樣丟 TypeError。

- 1c. 核可鏈某一筆的 `type` 是 list 或 dict。
  引句:「if set(e) - {"outcome"} != need or typ not in _SECAPR_TYPES or not all(」
  - 輸入:`{"seq":1,"prev_sha256":"","type":[],...}`。seq 和 prev 都對,所以不會先被判 `chain_broken`。
  - 重現:`_secapr_verify(...)` 丟 `TypeError: cannot use 'list' as a dict key (unhashable type: 'list')`。`typ not in _SECAPR_TYPES` 是對 dict 查 key,list 不能當 key。
  - 這條最重:核可鏈只追加、不能改前面的列。一旦有一行這樣的列進了提交,每次判定都會 `evaluation_error`,`security approvals verify` 也會當掉,而且沒辦法在鏈內修掉。正確做法是這一筆判 `approval_fields_missing`,其餘照鏈往下算。
  - `evaluation_error` 的 `gate_detail` 只有 `TypeError: ...` 和階段名「讀要推的提交」,看不出哪一行或哪個欄位。

3. 超過單檔上限的檔,和「不在樹上」一樣被當成不存在
severity: minor
blocking: 否

引句:「main_chain = run.mtree.read(_SECEV_APPROVALS_REL, deadline=run.deadline) if run.mtree else None」

- 輸入:主線 tip 的 `.lumos/security-approvals.jsonl` 或 `.lumos/config.json` 超過 `_SECEV_FILE_MAX`(16 MiB)。
- `_SecevTree.read` 對「不在樹上」和「太大」都回 None。主線鏈變成 None 後,`_secapr_verify` 裡的 `if main_raw and ...` 不成立,「主線版必須是推送版的開頭」這一步被略過,不會判 `approvals_diverged`。推送版只要小於上限,整條換掉也不會被點名。
- config 超大時,`_secev_config(None)` 不給警告就用預設值,`mainline` 設定被悄悄丟掉。
- 未能重現:沒有造出 16 MiB 以上的檔,只是從程式讀到的。要成立得先有超過 16 MiB、約數萬筆的核可鏈,在單人使用下機率低,所以降到 minor。建議和 `ctx.read` 一樣,回傳原因代碼(`evidence_too_large`)而不是 None。

最嚴重 severity: major,blocking 共 2 條。
