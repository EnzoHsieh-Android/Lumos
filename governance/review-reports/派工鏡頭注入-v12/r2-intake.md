# r2 前置留痕(派工鏡頭注入-v12)

末輪紀律:只審 r1 重寫段(r2-delta.diff)+r1 修復驗收。refcheck/lint 0。

## 收貨三道(五席)
| 席 | 條數 | 最高 | blocking | quote |
|---|---|---|---|---|
| s1 通才 | 6 | blocker | 4 | 全錨 |
| s2 載荷安全 | 4 | major | 2 | 全錨 |
| s3 極端輸入 | 4 | major | 3 | 全錨 |
| arch | 3 | major | 1 | 全錨 |
| ext Codex | 4 | blocker | 4 | 全錨 |
合計 21/blocking 14/blocker 5。r1 修復驗收:五席皆真修(通才席判 2 條「方向對沒收乾淨」重開,已併入本輪折入)。
## 佐證重現
- cx-f1「profile 從工作樹 config 讀」:`scripts/lumos:2622` 附近 load_test_profile 讀 repo_root/.lumos/config.json → HIT。
- cx-f2「快取鍵無版本」:`_lens_cache_path` 鍵=(repo,base,head) → HIT。
- s1-f?「stem lumos 命中 37.8%」:s1 實跑 221/585 → 採。
- s3「整檔刪除 hunk -1,N +0,0」:s3 實測 → HIT。
## 處置
21 條全折(blocker 輪 accepted 必空);v1.2 節整段重寫為第三版。
