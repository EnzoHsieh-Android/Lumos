severity: major

審查範圍：HEAD `598e41b23f85285d1f9e4429c5d5314f055fc8bc`；只讀指定四份 patch、binding、r1 intake/fix 與 manual lens，未讀其他 R2 報告。`r2-repair.patch` SHA-256 與 binding 的 `0dcdc6f…` 相符。

finding R2-S1：XML 拒收可被合法的非 ASCII XML 編碼繞過。檢查在解析前只搜尋原始 bytes 的 ASCII 字樣；UTF-16 的 DTD/entity 宣告不會命中，之後由 `ElementTree` 接受。這破壞明示的 XML 拒收約定，屬原有漏查，本輪 aggregate 修補未造成但也未補上。

severity: major

blocking: 是

引句:「if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():」

file: `scripts/test_quality.py:129`

最小重現：以純記憶體呼叫 `junit()`，輸入一份合法 UTF-16 JUnit，內容只有一個 passing testcase，並含 DTD／內部 entity 宣告。預期拋出 `ValueError`；實際回傳一筆 `passed`。已重現。無外部服務、無檔案寫入，未使用可操作攻擊 payload。

finding R2-S2：Semgrep 報告只驗 `check_id` 的值，未先驗其型別；非字串值會在 `.split()` 拋出未攔截的 `AttributeError`。CLI 因此無法輸出既定的結構化 `not_assessed` 報告，但仍為失敗關閉，不會誤報 clean。該行是由舊迴圈原樣抽成 helper，屬原有漏查。

severity: minor

blocking: 否

引句:「if item.get('check_id', '').split('.')[-1] != 'same-comparison' or item.get('path') != str(source):」

file: `scripts/test_quality_semgrep.py:28`

無害證據：直接傳入已解析的結果物件，其中 finding 具有效 `start.line` 與 snapshot path，但 `check_id` 為數字；實際得到 `AttributeError`，不會進入 `scan()` 現有的例外收斂清單。

固定席前 8 篇逐條核對：

1. `Issues/vendored測試套件在消費端假紅.md`：lens 只附事故名，未附合約行；修補未見重新擴大 vendored 判定，具體事故合約資格未知。
2. `Systems/lumos-cli-lifecycle.md`：re-inject sentinel 外 byte-equal 路徑未被本輪修補改動。已讀,無 finding。
3. `Systems/lumos-deinit.md`：bytecode 清理只枚舉 `_VENDORED_TOOLKIT` 的 Python stem，拒絕 symlink cache，保留使用者 cache；隔離控制通過。已讀,無 finding。
4. `Systems/lumos-cli-read.md`：修改限 impact 種子分類，search 的 stale／superseded 分流未改。已讀,無 finding。
5. `Systems/bound-tests-gate.md`：本輪未改 code-loop bound-tests 判定或 rc。已讀,無 finding。
6. `Systems/guard-kill.md`：rc 優先序與 JSON purity 路徑均未改。已讀,無 finding。
7. `Systems/授權與歸屬.md`：精確 vendored 白名單不含 LICENSE/COPYING/NOTICE；新增三支 test-quality 模組都有 SPDX，主程式授權檔頭未改。已讀,無 finding。
8. `Systems/測試假綠形態.md`：取消控制先確認子程序已進入，模型逾時控制先確認 fake executable 與 worker pid，輸出超限控制由實際超限結果證明路徑成立；aggregate 修補另有正常 XML 保留控制。已讀,無 finding。

原問題與保留行為核對：

- r1 的 aggregate summary 修補已生效；矛盾 suite/root 與正常 summary 三項控制全綠。
- 輸出上限、SIGTERM 清理、精確 bytecode 清理、部分部署、共同 scanner 入口等 32 項非模型 CLI 控制全綠。
- scanner 21 項控制全綠。
- 依指示未啟動 model command；`test_model_timeout_stops_worker_without_paid_call` 僅做靜態核對，因此該動態資格未知。
- `r1-fix.json` 列出 8 個程式根因組；intake 的 i1/i2 僅有文字處置、未列入 fix JSON。指定材料不足以判定其是否依文件／流程 finding 豁免，未把缺席當成已驗證。
- graph patch 宣稱的五棧重放、15 份 sidecar hash 與 33 項 CLI 全綠未以其他報告補證，本席不採作獨立放行證據。

剩餘固定席列名：

- `Systems/pitfalls-code-loop.md`
- `Systems/design-loop.md`
- `Systems/reversibility-governance-ledger.md`
- `Systems/loop-convergence-recording.md`
- `Systems/doctor-irreversible-hint.md`
- `Systems/lumos-refcheck.md`
- `Systems/check-t-sentinel.md`
- `Systems/check-r-guard.md`
- `Systems/節點範圍與索引守衛.md`
- `Systems/cochange-guard.md`
- `Systems/canary-audit.md`
- `Systems/slim-get-一行安裝.md`
- `Systems/slim-install-安裝器.md`
- `Systems/slim-uninstall-一行卸載.md`
- `Projects/規格落成可驗收條件_計劃.md`
- `Projects/雙向門放行_計劃.md`
- `Projects/引用座標依實際換行_計劃.md`
- `Projects/逃逸自動記_計劃.md`
- `Projects/異常派工單回報輸入錯誤_計劃.md`
- `Systems/judge-severity-gate.md`
- `Systems/core-invariant-baseline.md`

總結: 最嚴重 severity: major；blocking 條數: 1
