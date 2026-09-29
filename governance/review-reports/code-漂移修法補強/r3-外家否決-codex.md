severity: major

## F1 大小寫不敏感檔案系統會漏掉同提交卷證目錄

severity: major

blocking: 是

引句:「+        out += [x for x in (by_key.get(nfc(d), []) if d else []) if x not in out]」

file: `scripts/lumos:27989`

1. 新邏輯只用 NFC 當 Git 名稱與磁碟名稱的對應鍵，沒有處理大小寫不敏感檔案系統上的實際拼法。Git 記錄 `Code-Review`、磁碟列出 `code-review` 時，兩者指向同一目錄，但 `_drift_c4_same_commit` 回空。若計劃名比對也沒碰巧命中，證據頁會印「查不到」；命中時也只會錯標成「計劃名」，不會標「兩者」。

2. 本機已確認路徑查找不分大小寫：`test -d Governance/review-reports && echo case-insensitive-path-lookup=yes` 輸出 `case-insensitive-path-lookup=yes`。

3. 最小重現：

```sh
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 -B -c 'import runpy;d=runpy.run_path("scripts/lumos");f=d["_drift_c4_same_commit"];f.__globals__["_nodehome_git"]=lambda *_:b"governance/review-reports/Code-Review/r1.md\0";print(f(".","abc123",{"code-review"}))'
```

輸出：

```text
[]
```

預期應回磁碟上的實際名稱 `["code-review"]`。這違反 S1「一律印現存目錄的實際名字」，也讓修正後的證據頁仍可能漏掉真正卷證。

## 圖譜鏡頭逐條判定

- `Systems/存量漂移守衛`：受影響。c4 證據來源在大小寫不同時漏列或標錯來源，破壞本次新增的證據頁行為。
- `Systems/bound-tests-gate`：不影響。固定席合約測試的執行、懸空判定與退出碼未改。
- `Systems/guard-kill`：不影響。殺傷力驗證的退出碼優先序及 JSON 純度路徑未改。
- `Systems/授權與歸屬`：不影響。未增減 `_VENDORED_TOOLKIT`／`_VENDORED_ALL`，也未修改授權檔或移除流程。
- `Systems/測試假綠形態`：現有新增測試有前置斷言，但沒有覆蓋 Git 名稱與磁碟名稱只差大小寫的現場，因此未攔住本項。
- `Systems/lumos-cli-read`：不影響。搜尋的 superseded/stale 過濾契約未改。
- `Systems/lumos-cli-lifecycle`：不影響。re-inject sentinel 外內容保留與生命週期寫入路徑未改。
- `Systems/design-loop`：不影響。設計審處置閘、計劃綁測試及收斂判定未改。

最高等級:major