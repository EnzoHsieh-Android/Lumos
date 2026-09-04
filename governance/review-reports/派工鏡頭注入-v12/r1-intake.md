preflight-4: ran

# r1 前置留痕(派工鏡頭注入-v12)

前掃=編排者開檔核:testmap affected --diff/--repo/--json 存在、.lumos/testmap.json 已建;cochange 在 lumos 為 `_cochange_mine`/`cmd_cochange_rules`;呼叫者反查無既有工具;dispatch-lens 0 篇現況=text 空、hook 不輸出。refcheck/lint 0。

## 收貨三道(五席)
| 席 | 條數 | 最高 | blocking | quote |
|---|---|---|---|---|
| s1 通才 | 8 | blocker | 5 | 全錨 |
| s2 載荷安全 | 5 | blocker | 3 | 全錨 |
| s3 接手的人 | 6 | blocker | 6 | 全錨 |
| arch | 3 | major | 1 | 全錨 |
| ext Codex | 3 | blocker | 2 | 全錨 |
合計 25/blocking 17/blocker 7(同源:三格資料來源讀工作樹)。
## 佐證重現
- cx-f1/s1-f2/s2-f1/s3-f2「testmap 工作樹+stale」:`git check-ignore .lumos/testmap.json`、`built_at_commit` 2026-08-08 → HIT → 去 testmap。
- s1-f3/s2-f2/s3-f1「cochange 挖到 HEAD」:`_cochange_mine(upto="HEAD")` 預設 → HIT → upto=base、設定讀 base。
- s1-f1「呼叫者掃工作樹」:既有 os.walk 慣例讀 read_text → HIT → 改 base blob。
- s3-f3「t_dispatch_lens_base_and_zero 翻紅」:斷言 text=="" → HIT → 驗收改寫。
- s3-f6「pins vs listed 分岔」:cmd_dispatch_lens 判空點 → HIT。
## 處置
25 條全折(blocker 輪 accepted 必空);v1.2 節整段重寫。
## 鏡像核對:20 折入/3 找不到(s1-f7 testmap stale→地圖已拿掉隨之消失,補一句;s2-f3/f4 CJK 邊界→補 ASCII 識別字邊界規則)/2 不符(s1-f1 與 arch-f3 對「grep vs 製程內正規式」意見相反,採架構席既有慣例,兩席都算折入:一條採納一條以理由駁回並留痕)。
