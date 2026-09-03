preflight-4: ran

# r1 前置留痕(派工鏡頭注入-v11-std,由 light 升級)

前掃=light r1 的單席報告已做過機械宣稱驗語意(extract_contracts 只取 INVARIANT、_platform_test_index 例外、resolve_test_refs 吃字串);三條 major 已折入再凍結。refcheck ok/lint 0。

## 收貨三道(五席)

| 席 | 條數 | 最高 | blocking | quote-check | refcheck |
|---|---|---|---|---|---|
| s1 通才 | 6 | blocker | 4 | 全錨 | 11/11 |
| s2 載荷安全 | 4 | major | 3 | 全錨 | 見報告 |
| s3 接手的人 | 7 | major | 4 | 全錨 | 13/13 |
| arch 架構對齊 | 3 | major | 1 | 全錨 | 16/16 |
| ext Codex | 3 | major | 3 | 全錨 | 5/5 |

合計 23(6+4+7+3+3)/blocking 15(4+3+4+1+3)/blocker 1(s1-f1 截斷後分類)——逐檔 grep 數的。

## 佐證重現(編排者)
- s1-f1/cx-f2「截斷後 [test: 落在外」:s1 實跑驗收範例三條合約行 1400+ 字;編排者核 `_lens_contract_lines` 的 `s[:200]` → HIT。
- arch-f1「_classify_one 才是對的 helper」:`scripts/lumos:6372` docstring「單條 ★INVARIANT★ 的綁定狀態:naked/real/fake/dangling(多平台取最壞)」→ HIT。
- cx-f3/s2-f1「空殼測試 rc=0 放行」:`_run_bound_tests` 只看 rc → 開檔核 HIT;首版宣稱撤回。
- s3-f2「索引每節點重建撞 45 秒」:`_platform_test_index` os.walk 全庫 → HIT。

## 處置摘要
23 條全折(blocker 輪 accepted 必空):v1.1 節整段重寫(分類用 _classify_one、餵未截斷原文、既有字彙、四整數小計、索引建一次、整批 fail-open+固定留痕行、「有≠綠」固定尾行、三條界線、同步清單、五種 fixture)。
