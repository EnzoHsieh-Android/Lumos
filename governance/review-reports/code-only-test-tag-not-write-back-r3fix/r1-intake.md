# code-only-test-tag-not-write-back-r3fix r1 收貨紀錄(驗收原迴圈第三輪修正;Enzo 2026-10-05 裁另開新編號)

八席齊了才動工作目錄。report-normalize 八份合格;quote-check 六份全錨,兩句錨不到的都是引 repo 既有程式(不在差異裡),`grep -cF` 在 `scripts/lumos` 各 1 → HIT:判定路徑 #1(`_test_in_tree` 的說明字串)、資安 #5(git grep 呼叫)。
資安席、規格符合席 clean(資安席另列一條推論、沒給等級行——推送時整段共用終點測試清單,編排者寫進天花板 10,不記為發現)。

| id | 席 | 嚴重 | 重現/判讀 | 結論 |
|---|---|---|---|---|
| g1 | 通才 | major | 席實跑三道 rc0:上一版 `[test:test_drop]`,改成 `[test-gone:一串連字號英文:test_drop@1a2b3c4]`;編排者寫成 [S1] ⑤d 第一格,修前紅 | HIT 採信,折:test-gone 整串一致,不去前綴 |
| a1 | 架構對齊 | minor | `_NODEHOME_TAG_PREFIX_RE` 跟既有 `_NS_TR_PREFIX_RE` 重複 | HIT 採信,折(隨 g1 刪掉) |
| c1 | 正確性 | minor | `a [test:x].` 拿掉後 `a .`;[S4] ⑫「後面緊接句號」修前紅 | HIT 採信,折:後面不是英數或中文就連前面空白一起拿 |
| e1 | 邊界 | minor | 標記後接全形標點誤擋;[S4] ⑫「後面緊接全形逗號」修前紅 | HIT 採信,折(同 c1) |
| d1 | 判定路徑 | minor | 席實跑:未追蹤新測試、名稱出現在已提交檔的註解裡 → 推送前 rc0 | HIT 採信,折:天花板 9(兩條件同時湊齊才觸發) |
| k1 | 合約 1 | minor | @ 規則實作套一般綁定與只收小寫,筆記只寫 test-gone、沒測試格 | HIT 採信,折:筆記寫明,補 [S1] ⑤e 兩格(修前就綠) |
| k2 | 合約 2 | minor | ⑫ 三處改動併一個斷言、tab 沒測試 | HIT 採信,折:拆成獨立斷言、補 tab |

輪內有 major → accepted 一條都不帶;refuted 0。
