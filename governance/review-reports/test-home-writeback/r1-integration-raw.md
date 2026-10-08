severity: major

## integration-F1

severity: major  
blocking: 是

引句:「只有S13寫回路由用同次g_paths與較廣視圖的交集」

佐證 file: `scripts/lumos:27444`  
佐證 file: `scripts/lumos:27511`  
佐證 file: `scripts/lumos:27611`  
佐證 file: `scripts/lumos:27957`

觀察：推送模式的 `content_notes.own` 逐提交讀取前後版本；但提案的較廣檔案集合仍只從整段範圍的 B/N 端點建立。`g_paths` 雖屬各提交，無法補回只存在於中間提交的測試路徑。

具體輸入：C1 同時修改正式程式、新增 `tests/test_ephemeral.py`、把它加入 TestHome 並寫回教訓；C2 再刪除該測試及其宣告。整段起點與終點都沒有這條路徑。C1 的 `content_notes.own` 與 `g_paths` 都有它，但端點較廣集合沒有；照 spec 實作會把合法的同提交寫回判成落錯家。

判準：逐提交路由既要求使用該提交自己的 `g_paths/content_notes.own`，可核對集合也必須涵蓋該提交前後版本；不能由整段端點集合決定中間提交的路徑是否可作證。

建議：明定並測試中間提交新增後刪除的測試路徑。可為每組保存提交前後的可路由集合，或在 group 建立時用該提交快照完成相同分類；不得改用工作樹，也不得跨提交借證據。

## 風險逐類

- 守衛：有上述誤擋，屬 blocking。
- 併發：只讀既有 Git 快照與 side 快取，未見共享可變狀態新增。
- 效能／資源：每端多一次既有分類掃描且沿用 shebang 快取；若依 finding 改成逐提交分類，需另設成本界線與收據。
- 回退：局部撤除廣視圖即可恢復舊判定，界線清楚。
- 外部送出：沒有網路或外部訊息路徑。
- 不可逆：不遷移資料、不刪治理帳，未見不可逆操作。

最高 severity：major；blocking：1。

其餘已讀無 finding：問題與最小範圍、tag-only、foreign-ref、純測試啟動、S13b、刪除／改名單提交、回退及外部送出。固定圖譜節點沒有正式合約行；既有逐提交 KEY 與本案方向一致。唯讀環境未跑 fixture，提供的 16 通過／8 失敗不冒稱重驗。

已讀材料：`governance/review-reports/test-home-writeback/r1-snapshot.md`、`scripts/lumos`、`scripts/test_lumos.py`、`governance/review-reports/test-home-writeback/preflight-intake.md`、`governance/review-reports/test-home-writeback/r1-graph-context.txt`。