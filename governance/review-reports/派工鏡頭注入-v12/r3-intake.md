# r3 前置留痕(派工鏡頭注入-v12,上限輪)

只審 v1.2 第三版 delta(r3-delta.diff)+r2 修復驗收。refcheck/lint 0。

## 收貨三道(五席)
| 席 | 條數 | 最高 | blocking | quote |
|---|---|---|---|---|
| s1 通才 | 5 | blocker | 2 | 全錨 |
| s2 載荷安全 | 4 | major | 3 | 全錨 |
| s3 極端輸入 | 7 | major | 6 | 全錨 |
| arch | 2 | major | 1 | 全錨 |
| ext Codex | 3 | blocker | 2 | 1 句錨不到(f1 deadline 引句跨符號)→不採信,內容照折 |
合計 21/blocking 14/blocker 4。r2 修復驗收:五席皆判方向對,五條「沒收乾淨」重開併入本輪。
## 佐證重現
- s1-f1「45 秒總帳沒扣 impact」:dispatch-lens-hook.py INNER_TIMEOUT=45、impact 實測 12–35 → HIT。
- cx-f1「_cochange_transactions git 無 timeout」:`scripts/lumos:13416` 起 subprocess.run 無 timeout → HIT。
- cx-f3「Kotlin 反引號方法名」:KOTLIN_TEST_RE 接受反引號內任意文字 → HIT → 白名單。
- arch-f8「ast 先例」:slim-gen.py:202 ast.walk → HIT。
- s3「symlink 內容=目標路徑」:s3 自建 repo 實測 → 採。
## 處置
20 條採信全折(blocker 輪 accepted 必空),1 條不採信內容照折。第四版=上限;實作時每條驢收一支測試。
