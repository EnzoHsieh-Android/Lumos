severity: major

ls-tree 一次列出、預算分配、寫檔清暫存三處,實測都沒問題。但這輪順手改的 `_dispositions_verdict` 有一個必炸的 bug。

## finding 1

severity: major
blocking: 是 — 預設參數 `deadline=None` 的呼叫路徑必崩 TypeError,既有測試已實測變紅,屬於修補引入的回歸
引句:「+            if _time.monotonic() > deadline:」
問題:修補把表態核對迴圈的 `if deadline is not None and _time.monotonic() > deadline:` 縮成 `if _time.monotonic() > deadline:`。但函式簽名仍是 `deadline=None`。`_disp_record_for` 對 None 也原樣回傳(`deadline = None if deadline is None else ...`),所以沒傳 deadline 時,迴圈走到第一個適用題就拿 float 去比 None。
具體失敗情境:
- 我在 lens-repo 跑 `python3.14 scripts/test_lumos.py -k backing`,結果 40 過 1 敗。敗的是 `t_contract_backing_marked_questions`,錯誤為 `'>' not supported between instances of 'float' and 'NoneType'`。
- 該測試呼叫 `m._dispositions_verdict(d, pf, sha, "feat/disp", sha, "standard")`,沒帶 deadline。
- 另外兩處測試也不帶 deadline,同樣會炸。
- 目前唯一的正式呼叫端有傳 `deadline=_time.monotonic() + _DISP_BUDGET`,所以推送前閘暫時沒事。但這條既定的公開預設是 None,將來任何新呼叫端漏傳就是 traceback。
- 這些改動與本輪「共用時間預算」主題無關,是夾帶的順手修改。
修法:把比較改回 `deadline is not None and ...`,或把簽名預設值改成必填。

佐證:
- file: `scripts/lumos:51464`(簽名 `deadline=None`)
- file: `scripts/lumos:51579`(無守衛的比較)
- file: `scripts/lumos:51458`(`_disp_record_for` 保留 None)
- file: `scripts/test_lumos.py:76848`(測試呼叫不帶 deadline)
- 另見 `scripts/test_lumos.py:78756`、`78762`、`78773`

## finding 2

severity: minor
blocking: 否 — 只在超大 repo 退化成「提交寫法的補充資訊不附」,不拖垮掛鉤,也不崩
引句:「+    r = _lens_git(root, "--literal-pathspecs", "ls-tree", "-r", "-z", "--full-tree", commit, "--",」
問題:
- 成本隨目錄裡的檔案總數增加,不隨候選數增加。輸出整包進記憶體,沒有大小上限,只有 20 秒逾時,預算上限是 `min(20.0, rem)`。
- 逾時或失敗時 `cidx=None`,輸出只多一句「只算到一半」。「只在提交裡」的程式檔和節點都不列,連「兩邊都沒有」的計數也不給。這等於這個功能在那種 repo 不會有結果。
- 先拿 20 秒再給 impact 剩 10 秒,掛鉤 45 秒內仍然夠用,沒有溢出。
實測(合成 repo,50 萬檔放在 `src/`,路徑 100 位元組左右):
- git 的 `ls-tree -r -z` 輸出 51.6MB,耗時約 1.2 秒。
- Python 解析成 dict 共 1.7 秒,峰值 RSS 約 368MB。
- 照此估算,數百萬檔會到 GB 級。
- 候選最多 5 個程式檔加少量連結,用單一 `git cat-file --batch-check` 查是 O(候選) 就夠,不必列整棵樹。
- 威脅模型是單人,50 萬檔以下沒事,所以只列 minor。
佐證:file: `scripts/lumos:49312`

## 已讀,無 finding

- **預算分配:** 程式檔候選、連結、落點、impact 共用同一個 `deadline`,每個迴圈頂端都檢查,且有「算到一半」說明。impact 子行程帶剩餘秒數當 timeout,最多多 1 秒。`_t0` 之後仍會跑 `_platform_test_index` 和渲染,不受預算限制,但這是舊行為。
- **`_write_bytes_atomic` 清暫存:**
  - 暫存檔名帶 pid 和 uuid,用 O_EXCL 建立。
  - `except BaseException` 涵蓋 KeyboardInterrupt,會 unlink 後再往上丟。
  - `os.replace` 是原子的,`--out` 要嘛是舊內容、要嘛是完整新內容。
  - spec-freeze 只吞 OSError 和 ValueError,KeyboardInterrupt 照常往上傳,暫存已清。
  - 唯一的小縫是 `os.open` 成功到進 `try` 之間,實務上可忽略。

我實測時留下的 `gctl-run-*` 暫存現場已刪除。

最高等級 major,blocking 1 條。
