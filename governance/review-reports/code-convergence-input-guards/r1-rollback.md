severity: major

## rollback-F1 — 中間版本測試被端點測試污染，無法證明逐提交路由

severity: major  
blocking: 是

觀察：diff-middle-delete、diff-middle-rename 這些案例建立中間測試前，共通設定已先修改仍存在於起點、終點的 scripts/test_checks.py。TestHome 的舊版歸屬也包含該檔，因此即使把實作退化成只用 B/N 端點測試集合，第一個混合提交仍會靠 scripts/test_checks.py 通過；新增後刪除的 scripts/test_temp.py 是否被逐提交讀到，不影響 rc0。diff-double-rename 同樣從端點既有測試開始改名。

引句:「if case not in ("untouched-test", "symlink-test", "json-home"):」

file: `scripts/test_lumos.py:48008`  
file: `scripts/test_lumos.py:48028`

判準：這違反固定席 `Systems/測試假綠形態` 的硬合約——翻紅釘須先斷言目標現場確實成立。現在方法只檢查最後 rc，沒有確認該案例唯一可用的路由證據確實只存在中間版本。

具體輸入→錯結果：把推送路由暫時退化為每個 group 只取 `g_paths ∩ (routeB ∪ routeN)`；現有三個 middle 案例仍可能得到預期 rc0，而不是翻紅，故圖譜宣稱的「中間新增後刪除／多次改名覆蓋」不成立。

可執行證據：建立隔離 mutant 後跑 `python3 scripts/test_lumos.py -k t_nodehome_optional_test_home_writeback`；修正 fixture 時須讓第一個混合提交只改 src/a.py、節點與中間測試，不再同時修改端點既有測試，並加前置斷言核對每個提交的實際路徑與家歸屬。此席為唯讀且沒有可寫 tmp，未實跑 mutant；以上為逐語句推演。

## rollback-F2 — 新增圖譜行未使用 AGENTS v1.0 的機器欄位

severity: major  
blocking: 是

觀察：多條新增 WHY/PITFALL 把「出處」與測試名寫成散文，而不是 `[出處:…]`、`[test:…]`。受影響至少包括 design-loop 的兩條 PITFALL 與一條 WHY、每支檔有家的中間版本 PITFALL、測試假綠形態的兩條 PITFALL。

引句:「PITFALL:[2026-10-06 快照拒收設計R1 logic-F1]驗句讀取遇一次性I/O失敗後若只清空結果，稍後rawhash讀取恢復會把未驗材料追加，處置閘才quote FAIL而需重記。來源本案R1原報與非法UTF8/不錨對照；防回歸t_canary_carrier_snapshot_io_recovery_rejected」

file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:232`  
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:236`  
file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:91`  
file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:607`  
file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:609`

判準：依本次 AGENTS v1.0，只要求 WHY 有出處、PITFALL 有出處及防回歸測試；不額外要求更嚴欄位。但這些必要資訊仍須使用規定的 `[鍵:值]` 形狀，散文中的「來源／防回歸」不能建立正式機器關聯。

具體輸入→錯結果：圖譜 lint 或後續測試關聯查詢讀取這些新行時，無法把散文測試名辨識為正式 `[test:]` 證據，造成筆記看似有驗證、機器鏈卻沒有。

可執行證據：修正欄位後分別執行 `python3 scripts/lumos lint Systems/design-loop`、`python3 scripts/lumos lint Systems/每支檔有家`、`python3 scripts/lumos lint Systems/測試假綠形態`。本席未執行，以免唯讀審查觸碰帳或快取。

## 固定圖譜鏡頭

- `Systems/design-loop`：程式沒有動處置閘第五步或條款解析；該硬合約不受影響。新增筆記格式問題另見 rollback-F2。
- `Systems/pitfalls-code-loop`：沒有改風險分級或 dispositions，無影響。
- `Systems/bound-tests-gate`：沒有改固定席合約測試執行或 blocked 判定，無影響。
- `Systems/guard-kill`：沒有改 rc 優先序或 JSON stdout，無影響。
- `Systems/授權與歸屬`：沒有改 vendored 清單、deinit 或 SPDX，無影響。
- `Systems/測試假綠形態`：新 nodehome 測試缺現場前置斷言且 fixture 被端點檔污染，破壞此硬合約；見 rollback-F1。
- `Systems/lumos-cli-read`：沒有改 search 的 superseded/stale 過濾，無影響。
- `Systems/lumos-cli-lifecycle`：沒有改 re-inject 或 CLAUDE.md sentinel，無影響。

## 回退與驗證核對

- HEAD 確認為 4f0c979ab1ee524ce3ac5856e6c6556ae1207a9f；baseline 存在。
- 提交順序確認為 a83e2165（測試家寫回）→ 4f0c979a（快照拒收）。
- 當前 SHA256 符合派工資料：CLI `258dec…e7f`、測試 `57a9c…b42`。
- H 的捕捉範圍仍只有 `UnicodeDecodeError`、`OSError`；未知 RuntimeError 仍逸出，首次讀取失敗會在後續 hash/追加前返回 rc2。
- LF/CRLF 使用第一次讀入的原始 bytes 建指紋；非載體未被強制解碼。
- N 的 `include_tests` 預設仍關閉，正式安家、純測試啟動、`g_code` 與 `wb_files` 集合未擴張。
- 圖譜沒有把本批完整測試、CI、PR 或真實輪數下降寫成已完成；553 明確限定舊整合前來源，當前只宣稱 70 項。
- 未跑任何測試、mutant、CI 或 PR；父席正在跑的完整分片未計入本報告。

## 已讀材料

- source：`governance/review-reports/code-convergence-input-guards/r1-source.patch`，524 行
- graph：`governance/review-reports/code-convergence-input-guards/r1-graph.patch`，534 行
- full-index：`governance/review-reports/code-convergence-input-guards/r1-file-index.txt`，238 行
- 定點源码：`scripts/lumos`
- lens：`docs/lumos-toolchain-knowledge/Systems/design-loop.md`
- lens：`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`
- lens：`docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md`
- lens：`docs/lumos-toolchain-knowledge/Systems/guard-kill.md`
- lens：`docs/lumos-toolchain-knowledge/Systems/授權與歸屬.md`
- lens：`docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md`
- lens：`docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md`
- lens：`docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md`
- 其餘 lens 僅列名，依派工要求未讀。

最高級：major  
blocking findings：2