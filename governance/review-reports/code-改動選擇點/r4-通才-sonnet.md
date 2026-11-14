severity: minor

## g1 推送前碰到的計劃改走快取後,沒有測試釘住「一定要帶快取」
severity: minor
blocking: 否。這是測試漏洞,現行程式沒錯;能改壞而測試照綠,但被保護的是時限省算,不是條款本身。

- 輸入與路徑:`_choice_push_round` 呼叫 `_choice_guard(rr, rng, at_sha, cache=cache)`。修補拿掉了 `deadline` 與 `_CHOICE_GUARD_FLOOR`。「碰到的計劃」改成只靠 `_choice_requirement` 先填好的快取(鍵 `("spec", rng, at_sha)`),命中就不再吃時限。
- 現行程式正確:`_choice_requirement` 走到判計劃那步前就已回傳不要求,否則一定先寫入快取。
- 壞在哪:修前就算漏掉 `cache=cache`,重算還受 `deadline` 限制。修後 `deadline` 預設是 None,漏掉 `cache=cache` 就變成不設時限的整份圖譜重建。
- 預期與實際:預期有測試會在這個改壞下翻紅,實際是照綠。
- 重現:在修後副本把該行改成 `guard, why = _choice_guard(rr, rng, at_sha)   #`,跑 `python3.14 scripts/test_lumos.py -k spec_gate_push_choice`,輸出 `42 passed, 0 failed`。
- 缺口:`r4-repair-tests.patch` 沒有給這個修補(r3 g1)任何測試。專案裡也沒有任何測試引用 `_CHOICE_GUARD_FLOOR` 或針對 `_choice_guard` 的時限。

引句:「guard, why = _choice_guard(rr, rng, at_sha, cache=cache)   # 碰到的計劃吃判要不要求時的快取(_choice_push_scan)」
file: `scripts/lumos:78571`
歸因:有證據的原有漏查。修前 `_CHOICE_GUARD_FLOOR` 沒有任何測試引用(修前樹 `git show dbdc038622a:scripts/test_lumos.py | grep GUARD_FLOOR` 無輸出)。修後該缺口的風險略升,因為時限被拿掉,屬修補放大。

## 三問答覆

**①原問題的修復效果(修前、修後同一份修後測試檔,只換 `scripts/lumos`)**
- 修前樹是 `dbdc038622a`,修後樹是 `24ec789`;兩邊都用 `python3.14 scripts/test_lumos.py -k <名>`。

| 案例 | 修前 | 修後 |
|---|---|---|
| J1 `t_choice_test_blobs_name_shape` | 3 條紅:`FooTest.bar` 記成 `'?'`、雜湊不變、同時綁 `FooTest.bar` 與 `bar` 時前者是 `'?'` | 6 條全綠 |
| J2 `t_choice_scan_batch_no_ignore` | 紅:真 ast-grep 在 `.gitignore` 寫 `*.kt` 的 repo 底下 `{'a/A.kt': 0, 'b/B.kt': 0}`,整批參數沒帶 `--no-ignore` | 全綠:各 1 個命中,六種旗標一個一次 |
| 直接用 ast-grep 0.51.2 | 整批預設 0 筆 | 整批帶六種旗標 1 筆;逐檔點名本來就是 1 筆 |

- 逐檔點名不受忽略規則影響,所以退回逐檔那條路不需要 `--no-ignore`。

**②翻紅驗證(各改壞一處)**
- 把 `noig` 清空,no_ignore 那兩條紅。
- 句子名也取最後一段,name_shape 兩條紅。
- 整串 `-e` 沒改成 `term.values()`,兩條紅。
- 查表仍用原名 `found.get(n, ())`,三條紅。
- 副檔名路徑樣式改成 `"*"`,三條紅。
- `_CHOICE_BATCH_SHARE` 改成 1.0,share 測試紅。
- 另有一條翻紅釘沒驗:拿掉 `_choice_is_test` 過濾,`t_choice_test_blobs_name_shape` 照綠,但那條靠 `t_choice_kill_test_files_in_test_paths` 守,不算漏。
- 原本就綠的 `t_choice_scan_batch_share`、`t_choice_kill_partial_unverified_rc`、`t_lint_waive_choice_ai_summary`(k1、k2、k3)修前修後都綠,只是補釘,本身不是修復證據。
- 缺修前證據、未判定:k1、k2、k3 的對應程式在修前就正確,所以沒有「修前紅」可證。

**③修補處的正常、錯誤、相鄰路徑**
- 修後跑 `-k t_choice_kill`,83 passed、0 failed,涵蓋 J1 preserve(一般名、反引號名、兩平台同名、子字串名、只改計劃筆記)。
- 修後跑 `-k spec_gate_push_choice`,42 passed、0 failed。
- 修後跑 `-k t_choice_scan`,我只確認單條的 `t_choice_scan_batch_no_ignore` 和 `t_choice_scan_batch_share` 通過,整批 `t_choice_scan` 的最終輸出沒收到,這條列未判定。
- 推送前整圈的 `_choice_push_scan` 回傳形狀從三元組變二元組,呼叫端只有 `_choice_push_round`,測試端只有 `t_choice_scan_batch_budget` 那處,都一致。
- 沒驗的範圍:全套測試;Kotlin 方法名含中文且寫成 `類別.中文方法` 時不算 `_dotted_ident`,會整串找而查不到,這跟專案既有慣例一致,不屬這次修補,沒當 finding。

## 圖譜鏡頭
這次沒附固定席節點(鏡頭計算超時)。自己對照改到的兩個節點:
- `Projects/改動選擇點都要有需求守住_計劃.md`:只多了 `--no-ignore` 與 `類別.方法` 的敘述和兩列依據來源,不影響合約。
- `Systems/規格閘.md`:新增兩條 PITFALL(帶 `[出處:]` `[根因:]` `[test:]`)與改寫兩條 WHY(`--no-ignore` 與 `_dotted_ident`),不影響該節點行為。

暫存已刪(`/private/tmp/lumos-seat-work/code-改動選擇點/通才-sonnet`)。

最嚴重:minor;blocking 共 0 條
